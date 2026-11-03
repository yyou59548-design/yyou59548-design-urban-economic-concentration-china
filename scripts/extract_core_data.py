#!/usr/bin/env python3
"""Reproduce the five declared public-core subsets from the *complete* archive.

This does not modify the source archive. It is a source-selection audit, not an
independent reauthentication of the original statistical publisher records.
"""
from pathlib import Path
import argparse,csv
INPUTS={
'domains':'05_Recomputed_Results/National_2011_2023/Domain_Records.csv',
'local_peaks':'06_Robustness/Joint_Location_GDP_Bandwidth/Local_Continuous_Peaks.csv',
'sequences':'06_Robustness/Joint_Location_GDP_Bandwidth/Five_Year_Sequences.csv',
'vectors':'03_Harmonization/Analysis_Vectors.csv',
'coordinates':'03_Harmonization/Analysis_Coordinates.csv',
}
SELECT={
'domains':lambda r:r['scenario']=='corrected_scope_A' and r['is_PRD_reference']=='True' and int(r['max_dim'])==360 and 2019<=int(r['year'])<=2023 and r['threshold_rule']=='scenario_2019_fixed',
'local_peaks':lambda r:r['scenario']=='corrected_scope_A' and 2019<=int(r['year'])<=2023,
'sequences':lambda r:r['scenario']=='corrected_scope_A',
'vectors':lambda r:r['scenario']=='corrected_scope_A' and 2019<=int(r['year'])<=2023,
'coordinates':lambda r:r['scope']=='A',
}
COUNTS=dict(domains=150,local_peaks=150,sequences=30,vectors=2950,coordinates=885)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--complete-input-root',type=Path,required=True,help='Complete archived Replication_Inputs folder')
    p.add_argument('--output-root',type=Path,required=True,help='A new, empty target directory')
    a=p.parse_args()
    if a.output_root.exists():p.error('Provide a new output directory to avoid overwrites')
    a.output_root.mkdir(parents=True)
    for name,rel in INPUTS.items():
        source=a.complete_input_root/rel
        with source.open(encoding='utf-8-sig',newline='') as f:
            rdr=csv.DictReader(f);fields=rdr.fieldnames;rows=[row for row in rdr if SELECT[name](row)]
        if len(rows)!=COUNTS[name]:raise ValueError(f'{name}: {len(rows)} rows, expected {COUNTS[name]}')
        target=a.output_root/rel;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('w',encoding='utf-8-sig',newline='') as f:
            wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
        print(name,len(rows),target)

if __name__=='__main__':main()
