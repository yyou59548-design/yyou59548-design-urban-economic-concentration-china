#!/usr/bin/env python3
"""Independent theory and 2021 PRD checks; no archived peak coordinates read.

These are deliberately separate from src/joint_state_audit.py and
src/experiment_b_reproduce.py. Gaussian gradients, Hessians and roots are
computed here from the published synthetic configuration or current derived
GDP and longitude/latitude vectors. Checks do not rediscover all peaks or
contours, nor replace the complete research archive.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path

for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(key, "1")

import numpy as np
from scipy.optimize import brentq, root
from pyproj import Transformer

BASE = Path(__file__).resolve().parents[1]
TWOPI = 2.0 * math.pi


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def kernel(z: np.ndarray, xy: np.ndarray, weights: np.ndarray):
    delta = xy - z
    values = weights * np.exp(-0.5 * np.sum(delta * delta, axis=1)) / TWOPI
    height = float(np.sum(values))
    gradient = np.sum(values[:, None] * delta, axis=0)
    hessian = np.einsum("i,ij,ik->jk", values, delta, delta) - height * np.eye(2)
    return values, gradient, hessian


def stationary(xy, weights, seed, expected_kind="maximum"):
    w = np.asarray(weights, float)
    points = np.asarray(xy, float)
    result = root(lambda z: kernel(z, points, w)[1] / kernel(z, points, w)[0].sum(), seed, tol=1e-11)
    values, grad, hess = kernel(result.x, points, w)
    residual = float(np.linalg.norm(grad) / values.sum())
    eig = np.linalg.eigvalsh(hess)
    assert residual < 2e-9, (expected_kind, residual)
    if expected_kind == "maximum":
        assert eig[-1] < 0, (expected_kind, eig)
    elif expected_kind == "saddle":
        assert eig[0] < 0 < eig[1], (expected_kind, eig)
    else:
        raise ValueError(expected_kind)
    return result.x, values, residual, eig


def experiment_b():
    xy = np.array([[-0.8, 0], [0.8, 0], [-2.2, 0.8], [2.2, 0.8]]) / 1.1
    records = []
    for alpha in np.linspace(0.1, 0.9, 81):
        def eq(z):
            ratio = math.exp(z[2])
            w = np.array([0.6 / (1 + ratio), 0.6 * ratio / (1 + ratio), 0.4 * (1 - alpha), 0.4 * alpha])
            v, g, _ = kernel(z[:2], xy, w)
            return [*(g / v.sum()), math.log(v[1] / v[0])]
        answer = root(eq, [0.0, 0.06, 0.0], tol=1e-11)
        residual = float(np.max(np.abs(eq(answer.x))))
        ratio = float(math.exp(answer.x[2]))
        w = np.array([0.6 / (1 + ratio), 0.6 * ratio / (1 + ratio), 0.4 * (1 - alpha), 0.4 * alpha])
        contributions, _, hessian = kernel(answer.x[:2], xy, w)
        assert residual < 1e-9, (alpha, residual)
        assert np.linalg.eigvalsh(hessian)[-1] < 0
        assert set(np.argsort(contributions)[-2:]) == {0, 1}
        records.append({"alpha": float(alpha), "tie_ratio": ratio, "residual": residual})
    checks = {0: 1.408674766311907, 40: 1.0, 80: 0.709887068267809}
    for idx, target in checks.items():
        assert abs(records[idx]["tie_ratio"] - target) < 2e-9
    return {"solutions": len(records), "max_equation_residual": max(row["residual"] for row in records),
            "three_ratios": {"0.10": records[0]["tie_ratio"], "0.50": records[40]["tie_ratio"], "0.90": records[80]["tie_ratio"]}}


def event_order_checks():
    xy = np.array([[-1.0, -0.1], [-0.2, 0.1], [0.2, 0.65], [3.0, -0.2]]) / 0.65
    out = {}
    for label, mass_A in (("contributor_first", 0.45), ("component_first", 0.50)):
        def at(t, which):
            w = np.array([mass_A, 0.4, 0.02 + 0.36 * t, 0.7])
            w /= w.sum()
            seed = (np.array([-0.55, 0.05]) if which == "maximum" else np.array([1.4, 0.1])) / 0.65
            return stationary(xy, w, seed, which)[1]
        anchor = brentq(lambda t: math.log(at(t, "maximum")[0] / at(t, "maximum")[1]), 0, 1, xtol=1e-13)
        merger = brentq(lambda t: at(t, "saddle").sum() / 0.65**2 - 0.016, 0, 1, xtol=1e-13)
        assert (anchor < merger) if label == "contributor_first" else (merger < anchor)
        target = ((0.3424729656594205, 0.4747879198414802) if label == "contributor_first"
                  else (0.6770407279499371, 0.5570911644628365))
        assert max(abs(anchor - target[0]), abs(merger - target[1])) < 1e-8
        out[label] = {"contributor_tie": anchor, "component_saddle_crossing": merger}
    return out


def reflection_information_control():
    xy = np.array([[-2, -0.1], [-2, 0.1], [2, 0]]) / 0.8
    w1 = np.array([0.4, 0.1, 0.5])
    w2 = np.array([0.1, 0.4, 0.5])
    p1, c1, _, _ = stationary(xy, w1, np.array([-2, -0.06]) / 0.8)
    p2, c2, _, _ = stationary(xy, w2, np.array([-2, 0.06]) / 0.8)
    assert np.argmax(c1) == 0 and np.argmax(c2) == 1
    assert np.linalg.norm(p2 - p1 * np.array([1.0, -1.0])) < 1e-8
    max_error = 0.0
    for x in np.linspace(-2.4, 2.4, 17):
        for y in np.linspace(-1.1, 1.1, 13):
            q = np.array([x, y]) / 0.8
            r = q * np.array([1.0, -1.0])
            err = abs(kernel(q, xy, w1)[0].sum() - kernel(r, xy, w2)[0].sum())
            max_error = max(max_error, float(err))
    assert max_error < 1e-13
    return {"peak_A_or_B_changes": True, "max_field_reflection_residual": max_error,
            "interpretation": "The analytic reflection relates complete superlevel filtrations; this finite sample checks its numerical identity, not persistence software."}


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def prd_2021():
    vectors = BASE / "data/derived/03_Harmonization/Analysis_Vectors.csv"
    coords = BASE / "data/derived/03_Harmonization/Analysis_Coordinates.csv"
    v = read_csv(vectors)
    co = read_csv(coords)
    names = sorted({r["city_name"] for r in v})
    assert len(names) == 295
    c = {r["city_name"]: r for r in co if r["scope"] == "A" and r["geo"] == "admin"}
    assert set(names).issubset(c)
    transform = Transformer.from_crs(
        "EPSG:4326", "+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +datum=WGS84 +units=m +no_defs",
        always_xy=True,
    )
    longitude = [float(c[n]["lon"]) for n in names]
    latitude = [float(c[n]["lat"]) for n in names]
    east, north = transform.transform(longitude, latitude)
    xy = np.column_stack([east, north])
    H = (0.5 * len(names) ** (-1.0 / 6.0)) ** 2 * np.cov(xy.T)
    H += 1e-10 * max(float(np.trace(H)), 1.0) * np.eye(2)
    whitened = np.linalg.solve(np.linalg.cholesky(H), xy.T).T
    a, b = names.index("广州市"), names.index("深圳市")
    seed = (whitened[a] + whitened[b]) / 2.0
    out = {}
    for price, target_ratio, expected_label in (
        ("nominal", 1.0956998712571533, "广州市"),
        ("real", 1.096290758025832, "深圳市"),
    ):
        records = {r["city_name"]: float(r["mass"]) for r in v
                   if r["scenario"] == "corrected_scope_A" and r["year"] == "2021" and r["price"] == price}
        assert len(records) == 295, (price, len(records))
        mass = np.array([records[n] for n in names])
        _, contributions, residual, _ = stationary(whitened, mass / mass.sum(), seed)
        label = names[int(np.argmax(contributions))]
        assert label == expected_label, (price, label)
        pair_total = mass[a] + mass[b]
        def margin(log_ratio):
            ratio = math.exp(log_ratio)
            amended = mass.copy()
            amended[a] = pair_total / (1 + ratio)
            amended[b] = pair_total * ratio / (1 + ratio)
            _, values, _, _ = stationary(whitened, amended / amended.sum(), seed)
            return math.log(values[b] / values[a])
        observed_ratio = mass[b] / mass[a]
        tie = brentq(margin, math.log(observed_ratio / 4), math.log(observed_ratio * 4), xtol=1e-12)
        assert abs(math.exp(tie) - target_ratio) < 1e-5, (price, tie)
        out[price] = {"leading_city": label, "gdp_ratio_SZ_to_GZ": float(observed_ratio),
                      "tie_ratio": math.exp(tie), "log_contribution_margin": math.log(contributions[b] / contributions[a]),
                      "stationarity_residual": residual}
    return {"fields": out, "coordinate_sha256": sha256(coords), "mass_vector_sha256": sha256(vectors),
            "scope": "Only 2021 nominal and comparable-growth-chain fields, not all 2,062 GIS fields."}


def main():
    if not __debug__:
        raise RuntimeError("Scientific and integrity assertions require normal Python execution; do not use -O.")
    tests = {"experiment_B": experiment_b(), "two_event_orders": event_order_checks(),
             "reflection": reflection_information_control(), "PRD_2021": prd_2021()}
    print(json.dumps({"status": "PASS", "scope": "independent equations, no archived peak positions or code imports", "tests": tests},
                     ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"FAIL: {type(error).__name__}: {error}", file=sys.stderr)
        raise
