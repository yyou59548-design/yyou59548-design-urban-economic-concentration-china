# Urban Economic Concentration in China: Spatial Structure and Changing City Contributions

**Private, pre-publication core replication snapshot — not approved for public release.** This private repository snapshot contains a reproducible **core** of the manuscript's empirical and synthetic calculations. It is not yet a complete archive of every computation in the paper. Source files were selected from the 28 October 2026 research archive and reconciled against the 3 November 2026 manuscript revision.

## What the code independently checks

The core empirical checker reconstructs WGS84 Albers coordinates, GDP shares and Gaussian bandwidth matrices from the supplied 295-city analysis vectors. At 150 **archived continuous peak locations**, it independently evaluates city contributions, validates leading contributor labels and forms 120 adjacent-year comparisons across 30 specifications. It reproduces the exact GDP-ratio and summit-location identity and compares four fresh output tables byte-for-byte against the archived reference tables.

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

## What is **not** proved by these tests

- The empirical audit reads **previously refined summits and component geometries**. It independently checks mass inputs, projections, bandwidths, contributions, identities, labels and adjacent-year records; it does **not** find every continuous peak or regenerate every fixed-level contour from scratch.
- The full research archive separately implements seven-scale verification for 2,062 fields, reconstruction of 150 contours, national/regional mode-count probes, statistical provenance audits and external baselines. Those procedures are **not** included as fresh end-to-end tests in this compact candidate, and their historical logs should not be represented as new runs.
- The 2,950-cell original statistics, third-party publication vintages, spatial boundaries and WorldPop population rasters have **not** been independently authenticated by this core package. The 885 analysis coordinates are derived inputs, not a redistribution of the original raster data.
- Stable, highly overlapping observed annual components do not establish that no unobserved within-year topological transition occurred. The exact contribution identity is descriptive rather than a causal attribution.

See `docs/REPRODUCTION_SCOPE_CN.md` for the detailed audit coverage and known limitations.

## Repository map

`src/` contains the original, unchanged independent joint-state audit and a fresh four-city solver. `data/derived/` contains the declared finite-selection subsets of five archived input tables. `data/references/` contains the archived target CSVs used exclusively for comparisons. `data/PROVENANCE.json` records source and subset SHA-256 identities. `scripts/extract_core_data.py` reproduces the input filtering from the complete archived replication folder. `tests/run_core_checks.py` runs the two scientific checks; `.github/workflows/core-tests.yml` enables a reproducible CI test in the private repository and after any authorized publication.

## Data provenance and access

The original statistical source register, 2011/2019–2023 vintage material, geographic input files and the complete scientific replication corpus are retained by the authors. Some upstream inputs were published by third parties. This candidate intentionally excludes third-party yearbook PDFs, original workbooks, full WorldPop rasters, external copyrighted source code, reviewer correspondence and historical intermediate caches.

The rights for the **derived** GDP and representative-coordinate CSVs still require a final data-sharing review before any public disclosure. The code licensing choice, authorship metadata, and permanent archive link have not been approved. Accordingly, **do not make this candidate publicly accessible before those checks are resolved**; see `docs/PUBLICATION_GATE_CN.md`. No licence is assigned by this draft.

## Integrity and version discipline

Run `python scripts/verify_manifest.py` before the numerical suite. The manifest covers every research file except itself, including the exact UTF-8-BOM/CRLF encoding of the supplied CSV inputs. Do not modify an archived reference table merely to make a numerical test pass. When changing a verified dataset or source program, rerun the independent test suite and regenerate the manifest as part of a new reviewed snapshot.

This private draft contains **no public software or data licence**, and it is not a public data-availability deposit or a DOI-registered replication archive. Do not change repository visibility, publish a release, or cite it as fully reproducible without the publication checks in `docs/PUBLICATION_GATE_CN.md`.
