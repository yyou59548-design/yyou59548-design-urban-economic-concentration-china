# Urban Economic Concentration in China: Spatial Structure and Changing City Contributions

**Public core-replication repository (visibility verified 5 November 2026; no express reuse licence assigned).** This repository contains an executable **core** of the manuscript's empirical and synthetic calculations. It is not yet a complete archive of every computation in the paper. Source files were selected from the 28 October 2026 research archive and reconciled against the 3 November 2026 manuscript revision.

**Access and scope:** https://github.com/yyou59548-design/yyou59548-design-urban-economic-concentration-china is publicly viewable. The complete original-source-to-results archive, copyrighted statistical originals and third-party raster inputs are **not** contained here. Author/data rights and an explicit reuse licence remain to be resolved. See [current access status](docs/PUBLIC_ACCESS_STATUS_20261105.md) and the [separate full-archive re-execution receipts](docs/UPSTREAM_REEXECUTION_20261104.md).

## What the code independently checks

The core empirical checker reconstructs WGS84 Albers coordinates, GDP shares and Gaussian bandwidth matrices from the supplied 295-city analysis vectors. At 150 **archived continuous peak locations**, it independently evaluates city contributions, validates leading contributor labels and forms 120 adjacent-year comparisons across 30 specifications. It reproduces the exact GDP-ratio and summit-location identity and compares four fresh output tables against archived references. Both byte identity and strict per-cell scientific agreement are reported; changes to labels, statuses, row order, or materially different numerical results fail.

The synthetic checker solves the stationary-point and equal-contribution equations **afresh** for all 81 parameter values in Experiment B, using the four coordinates, GDP masses and bandwidth written in the paper. It checks the negative-definite Hessian and that the two focal cities are the leading contributors. Archived results are comparison targets, not solver inputs.

These tests recover 4 specifications with 8 observed annual contributor changes, a minimum adjacent-year Jaccard overlap of 0.9689207388 among label-changing pairs, and the Experiment B tie ratios 1.4086747663, 1.0000000000 and 0.7098870683 at surrounding-GDP allocation parameters 0.10, 0.50 and 0.90.

## Run the checked core

Use Python 3.13 and the pinned dependencies in `requirements-core.txt` (also tested here with NumPy 2.3.5 and SciPy 1.17.0).

```bash
python -m venv .venv
# Activate the environment appropriate for your operating system.
python -m pip install -r requirements-core.txt
python tests/run_core_checks.py
```

Expected result: a JSON object with `"status": "PASS"`. The tests create outputs in a temporary directory; no publication source files or input data are overwritten, no network requests are made by the scripts, and no external installation is attempted by the scripts themselves.


## 4 November 2026 independent audit extension

In addition to the original archived-peak joint-state check, `tests/run_independent_oracles.py` computes Gaussian gradients and stationary points **without reading saved peaks**. It independently solves **81 Experiment B contributor ties**, the **two opposite event-order constructions**, a **reflection/source-attribution control**, and the **2021 Pearl River Delta nominal and comparable-growth-chain peak/tie** using the supplied 295-city masses and geographic coordinates. Its results have been checked in a separate local Linux run. These checks add evidence for specific propositions and examples; they do **not** reconstruct all national fields, full contours or original statistical publications. `tests/run_table_contract_tests.py` confirms that limited numeric formatting drift is reported separately from exact byte identity and that substantive discrepancies are rejected. `tests/run_prd_150_fresh_peaks.py` independently resolves all 150 declared PRD target local peaks from GDP masses and three coordinate definitions (with the archived peak table used only for post-solution comparisons), recovers 4 specifications/8 observed label changes and the 30/30 signed-margin pattern. It does **not** regenerate the full component contours. `tests/run_integrity_negative_tests.py` tests rejection of a changed input byte, a missing reference, an untracked file and a changed manifest. Both are included in CI.

