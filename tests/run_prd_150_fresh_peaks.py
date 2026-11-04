#!/usr/bin/env python3
"""Re-solve all 150 declared principal PRD local peaks from GDP and coordinates.

Inputs: 295-city GDP analysis vectors and three geographic point definitions.
Archived Local_Continuous_Peaks.csv is read ONLY as a post-solution reference
for positions, margins and labels; its positions are not passed to the solver.
This does not regenerate their connected superlevel polygons or their
upstream seven-scale qualification from raw source publications.
"""
from __future__ import annotations
import json
import math
from collections import defaultdict
from pathlib import Path
import numpy as np
from pyproj import Transformer
from run_independent_oracles import BASE, read_csv, stationary, sha256


def main():
    if not __debug__:
        raise RuntimeError('Normal Python assertions must remain enabled')
    derived = BASE/'data/derived'
    source_vectors=derived/'03_Harmonization/Analysis_Vectors.csv'
    source_coords=derived/'03_Harmonization/Analysis_Coordinates.csv'
    reference=derived/'06_Robustness/Joint_Location_GDP_Bandwidth/Local_Continuous_Peaks.csv'
    vectors=read_csv(source_vectors)
    coord_rows=read_csv(source_coords)
    targets=read_csv(reference)
    names=sorted({r['city_name'] for r in vectors})
    assert len(names)==295 and len(targets)==150
    coords={(r['geo'],r['city_name']):r for r in coord_rows if r['scope']=='A'}
    masses={(r['year'],r['price'],r['city_name']):float(r['mass']) for r in vectors if r['scenario']=='corrected_scope_A'}
    assert len(masses)==2950
    transformer=Transformer.from_crs('EPSG:4326',
         '+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 +datum=WGS84 +units=m +no_defs',always_xy=True)
    ia,ib=names.index('广州市'), names.index('深圳市')
    settings={}
    for geo in ('admin','pop2020','pop2023'):
        rows=[coords[(geo,n)] for n in names]
        east,north=transformer.transform([float(r['lon']) for r in rows],
                                        [float(r['lat']) for r in rows])
        xy=np.column_stack((east,north))
        for b in (0.40,0.45,0.50,0.55,0.60):
            H=(b*len(names)**(-1.0/6))**2*np.cov(xy.T)
            H+=1e-10*max(float(np.trace(H)),1.0)*np.eye(2)
            L=np.linalg.cholesky(H)
            white=np.linalg.solve(L,xy.T).T
            seed=(white[ia]+white[ib])/2.0
            settings[(geo,b)]=(L,white,seed)
    positions=[];margins=[];seq=defaultdict(list)
    unique=set()
    for row in targets:
        year,price,geo,b=row['year'],row['price'],row['geo'],float(row['b'])
        key=(geo,price,b,int(year))
        assert key not in unique, f'duplicate reference state {key}'
        unique.add(key)
        L,white,seed=settings[(geo,b)]
        mass=np.array([masses[(year,price,n)] for n in names])
        peak,contrib,residual,_=stationary(white,mass/mass.sum(),seed,'maximum')
        physical=L@peak
        delta=float(np.linalg.norm(physical-np.array([float(row['peak_x']),float(row['peak_y'])])))
        margin=math.log(contrib[ib]/contrib[ia])
        mdiff=abs(margin-float(row['log_contribution_margin_SZ_GZ']))
        name=names[int(np.argmax(contrib))]
        assert name==row['top_city'], (key, name, row['top_city'])
        assert delta<1e-3, (key,'position_delta_m',delta)
        assert mdiff<1e-8, (key,'log_margin_delta',mdiff)
        assert residual<2e-9
        positions.append(delta);margins.append(mdiff)
        seq[(geo,price,b)].append((int(year),name,margin))
    assert len(unique)==150 and len(seq)==30
    change_pairs=0;change_specs=0;strict_min_count=0;rise_count=0
    for key,records in seq.items():
        records.sort()
        assert [x[0] for x in records]==[2019,2020,2021,2022,2023],key
        n=sum(a[1]!=b[1] for a,b in zip(records,records[1:]))
        change_pairs+=n
        change_specs+=bool(n)
        if records[2][2]<min(x[2] for j,x in enumerate(records) if j!=2):strict_min_count+=1
        if records[3][2]>records[2][2]:rise_count+=1
    assert (change_pairs,change_specs,strict_min_count,rise_count)==(8,4,30,30), \
           (change_pairs,change_specs,strict_min_count,rise_count)
    print(json.dumps({
        'status':'PASS','fresh_local_peak_solutions':len(positions),
        'geographies':3,'GDP_measures':2,'bandwidths':5,'years':5,
        'maximum_peak_position_difference_m':max(positions),
        'maximum_signed_log_margin_difference':max(margins),
        'specifications_with_label_change':change_specs,'adjacent_label_changes':change_pairs,
        'specifications_with_strict_2021_signed_minimum':strict_min_count,
        'specifications_with_2022_signed_rise':rise_count,
        'input_sha256':{'vectors':sha256(source_vectors),'coordinates':sha256(source_coords)},
        'scope':'Recomputed 150 target PRD local maxima from derived GDP/point inputs; historical peaks only compared after solving. No new source-statistics authentication, seven-scale search, contour extraction or all-national results.'
    },ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
