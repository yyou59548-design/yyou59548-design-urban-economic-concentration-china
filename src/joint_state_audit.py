#!/usr/bin/env python3
"""Audit current PRD component/contributor states and exact log-odds changes.

Run with Python 3 and NumPy; no original pipeline imports or GIS dependency:
    python joint_state_audit.py --baseline /path/to/TGIS_GDP_Source_Closure_FINAL

The packaged default looks under ../Replication_Inputs, either directly or in
its TGIS_GDP_Source_Closure_FINAL subdirectory. All five required input files
retain their original relative paths. Outputs default to this script's folder.

Sign convention (the manuscript's eq:logmargin and eq:finite-margin-change):
    log_odds = log(C_SZ/C_GZ)
             = log(G_SZ/G_GZ) + (s_SZ-s_GZ)' H^-1 [p-(s_SZ+s_GZ)/2].
At fixed locations and H, its annual change is the direct log-GDP-ratio change
plus (p_to-p_from)' H^-1 (s_SZ-s_GZ). Absolute imbalance is abs(log_odds).

This is an independent arithmetic/join audit of saved continuous summits and
sampled components, not a new peak search, contour extraction, or certificate
that no component event occurred between observed annual endpoints.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


SCENARIO = "corrected_scope_A"
SCOPE = "A"
YEARS = tuple(range(2019, 2024))
BANDWIDTHS = (0.40, 0.45, 0.50, 0.55, 0.60)
PRICES = ("nominal", "real")
# These explicit identity mappings were checked in all five supplied tables.
# Unknown labels fail rather than being silently attached to a different point set.
GEO_MAPPING = {"admin": "admin", "pop2020": "pop2020", "pop2023": "pop2023"}
GEO_LABELS = {"admin": "DataV", "pop2020": "WorldPop 2020", "pop2023": "WorldPop 2023"}
INPUTS = {
    "domains": "05_Recomputed_Results/National_2011_2023/Domain_Records.csv",
    "local_peaks": "06_Robustness/Joint_Location_GDP_Bandwidth/Local_Continuous_Peaks.csv",
    "sequences": "06_Robustness/Joint_Location_GDP_Bandwidth/Five_Year_Sequences.csv",
    "vectors": "03_Harmonization/Analysis_Vectors.csv",
    "coordinates": "03_Harmonization/Analysis_Coordinates.csv",
}
LOG_IDENTITY_TOL = 1e-10
PATTERN_GUARD = 1e-9
PEAK_MATCH_TOL_M = 1e-3
RELATIVE_TOL = 1e-11
ALBERS_DESCRIPTION = "+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +datum=WGS84 +units=m +no_defs"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def array_signature(values):
    encoded = json.dumps(values.tolist(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


def as_bool(value):
    require(str(value).lower() in ("true", "false"), f"Unresolved Boolean: {value!r}")
    return str(value).lower() == "true"


def geo_key(value):
    require(value in GEO_MAPPING, f"Unknown geography label {value!r}; verify the mapping first")
    return GEO_MAPPING[value]


def seq_key(row):
    return (row["scenario"], row["scope"], geo_key(row["geo"]), row["price"], float(row["b"]))


def state_key(row):
    return (*seq_key(row), int(row["year"]))


def index_unique(rows, key, name):
    output = {}
    for row in rows:
        k = key(row)
        require(k not in output, f"Duplicate {name} key: {k}")
        output[k] = row
    return output


def resolve_baseline(argument):
    root = argument if argument is not None else Path(__file__).resolve().parent.parent / "Replication_Inputs"
    candidates = [root, root / "TGIS_GDP_Source_Closure_FINAL"]
    valid = [p.resolve() for p in candidates if all((p / rel).is_file() for rel in INPUTS.values())]
    require(len(valid) == 1, f"Expected one baseline with all five input CSVs under {root}; found {valid}")
    return valid[0]


def project_albers_wgs84(rows, names):
    """Independent ellipsoidal Albers forward equations for the declared CRS.

    Parameters are the WGS84 semi-major axis and inverse flattening, and the
    baseline model's 25/47 degree standard parallels, 0 latitude of origin,
    and 105 degree central meridian. The implementation does not import the
    baseline projection, numerical model, or stored contributor calculations.
    """
    semi_major = 6378137.0
    flattening = 1.0 / 298.257223563
    eccentricity_sq = flattening * (2.0 - flattening)
    eccentricity = math.sqrt(eccentricity_sq)

    def authalic_q(latitude):
        sine = np.sin(latitude)
        return (1.0 - eccentricity_sq) * (
            sine / (1.0 - eccentricity_sq * sine * sine)
            - np.log((1.0 - eccentricity * sine) / (1.0 + eccentricity * sine)) / (2.0 * eccentricity)
        )

    first, second = np.radians([25.0, 47.0])
    m_first = np.cos(first) / np.sqrt(1.0 - eccentricity_sq * np.sin(first) ** 2)
    m_second = np.cos(second) / np.sqrt(1.0 - eccentricity_sq * np.sin(second) ** 2)
    cone = (m_first * m_first - m_second * m_second) / (authalic_q(second) - authalic_q(first))
    constant = m_first * m_first + cone * authalic_q(first)
    latitude = np.radians([float(rows[name]["lat"]) for name in names])
    longitude = np.radians([float(rows[name]["lon"]) for name in names])
    radius = semi_major * np.sqrt(constant - cone * authalic_q(latitude)) / cone
    origin_radius = semi_major * np.sqrt(constant - cone * authalic_q(0.0)) / cone
    angle = cone * (longitude - np.radians(105.0))
    return np.column_stack((radius * np.sin(angle), origin_radius - radius * np.cos(angle)))


def bandwidth_matrix(coordinates, b):
    scale = b * len(coordinates) ** (-1.0 / 6.0)
    matrix = scale * scale * np.cov(coordinates.T, ddof=1)
    matrix += max(float(np.trace(matrix)), 1.0) * 1e-10 * np.eye(2)
    return matrix


def strict_2021_minimum(values):
    return all(values[2] + PATTERN_GUARD < value for i, value in enumerate(values) if i != 2)


def minimum_years(values):
    least = min(values)
    return "|".join(str(year) for year, value in zip(YEARS, values) if value <= least + PATTERN_GUARD)


def component_signature(row):
    # Equal endpoint signatures do not establish a continuous path with no event.
    return (
        row["status"], row["continuous_status"], row["geometry_status"],
        row["target_component_count_8"], row["target_component_count_4"],
        row["holes"], row["touches_grid_boundary"], row["peak_inside_domain"],
    )


def feature_signature(row):
    return (row["base_peaks_inside"], row["stable_peaks_inside"], row["reference_branch_is_highest_detected_peak"])


def write_csv(path, rows):
    require(rows, f"No rows to write: {path.name}")
    keys = list(rows[0])
    require(all(set(row) == set(keys) for row in rows), f"Inconsistent output columns: {path.name}")
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def run(baseline, output):
    paths = {name: baseline / rel for name, rel in INPUTS.items()}
    raw = {name: read_csv(path) for name, path in paths.items()}
    domains = [r for r in raw["domains"] if r["scenario"] == SCENARIO
               and r["is_PRD_reference"] == "True" and int(r["max_dim"]) == 360
               and int(r["year"]) in YEARS and r["threshold_rule"] == "scenario_2019_fixed"]
    local = [r for r in raw["local_peaks"] if r["scenario"] == SCENARIO and int(r["year"]) in YEARS]
    original_sequences = [r for r in raw["sequences"] if r["scenario"] == SCENARIO]
    vectors = [r for r in raw["vectors"] if r["scenario"] == SCENARIO and int(r["year"]) in YEARS]
    coordinates = [r for r in raw["coordinates"] if r["scope"] == SCOPE]
    expected_sequences = set(itertools.product([SCENARIO], [SCOPE], GEO_MAPPING.values(), PRICES, BANDWIDTHS))
    expected_states = {(*key, year) for key in expected_sequences for year in YEARS}
    domain_by = index_unique(domains, state_key, "domain")
    local_by = index_unique(local, state_key, "local peak")
    original_seq_by = index_unique(original_sequences, seq_key, "five-year sequence")
    require(set(domain_by) == expected_states, "Domain records do not cover exactly the expected 150 fields")
    require(set(local_by) == expected_states, "Local peaks do not cover exactly the expected 150 fields")
    require(set(original_seq_by) == expected_sequences, "Sequences do not cover exactly the expected 30 specifications")

    vector_rows = defaultdict(dict)
    for row in vectors:
        key = (row["scenario"], row["scope"], int(row["year"]), row["price"])
        require(row["city_name"] not in vector_rows[key], f"Duplicate vector city: {key}, {row['city_name']}")
        vector_rows[key][row["city_name"]] = row
    names = sorted(vector_rows[(SCENARIO, SCOPE, 2019, "nominal")])
    require(len(names) == 295, f"Expected 295 cities, found {len(names)}")
    expected_vectors = set(itertools.product([SCENARIO], [SCOPE], YEARS, PRICES))
    require(set(vector_rows) == expected_vectors, "Missing or extra principal mass vector")
    masses = {}
    share_residuals = []
    for key, rows in vector_rows.items():
        require(set(rows) == set(names), f"City set differs for {key}")
        values = np.array([float(rows[name]["mass"]) for name in names])
        require(np.isfinite(values).all() and (values > 0).all(), f"Non-positive or nonfinite mass: {key}")
        error = float(np.max(np.abs(values / values.sum() - np.array([float(rows[name]["share"]) for name in names]))))
        require(error < 2e-12, f"Stored shares do not match actual masses: {key}")
        share_residuals.append(error)
        masses[key] = values
    coordinate_rows = defaultdict(dict)
    for row in coordinates:
        key = geo_key(row["geo"])
        require(row["city_name"] not in coordinate_rows[key], f"Duplicate coordinate: {key}, {row['city_name']}")
        coordinate_rows[key][row["city_name"]] = row
    require(set(coordinate_rows) == set(GEO_MAPPING.values()), "Coordinate geography set differs")
    for key, rows in coordinate_rows.items():
        require(set(rows) == set(names), f"Coordinate city set differs for {key}")
    xy_by = {geo: project_albers_wgs84(rows, names) for geo, rows in coordinate_rows.items()}
    gz, sz = names.index("广州市"), names.index("深圳市")
    states = []
    details = {}
    checks = defaultdict(list)
    int_geometry = ("target_component_count_8", "target_component_count_4", "base_peaks_inside", "stable_peaks_inside", "holes", "superlevel_component_count_8", "superlevel_component_count_4")
    bool_geometry = ("peak_regular", "peak_converged", "touches_grid_boundary", "peak_inside_domain", "reference_branch_is_highest_detected_peak")

    for key in sorted(expected_states):
        scenario, scope, geo, price, b, year = key
        domain, peak = domain_by[key], local_by[key]
        require(domain["region"] == "China" and domain["projection"] == "china", f"Unexpected projection: {key}")
        mass = masses[(scenario, scope, year, price)]
        mass_sha = array_signature(mass)
        require(mass_sha == domain["input_mass_sha256"] == peak["input_mass_sha256"], f"Mass hash mismatch: {key}")
        require(all(as_bool(peak[field]) for field in ("converged", "regular", "stationarity_pass", "top_two_are_GZ_SZ")), f"Unresolved local peak: {key}")
        require(peak["anchor_status"] == "numerically_resolved_unique", f"Unresolved contributor: {key}")
        xy = xy_by[geo]
        matrix = np.asarray(json.loads(domain["H"]), dtype=float)
        matrix_recomputed = bandwidth_matrix(xy, b)
        h_relative_error = float(np.max(np.abs(matrix - matrix_recomputed)) / np.max(np.abs(matrix)))
        require(h_relative_error < RELATIVE_TOL, f"Bandwidth does not match locations: {key}")
        require(np.all(np.linalg.eigvalsh(matrix) > 0), f"Nonpositive bandwidth: {key}")
        inverse = np.linalg.inv(matrix)
        point = np.array([float(peak["peak_x"]), float(peak["peak_y"])])
        domain_point = np.array([float(domain["peak_x"]), float(domain["peak_y"])])
        point_gap = float(np.linalg.norm(point - domain_point))
        require(point_gap <= PEAK_MATCH_TOL_M, f"Local and component summit mismatch: {key}")
        displacement = point - xy
        distance_sq = np.einsum("ij,jk,ik->i", displacement, inverse, displacement)
        log_contributions = (np.log(mass / mass.sum()) - math.log(2.0 * math.pi)
                             - 0.5 * np.linalg.slogdet(matrix)[1] - 0.5 * distance_sq)
        order = np.argsort(log_contributions)[::-1]
        recomputed_anchor = names[int(order[0])]
        require(recomputed_anchor == peak["anchor_city"] == domain["current_anchor"] == domain["highest_detected_summit_city"], f"Contributor labels differ: {key}")
        require({names[int(order[0])], names[int(order[1])]} == {"广州市", "深圳市"}, f"Wrong leading contributor pair: {key}")
        require(log_contributions[order[0]] - log_contributions[order[1]] > float(peak["numeric_log_tolerance"]), f"Unresolved recomputed label: {key}")
        stored_gz, stored_sz = float(peak["C_GZ"]), float(peak["C_SZ"])
        require(stored_gz > 0 and stored_sz > 0, f"Nonpositive saved contributions: {key}")
        recomputed_gz, recomputed_sz = math.exp(log_contributions[gz]), math.exp(log_contributions[sz])
        c_error = max(abs(recomputed_gz / stored_gz - 1.0), abs(recomputed_sz / stored_sz - 1.0))
        require(c_error < RELATIVE_TOL, f"Independent contributions do not match: {key}")
        log_odds = math.log(stored_sz / stored_gz)
        direct = math.log(mass[sz] / mass[gz])
        spatial = float((xy[sz] - xy[gz]) @ inverse @ (point - (xy[sz] + xy[gz]) / 2.0))
        residual = log_odds - direct - spatial
        saved_margin_error = log_odds - float(peak["log_contribution_margin_SZ_GZ"])
        recomputed_log_error = log_odds - float(log_contributions[sz] - log_contributions[gz])
        require(max(abs(residual), abs(saved_margin_error), abs(recomputed_log_error)) < LOG_IDENTITY_TOL, f"Signed identity mismatch: {key}")
        state = {
            "scenario": scenario, "scope": scope, "geo": geo, "geo_label": GEO_LABELS[geo], "price": price, "b": b, "year": year,
            "field_id": domain["field_id"], "input_mass_sha256": mass_sha,
            "threshold_rule": domain["threshold_rule"], "max_dim": int(domain["max_dim"]), "projection": domain["projection"],
            "level": float(domain["level"]), "status": domain["status"], "continuous_status": domain["continuous_status"], "geometry_status": domain["geometry_status"],
            **{field: int(domain[field]) for field in int_geometry},
            **{field: as_bool(domain[field]) for field in bool_geometry},
            "component_anchor": domain["current_anchor"], "local_anchor": peak["anchor_city"], "recomputed_anchor": recomputed_anchor,
            "highest_detected_summit_city": domain["highest_detected_summit_city"], "anchor_status": peak["anchor_status"],
            "domain_peak_x_m": domain_point[0], "domain_peak_y_m": domain_point[1], "local_peak_x_m": point[0], "local_peak_y_m": point[1],
            "local_domain_peak_distance_m": point_gap, "contour_area_km2": float(domain["contour_area_km2"]),
            "jaccard_vs_2019_reference": float(domain["jaccard_vs_2019_reference"]),
            "adjacent_year_jaccard": float(domain["adjacent_year_jaccard"]) if domain["adjacent_year_jaccard"] else "",
            "adjacent_year_status": domain["adjacent_year_status"],
            "G_GZ": mass[gz], "G_SZ": mass[sz], "total_city_mass": float(mass.sum()),
            "GZ_x_m": xy[gz, 0], "GZ_y_m": xy[gz, 1], "SZ_x_m": xy[sz, 0], "SZ_y_m": xy[sz, 1], "H_json": domain["H"],
            "C_GZ_saved": stored_gz, "C_SZ_saved": stored_sz, "C_GZ_recomputed": recomputed_gz, "C_SZ_recomputed": recomputed_sz,
            "signed_log_odds_from_C": log_odds, "absolute_log_odds": abs(log_odds),
            "direct_log_GDP_ratio": direct, "spatial_summit_distance_term": spatial,
            "annual_identity_residual": residual, "saved_margin_residual": saved_margin_error,
            "independent_contribution_log_odds_residual": recomputed_log_error,
            "max_pair_contribution_relative_error": c_error, "H_reconstruction_relative_error": h_relative_error,
        }
        states.append(state)
        details[key] = {"state": state, "domain": domain, "peak": peak, "H": matrix, "inverse": inverse, "point": point, "xy": xy}
        for name, value in (("local_domain_peak_distance_m", point_gap), ("annual_identity_residual", abs(residual)),
                            ("saved_margin_residual", abs(saved_margin_error)), ("contribution_log_odds_residual", abs(recomputed_log_error)),
                            ("pair_contribution_relative_error", c_error), ("H_reconstruction_relative_error", h_relative_error)):
            checks[name].append(float(value))

    transitions, decompositions, sequence_output = [], [], []
    for key in sorted(expected_sequences):
        scenario, scope, geo, price, b = key
        annual = [details[(*key, year)] for year in YEARS]
        original = original_seq_by[key]
        original_hashes = json.loads(original["input_vector_sha256_by_year"])
        labels = [entry["state"]["local_anchor"] for entry in annual]
        margins = [entry["state"]["signed_log_odds_from_C"] for entry in annual]
        absolute = [abs(value) for value in margins]
        direct_values = [entry["state"]["direct_log_GDP_ratio"] for entry in annual]
        spatial_values = [entry["state"]["spatial_summit_distance_term"] for entry in annual]
        require("|".join(labels) == original["ordered_anchors"], f"Saved sequence labels differ: {key}")
        for year, entry, margin in zip(YEARS, annual, margins):
            require(original_hashes[str(year)] == entry["state"]["input_mass_sha256"], f"Sequence vector hash mismatch: {key}, {year}")
            require(abs(margin - float(original[f"margin_{year}"])) < LOG_IDENTITY_TOL, f"Saved sequence margin differs: {key}, {year}")
        signed_minimum = strict_2021_minimum(margins)
        signed_rise = margins[3] - margins[2] > PATTERN_GUARD
        require(signed_minimum == as_bool(original["strict2021minimum"]) and signed_rise == as_bool(original["rise2022"]), f"Saved signed patterns differ: {key}")
        require(as_bool(original["all_peak_checks_pass"]), f"Saved sequence has unresolved peak checks: {key}")
        group_transitions = []
        for left, right in zip(annual, annual[1:]):
            old, new = left["state"], right["state"]
            old_domain, new_domain = left["domain"], right["domain"]
            require(np.array_equal(left["H"], right["H"]), f"Bandwidth changes within sequence: {key}")
            require(math.isclose(old["level"], new["level"], rel_tol=1e-12, abs_tol=0.0), f"Contour level is not frozen: {key}")
            require(new_domain["adjacent_year_status"] == "defined" and int(float(new_domain["adjacent_year_reference"])) == old["year"], f"Undefined or wrong adjacent geometry: {key}")
            require(0 <= new["adjacent_year_jaccard"] <= 1, f"Invalid adjacent overlap: {key}")
            changed = old["local_anchor"] != new["local_anchor"]
            signature_changed = component_signature(old) != component_signature(new)
            delta_odds = new["signed_log_odds_from_C"] - old["signed_log_odds_from_C"]
            direct_delta = math.log((new["G_SZ"] / new["G_GZ"]) / (old["G_SZ"] / old["G_GZ"]))
            spatial_delta = float((right["point"] - left["point"]) @ left["inverse"] @ (left["xy"][sz] - left["xy"][gz]))
            residual = delta_odds - direct_delta - spatial_delta
            require(abs(residual) < LOG_IDENTITY_TOL, f"Annual-change identity mismatch: {key}, {new['year']}")
            require(abs(spatial_delta - (new["spatial_summit_distance_term"] - old["spatial_summit_distance_term"])) < LOG_IDENTITY_TOL, f"Summit-distance term mismatch: {key}")
            checks["change_identity_residual"].append(abs(residual))
            prefix = {"scenario": scenario, "scope": scope, "geo": geo, "geo_label": GEO_LABELS[geo], "price": price, "b": b, "year_from": old["year"], "year_to": new["year"]}
            transition = {
                **prefix, "anchor_from": old["local_anchor"], "anchor_to": new["local_anchor"], "contributor_label_changed": changed,
                "endpoint_component_diagnostics_changed": signature_changed,
                "endpoint_feature_diagnostics_changed": feature_signature(old) != feature_signature(new),
                "endpoint_component_signature_from": json.dumps(component_signature(old), ensure_ascii=False),
                "endpoint_component_signature_to": json.dumps(component_signature(new), ensure_ascii=False),
                "global_component_count_8_from": old["superlevel_component_count_8"], "global_component_count_8_to": new["superlevel_component_count_8"],
                "adjacent_jaccard": new["adjacent_year_jaccard"], "area_from_km2": old["contour_area_km2"], "area_to_km2": new["contour_area_km2"],
                "area_change_km2": new["contour_area_km2"] - old["contour_area_km2"],
                "area_change_percent": 100 * (new["contour_area_km2"] / old["contour_area_km2"] - 1),
                "domain_peak_displacement_m": math.hypot(new["domain_peak_x_m"] - old["domain_peak_x_m"], new["domain_peak_y_m"] - old["domain_peak_y_m"]),
                "local_peak_displacement_m": float(np.linalg.norm(right["point"] - left["point"])),
                "signed_log_odds_from": old["signed_log_odds_from_C"], "signed_log_odds_to": new["signed_log_odds_from_C"],
                "signed_log_odds_change": delta_odds, "absolute_log_odds_change": new["absolute_log_odds"] - old["absolute_log_odds"],
                "frozen_level": old["level"], "interpretation": "Observed endpoint diagnostics; no claim of no intervening component event",
            }
            transitions.append(transition)
            group_transitions.append(transition)
            decompositions.append({
                **prefix, "G_GZ_from": old["G_GZ"], "G_SZ_from": old["G_SZ"], "G_GZ_to": new["G_GZ"], "G_SZ_to": new["G_SZ"],
                "C_GZ_from": old["C_GZ_saved"], "C_SZ_from": old["C_SZ_saved"], "C_GZ_to": new["C_GZ_saved"], "C_SZ_to": new["C_SZ_saved"],
                "signed_log_odds_from_C_from": old["signed_log_odds_from_C"], "signed_log_odds_from_C_to": new["signed_log_odds_from_C"],
                "signed_log_odds_change": delta_odds,
                "direct_log_GDP_ratio_from": old["direct_log_GDP_ratio"], "direct_log_GDP_ratio_to": new["direct_log_GDP_ratio"],
                "direct_log_GDP_ratio_change": direct_delta,
                "spatial_summit_distance_term_from": old["spatial_summit_distance_term"], "spatial_summit_distance_term_to": new["spatial_summit_distance_term"],
                "spatial_summit_distance_change": spatial_delta,
                "reconstructed_signed_change": direct_delta + spatial_delta, "change_identity_residual": residual,
                "spatial_change_reinforces_direct_change": direct_delta * spatial_delta > 0,
                "contributor_label_changed": changed,
            })
        sequence_output.append({
            "scenario": scenario, "scope": scope, "geo": geo, "geo_label": GEO_LABELS[geo], "price": price, "b": b,
            "annual_states": len(annual), "adjacent_pairs": len(group_transitions), "ordered_anchors": "|".join(labels),
            "adjacent_label_changes": sum(r["contributor_label_changed"] for r in group_transitions),
            "label_change_intervals": "|".join(f"{r['year_from']}-{r['year_to']}" for r in group_transitions if r["contributor_label_changed"]),
            "endpoint_component_diagnostic_changes": sum(r["endpoint_component_diagnostics_changed"] for r in group_transitions),
            "all_states_active_resolved": all(e["state"]["status"] == "active" and e["state"]["geometry_status"] == "resolved" for e in annual),
            "all_reference_branches_highest_detected": all(e["state"]["reference_branch_is_highest_detected_peak"] for e in annual),
            "minimum_adjacent_jaccard": min(r["adjacent_jaccard"] for r in group_transitions),
            "minimum_reference_2019_jaccard": min(e["state"]["jaccard_vs_2019_reference"] for e in annual),
            "minimum_area_km2": min(e["state"]["contour_area_km2"] for e in annual), "maximum_area_km2": max(e["state"]["contour_area_km2"] for e in annual),
            "maximum_abs_annual_area_change_percent": max(abs(r["area_change_percent"]) for r in group_transitions),
            "maximum_annual_peak_displacement_m": max(r["domain_peak_displacement_m"] for r in group_transitions),
            "signed_minimum_years": minimum_years(margins), "signed_strict_2021_minimum": signed_minimum, "signed_rise_2022": signed_rise,
            "absolute_minimum_years": minimum_years(absolute), "absolute_strict_2021_minimum": strict_2021_minimum(absolute), "absolute_rise_2022": absolute[3] - absolute[2] > PATTERN_GUARD,
            "direct_ratio_strict_2021_minimum": strict_2021_minimum(direct_values), "direct_ratio_rise_2022": direct_values[3] - direct_values[2] > PATTERN_GUARD,
            "spatial_term_strict_2021_minimum": strict_2021_minimum(spatial_values), "spatial_term_rise_2022": spatial_values[3] - spatial_values[2] > PATTERN_GUARD,
            **{f"signed_log_odds_{year}": value for year, value in zip(YEARS, margins)},
            **{f"direct_log_GDP_ratio_{year}": value for year, value in zip(YEARS, direct_values)},
            **{f"spatial_summit_distance_term_{year}": value for year, value in zip(YEARS, spatial_values)},
        })

    require(len(states) == 150 and len(transitions) == 120 and len(sequence_output) == 30 and len(decompositions) == 120, "Output coverage mismatch")
    change_rows = [row for row in transitions if row["contributor_label_changed"]]
    summary_by_interval = []
    for price in PRICES:
        for year in YEARS[:-1]:
            rows = [r for r in decompositions if r["price"] == price and r["year_from"] == year]
            summary_by_interval.append({
                "price": price, "year_from": year, "year_to": year + 1, "specifications": len(rows),
                "direct_log_GDP_ratio_change": rows[0]["direct_log_GDP_ratio_change"],
                "spatial_change_min": min(r["spatial_summit_distance_change"] for r in rows), "spatial_change_max": max(r["spatial_summit_distance_change"] for r in rows),
                "signed_change_min": min(r["signed_log_odds_change"] for r in rows), "signed_change_max": max(r["signed_log_odds_change"] for r in rows),
                "spatial_reinforces_direct_count": sum(r["spatial_change_reinforces_direct_change"] for r in rows),
            })
    pattern_columns = ("signed_strict_2021_minimum", "signed_rise_2022", "absolute_strict_2021_minimum", "absolute_rise_2022", "direct_ratio_strict_2021_minimum", "direct_ratio_rise_2022", "spatial_term_strict_2021_minimum", "spatial_term_rise_2022")
    geometry_counts = {field: dict(Counter(str(r[field]) for r in states)) for field in ("status", "continuous_status", "geometry_status", *int_geometry, *bool_geometry)}
    results = {
        "status": "PASS", "scope": "Independent joins and arithmetic verification of current saved finite annual states",
        "scenario": SCENARIO, "years": list(YEARS), "threshold_rule": "scenario_2019_fixed", "max_dim": 360,
        "counts": {"annual_states": len(states), "adjacent_pairs": len(transitions), "five_year_sequences": len(sequence_output), "mass_vectors": len(masses), "cities_per_vector": len(names),
                   "adjacent_label_changes": len(change_rows), "sequences_with_any_label_change": sum(r["adjacent_label_changes"] > 0 for r in sequence_output),
                   "active_resolved_single_peak_zero_hole_endpoint_states": sum(
                       r["status"] == "active" and r["continuous_status"] == "active" and r["geometry_status"] == "resolved"
                       and r["target_component_count_8"] == r["target_component_count_4"] == 1
                       and r["base_peaks_inside"] == r["stable_peaks_inside"] == 1 and r["holes"] == 0
                       and not r["touches_grid_boundary"] and r["peak_inside_domain"]
                       and r["reference_branch_is_highest_detected_peak"] for r in states),
                   "endpoint_component_diagnostic_changes": sum(r["endpoint_component_diagnostics_changed"] for r in transitions),
                   "endpoint_feature_diagnostic_changes": sum(r["endpoint_feature_diagnostics_changed"] for r in transitions),
                   "unresolved_principal_peak_checks": 0, "unavailable_adjacent_overlaps": sum(r["adjacent_jaccard"] == "" for r in transitions)},
        "geo_mapping": GEO_MAPPING,
        "observed_geo_labels_by_input": {"domains": sorted({r["geo"] for r in domains}), "local_peaks": sorted({r["geo"] for r in local}), "sequences": sorted({r["geo"] for r in original_sequences}), "coordinates": sorted({r["geo"] for r in coordinates})},
        "geometry_counts": geometry_counts,
        "geometry_summary": {"minimum_adjacent_jaccard": min(r["adjacent_jaccard"] for r in transitions), "minimum_reference_2019_jaccard": min(r["jaccard_vs_2019_reference"] for r in states),
                             "minimum_jaccard_among_label_changes": min(r["adjacent_jaccard"] for r in change_rows),
                             "max_abs_adjacent_area_change_percent": max(abs(r["area_change_percent"]) for r in transitions),
                             "max_adjacent_domain_peak_displacement_m": max(r["domain_peak_displacement_m"] for r in transitions)},
        "endpoint_joint_counts": [{"contributor_label_changed": label, "endpoint_component_diagnostics_changed": component,
                                   "count": sum(r["contributor_label_changed"] == label and r["endpoint_component_diagnostics_changed"] == component for r in transitions)}
                                  for label, component in itertools.product((False, True), repeat=2)],
        "changing_configurations": [r for r in sequence_output if r["adjacent_label_changes"] > 0],
        "label_change_geometry": change_rows,
        "pattern_counts_out_of_30": {column: sum(r[column] for r in sequence_output) for column in pattern_columns},
        "absolute_pattern_exceptions": [{key: r[key] for key in ("geo", "price", "b", "absolute_minimum_years", "absolute_rise_2022")} for r in sequence_output if not r["absolute_strict_2021_minimum"] or not r["absolute_rise_2022"]],
        "decomposition_summary_by_price_and_interval": summary_by_interval,
        "identity_verification": {"maximum_absolute_residuals": {name: max(values) for name, values in checks.items()}, "maximum_share_reconstruction_residual": max(share_residuals),
                                  "actual_mass_sha_matches": 150, "local_component_coordinate_matches": 150, "independent_contributor_label_matches": 150,
                                  "pair_contributions_independently_recomputed": 300, "sign_convention": "log(C_SZ / C_GZ); positive favors Shenzhen",
                                  "spatial_term_source": "Independent WGS84 Albers coordinates and actual summit coordinates; not inferred by subtracting log margins"},
        "tolerances": {"log_identity_absolute": LOG_IDENTITY_TOL, "annual_pattern_log_guard": PATTERN_GUARD, "local_domain_peak_match_m": PEAK_MATCH_TOL_M, "relative_contribution_and_H": RELATIVE_TOL},
        "projection": ALBERS_DESCRIPTION,
        "limitations": ["Equal observed endpoint component diagnostics and high Jaccard are not certificates of no event between observations.",
                        "Saved continuous summits are checked against independent fields and each other; no exhaustive peak search or fresh contour extraction is claimed.",
                        "A highest detected component summit is not a certificate that every stationary point in the plane was found.",
                        "The direct GDP-ratio and summit-displacement terms are exact descriptive identities, not causal effects or inflation decompositions."],
        "sources": {name: {"relative_path": INPUTS[name], "sha256": sha256(paths[name])} for name in INPUTS},
        "implementation": {"script_sha256": sha256(Path(__file__)), "python": sys.version.split()[0], "numpy": np.__version__, "dependencies": ["numpy"]},
    }
    output.mkdir(parents=True, exist_ok=True)
    tables = {"Joint_States_150.csv": states, "Adjacent_Transitions_120.csv": transitions, "Joint_Sequences_30.csv": sequence_output, "Contribution_Decomposition_120.csv": decompositions}
    for name, rows in tables.items():
        write_csv(output / name, rows)
    results["output_csv_sha256"] = {name: sha256(output / name) for name in tables}
    (output / "joint_state_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    write_notes(output / "Joint_State_Audit_Notes.md", results)
    print(json.dumps({"status": results["status"], "counts": results["counts"], "patterns": results["pattern_counts_out_of_30"], "geometry": results["geometry_summary"], "max_residuals": results["identity_verification"]["maximum_absolute_residuals"]}, ensure_ascii=False, indent=2))


def write_notes(path, results):
    counts = results["counts"]
    pattern = results["pattern_counts_out_of_30"]
    geometry = results["geometry_summary"]
    error = results["identity_verification"]["maximum_absolute_residuals"]
    config_lines = ["| Geography | Weights | b | Labels, 2019–2023 | Changing intervals | Minimum adjacent Jaccard |", "|---|---|---:|---|---|---:|"]
    for row in results["changing_configurations"]:
        config_lines.append(f"| {row['geo_label']} | {row['price']} | {row['b']:.2f} | {row['ordered_anchors']} | {row['label_change_intervals']} | {row['minimum_adjacent_jaccard']:.10f} |")
    text = f"""# Joint state and contribution decomposition audit

