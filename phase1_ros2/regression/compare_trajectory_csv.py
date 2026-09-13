#!/usr/bin/env python3
from pathlib import Path
import csv,json,math,sys
ROOT=Path(__file__).resolve().parent
TR=ROOT/'out/trajectories'; tol=json.loads((ROOT/'trajectory_schema.json').read_text())['comparison']['absolute_tolerance']
results=[]; overall=True
for lp in sorted((TR/'legacy').glob('*.csv')):
    cp=TR/'core'/lp.name
    if not cp.exists(): results.append({'id':lp.stem,'status':'FAIL','reason':'core csv missing'}); overall=False; continue
    L=list(csv.DictReader(lp.open())); C=list(csv.DictReader(cp.open()))
    if len(L)!=len(C): results.append({'id':lp.stem,'status':'FAIL','reason':'row count mismatch'}); overall=False; continue
    maxerr={k:0.0 for k in ['t','x','y','yaw_raw','yaw_canonical','u','v','r']}
    for a,b in zip(L,C):
        for k in ['t','x','y','u','v','r']: maxerr[k]=max(maxerr[k],abs(float(a[k])-float(b[k])))
        ya,yb=float(a['yaw']),float(b['yaw']); maxerr['yaw_raw']=max(maxerr['yaw_raw'],abs(ya-yb)); maxerr['yaw_canonical']=max(maxerr['yaw_canonical'],abs(math.atan2(math.sin(ya),math.cos(ya))-math.atan2(math.sin(yb),math.cos(yb))))
    ok=max(maxerr.values())<=tol; overall &= ok; results.append({'id':lp.stem,'status':'PASS' if ok else 'FAIL','max_error':maxerr})
rep={'schema':'usv-trajectory-comparison/v1','status':'PASS' if overall else 'FAIL','tolerance':tol,'results':results}
(ROOT/'out/TRAJECTORY_CSV_REPORT.json').write_text(json.dumps(rep,indent=2)+'\n'); print(json.dumps(rep,indent=2)); sys.exit(0 if overall else 1)
