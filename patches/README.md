# Patch policy

Phase 0 has two tracks:

- `legacy-pristine`: pinned source, no algorithm changes; used only to establish golden outputs.
- `legacy-recovery`: build/security/reproducibility fixes only. Algorithm changes are forbidden until a failing deterministic regression test exists.

Do not silently fix Quadtree, LOS, coordinate semantics or COLAV bounds before their legacy behavior is captured.
