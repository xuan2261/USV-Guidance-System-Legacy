# Coordinate and unit contract

This contract fixes the most serious semantic ambiguity found in the legacy stack.

- Internal planning, TF, odometry, path and collision-query coordinates: **local metric ENU**.
- `x`, `y`, distances and clearances: **metres**.
- yaw/course: **radians**, wrapped consistently.
- linear velocities: **m/s**; yaw rate: **rad/s**.
- WGS84 latitude/longitude is allowed only at explicit system boundaries (GNSS ingestion, ENC/GPX import-export, operator UI).
- A `nav_msgs/Path`, `geometry_msgs/PoseStamped`, `nav_msgs/Odometry` or TF frame must never encode degrees in `position.x/y`.
- Every conversion between WGS84 and ENU must use an explicit origin object, not a hidden ROS-global service state.
