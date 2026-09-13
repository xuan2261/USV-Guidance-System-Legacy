#!/usr/bin/env bash
set -euo pipefail
source /opt/ros/jazzy/setup.bash
WS="${1:-/ws}"
cd "$WS"
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --event-handlers console_direct+
colcon test --event-handlers console_direct+
colcon test-result --verbose
