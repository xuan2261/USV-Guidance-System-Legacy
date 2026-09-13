# Golden scenario set

All runtime scenarios are bounded to 180 seconds and capture stdout/stderr, return code, elapsed time and verdict.

| ID | Launch | Purpose | Mode |
|---|---|---|---|
| G01 | `full_mission_test.launch` | end-to-end mission baseline | smoke/all |
| G02 | `ny_mission.launch` | geographic/map regression | all |
| G03 | `ryfylke_mission.launch` | long-route regression | all |
| G04 | `tss_mission.launch` | traffic-separation map semantics | all |
| G05 | `test_dubin.launch` | Dubins baseline | all |
| G06 | `test_quadtree.launch` | Quadtree characterization | all |
