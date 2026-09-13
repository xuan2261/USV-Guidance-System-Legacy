# Phase 0.5 Qualification Gate Matrix

| Gate | Check | Pass criterion | Failure meaning |
|---|---|---|---|
| Q0 | Upstream identity | exact pinned HEAD | source drift / wrong checkout |
| Q1 | Dependency identity | every source dependency matches lock SHA | dependency drift |
| Q2 | Qualification image | pinned image builds or explicitly reused | environment unavailable |
| Q3 | Catkin build | compile/link succeeds | baseline not reproduced |
| Q4 | Launch parse | selected launch files resolve and parse | package/launch dependency problem |
| Q5 | Full mission runtime | bounded full mission completes | runtime baseline incomplete; optional evidence gate |
| Q6 | LOS legacy defect | expected initialization defect signature observed | upstream drift / audit revision needed |
| Q7 | Quadtree legacy defect | upstream known-bug signature observed | upstream drift / audit revision needed |
| Q8 | COLAV ID risk | fixed-size obstacle-array signature observed | upstream drift / audit revision needed |
| Q9 | Golden evidence | at least one scenario log+JSON exists | runtime not requested or not reached |
| Q10 | ROS2-ready | Q0–Q4,Q6–Q8 pass and full-mission runtime passes | remain in legacy recovery/fix phase |
