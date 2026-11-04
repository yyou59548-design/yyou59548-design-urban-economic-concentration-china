#!/usr/bin/env python3
"""Run both *fresh* research checks and enforce archived output identity.

This checks principal PRD end-point attribution and Experiment B's 81 regular
contributor ties. It does not regenerate the 2,062 seven-scale fields or all
150 new contours; see README.md for the exact boundary.
"""
import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from table_comparison import compare_csv

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'data/references'
EXPECTED_CSV={
 'Joint_States_150.csv':150,
 'Adjacent_Transitions_120.csv':120,
 'Joint_Sequences_30.csv':30,
 'Contribution_Decomposition_120.csv':120,
}


def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def lines_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return sum(1 for _ in csv.DictReader(f))


def run_cmd(command):
    env=os.environ.copy()
    env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
    completed=subprocess.run(command,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if completed.returncode:
        raise RuntimeError(f'Command exited {completed.returncode}: {command}\n{completed.stdout[-2500:]}')
    return completed.stdout


def main():
    with tempfile.TemporaryDirectory(prefix='tgi_core_check_') as temp:
        parent=Path(temp)
        joint=parent/'joint'
        exp=parent/'experiment_b'
        run_cmd([sys.executable,'-B',str(ROOT/'src/joint_state_audit.py'),'--baseline',str(ROOT/'data/derived'),'--output',str(joint)])
        j=json.loads((joint/'joint_state_results.json').read_text(encoding='utf-8'))
        c=j['counts']
        assert j['status']=='PASS' and c['annual_states']==150 and c['adjacent_pairs']==120 and c['five_year_sequences']==30
        assert c['adjacent_label_changes']==8 and c['sequences_with_any_label_change']==4
        jaccard=j['geometry_summary']['minimum_jaccard_among_label_changes']
        assert abs(jaccard-0.9689207388098996)<1e-12
        assert j['identity_verification']['maximum_absolute_residuals']['change_identity_residual']<1e-10
        identical={}
        semantic={}
        comparison_reports={}
        for name,count in EXPECTED_CSV.items():
            assert lines_csv(joint/name)==count
            comparison_reports[name]=compare_csv(REF/name,joint/name)
            identical[name]=comparison_reports[name]['byte_identical']
            semantic[name]=comparison_reports[name]['semantic_equivalent']
            if not semantic[name]:
                raise AssertionError(f'Scientific CSV comparison FAILED for {name}: {comparison_reports[name]["errors"]}')
        run_cmd([sys.executable,'-B',str(ROOT/'src/experiment_b_reproduce.py'),
                 '--reference',str(REF/'Experiment_B_Recomputed_Tie_Path_81.csv'),'--output',str(exp)])
        b=json.loads((exp/'experiment_b_fresh_results.json').read_text(encoding='utf-8'))
        assert b['status']=='PASS' and b['fresh_solutions']==81
        assert b['max_absolute_tie_ratio_difference']<1e-9
        report={'status':'PASS','principal_annual_states':150,'principal_adjacent_year_pairs':120,
                'specifications_with_a_contributor_change':4,'contributor_changes':8,
                'minimum_jaccard_for_changed_labels':jaccard,'four_reference_tables_byte_identical':identical,
                'four_reference_tables_semantically_equivalent':semantic,
                'float_comparison_contract':comparison_reports,
                'synthetic_experiment_b_fresh_solutions':81,'synthetic_max_ratio_error':b['max_absolute_tie_ratio_difference'],
                'limitations':'Saved continuous summit and contour records are INPUTS for the joint audit; this suite does not fresh-recompute every summit/contour of the whole publication.'}
        print(json.dumps(report,indent=2))

if __name__=='__main__':
    main()