The author-retained three-volume 28 October 2026 source archive has also been inspected **without uploading its content to GitHub**. Its 5,403 distinct ZIP entries passed CRC validation; 5,401 extracted file hashes passed the original release manifest; and the protected input verification passed. See `docs/REPRODUCTION_COVERAGE_20261104.md` and the read-only `scripts/audit_full_archive.py` for precise commands and scope. That specific ZIP/file scan is an **archive-integrity pass**, distinct from scientific recomputation. Separately, an author-retained full-archive execution on 4 November recomputed 2,062 seven-scale field records, 150 principal PRD contours and 273 P₂ source-version cases, with numerical PASS receipts in [UPSTREAM_REEXECUTION_20261104.md](docs/UPSTREAM_REEXECUTION_20261104.md). The complete upstream programs and third-party original data are **not** included here. The frozen four-stage Excel source replay remains unverified in that execution environment because `xlrd==2.0.1` was unavailable.

To run the extended checked core:

```bash
python -m pip install -r requirements-core.txt
python scripts/verify_manifest.py
python tests/run_table_contract_tests.py
python tests/run_core_checks.py
python tests/run_independent_oracles.py
python tests/run_prd_150_fresh_peaks.py
python tests/run_integrity_negative_tests.py
```

## What is **not** proved by these tests

- The **original joint-state core audit** reads previously refined summits and component geometries; the separate core peak test independently re-solves 150 targeted peaks. This GitHub checkout does not regenerate all fixed-level component contours or certify an exhaustive list of every stationary point.
- The author-retained full archive has **separate** newly audited re-executions for the 2,062 fields, 150 principal contours and 273 P₂ cases. These PASS receipts cannot be treated as tests that an external user can rerun using only this GitHub checkout. Historical source/producer identity audit still has two unresolved failures.
- The 2,950-cell original statistics, third-party publication vintages, spatial boundaries and WorldPop population rasters have **not** been independently authenticated by this core package. The 885 analysis coordinates are derived inputs, not a redistribution of the original raster data.
- Stable, highly overlapping observed annual components do not establish that no unobserved within-year topological transition occurred. The exact contribution identity is descriptive rather than a causal attribution.

See `docs/REPRODUCTION_SCOPE_CN.md` for the detailed audit coverage and known limitations.

## Repository map

`src/` contains the original, unchanged independent joint-state audit and a fresh four-city solver. `data/derived/` contains the declared finite-selection subsets of five archived input tables. `data/references/` contains the archived target CSVs used exclusively for comparisons. `data/PROVENANCE.json` records source and subset SHA-256 identities. `scripts/extract_core_data.py` reproduces the input filtering from the complete archived replication folder. `tests/run_core_checks.py` runs the two scientific checks; `.github/workflows/core-tests.yml` enables a reproducible CI test in this publicly visible repository.

## Data provenance and access

The original statistical source register, 2011/2019–2023 vintage material, geographic input files and the complete scientific replication corpus are retained by the authors. Some upstream inputs were published by third parties. This candidate intentionally excludes third-party yearbook PDFs, original workbooks, full WorldPop rasters, external copyrighted source code, reviewer correspondence and historical intermediate caches.

The owner has made this repository public, but the redistribution permissions for some **derived** GDP and representative-point data, complete co-author approvals, software/data licensing and a permanent DOI have **not** been independently confirmed. No `LICENSE` or `CITATION.cff` has been assigned. Public visibility is not an open-source licence or unrestricted data permission. The current review requirements and excluded third-party material are documented in [PUBLICATION_GATE_CN.md](docs/PUBLICATION_GATE_CN.md).

## Integrity and version discipline

Run `python scripts/verify_manifest.py` before the numerical suite. The manifest covers every research file except itself, including the exact UTF-8-BOM/CRLF encoding of the supplied CSV inputs. Do not modify an archived reference table merely to make a numerical test pass. When changing a verified dataset or source program, rerun the independent test suite and regenerate the manifest as part of a new reviewed snapshot.

This public checkout currently carries **no express software or data reuse licence**, and it is not a DOI-registered or full-paper replication deposit. A GitHub URL or commit permalink identifies the accessible core files; it does not replace legal authorization for reuse or an original-data-to-results archive.
