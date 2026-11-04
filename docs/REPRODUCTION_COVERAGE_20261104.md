# Reproduction evidence and limits (2026-11-04)

**Manuscript:** *Urban Economic Concentration in China: Spatial Structure and Changing City Contributions* (Transactions in GIS revision, submission 7979419).

**Status:** Private, pre-publication validation snapshot. **Core calculations and specific independent mathematical oracles pass; whole-paper source-to-figures reproduction remains unverified in this snapshot.** A PASS for an archive checksum, a saved-peak arithmetic audit or a synthetic root check must not be presented as a PASS for rebuilding all upstream GIS fields.

## Verified again on 4 November 2026

| Evidence | Method | Actual result | Interpretation |
| --- | --- | --- | --- |
| GitHub core test | `tests/run_core_checks.py` on subset inputs and saved peak/component records | PASS; 150 states, 120 adjacent pairs, four specifications/eight switches; four reproduced tables byte-identical; 81 Experiment B roots | Independent checks at **archived** peak locations, not new detection |
| New independent theory test | `tests/run_independent_oracles.py`; separate Gaussian derivatives and root equations | PASS; 81 new Experiment B solutions; both event orders; reflection control | No saved peak coordinates or original production solver used; **specific constructions only** |
| New 150-target PRD peak reconstruction | `tests/run_prd_150_fresh_peaks.py` independently optimizes each targeted peak from 295-city GDP and projected coordinates; archived peak CSV used only after solving | PASS; 150 local peaks, max location gap 7.11e-7 m, 4 specifications/8 switches, 30/30 signed 2021 min and 2022 rise | Fresh **local peak positions**, not 150 full connected polygons or a global enumeration of all peaks |
| New 2021 empirical peak test | The same independent test reprojects 295 supplied cities from WGS84 coordinates, constructs bandwidth and optimizes a continuous peak | PASS; nominal peak: Guangzhou leads, tie ratio about 1.09569987; growth-chain peak: Shenzhen leads, tie ratio about 1.09629076 | Two 2021 PRD fields, **not** all 2,062 GIS fields |
| Cross-platform CSV comparison and its negative controls | `src/table_comparison.py`, `tests/run_table_contract_tests.py` | PASS locally; report byte equality separately, require row/column/category exact equality and per-cell numeric tolerance | Supports cross-platform scientific comparison without rewriting original references |
| Manifest negative tests | `tests/run_integrity_negative_tests.py` | PASS; four deliberately corrupted or incomplete **temporary copies** rejected | Checks the integrity gate's ability to reject tampering, not independent scientific correctness |
| Three 28 October source volumes | `scripts/audit_full_archive.py` on the three author-retained ZIPs and an extracted research folder | PASS; 5,403 unique ZIP entries, all volume CRCs, all 5,401 manifest SHA256 values | **Full archive integrity**, not fresh full scientific computation |
| Protected original/companion input checks | Original `Replication_Inputs/verify_inputs.py` | PASS; 10 principal inputs, three companions, 46 supplemental files | Confirmed archived baseline bytes |
| P₂ finite-decision regression controls | Invoked `negative_regressions()` in the original `Revision_Validation/recompute_p2_contract.py` | PASS; eight finite acceptance/rejection cases | Does not recompute all national/regional P₂ results |

Local recheck environment: Linux, CPython 3.13.5, NumPy 2.3.5, SciPy 1.17.0 and pyproj **3.7.2**. The repository's new CI request pins pyproj **3.8.0**; CI passing must be checked independently after the push. The full archive's frozen Python 3.12 / GIS stack has not been duplicated in this local environment. The 28 October archive includes historical full-run reports; these have not been transformed into new 4 November run claims.

## Items not yet fully executed or authenticated

1. The 2,062 seven-scale qualification records and the full set of upstream density fields and their **global peak enumeration** from raw inputs. All 150 **specified PRD local target peaks** have now also been re-solved from derived mass/coordinate inputs, but this is not the complete multi-region, multi-scale detector.
2. A fresh full 150-contour regeneration and its complete geometric comparisons, rather than reading saved components/peak records.
3. Full national and regional P₂ calculations, source-vintage alternatives, native SSTD/mtlib/Dionysus baseline campaigns, and complete numerical certificates for revised inputs.
4. Independent page-by-page verification of all 2,950 original statistical source cells; reproducible computations do not establish third-party publication authentication.
5. Redistribution rights for some compiled GDP vectors and derived representative coordinates, complete authorship/affiliations, code/data licence, public availability, and permanent archive identifier.

