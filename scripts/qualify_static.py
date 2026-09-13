#!/usr/bin/env python3
from pathlib import Path
import argparse, json
p=argparse.ArgumentParser(); p.add_argument('root',nargs='?',default='/workspace/src/usv_guidance_system'); p.add_argument('--out',default='/return/static_audit.json'); a=p.parse_args(); root=Path(a.root); checks=[]
def check(name,path,predicate,severity,note,expected='OBSERVED'):
    fp=root/path; text=fp.read_text(errors='ignore') if fp.exists() else ''; observed='OBSERVED' if predicate(text) else 'NOT_OBSERVED'
    checks.append({'name':name,'severity':severity,'status':observed,'expected':expected,'expectation_match':observed==expected,'file':str(path),'note':note})
check('stale_usv_motion_planning_path',Path('Dockerfile.Main'),lambda t:'usv_motion_planning/scripts/common_commands.sh' in t,'P0','Legacy Dockerfile stale path')
check('hardcoded_password',Path('Dockerfile.Main'),lambda t:'chpasswd' in t,'P0','Legacy Dockerfile hard-coded passwords')
check('los_first_waypoint_init',Path('usv_path_trackers/src/usv_path_trackers/los_usv.py'),lambda t:'self.current_waypoint = Pose()' in t and 'if self.current_waypoint is None' in t,'P1','First waypoint state mismatch')
check('colav_fixed_obstacle_array',Path('usv_colav/src/colav.cpp'),lambda t:'std::vector<geometry_msgs::Point>(4)' in t and 'obstacle_pose_local[' in t,'P1','Potential OOB when obstacle id >=4')
check('odom_wgs84_in_map_frame',Path('usv_simulator/src/sim_vessel.cpp'),lambda t:'odom.header.frame_id = "map"' in t and 'global_initial_pose.x()' in t,'P0','Odometry map frame carries WGS84 degrees')
check('quadtree_known_bug_comment',Path('usv_mission_planner/src/hybrid_astar.cpp'),lambda t:'fundamental bug in quadtree builder' in t,'P0','Upstream acknowledges rare Quadtree failure')
check('hardcoded_turn_radius',Path('usv_mission_planner/src/hybrid_astar.cpp'),lambda t:'turning_radius = 9' in t,'P1','Dubins radius hard-coded')
check('streamed_pose_path',Path('usv_mission_planner/src/mission_planner.cpp'),lambda t:'advertise<geometry_msgs::Pose>("mission_planner/geo_waypoint"' in t and 'ros::Duration(0.01).sleep()' in t,'P1','Path transmitted as individual Pose messages')
summary={'root':str(root),'status':'PASS' if all(c['expectation_match'] for c in checks) else 'DRIFT','checks':checks,'counts':{'observed':sum(c['status']=='OBSERVED' for c in checks),'expectation_matches':sum(c['expectation_match'] for c in checks)}}
out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))
