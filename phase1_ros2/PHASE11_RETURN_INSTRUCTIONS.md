# Phase 1.1 return instructions

Run on Windows with Docker Desktop in Linux-container mode:

```bat
RUN_PHASE11.cmd
```

The wrapper always attempts to create:

```text
PHASE11_RETURN.zip
```

Send that ZIP back even if the command reports FAIL.

The Phase 1.1 bundle only qualifies:
- `usv_model_core`
- `usv_geodesy`
- `usv_map_core`

It does **not** qualify the guarded Nav2 Hybrid A* adapter and it does **not** override legacy gate Q10.
