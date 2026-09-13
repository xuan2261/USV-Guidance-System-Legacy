#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys, tempfile, yaml, xml.etree.ElementTree as ET
root=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]); checks=[]
def add(n,ok,d=''): checks.append({'name':n,'status':'PASS' if ok else 'FAIL','detail':d})
try:
 for p in root.rglob('*.json'): json.loads(p.read_text())
 add('json_parse',True)
except Exception as e:add('json_parse',False,str(e))
try:
 dep=yaml.safe_load((root/'locks/dependencies.repos').read_text())['repositories']; add('dependency_lock_shape',len(dep)==5 and all(len(v['version'])==40 and v['url'].startswith('https://') for v in dep.values()))
except Exception as e:add('dependency_lock_shape',False,str(e))
try:
 py=list((root/'scripts').glob('*.py'))+list((root/'phase1_ros2/scripts').glob('*.py'))+list((root/'phase1_ros2/regression').glob('*.py'))
 for p in py: compile(p.read_text(),str(p),'exec')
 add('python_compile',True)
except Exception as e:add('python_compile',False,str(e))
bash_ok=True; det=[]
for p in list((root/'scripts').glob('*.sh'))+list((root/'phase1_ros2/scripts').glob('*.sh')):
 r=subprocess.run(['bash','-n',str(p)],capture_output=True,text=True); bash_ok &= r.returncode==0
 if r.returncode: det.append(f'{p.name}:{r.stderr.strip()}')
add('bash_syntax',bash_ok,';'.join(det))
sec='\n'.join(p.read_text(errors='ignore') for p in [root/'Dockerfile.legacy',root/'.devcontainer/devcontainer.json',root/'RUN_ALL.ps1',root/'phase1_ros2/Dockerfile.phase11',root/'phase1_ros2/RUN_PHASE11.ps1'])
bad=[x for x in ['--privileged','/dev:/dev','chpasswd','--network host','--net=host','.ssh,target'] if x in sec]; add('security_patterns',not bad,','.join(bad))
up=json.loads((root/'locks/upstream.json').read_text()); add('upstream_pin',up.get('commit')=='c930b938302d8cfe8c378dfa69748a33d3d76459',up.get('commit',''))
required=['RUN_ALL.cmd','RUN_ALL.ps1','PRECHECK.cmd','PRECHECK.ps1','phase1_ros2/RUN_PHASE11.cmd','phase1_ros2/RUN_PHASE11.ps1','phase1_ros2/Dockerfile.phase11','phase1_ros2/PHASE11_RETURN_INSTRUCTIONS.md','phase1_ros2/docs/PHASE11_BUILD_CONTRACT.md','phase1_ros2/scripts/run_phase11_build.sh','phase1_ros2/scripts/make_phase11_report.py','phase1_ros2/scripts/validate_phase11_return.py','phase1_ros2/regression/trajectory_schema.json','phase1_ros2/regression/legacy_final_fixtures.json','phase1_ros2/regression/export_trajectory_csv.py','phase1_ros2/regression/compare_trajectory_csv.py']
missing=[x for x in required if not (root/x).exists()]; add('required_v06_files',not missing,','.join(missing))
runall=(root/'RUN_ALL.ps1').read_text(); add('legacy_evidence_always_returned','finally {' in runall and 'Package-Return' in runall and 'harness_error.json' in runall)
p11=(root/'phase1_ros2/RUN_PHASE11.ps1').read_text(); add('phase11_evidence_always_returned','finally {' in p11 and 'PHASE11_RETURN.zip' in p11 and 'wrapper_error.json' in p11)
r=subprocess.run([sys.executable,str(root/'phase1_ros2/scripts/verify_scaffold.py'),str(root/'phase1_ros2')],capture_output=True,text=True); add('phase1_scaffold_static',r.returncode==0,(r.stdout+r.stderr)[-700:])
# Pure model/geodesy differential regression + paired CSVs
r=subprocess.run(['bash',str(root/'phase1_ros2/scripts/run_phase1_regression.sh')],capture_output=True,text=True)
try:
 mr=json.loads((root/'phase1_ros2/regression/out/MODEL_DIFFERENTIAL_REPORT.json').read_text())
 gr=json.loads((root/'phase1_ros2/regression/out/geodesy_reference_report.json').read_text())
 cr=json.loads((root/'phase1_ros2/regression/out/TRAJECTORY_CSV_REPORT.json').read_text())
 add('phase1_differential_regression',r.returncode==0 and mr.get('status')=='PASS' and gr.get('status')=='PASS' and cr.get('status')=='PASS',(r.stdout+r.stderr)[-500:])
