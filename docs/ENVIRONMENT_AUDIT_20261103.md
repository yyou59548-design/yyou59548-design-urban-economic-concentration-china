# Environment and whole-archive reproduction status

Independent core suite (Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0): **PASS**. The source-filtering script was run separately, and the five filtered data tables were byte-identical to those shipped here.

Source-archive verification: **PASS**, with 10 baseline files, 3 required companions and 46 supplementary files matching their archived hashes. The three research archive volumes were independently ZIP-CRC verified and had 5,403 unique paths.

The complete computational archive requires a different, historically frozen environment (Python 3.12.14, `xlrd==2.0.1`, `pyproj==3.8.0`, `shapely==2.2.0`, `networkx==3.7`, etc.). In this testing environment `xlrd` was absent. A package-install attempt was unsuccessful because the package index could not be reached. This missing module blocks the root four-stage runner, including the provenance and official-growth stages. The isolated `joint_state_audit.py` does not require this module and did pass.

An additional attempt was made to rerun the archived seven-scale engine with `--max-groups 1 --workers 1` using a new output directory. The engine reported a 2,062-field catalogue, 1,156 unique density evaluations and 60 geometry groups. It produced 52 intermediate checkpoint files, but did **not** complete the first selected group under the 240-second process limit (exit 124). Its partial checkpoints are **not** accepted or interpreted as validated results. The full run and acceptance gate remain outstanding.

This file records scope to prevent a numerical subset test or earlier archived receipts from being misrepresented as a newly executed end-to-end run.
