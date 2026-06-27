# AeroRoute MLX implementation checkpoint

Date: 2026-06-27

This checkpoint compares the current eight-repository workspace with HLD phases
0 through 10. A phase is marked complete only when its implementation and its
acceptance evidence are both present. Later work does not implicitly close an
earlier phase.

## Executive status

The product now has a complete Phase 9 user journey over the deterministic API
and database stack. It is not ready to enter Phase 10 because earlier acceptance
criteria remain open, chiefly external repository governance and native MLX
validation.

| Phase | Status | Implemented evidence | Remaining acceptance work |
| --- | --- | --- | --- |
| 0. Governance and skeleton | Partial | Eight repositories, boundaries, READMEs, AGENTS files, lock files, Compose, release manifest and local harness exist. Standard checks, CI workflows, CONTRIBUTING guides, CODEOWNERS and PR templates now exist in every repository. | Select and add the organization license, then verify GitHub branch protection, required checks and tracking issues outside the repositories. |
| 1. Pure domain foundations | Complete | SI units, WGS84 geodesy, normalization, wind vectors and pure tests live in `aeroroute-optimizer`. | Keep numerical fixtures reviewed when algorithms change. |
| 2. Database and airport catalogue | Complete | PostGIS schema, Alembic migrations, immutable bundle generation/import, airport search and a real-PostGIS integration test cover upgrade/downgrade, idempotency and spatial coordinate order. A reproducible public-domain OurAirports MVP bundle now provides 35 globally distributed ICAO airports instead of the original two-airport fixture. | Keep the PostGIS image, source checksum and migration test aligned with supported release platforms. |
| 3. Aircraft performance abstraction | Complete | The provider port supports curated and optional OpenAP 2.5 adapters, explicit package provenance, strict SI conversion, fixed climb/descent estimates and adapter contract tests. Aircraft-specific profiles and mass assumptions cover A320, B738, B77W, B788, A359 and A388; real OpenAP calls were verified locally for all six types. | Keep OpenAP optional and review its LGPL-3.0 dependency obligations before distribution. |
| 4. Still-air optimizer and solver | Complete | The bounded lattice, exhaustive oracle, layered label-setting solver, alternatives, budgets, diagnostics and golden fixtures now run inside a pure production use case with three-pass mass/fuel convergence, monotonically decreasing representative mass, fixed terminal phases and a complete normalized objective breakdown. | Keep algorithm-versioned golden review mandatory when numerical assumptions change. |
| 5. Weather integration | Complete | The API builds ordered route snapshots from batched Open-Meteo coordinates, three pressure levels and adjacent forecast hours, with vector/time/geopotential interpolation, retries, cache/stale policy and explicit still-air fallback. The optimizer consumes the resulting wind field per layer and records tailwind components. Zero-wind, tailwind, headwind, reverse-route and longer-tailwind-corridor scenarios pass; a live Open-Meteo MAD-JFK run was also verified. | Keep provider fixtures synchronized with documented Open-Meteo response changes and retain offline default tests. |
| 6. Application use case and API | Complete | Typed request/response, OpenAPI, canonical request hashing, idempotent reuse, history/detail and effective provider health now run with explicit `running`, `completed`, and `failed` short transactions. External calculation occurs after the running commit; concurrency, queue and deadline guards map to stable public errors. Migration 0004 upgrades historical snapshots, and isolated PostGIS verifies the lifecycle and immutable input. | Keep capacity/deadline defaults tuned from measured workloads and preserve the no-long-transaction boundary as orchestration grows. |
| 7. Deterministic explanation | Complete | The fact mapper reads only versioned result snapshots, distinguishes modeled trip fuel from phase/reserve assumptions, renders stable positive, negative and negligible deltas, propagates degraded-data warnings and retains the non-operational disclaimer. Migration 0005 persists one idempotent template or MLX explanation and its facts per completed run. | Keep wording changes golden-reviewed and never permit the explanation layer to recalculate authoritative route values. |
| 8. MLX prompt-only service | Partial | Separate service, constrained prompt, output contract, numeric validator and fallback behavior exist. | Run and record Gemma 3 12B/4B Apple Silicon compatibility, model lifecycle, memory/latency benchmark and repeated native contract suite. |
| 8B. QLoRA training | Partial, pre-training | Deterministic records, grouped split, evaluation metrics, promotion logic and example configs exist. | No smoke training, adapter save/load, gold-set comparison, cards, compatibility report, checksums or promoted artifact exist. This remains optional until Phase 8 baselines are measured. |
| 9. Frontend vertical slices | Complete | Generated OpenAPI types, React Hook Form/Zod, 35-airport autocomplete, six selectable aircraft types, TanStack Query, deterministic results, backend GeoJSON, layer controls, explicitly labelled synthetic-node details, dynamic route endpoints, history/detail routes, objective and fuel breakdown, and Storybook exist. React Testing Library/MSW covers widebody submission and degraded behavior; CI checks generated-client freshness against `aeroroute-contracts`; six mocked Playwright journeys cover happy/degraded/MLX/history/accessibility behavior; and a no-mock B788 journey passes against the live API and PostGIS. | Keep mocked browser tests in PR CI and run the real-stack journey in release verification whenever API or contract behavior changes. |
| 10. Hardening | Not started | Health endpoints and some graceful fallback behavior are useful prerequisites only. | Do not begin until the closure sequence below is complete. |

## Verification evidence

All commands were run from the current workspace with dependency environments
outside the external volume to avoid AppleDouble metadata interference.

| Repository | Result |
| --- | --- |
| `aeroroute-optimizer` | Ruff, mypy, 47 tests and 89.57% coverage passed; OpenAP 2.5.0 was exercised directly for A320, B738, B77W, B788, A359 and A388. |
| `aeroroute-api` | Ruff, 36 collected tests including real PostGIS migration/import/lifecycle/explanation coverage, weather forecast/fallback orchestration, idempotency, concurrency/deadline guards, stable errors and CORS preflight, Alembic SQL through revision 0005, sdist and wheel passed. |
| `aeroroute-data` | Ruff, 5 tests, deterministic 35-airport bundle, sdist and wheel passed. |
| `aeroroute-mlx` | Ruff, 4 tests, sdist and wheel passed. Native Gemma execution was not part of this check. |
| `aeroroute-mlx-training` | Ruff, 6 tests, sdist and wheel passed. No training run was performed. |
| `aeroroute-web` | ESLint/Prettier, TypeScript, generated-client freshness, 4 unit/component tests, production build, Storybook build, 6 mocked Playwright tests and 1 real-stack Playwright test passed. |
| `aeroroute-contracts` | Three standard-library tests, four validated JSON/OpenAPI documents and a versioned ZIP build passed. |
| `aeroroute-platform` | Ruff, 2 tests, Compose configuration and release-manifest validation passed through the reproducible `make check` command. |

Total automated tests observed: 114.

## Required closure sequence

1. Close Phase 0 reproducibility: governance files, standard commands, declared
   platform dependencies and repository-local CI.
2. Record native Phase 8 baselines. Keep Phase 8B unpromoted unless those
   baselines justify training.
3. Keep the completed Phase 9 real-stack journey in release verification.
4. Only after Phases 0 and 8 close, open Phase 10 hardening work.

## Git hygiene decision

`core.filemode=false` is configured locally in all eight repositories because
the external volume reports regular source files as executable. `.DS_Store`,
AppleDouble `._*`, and `.AppleDouble/` remain ignored. Generated build and test
artifacts are excluded from commits.
