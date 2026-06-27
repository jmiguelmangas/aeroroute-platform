# AeroRoute MLX implementation checkpoint

Date: 2026-06-27

This checkpoint compares the current eight-repository workspace with HLD phases
0 through 10. A phase is marked complete only when its implementation and its
acceptance evidence are both present. Later work does not implicitly close an
earlier phase.

## Executive status

The product currently has a working Phase 9 user journey over a deterministic
still-air backend. It is not ready to enter Phase 10 because several earlier
phase acceptance criteria remain open, chiefly repository governance,
PostGIS-backed integration coverage, aircraft-adapter scope, weather-aware
orchestration, and native MLX validation.

| Phase | Status | Implemented evidence | Remaining acceptance work |
| --- | --- | --- | --- |
| 0. Governance and skeleton | Partial | Eight repositories, boundaries, READMEs, AGENTS files, lock files, Compose, release manifest and local harness exist. Platform and contracts tooling now declare reproducible standard `make check` surfaces. | LICENSE, CONTRIBUTING, CODEOWNERS and PR templates are absent across the organization. Several repositories lack CI. |
| 1. Pure domain foundations | Complete | SI units, WGS84 geodesy, normalization, wind vectors and pure tests live in `aeroroute-optimizer`. | Keep numerical fixtures reviewed when algorithms change. |
| 2. Database and airport catalogue | Partial | PostGIS schema, Alembic airport migration, immutable bundle generation/import and airport search endpoint exist. | Add disposable real-PostGIS migration up/down and repository integration tests. |
| 3. Aircraft performance abstraction | Partial | Provider port, curated deterministic performance and still-air segment estimates exist. | Implement or explicitly defer the OpenAP adapter; add fixed climb/descent estimates and adapter provenance/contract tests. |
| 4. Still-air optimizer and solver | Partial | Bounded lattice, exhaustive oracle, layered label-setting solver, alternatives, budgets, diagnostics and golden fixtures exist. | Integrate the mass/fuel fixed-point loop into the production use case and expose the full objective/cost breakdown required by the HLD. |
| 5. Weather integration | Partial | Weather port, Open-Meteo client, cache/stale policy, interpolation and provider-neutral wind segment evaluation exist. | The optimization endpoint still calls `optimize_still_air`; connect normalized weather snapshots to problem construction and pass the required metamorphic end-to-end scenarios. |
| 6. Application use case and API | Partial | Typed request/response, OpenAPI, request hashing, persistence, history, stored result detail and provider health exist. | Implement running/completed/failed lifecycle transactions, stable provider failure mapping, concurrency limits, cancellation/deadline behavior and real database integration tests. |
| 7. Deterministic explanation | Partial | Fact mapper, deterministic fallback, warnings, provider label and endpoint exist. | Persist explanations and broaden golden tests for deltas and stable wording. |
| 8. MLX prompt-only service | Partial | Separate service, constrained prompt, output contract, numeric validator and fallback behavior exist. | Run and record Gemma 3 12B/4B Apple Silicon compatibility, model lifecycle, memory/latency benchmark and repeated native contract suite. |
| 8B. QLoRA training | Partial, pre-training | Deterministic records, grouped split, evaluation metrics, promotion logic and example configs exist. | No smoke training, adapter save/load, gold-set comparison, cards, compatibility report, checksums or promoted artifact exist. This remains optional until Phase 8 baselines are measured. |
| 9. Frontend vertical slices | Functional, acceptance partial | Generated OpenAPI types, React Hook Form/Zod, airport autocomplete, TanStack Query, deterministic results, backend GeoJSON, layer controls, waypoint details, history/detail routes, Storybook, Playwright degraded paths and axe checks exist. | Add React Testing Library/MSW behavior tests, score breakdown, full real-stack Playwright acceptance and a generated-client compatibility check in CI. |
| 10. Hardening | Not started | Health endpoints and some graceful fallback behavior are useful prerequisites only. | Do not begin until the closure sequence below is complete. |

## Verification evidence

All commands were run from the current workspace with dependency environments
outside the external volume to avoid AppleDouble metadata interference.

| Repository | Result |
| --- | --- |
| `aeroroute-optimizer` | Ruff, mypy, 24 tests, 89.88% coverage, sdist and wheel passed. |
| `aeroroute-api` | Ruff, 21 tests, Alembic offline SQL through revision 0003, sdist and wheel passed. |
| `aeroroute-data` | Ruff, 3 tests, sdist and wheel passed. |
| `aeroroute-mlx` | Ruff, 4 tests, sdist and wheel passed. Native Gemma execution was not part of this check. |
| `aeroroute-mlx-training` | Ruff, 6 tests, sdist and wheel passed. No training run was performed. |
| `aeroroute-web` | ESLint/Prettier, TypeScript, 3 unit tests, production build, Storybook build and 6 Playwright tests passed. |
| `aeroroute-contracts` | Three standard-library tests, four validated JSON/OpenAPI documents and a versioned ZIP build passed. |
| `aeroroute-platform` | Ruff, 2 tests, Compose configuration and release-manifest validation passed through the reproducible `make check` command. |

Total automated tests observed: 72.

## Required closure sequence

1. Close Phase 0 reproducibility: governance files, standard commands, declared
   platform dependencies and repository-local CI.
2. Close Phase 2 integration with disposable PostGIS migration and importer
   tests.
3. Decide the Phase 3 OpenAP scope and integrate production mass iteration for
   Phase 4.
4. Connect weather snapshots to optimization and pass Phase 5 metamorphic
   scenarios.
5. Complete the Phase 6 run lifecycle and concurrency behavior, then persist
   Phase 7 explanations.
6. Record native Phase 8 baselines. Keep Phase 8B unpromoted unless those
   baselines justify training.
7. Finish Phase 9 component/MSW and real-stack acceptance tests.
8. Only then open Phase 10 hardening work.

## Git hygiene decision

`core.filemode=false` is configured locally in all eight repositories because
the external volume reports regular source files as executable. `.DS_Store`,
AppleDouble `._*`, and `.AppleDouble/` remain ignored. Generated build and test
artifacts are excluded from commits.
