#!/usr/bin/env python3
"""Independent fresh solution of the four-city Gaussian Experiment B.

The 81 supplied rows are used ONLY as post-solve comparison targets. Every
peak coordinate and equal-contribution GDP ratio is solved from the declared
four source positions, total masses, sigma, and alpha. No cached field/peak
values enter the numerical solution.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from scipy.optimize import root

SIGMA = 1.1
POSITIONS = np.array([[-0.8, 0.0], [0.8, 0.0], [-2.2, 0.8], [2.2, 0.8]], dtype=float)
PAIR_MASS = 0.6
SURROUNDING_MASS = 0.4


def evaluate(alpha, variables):
    x, y, log_ratio = map(float, variables)
    ratio = float(np.exp(log_ratio))
    masses = np.array([PAIR_MASS / (1 + ratio), PAIR_MASS * ratio / (1 + ratio),
                       SURROUNDING_MASS * (1 - alpha), SURROUNDING_MASS * alpha])
    p = np.array([x, y])
    dx = p - POSITIONS
    contributions = masses * np.exp(-np.einsum('ij,ij->i', dx, dx) / (2 * SIGMA**2)) / (2 * np.pi * SIGMA**2)
    gradient = -np.sum(contributions[:, None] * dx, axis=0) / SIGMA**2
    hessian = np.einsum('i,ij,ik->jk', contributions / SIGMA**4, dx, dx) - np.eye(2) * contributions.sum() / SIGMA**2
    log_balance = np.log(contributions[1] / contributions[0])
    return np.array([gradient[0], gradient[1], log_balance]), contributions, hessian


def solve(alpha, initial):
    result = root(lambda v: evaluate(alpha, v)[0], initial, method='hybr', tol=1e-12)
    residuals, c, hessian = evaluate(alpha, result.x)
    residual = float(np.max(np.abs(residuals)))
    success = residual < 1e-11 and np.isfinite(result.x).all()
    if not success:
        raise RuntimeError(f'Experiment B solve failed at alpha={alpha}: status {result.success}, residual {residual}')
    max_eigen = float(np.linalg.eigvalsh(hessian)[-1])
    if max_eigen >= -1e-12 or min(c[0], c[1]) <= max(c[2:]):
        raise ValueError(f'Experiment B root not a regular A/B-leading maximum at alpha {alpha}')
    return result.x, residual, max_eigen, c


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True, help='Archived 81-row result, read only for comparison')
    parser.add_argument('--output', type=Path, required=True, help='Fresh output directory')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output directory must not exist, preventing accidental overwrites')
    with args.reference.open(encoding='utf-8-sig', newline='') as file:
        references = list(csv.DictReader(file))
    if len(references) != 81:
        raise ValueError(f'Expected 81 alpha records, found {len(references)}')
    rows = []
    initial = np.array([0., 0., 0.])
    for source in references:
        alpha = float(source['alpha'])
        solution, residual, max_eigen, c = solve(alpha, initial)
        x, y, lr = map(float, solution)
        ratio = float(np.exp(lr))
        row = dict(alpha=alpha, tie_ratio=ratio, peak_x=x, peak_y=y,
                   stationarity_and_log_balance_max_residual=residual,
                   largest_hessian_eigenvalue=max_eigen,
                   other_max_contribution=float(max(c[2:])),
                   A_contribution=float(c[0]), B_contribution=float(c[1]),
                   tie_ratio_difference=ratio-float(source['tie_ratio']),
                   peak_coordinate_difference=float(np.linalg.norm(solution[:2]-[float(source['peak_x']),float(source['peak_y'])])))
        if abs(row['tie_ratio_difference']) > 1e-9 or row['peak_coordinate_difference'] > 1e-8:
            raise ValueError(f'Fresh experiment B solve disagrees with archived answer: {row}')
        rows.append(row)
        initial = solution
    args.output.mkdir(parents=True)
    with (args.output/'experiment_b_fresh_81.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    report={'status':'PASS','fresh_solutions':len(rows),
            'max_absolute_tie_ratio_difference':max(abs(x['tie_ratio_difference']) for x in rows),
            'max_peak_coordinate_difference':max(x['peak_coordinate_difference'] for x in rows),
            'max_stationarity_log_balance_residual':max(x['stationarity_and_log_balance_max_residual'] for x in rows),
            'largest_hessian_eigenvalue':max(x['largest_hessian_eigenvalue'] for x in rows),
            'selected': {str(round(x['alpha'],2)): x['tie_ratio'] for x in rows if min(abs(x['alpha']-a) for a in [.1,.5,.9])<1e-10}}
    (args.output/'experiment_b_fresh_results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
