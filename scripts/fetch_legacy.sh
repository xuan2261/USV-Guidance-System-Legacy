#!/usr/bin/env bash
set -euo pipefail
WS="${1:-/workspace}"
HARNESS="${HARNESS_ROOT:-/harness}"
SRC="$WS/src"
UPSTREAM="$SRC/usv_guidance_system"
mkdir -p "$SRC"
repo_url="https://github.com/sanderfu/USV-Guidance-System.git"
repo_sha="c930b938302d8cfe8c378dfa69748a33d3d76459"
if [[ ! -d "$UPSTREAM/.git" ]]; then git clone --filter=blob:none "$repo_url" "$UPSTREAM"; fi
git -C "$UPSTREAM" fetch --tags --force origin "$repo_sha"
git -C "$UPSTREAM" checkout --detach "$repo_sha"
actual="$(git -C "$UPSTREAM" rev-parse HEAD)"
[[ "$actual" == "$repo_sha" ]]
python3 "$HARNESS/scripts/fetch_dependencies.py" "$HARNESS/locks/dependencies.repos" "$SRC"
python3 "$HARNESS/scripts/write_identity.py" \
  --workspace "$WS" --upstream "$UPSTREAM" --deps-lock "$HARNESS/locks/dependencies.repos" \
  --source-out "${RETURN_DIR:-/return}/source_identity.json" \
  --deps-out "${RETURN_DIR:-/return}/dependency_identity.json"
