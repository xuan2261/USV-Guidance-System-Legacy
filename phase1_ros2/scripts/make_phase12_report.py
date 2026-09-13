#!/usr/bin/env python3
from pathlib import Path
import datetime, json, sys
out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'phase12_out')
out.mkdir(parents=True, exist_ok=True)
def load(name):
    try: return json.loads((out / name).read_text())
    except Exception: return {'status': 'MISSING'}
static=load('static_contract.json'); standalone=load('standalone_sanitizer.json'); rosdep=load('rosdep.json'); build=load('build.json'); tests=load('tests.json')
static_checks={x.get('name'):x for x in static.get('checks',[])}
def scheck(name): return static_checks.get(name,{}).get('status')=='PASS'
def gate(name,ok,evidence): return {'name':name,'status':'PASS' if ok else 'FAIL','evidence':evidence}
standalone_ok=standalone.get('status')=='PASS'
ros2_ok=rosdep.get('status')=='PASS' and build.get('status')=='PASS' and tests.get('status')=='PASS'
gates={
'M12-01':gate('Pure C++ metric API',scheck('ros_free_public_api'),static_checks.get('ros_free_public_api')),
'M12-02':gate('No degree/metre ambiguity',scheck('metric_identifiers') and scheck('no_degree_semantics_in_public_api'),{'metric':static_checks.get('metric_identifiers'),'degree':static_checks.get('no_degree_semantics_in_public_api')}),
'M12-03':gate('Quadtree deterministic fixtures',scheck('quadtree_boundary_regression') and ros2_ok,{'static':static_checks.get('quadtree_boundary_regression'),'tests':tests}),
'M12-04':gate('Legacy quadtree boundary/null-path regression characterized',scheck('quadtree_boundary_regression') and standalone_ok,standalone),
'M12-05':gate('Collision/distance synthetic fixtures',scheck('collision_distance_fixture') and ros2_ok,tests),
'M12-06':gate('Voronoi synthetic fixture',scheck('voronoi_formula_fixture') and ros2_ok,tests),
'M12-07':gate('ASan/UBSan',standalone_ok,standalone),
'M12-08':gate('ROS-free standalone build',standalone_ok,standalone),
'M12-09':gate('ROS 2 Jazzy colcon integration',ros2_ok,{'rosdep':rosdep,'build':build,'tests':tests}),
'M12-10':{'name':'Real-map parity','status':'BLOCKED_PENDING_LEGACY_ASSET','evidence':'outside_ny_updated region.sqlite and region_detailed.sqlite are not versioned upstream; synthetic fixtures do not claim real-map parity.'}}
mandatory_ok=all(v['status']=='PASS' for k,v in gates.items() if k!='M12-10')
result={'schema':'usv-phase12a-qualification/v1','captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overall':'PASS_WITH_EXTERNAL_BLOCKER' if mandatory_ok else 'FAIL','real_map_parity_claimed':False,'gates':gates}
(out/'phase12_report.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['# Phase 1.2a Map Core Qualification','',f"Overall: **{result['overall']}**",'','| Gate | Name | Status |','|---|---|---|']
for key,value in gates.items(): lines.append(f"| {key} | {value['name']} | {value['status']} |")
lines += ['','## Scope boundary','','- Synthetic metric geometry only; no real mission-region dataset is fabricated.','- No planner, controller, COLAV, Nav2 mission behavior, target logic, or vehicle actuation logic is changed.','- M12-10 remains blocked until the original legacy mission-region dataset is recovered and independently verified.']
(out/'PHASE12A_REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(result,indent=2)); sys.exit(0 if mandatory_ok else 3)
