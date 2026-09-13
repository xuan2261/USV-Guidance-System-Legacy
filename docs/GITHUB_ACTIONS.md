# GitHub Actions execution guide — v0.6

This kit can run on GitHub-hosted `ubuntu-24.04` runners. It intentionally does not use `pull_request_target`, repository secrets, privileged containers, host networking, `/dev` passthrough, or SSH-key mounts.

## Workflows

### 1. Static audit
`.github/workflows/static-audit.yml`

Runs automatically on pushes / pull requests to `main`, and manually. It validates workflow YAML, runs the artifact self-test, and uploads a small evidence artifact.

### 2. Phase 1.1 ROS 2 qualification
`.github/workflows/phase11-ros2.yml`

Manual workflow. It pulls `ros:jazzy-ros-base-noble`, records its full RepoDigest, builds the Phase 1.1 image, runs `rosdep`, `colcon build`, `colcon test`, and uploads `PHASE11_RETURN.zip` even when qualification fails.

### 3. Legacy ROS 1 qualification
`.github/workflows/legacy-qualification.yml`

Manual workflow with input `runtime_mode = none | smoke | all`. It builds the pinned Noetic qualification image and runs Q0–Q10 evidence collection. The return bundle is uploaded with `if: always()`.

## Recommended first run
1. Push the extracted v0.6 folder as the root of a new GitHub repository.
2. Open **Actions → Static audit → Run workflow** (or push to `main`).
3. Run **Phase 1.1 ROS 2 qualification**.
4. Run **Legacy ROS 1 qualification** with `runtime_mode=none` first; if build/launch parsing succeeds, rerun with `smoke`.
5. Download both workflow artifacts and return `PHASE11_RETURN.zip` and `QUALIFICATION_RETURN.zip` for differential audit.

## Why the legacy job is manual
The Noetic desktop image plus build dependencies are large. GitHub standard hosted Linux runners have finite local SSD, so keeping the legacy job manual prevents expensive/redundant pulls on every commit. If the job hits disk pressure, use a larger or self-hosted Linux runner; do not weaken dependency pinning to make it smaller.

## Security model
- `permissions: contents: read`
- no secrets are referenced
- no `pull_request_target`
- checkout credentials are not persisted
- third-party GitHub-owned actions are pinned by full commit SHA
- Docker containers run only on ephemeral GitHub-hosted VMs; `--privileged`, host network and device passthrough are not used
- evidence upload runs with `if: always()`

## Expected Actions artifacts
- `usv-static-evidence-<run_id>`
- `phase11-return-<run_id>`
- `legacy-qualification-return-<run_id>`

Artifacts are configured for 30-day retention by the workflows. Repository/org policy may impose a different upper bound.
