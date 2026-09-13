#!/usr/bin/env python3
from pathlib import Path
import json, sys, xml.etree.ElementTree as ET
root=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1])
checks=[]
def add(n,ok,d=''): checks.append({'name':n,'status':'PASS' if ok else 'FAIL','detail':d})
req=[
 'ros2_ws/src/usv_model_core/package.xml','ros2_ws/src/usv_geodesy/package.xml',
 'ros2_ws/src/usv_map_core/package.xml','ros2_ws/src/usv_nav2_hybrid_planner/package.xml',
 'docs/COORDINATE_CONTRACT.md','docs/PHASE11_BUILD_CONTRACT.md','locks/stack.json',
 'Dockerfile.phase11','RUN_PHASE11.cmd','RUN_PHASE11.ps1','scripts/run_phase11_build.sh',
 'regression/trajectory_schema.json','regression/legacy_final_fixtures.json'
]
missing=[x for x in req if not (root/x).exists()]; add('required_files',not missing,','.join(missing))
text='\n'.join(p.read_text(errors='ignore') for p in (root/'ros2_ws/src').rglob('*') if p.is_file())
add('no_legacy_ros1_api','ros::NodeHandle' not in text and 'catkin_' not in text)
add('metric_api_contract','distance_m' in text and 'east_m' in text and 'north_m' in text)
plugin=(root/'ros2_ws/src/usv_nav2_hybrid_planner/include/usv_nav2_hybrid_planner/hybrid_planner_adapter.hpp').read_text()
add('jazzy_nav2_signature','createPlan(const geometry_msgs::msg::PoseStamped & start, const geometry_msgs::msg::PoseStamped & goal, std::function<bool()> cancel_checker)' in plugin)
add('guarded_plugin','core is not connected' in (root/'ros2_ws/src/usv_nav2_hybrid_planner/src/hybrid_planner_adapter.cpp').read_text())
stack=json.loads((root/'locks/stack.json').read_text()); add('stack_lock',stack.get('ros2')=='Jazzy Jalisco' and stack.get('gazebo')=='Harmonic' and stack.get('vrx',{}).get('tag')=='v3.1.0')
model_cmake=(root/'ros2_ws/src/usv_model_core/CMakeLists.txt').read_text(); model_pkg=(root/'ros2_ws/src/usv_model_core/package.xml').read_text()
add('model_core_stdlib_only','find_package(Eigen3' not in model_cmake and 'find_package(Boost' not in model_cmake and '<depend>eigen</depend>' not in model_pkg and '<depend>boost</depend>' not in model_pkg)
add('phase11_core_only','--packages-select usv_model_core usv_geodesy usv_map_core' in (root/'scripts/run_phase11_build.sh').read_text() and 'usv_nav2_hybrid_planner' not in (root/'scripts/run_phase11_build.sh').read_text())
# Parse package/plugin XMLs
try:
 for p in (root/'ros2_ws/src').glob('*/package.xml'): ET.parse(p)
 ET.parse(root/'ros2_ws/src/usv_nav2_hybrid_planner/usv_hybrid_planner_plugin.xml')
 add('xml_parse',True)
except Exception as e:add('xml_parse',False,str(e))
ok=all(x['status']=='PASS' for x in checks); print(json.dumps({'status':'PASS' if ok else 'FAIL','checks':checks},indent=2)); sys.exit(0 if ok else 2)
