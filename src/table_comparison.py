#!/usr/bin/env python3
"""Strict CSV structure and scientific-value comparison with transparent float tolerance.

Production results must preserve row order, column order, identifiers, labels,
statuses, boolean values and nonnumeric strings exactly. Numbers may differ
only by <= 2e-11 relative + 1e-17 absolute; explicitly declared numerical
identity residuals may vary below the paper's 1e-10 acceptance bound.

Return both byte_identity and semantic_identity. Never overwrite a reference,
never interpret a semantic match as byte identity, and fail closed for invalid
or missing CSV values.
"""
from __future__ import annotations
import csv
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

REL_TOL = Decimal("2e-11")
ABS_TOL = Decimal("1e-17")
RESIDUAL_GUARD = Decimal("1e-10")


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def decimal_value(v):
    try:
        d = Decimal(str(v))
        return d if d.is_finite() else None
    except (InvalidOperation, TypeError, ValueError):
        return None


def compare_one(reference, actual, key):
    if reference == actual and type(reference) is type(actual):
        return True, "exact"
    if isinstance(reference, bool) or isinstance(actual, bool):
        return False, "boolean changed"
    dr, da = decimal_value(reference), decimal_value(actual)
    if dr is not None and da is not None:
        # Identity residuals are numerical error measures, not substantive outcomes.
        if "residual" in key.lower() and max(abs(dr), abs(da)) <= RESIDUAL_GUARD:
            return True, "bounded numerical residual"
        diff = abs(dr - da)
        if diff <= ABS_TOL + REL_TOL * max(abs(dr), abs(da)):
            return True, "numeric tolerance"
        return False, f"numeric disagreement delta={diff}"
    if isinstance(reference, dict) and isinstance(actual, dict):
        if set(reference) != set(actual):
            return False, "JSON object keys changed"
        statuses = [compare_one(reference[k], actual[k], f"{key}.{k}")[0] for k in reference]
        return (all(statuses), "structured JSON numeric agreement" if all(statuses) else "JSON member changed")
    if isinstance(reference, list) and isinstance(actual, list):
        if len(reference) != len(actual):
            return False, "JSON sequence length changed"
        statuses = [compare_one(a,b,f"{key}[{i}]")[0] for i,(a,b) in enumerate(zip(reference,actual))]
        return all(statuses), "structured JSON numeric agreement" if all(statuses) else "JSON sequence member changed"
    if isinstance(reference, str) and isinstance(actual, str) and reference[:1] in ("{", "[") and actual[:1] in ("{", "["):
        try:
            a = json.loads(reference)
            b = json.loads(actual)
        except (ValueError, TypeError):
            return False, "malformed or changed structured text"
        return compare_one(a, b, key)
    return False, "non-numeric text changed"


def compare_csv(reference: Path, actual: Path):
    refpath, actualpath = Path(reference), Path(actual)
    with refpath.open(newline="", encoding="utf-8-sig") as f:
        rr = csv.DictReader(f)
        ref_header = rr.fieldnames
        ref_rows = list(rr)
    with actualpath.open(newline="", encoding="utf-8-sig") as f:
        ar = csv.DictReader(f)
        actual_header = ar.fieldnames
        actual_rows = list(ar)
    errors = []
    changed_cells = 0
    if ref_header != actual_header:
        errors.append("column names/order changed")
    if len(ref_rows) != len(actual_rows):
        errors.append(f"row count changed: {len(ref_rows)}->{len(actual_rows)}")
    if not errors:
        for i,(r,a) in enumerate(zip(ref_rows,actual_rows),start=1):
            for col in ref_header:
                if r[col] == a[col]:
                    continue
                changed_cells += 1
                accepted,reason = compare_one(r[col], a[col], col)
                if not accepted and len(errors)<10:
                    errors.append(f"row {i}, column {col}: {reason}; expected={r[col][:70]!r}, got={a[col][:70]!r}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "byte_identical": sha256(refpath) == sha256(actualpath),
        "semantic_equivalent": not errors,
        "columns": len(ref_header or []),
        "reference_rows": len(ref_rows),
        "actual_rows": len(actual_rows),
        "differing_text_cells": changed_cells,
        "tolerance": {"relative": str(REL_TOL), "absolute": str(ABS_TOL), "identity_residual_max": str(RESIDUAL_GUARD)},
        "errors": errors,
    }