The author-retained October archive reports historical coverage of many of these calculations, but its `New_Validation/Compact_Acceptance.json` is marked **FAIL** for strict cross-platform byte identity despite its separate numerical agreement report. That FAIL is preserved and is **not** converted into a PASS. This November run attempted the archived compact runner and obtained `MISSING_DEPENDENCIES` (`xlrd==2.0.1`). The Python dependency was not obtainable in the sandbox, so the compact four-stage run was **not performed** in this environment.

## Reproduce the core checks (no third-party raw files required)

```bash
python -m pip install -r requirements-core.txt
python scripts/verify_manifest.py
python tests/run_table_contract_tests.py
python tests/run_core_checks.py
python tests/run_independent_oracles.py
python tests/run_prd_150_fresh_peaks.py
python tests/run_integrity_negative_tests.py
```

Both scientific check scripts emit `status=PASS` JSON and terminate nonzero on a failed assertion. The independent checker evaluates specified mathematical configurations and two particular empirical fields; it does not silently import the original numerical solver.

## Independently audit the author's complete, unredistributed archive

The exact original three volumes are (see `scripts/audit_full_archive.py` for the pinned SHA-256 values):

- `TGIS_FINAL_02_Replication_Part1.zip` (363,781,932 bytes)
- `TGIS_FINAL_02_Replication_Part2.zip` (363,778,749 bytes)
- `TGIS_FINAL_02_Replication_Part3.zip` (363,781,967 bytes)

On an authorized machine with the three volumes locally available, extract all their **nonoverlapping paths** into a single folder. Then run, from this GitHub repository:

```bash
python scripts/audit_full_archive.py \
  --part /secure/archive/TGIS_FINAL_02_Replication_Part1.zip \
  --part /secure/archive/TGIS_FINAL_02_Replication_Part2.zip \
  --part /secure/archive/TGIS_FINAL_02_Replication_Part3.zip \
  --root /secure/unpacked/Replication \
  --output /secure/results/full_archive_audit.json
```

The audit checks zip checksums, safe paths, cross-volume duplicates, all extracted release hashes and archived input protection. No raw source inputs are uploaded to GitHub and no network retrieval occurs.

## Continue the genuine upstream computation in a separate controlled environment

The full archive contains the original executable scripts at `Replication_Inputs/04_Reproduction_Code/` and the 28 October numerical/audit commands. On an **isolated copy** of the original extracted folder with storage and dependency versions appropriate for the frozen run:

```bash
cd /secure/unpacked-copy/Replication
python -m pip install -r Replication_Addendum/requirements.txt
python -B Replication_Inputs/verify_inputs.py
python -B Replication_Addendum/run_checks.py --dry-run
python -B Replication_Addendum/run_checks.py --run-label new_external_validation
```

For the **much more extensive** source-to-manuscript pipeline, use the archived `Replication_Inputs/04_Reproduction_Code/reproduce_all.py` and its frozen requirements on a separate copy. Do not conflate the October release's manuscript-generation outputs with the current 3 November manuscript without an explicit diff and scientific consistency review. It writes local outputs and receipts; do not run directly on irreplaceable original archives. A completed run is only accepted when its scientific receipts, expected result tables and numerical tolerances pass; an exit code alone is insufficient.

## Publication gate

**Keep this repository private.** The scripts and subset data have not been granted a public release licence. Some source values originate in third-party publications; derived coordinates have their own upstream licence/attribution questions. Before making the repository public, obtaining a DOI, issuing a public release or asserting complete data availability: verify rights, obtain all author approvals, complete the remaining scientific tests, fix author/citation metadata and update the manuscript's actual data-and-code statement. A private repository URL is not a public archival identifier.

## CI variability discovered and followed up

The first push-triggered GitHub Actions run for commit `1d8bbcb` (run 41804731398) **failed** at an exact-byte comparison of `Joint_States_150.csv`. A separate pull-request run for **the same code commit** (run 41804805757) passed all steps. This history is preserved. The old wrapper did not record the differing cells, so the cause **cannot be inferred as merely floating point** from that failure alone. The updated runner will report exact-byte results *and* compare every cell, rejecting any categorical, structural, or material numerical discrepancies and transparently reporting cells within its explicit numerical tolerance. Negative tests show that changes in a city label, an economically material density, a matrix entry, a residual above tolerance, or the row count fail. This is a scientific comparability check, **not** a claim of exact byte reproducibility.

The updated CI also invokes the core checker twice in one job, alongside the explicit table-comparison negative tests; numerical equivalence and byte identity are displayed separately. Six separate local PYTHONHASHSEED settings passed with exact reference byte identity on the local platform, but this does not demonstrate cross-platform byte identity.