## Reproduction

Run `python joint_state_audit.py` in this folder after placing the supplied baseline
under `../Replication_Inputs/`, either directly or in its
`TGIS_GDP_Source_Closure_FINAL` subfolder. Alternatively run
`python joint_state_audit.py --baseline /path/to/TGIS_GDP_Source_Closure_FINAL`.
Use `--output /path/to/output` to select another destination. Python 3 and NumPy
are the only dependencies. The JSON records SHA-256 hashes of the five exact
input CSVs, the script, and all four generated CSVs.

## Selection and independent checks

The selection is scenario `corrected_scope_A`, scope A, PRD reference,
`max_dim=360`, years 2019–2023, and `threshold_rule=scenario_2019_fixed`.
Geography labels were inspected in all contributing tables; `admin`, `pop2020`,
and `pop2023` correspond directly and are not guessed from row order.
The resulting {counts['annual_states']} component records join one-to-one to the
same number of local continuous peaks and to {counts['five_year_sequences']} five-year sequences.
There are {counts['adjacent_pairs']} adjacent-year pairs.

{counts['active_resolved_single_peak_zero_hole_endpoint_states']} of 150 states are active and have resolved sampled geometry, one target
component under each of 4- and 8-neighbour connectivity, one detected base peak,
one detected stable peak, zero holes, no edge contact, and the continued branch
is the highest detected component peak. These properties are audited from the
saved records; a new exhaustive stationary-point or contour search is not claimed.
Minimum adjacent physical Jaccard is {geometry['minimum_adjacent_jaccard']:.15f};
minimum overlap with each specification's own 2019 component is
{geometry['minimum_reference_2019_jaccard']:.15f}.

