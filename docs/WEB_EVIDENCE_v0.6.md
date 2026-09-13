# Web evidence — v0.6 GitHub Actions

Verified 2026-09-13.

- GitHub-hosted `ubuntu-24.04` is a full VM runner; public repos currently receive 4 CPU, 16 GB RAM and 14 GB SSD on standard Linux runners. `ubuntu-slim` is an unprivileged container and is not suitable for Docker-heavy qualification.
- GitHub-hosted workflows can run commands directly on the VM or in Docker containers.
- Workflow artifacts can be uploaded after build/test steps; artifact retention is configurable. The v0.6 workflows use 30 days.
- `actions/checkout` current v7.0.1 commit pinned in this kit: `3d3c42e5aac5ba805825da76410c181273ba90b1`.
- `actions/upload-artifact` v7.0.0 commit pinned in this kit: `bbbca2ddaa5d8feaa63e36b76fdaad77386f024f`.

See response citations for official GitHub documentation / release references.
