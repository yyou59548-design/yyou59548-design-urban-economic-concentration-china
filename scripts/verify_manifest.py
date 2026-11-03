#!/usr/bin/env python3
"""Validate the repository snapshot's complete file inventory and SHA-256 values.

The manifest itself is excluded from the manifest.  The `.git` control
folder and ordinary local Python/venv caches are excluded from the inventory.
"""
from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'SHA256SUMS.txt'
EXCLUDED_DIRS = {'.git', '.venv', '__pycache__', '.pytest_cache', '.mypy_cache'}
EXCLUDED_FILES = {'.DS_Store'}


def sha256(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main():
    actual = {}
    for path in ROOT.rglob('*'):
        if not path.is_file() or any(part in EXCLUDED_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.name in EXCLUDED_FILES or path.name == MANIFEST.name:
            continue
        actual[path.relative_to(ROOT).as_posix()] = sha256(path)
    expected = {}
    for line_no, line in enumerate(MANIFEST.read_text(encoding='utf-8').splitlines(), start=1):
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if match is None:
            raise ValueError(f'Invalid manifest entry on line {line_no}')
        digest, name = match.groups()
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or name in expected or name == MANIFEST.name:
            raise ValueError(f'Unsafe, duplicate or self-referential manifest path on line {line_no}')
        expected[name] = digest
    absent = sorted(expected.keys() - actual.keys())
    unexpected = sorted(actual.keys() - expected.keys())
    mismatches = sorted(name for name in expected.keys() & actual.keys() if expected[name] != actual[name])
    if absent or unexpected or mismatches:
        raise RuntimeError(f'SHA-256 inventory FAIL: missing={absent}, extra={unexpected}, mismatched={mismatches}')
    print(f'PASS: {len(expected)} research files match SHA256SUMS.txt exactly')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        raise SystemExit(1)
