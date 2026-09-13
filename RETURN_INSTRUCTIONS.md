# Return instructions — v0.5

There are now two evidence bundles.

## A. Legacy ROS1 qualification
Run from package root:
```bat
PRECHECK.cmd
RUN_ALL.cmd
```
Return:
```text
QUALIFICATION_RETURN.zip
```

## B. ROS2 Jazzy Phase 1.1 core qualification
Run:
```bat
cd phase1_ros2
RUN_PHASE11.cmd
```
Return:
```text
PHASE11_RETURN.zip
```

Send either ZIP even if the corresponding command reports FAIL. Failure evidence is intentional and useful for the next debug/audit round.
