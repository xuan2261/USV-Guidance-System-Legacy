#!/usr/bin/env python3
import csv,json,math,subprocess,sys,tempfile
from pathlib import Path
from legacy_model_reference import trajectory
ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'ros2_ws/src/usv_model_core'
REG=Path(__file__).resolve().parent
OUT=REG/'out'; OUT.mkdir(exist_ok=True)
BIN=OUT/'core_model_runner'
compile_cmd=['g++','-std=c++17','-O2','-I',str(MODEL/'include'),str(MODEL/'src/viknes830.cpp'),str(REG/'core_model_runner.cpp'),'-o',str(BIN)]
cp=subprocess.run(compile_cmd,text=True,capture_output=True)
if cp.returncode:
    (OUT/'compile.log').write_text(cp.stdout+cp.stderr); print('FAIL compile'); sys.exit(2)
sc=json.loads((REG/'model_scenarios.json').read_text())
dt=float(sc['integration']['dt_s']); rows=[]; overall=True

def canon(a): return math.atan2(math.sin(a),math.cos(a))
for item in sc['scenarios']:
    args=[str(BIN),str(item['duration_s']),str(dt),*map(str,item['state']),*map(str,item['command'])]
    rp=subprocess.run(args,text=True,capture_output=True,check=True)
    core=list(csv.DictReader(rp.stdout.splitlines()))
    ref=trajectory(item['state'],item['command'],item['duration_s'],dt)
    maxerr={k:0.0 for k in ['x','y','yaw_canonical','u','v','r']}; raw_yaw=0.0
    for crow,(t,s) in zip(core,ref):
        vals={'x':s[0],'y':s[1],'u':s[3],'v':s[4],'r':s[5]}
        for k in ['x','y','u','v','r']: maxerr[k]=max(maxerr[k],abs(float(crow[k])-vals[k]))
        maxerr['yaw_canonical']=max(maxerr['yaw_canonical'],abs(canon(float(crow['yaw']))-canon(s[2])))
        raw_yaw=max(raw_yaw,abs(float(crow['yaw'])-s[2]))
    passed=max(maxerr.values())<=1e-9 and raw_yaw<=1e-9
    overall &= passed
    rows.append({'id':item['id'],'pass':passed,'max_error':maxerr,'max_raw_yaw_error':raw_yaw,'expect':item['expect']})
report={'schema':1,'status':'PASS' if overall else 'FAIL','source_commit':sc['source_commit'],'scenarios':rows}
(OUT/'MODEL_DIFFERENTIAL_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2)); sys.exit(0 if overall else 1)
