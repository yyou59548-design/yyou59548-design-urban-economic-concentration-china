#!/usr/bin/env python3
"""Check that the archive manifest validator rejects real corruption.

All mutations occur in isolated temporary copies. The repository and its
archived research inputs are never changed by these tests.
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(folder: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, str(folder / "scripts/verify_manifest.py")],
                          cwd=folder, env=env, capture_output=True, text=True)


def main():
    if not __debug__:
        raise RuntimeError("Scientific and integrity assertions require normal Python execution; do not use -O.")
    passed = verify(ROOT)
    assert passed.returncode == 0, passed.stderr
    cases = []
    with tempfile.TemporaryDirectory(prefix="tgis_integrity_negative_") as workspace:
        for name in ("changed_data_byte", "removed_reference", "untracked_file", "changed_manifest_digest"):
            folder = Path(workspace) / name
            shutil.copytree(ROOT, folder, ignore=shutil.ignore_patterns(
                ".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache"))
            if name == "changed_data_byte":
                file = folder / "data/derived/03_Harmonization/Analysis_Vectors.csv"
                with file.open("r+b") as stream:
                    head = stream.read(24)
                    stream.seek(22)
                    stream.write(b"Z" if head[22:23] != b"Z" else b"Y")
            elif name == "removed_reference":
                (folder / "data/references/Joint_States_150.csv").unlink()
            elif name == "untracked_file":
                (folder / "unreviewed.txt").write_text("unexpected", encoding="utf-8")
            elif name == "changed_manifest_digest":
                file = folder / "SHA256SUMS.txt"
                contents = file.read_text(encoding="utf-8")
                file.write_text(("0" if contents[0] != "0" else "1") + contents[1:], encoding="utf-8")
            check = verify(folder)
            assert check.returncode != 0, (name, check.stdout, check.stderr)
            cases.append({"test": name, "rejection": "PASS"})
    print(json.dumps({"status": "PASS", "manifest_baseline": "PASS", "rejected_mutations": cases}, indent=2))


if __name__ == "__main__":
    main()