except Exception as e:add('phase1_differential_regression',False,str(e))
# Standalone C++ compile without Eigen/Boost/ROS
with tempfile.TemporaryDirectory() as td:
 model=root/'phase1_ros2/ros2_ws/src/usv_model_core'; exe=Path(td)/'model_smoke'
 src=Path(td)/'smoke.cpp'; src.write_text('#include <cmath>\n#include "usv_model_core/viknes830.hpp"\nint main(){usv_model_core::Viknes830 m; usv_model_core::VesselState s; usv_model_core::ControlSetpoint c{2,0}; for(int i=0;i<10;++i)s=m.step_rk4(s,c,0.1); return std::isfinite(s.u_mps)&&s.u_mps>0?0:1;}\n')
 cp=subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Wpedantic','-I',str(model/'include'),str(model/'src/viknes830.cpp'),str(src),'-o',str(exe)],capture_output=True,text=True)
 rr=subprocess.run([str(exe)],capture_output=True,text=True) if cp.returncode==0 else None
 add('model_core_stdlib_compile',cp.returncode==0 and rr.returncode==0,(cp.stderr if cp.returncode else ''))
# XML package/plugin parse
try:
 for p in (root/'phase1_ros2/ros2_ws/src').glob('*/package.xml'): ET.parse(p)
 ET.parse(root/'phase1_ros2/ros2_ws/src/usv_nav2_hybrid_planner/usv_hybrid_planner_plugin.xml')
 add('xml_parse',True)
except Exception as e:add('xml_parse',False,str(e))
# Phase 1.1 report smoke: simulated build evidence + real pure regression outputs
with tempfile.TemporaryDirectory() as td:
 d=Path(td)
 for name in ['rosdep.json','build.json','tests.json']:(d/name).write_text(json.dumps({'status':'PASS','detail':'smoke'}))
 rr=subprocess.run([sys.executable,str(root/'phase1_ros2/scripts/make_phase11_report.py'),str(d)],capture_output=True,text=True)
 try: j=json.loads((d/'PHASE11_REPORT.json').read_text()); ok=rr.returncode==0 and j['status']=='PASS' and j['parity_claim']=='BLOCKED_PENDING_LEGACY_Q10'
 except Exception: ok=False
 add('phase11_report_smoke',ok,(rr.stdout+rr.stderr)[-400:])

# GitHub Actions workflow validation
r=subprocess.run([sys.executable,str(root/'ci/validate_github_actions.py')],capture_output=True,text=True)
add('github_actions_validation',r.returncode==0,(r.stdout+r.stderr)[-700:])

# Existing early-failure return triage
with tempfile.TemporaryDirectory() as td:
 d=Path(td); (d/'preflight.json').write_text('{}'); (d/'environment.json').write_text('{}'); (d/'docker_build.json').write_text('{}'); (d/'harness_error.json').write_text(json.dumps({'status':'FAIL'}))
 r=subprocess.run([sys.executable,str(root/'scripts/validate_return.py'),str(d)],capture_output=True,text=True); j=json.loads((d/'RETURN_AUDIT.json').read_text()); add('return_triage_early_failure',r.returncode==0 and j['next_action']=='FIX_HOST_OR_WRAPPER',r.stdout[-300:])
ok=all(x['status']=='PASS' for x in checks); print(json.dumps({'version':'0.6','status':'PASS' if ok else 'FAIL','checks':checks},indent=2)); sys.exit(0 if ok else 1)