The script independently projects the actual 295-city coordinate vectors using
the declared ellipsoidal WGS84 Albers equations, reconstructs H including its
recorded jitter, reads actual masses from `Analysis_Vectors.csv`, recomputes all
source contributions at the saved continuous summit, and verifies source-vector
hashes. The maximum local-versus-component summit discrepancy is
{error['local_domain_peak_distance_m']:.6g} m. Maximum relative H reconstruction
error is {error['H_reconstruction_relative_error']:.6g}; maximum relative error in
the independently recomputed Guangzhou/Shenzhen contributions is
{error['pair_contribution_relative_error']:.6g}. All 150 contributor labels match.

## Joint observed states

There are {counts['adjacent_label_changes']} adjacent-year contributor changes in
{counts['sequences_with_any_label_change']} specifications. The recorded endpoint
component signature differs in {counts['endpoint_component_diagnostic_changes']} of 120 pairs; area and peak position can still
change. `Adjacent_Transitions_120.csv` gives every overlap, area change, and peak
displacement, including all label-changing pairs.

{chr(10).join(config_lines)}

This is an endpoint diagnostic cross-tab. It does **not** assert that no merger,
split, birth, or death occurred between annual observations. A one-component
target count is also separate from the number of other components in the national field.

## Exact signed decomposition

