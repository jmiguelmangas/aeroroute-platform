# AeroRoute platform rules

Read `README.md`, `docs/HLD.md`, and the relevant ADR before changing this
repository. Do not put product logic here or patch sibling source at runtime.
Integration tests consume released artifacts. Never describe the simulator as
operational flight planning.

Context: architecture decisions and cross-repo history live in the
wiki-personal repo (wiki/projects/aeroroute.md). Run
`python3 scripts/graphify_export.py .` here to refresh this repo's code+docs
dependency graph.
