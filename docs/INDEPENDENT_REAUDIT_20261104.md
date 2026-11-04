# TGIS 2026-11-04 independent reproduction re-audit (private)

Scope: independent re-execution and acceptance checks against the archived 2026-10-28 research inputs and the validated 2026-11-04 full scientific outputs. This note is not a public release or a claim of unrestricted full-paper end-to-end reproduction.

## Confirmed computational evidence

- GitHub core: 35 research files verified against SHA256SUMS; core joint states (150), adjacent pairs (120), four specifications/eight switches, independent Experiment B (81 roots), 150 target peak solves and negative integrity controls passed in a fresh local run.
- Complete three-volume archived source: 5,403 distinct entries and CRC passed; 5,401 extracted research SHA256 values and 10+3+46 protected inputs matched.
- Seven-scale scientific output: 2,062 field aliases, 14,434 scale comparisons, 60 geometry groups, 1,156 density checkpoints; independent check PASS. Every checkpoint re-verified in 32 contiguous batches; three deliberately corrupted or misbound checkpoints were rejected. The historical complete run combined 572 fresh evaluations with 584 identity-bound same-run resumed evaluations.
- Newly uncached subset: one of 60 geometry groups was re-evaluated from scratch (214 density evaluations, 478 field aliases and 3,346 seven-scale rows), and every declared result row matched the corresponding complete output exactly. Its run's status is PARTIAL by design, not a whole-run PASS.
- Fresh 150-contour recomputation: 150/150 principal PRD targets PASS; extracted contour CSV was byte-identical to the previous verified run, and decompressed geometry payloads were identical despite gzip wrapper SHA differences.
- Fresh 273-source-case P2 computation: 273 cases, 35 genuinely distinct numerical solutions and 144 accepted endpoint pairs; PASS. Source-case CSV and endpoint-change CSV were byte-identical to the previous complete run. JSON summary differed only in elapsed_seconds. Maximum change under double grid: 6.31540062578928e-7.
- Upstream scientific/packaging regressions: 57 final-binding tests, 43 seven-scale acceptance tests, 86 refined-packager tests and 37 legacy synthetic packaging tests all passed; five mocked external-wrapper safety cases and two real-data fault injections were correctly handled. The scientific-contract suite had 73 passes and two tests blocked by unavailable xlrd==2.0.1.

## Unresolved: do not convert to PASS

- The archived provenance QA remains 40 PASS / 42 with two FAIL: the registered safe_domain semantic correction changes one safeguarded function; and 27,970 historical Domain_Records lines retain old producer/input identity hashes whose exact old source has not been located. A two-summit regression supports the corrected attribution semantics but does not resolve old provenance identities.
- The original four-stage frozen Excel processing runner cannot pass in this environment without xlrd==2.0.1; 120/139 explicitly located legacy XLS source cells were independently reread, 19 lack exact locators. Not all 2,950 original publication cells have independent source-page confirmation.
- SSTD 90 pairwise distances were independently checked using archived persistence arrays; original OD-to-persistence generation was not newly executed. Historical native mtlib outputs (153 files) match SHA256, but the native third-party program was not newly rebuilt/run in this pass.
- Only representative headline manuscript figures/tables/text were crosschecked; this pass did not recreate every published graphic.
- Repo remains Private. No public release, DOI, all-author permission or rights clearance is implied. Do not expose third-party yearbooks, WorldPop grids, proprietary coordinates or reviewer files.

The detailed, file-hashed local audit and full rerun receipts are retained in the author-owned evidence package. This Markdown note intentionally excludes private local paths, restricted source assets and unpublished source data.
