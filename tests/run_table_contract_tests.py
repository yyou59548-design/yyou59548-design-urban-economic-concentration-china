#!/usr/bin/env python3
"""Show that small numerical formatting drift is accepted and substantive drift rejected."""
import csv
import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from table_comparison import compare_csv


def write(p,rows):
    with Path(p).open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerows(rows)


def main():
    if not __debug__:raise RuntimeError('Do not run tests with assertions disabled')
    with tempfile.TemporaryDirectory(prefix='tgis_comparator_') as d:
        ref,now=Path(d)/'reference.csv',Path(d)/'output.csv'
        data=[['city','year','log_margin','density','H_json','annual_identity_residual','H_reconstruction_relative_error'],
              ['广州',2021,'-0.009959466807274537','3.058503028864548e-13','[[123456.789,0],[0,999999.6]]','6e-15','6.579024400613749e-16']]
        write(ref,data);write(now,data)
        assert compare_csv(ref,now)['byte_identical']
        near=[x[:] for x in data];near[1][2]='-0.0099594668072800';near[1][4]='[[123456.789000002,0],[0,999999.6]]';near[1][5]='3e-15';near[1][6]='5.263219520490999e-16'
        write(now,near)
        x=compare_csv(ref,now)
        assert x['status']=='PASS' and not x['byte_identical'] and x['differing_text_cells']==4,x
        wrong=[x[:] for x in data];wrong[1][0]='深圳';write(now,wrong)
        assert compare_csv(ref,now)['status']=='FAIL'
        wrong=[x[:] for x in data];wrong[1][3]='3.058503028864548e-11';write(now,wrong)
        assert compare_csv(ref,now)['status']=='FAIL'
        wrong=[x[:] for x in data];wrong[1][4]='[[123456.789,0],[0,899999.6]]';write(now,wrong)
        assert compare_csv(ref,now)['status']=='FAIL'
        wrong=[x[:] for x in data];wrong[1][5]='1e-5';write(now,wrong)
        assert compare_csv(ref,now)['status']=='FAIL'
        wrong=[x[:] for x in data];wrong[1][6]='1e-7';write(now,wrong)
        assert compare_csv(ref,now)['status']=='FAIL'
        write(now,data[:-1]);assert compare_csv(ref,now)['status']=='FAIL'
    print(json.dumps({'status':'PASS','small_float_drift':'accepted_with_byte_mismatch_reported',
                     'substantive_changes_rejected':6},ensure_ascii=False))


if __name__=='__main__':main()