Use `log_odds = log(C_SZ/C_GZ)`, so positive values favour Shenzhen. For fixed
coordinates and H, the exact adjacent-year identity is

`change(log_odds) = log[(G_SZ_to/G_GZ_to)/(G_SZ_from/G_GZ_from)]
                    + (p_to-p_from)' H^(-1) (s_SZ-s_GZ)`.

The first term uses actual masses; the second is independently evaluated from
projected locations, H, and the summit displacement. The left-hand side is read
independently as the log ratio of saved positive `C_SZ` and `C_GZ`, with those
contributions also independently recomputed. The spatial term is not obtained
as a residual. Maximum absolute annual-level identity residual is
{error['annual_identity_residual']:.6g} log units; maximum change-identity residual
over all 120 pairs is {error['change_identity_residual']:.6g} log units.

Signed 2021 minima and signed 2022 rises occur in
{pattern['signed_strict_2021_minimum']}/30 and {pattern['signed_rise_2022']}/30 sequences.
For absolute imbalance `abs(log_odds)`, the counts are
{pattern['absolute_strict_2021_minimum']}/30 and {pattern['absolute_rise_2022']}/30.
The direct city GDP-ratio term itself has the 2021 minimum and 2022 rise in
{pattern['direct_ratio_strict_2021_minimum']}/30 and {pattern['direct_ratio_rise_2022']}/30
specifications. Thus these temporal orderings already exist in the two underlying
GDP-ratio series; the spatial term affects their magnitudes and the contributor
label. The JSON supplies direct and spatial changes by price and year interval.
These are descriptive identities and finite sensitivity comparisons, not a
causal mechanism or an inflation decomposition.

## Files

- `Joint_States_150.csv`: joined annual geometry, local summits, labels, actual
  pair masses, independent contributions, and level decomposition.
- `Adjacent_Transitions_120.csv`: annual label changes and physical geometry changes.
- `Joint_Sequences_30.csv`: all five-year configurations and signed/absolute patterns.
- `Contribution_Decomposition_120.csv`: exact direct and spatial change decomposition.
- `joint_state_results.json`: aggregate counts, exceptions, tolerances, checks,
  source hashes, and individual geometry records for label-changing pairs.
"""
    path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    arguments = parser.parse_args()
    run(resolve_baseline(arguments.baseline), arguments.output.resolve())


if __name__ == "__main__":
    main()
