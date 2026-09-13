#!/usr/bin/env python3
from pathlib import Path
import json
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
pkg = root / 'ros2_ws/src/usv_map_core'
checks = []
def add(name, ok, detail=''):
    checks.append({'name': name, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
required = ['include/usv_map_core/map_query.hpp','include/usv_map_core/geometry.hpp','include/usv_map_core/quadtree.hpp','include/usv_map_core/synthetic_map.hpp','src/quadtree.cpp','src/synthetic_map.cpp','test/test_geometry.cpp','test/test_quadtree.cpp','test/test_synthetic_map.cpp']
missing = [p for p in required if not (pkg / p).exists()]
add('required_files', not missing, ','.join(missing))
headers = '\n'.join(p.read_text(errors='ignore') for p in (pkg / 'include').rglob('*.hpp'))
ros_tokens = ['rclcpp', 'geometry_msgs', 'nav_msgs', 'tf2', 'ros::', '#include <ros/']
found_ros = [token for token in ros_tokens if token in headers]
add('ros_free_public_api', not found_ros, ','.join(found_ros))
metric_required = ['Point2dM', 'AabbM', 'Segment2dM', 'distance_m', 'alpha_m', 'default_saturation_m']
metric_missing = [token for token in metric_required if token not in headers]
add('metric_identifiers', not metric_missing, ','.join(metric_missing))
public_ambiguous = [token for token in ['longitude', 'latitude', 'degrees squared'] if token in headers.lower()]
add('no_degree_semantics_in_public_api', not public_ambiguous, ','.join(public_ambiguous))
cmake = (pkg / 'CMakeLists.txt').read_text(errors='ignore')
add('ament_gtests', 'ament_cmake_gtest' in cmake and cmake.count('ament_add_gtest(') == 3)
add('cxx17', 'cxx_std_17' in cmake)
qt_test = (pkg / 'test/test_quadtree.cpp').read_text(errors='ignore')
add('quadtree_boundary_regression', 'BoundaryAndStraddleQueriesNeverLoseItems' in qt_test)
map_test = (pkg / 'test/test_synthetic_map.cpp').read_text(errors='ignore')
add('collision_distance_fixture', 'DistanceSaturatesLikeLegacyMapService' in map_test)
add('voronoi_formula_fixture', 'VoronoiFieldPreservesPinnedLegacyFormulaInMetres' in map_test)
ok = all(c['status'] == 'PASS' for c in checks)
print(json.dumps({'schema': 'usv-phase12-map-core-static/v1', 'status': 'PASS' if ok else 'FAIL', 'checks': checks}, indent=2))
sys.exit(0 if ok else 2)
