#!/usr/bin/env python3
from pathlib import Path
import json, sys
ret=Path(sys.argv[1] if len(sys.argv)>1 else '/return')
def load(name,default=None):
    try: return json.loads((ret/name).read_text())
    except Exception: return default if default is not None else {}
source=load('source_identity.json'); deps=load('dependency_identity.json'); db=load('docker_build.json'); build=load('build.json'); tests=load('tests.json'); lp=load('launch_parse.json'); static=load('static_audit.json')
scenario_files=sorted((ret/'scenarios').glob('*.json')) if (ret/'scenarios').exists() else []; scenarios=[json.loads(p.read_text()) for p in scenario_files]
expected='c930b938302d8cfe8c378dfa69748a33d3d76459'; q={}
def gate(i,n,s,e,m=True): q[i]={'name':n,'status':s,'evidence':e,'mandatory':m}
gate('Q0','Source SHA','PASS' if source.get('head')==expected else 'FAIL',source.get('head'))
gate('Q1','Dependency SHAs','PASS' if deps.get('status')=='PASS' else 'FAIL',deps.get('status'))
gate('Q2','Docker image','PASS' if db.get('status') in ('PASS','SKIPPED') else 'FAIL',db.get('status'))
gate('Q3','catkin build','PASS' if build.get('status')=='PASS' else 'FAIL',build.get('status'))
gate('Q4','Launch parse','PASS' if lp.get('status')=='PASS' else 'FAIL',lp.get('status'))
full=next((x for x in scenarios if x.get('scenario')=='full_mission_test'),None)
gate('Q5','Planner runtime baseline','PASS' if full and full.get('status')=='PASS' else ('NOT_RUN' if full is None else full.get('status','FAIL')),full,False)
sm={c['name']:c for c in static.get('checks',[])}
gate('Q6','LOS regression characterized','PASS' if sm.get('los_first_waypoint_init',{}).get('status')=='OBSERVED' else 'DRIFT',sm.get('los_first_waypoint_init'))
gate('Q7','Quadtree defect characterized','PASS' if sm.get('quadtree_known_bug_comment',{}).get('status')=='OBSERVED' else 'DRIFT',sm.get('quadtree_known_bug_comment'))
gate('Q8','COLAV bounds risk characterized','PASS' if sm.get('colav_fixed_obstacle_array',{}).get('status')=='OBSERVED' else 'DRIFT',sm.get('colav_fixed_obstacle_array'))
gate('Q9','Golden evidence captured','PASS' if scenarios else 'NOT_RUN',{'scenario_count':len(scenarios)},False)
pre_q10_ok=all(v['status']=='PASS' for k,v in q.items() if v['mandatory']); golden_ok=full is not None and full.get('status')=='PASS'; ready='PASS' if pre_q10_ok and golden_ok else 'BLOCKED'
gate('Q10','Ready for ROS2 migration',ready,{'mandatory_pre_q10_pass':pre_q10_ok,'full_mission_pass':golden_ok},True)
overall='PASS' if all(v['status']=='PASS' for v in q.values() if v['mandatory']) else 'BLOCKED'
result={'overall':overall,'ros2_migration_ready':ready=='PASS','tests_status':tests.get('status'),'gates':q,'scenarios':scenarios}
(ret/'gates.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['# Qualification Report','',f'Overall: **{overall}**','', '| Gate | Name | Status | Mandatory |','|---|---|---:|---:|']
for k,v in q.items(): lines.append(f"| {k} | {v['name']} | {v['status']} | {'yes' if v['mandatory'] else 'no'} |")
lines += ['', '## Interpretation', '', '- `PASS`: evidence meets the gate.', '- `DRIFT`: source no longer matches expected legacy characterization.', '- `NOT_RUN`: optional runtime evidence was not requested.', '- `BLOCKED`: remain in recovery/fix phase before semantic ROS 2 porting.', '', 'Known legacy defects are characterization targets and are not silently patched in Phase 0.5.']
(ret/'QUALIFICATION_REPORT.md').write_text('\n'.join(lines)+'\n'); print(json.dumps(result,indent=2)); sys.exit(0 if overall=='PASS' else 3)
