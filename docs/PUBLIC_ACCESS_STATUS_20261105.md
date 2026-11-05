# Public access and reproducibility status (5 November 2026)

**Repository:** https://github.com/yyou59548-design/yyou59548-design-urban-economic-concentration-china  
**Current visibility:** Public (verified from GitHub repository metadata).  
**Scientific scope:** Executable **core** validation, not a full source-statistics-to-every-paper-result archive.

## Publicly accessible here

The repository contains Python core checks, 295-city analysis-vector subsets and three representative-location definitions, archived target CSVs and numerical tests. The commands below check 150 PRD states, 120 adjacent comparisons, 30 specifications, 81 independently solved Experiment B tie states, and the independently solved 150 target-peak set. The GitHub Actions workflow also runs core verification.

```bash
python -m pip install -r requirements-core.txt
python scripts/verify_manifest.py
python tests/run_table_contract_tests.py
python tests/run_core_checks.py
python tests/run_independent_oracles.py
python tests/run_prd_150_fresh_peaks.py
python tests/run_integrity_negative_tests.py
```

## Separate scientific evidence

A 4 November 2026 re-execution on the **author-retained full three-volume research archive** passed declared numerical tests for **2,062 seven-scale field records, 150 PRD component contours and 273 P₂ source-version cases (144 endpoint comparisons)**. The calculation identities, precise scope and known exceptions are documented in [UPSTREAM_REEXECUTION_20261104.md](UPSTREAM_REEXECUTION_20261104.md). These full calculations **cannot be reproduced with this compact public checkout alone**; their complete original inputs and production programs were not uploaded.

The same audit retains two historical source/code hash-binding FAILs, an unverified frozen Excel-dependent stage, incomplete third-party statistical authentication, and third-party baseline native reruns outside this round's scope.

## Licence, author approval and data rights

The repository was made public before complete sign-off on third-party derived-data redistribution and code/data licences. There is **no LICENSE file and no DOI**. Under GitHub's licensing guidance, public visibility permits access, but it does not make this an unrestricted open-source dataset or grant general reuse permission. The source yearbooks, population rasters and third-party native code are not included.

## Appropriate editorial reference

The repository URL identifies **publicly accessible core replication materials**. A manuscript Data and code availability statement should describe that precise scope and separately identify restricted original-source materials and author-retained full-archive calculations. Do not claim this repo alone provides full end-to-end reproduction or a permanent research-data DOI.

See [PUBLICATION_GATE_CN.md](PUBLICATION_GATE_CN.md) for outstanding rights and submission checks. Other dated audits record conditions at their original execution dates and have deliberately not been rewritten.
