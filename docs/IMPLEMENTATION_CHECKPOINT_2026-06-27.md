# AeroRoute MLX implementation checkpoint

Date: 2026-06-27

> Historical checkpoint: this report assessed the Version 5 trajectory-simulator
> scope. Version 6 expands the MVP with terminal navigation, complete fuel
> planning, alternates, diversions, and OFP presentation. Version 6 therefore
> assigns Phase 10 to terminal navigation and moves hardening to Phase 14; see
> `docs/HLD.md` for the current source of truth and progress baseline.

## Version 6 delivery update — 28 June 2026

Expanded-MVP progress is **70%**. Phase 10 terminal navigation is complete; the
next implementation phase is Phase 11 fuel, alternates, and diversions.

Implemented evidence:

- additive OpenAPI/contracts `0.2.0` preserve `/optimizations` compatibility and
  add optional departure/arrival runway inputs, terminal-selection output, and
  AIRAC runway/procedure catalogue endpoints;
- the UI loads AIRAC runway choices, shows deterministic recommendations, lets
  the user override each runway, submits explicit selections, and displays the
  resulting SID/STAR and cycle provenance;
- the AIRAC adapter expands both physical runway ends, supports runway-family
  procedures and runway-independent `ALL` transitions, and rejects explicit
  runways without compatible procedures;
- the graph assembler supports SID exits and STAR entry goals. A real DXB–MAD
  B77W run resolved `RWY 30L → NABI3F → AIRAC airway graph → RIDA5C → RWY 32L`;
- disconnected terminal graphs retain runway-compatible SID/STAR around
  explicit oceanic `DCT`/coordinate legs and return
  `TERMINAL_ROUTE_DISCONNECTED`; no identifier is fabricated;
- request hashes now include a terminal-navigation version, preventing reuse of
  Version 5 snapshots, and enrichment failures correctly mark runs failed;
- the interactive map has an accessible full-viewport mode with `Esc`, layer
  controls, background-scroll locking, and MapLibre resize handling.
- the reproducible airport bundle now contains 37 airports, including RJAA/NRT
  and KSFO/SFO; it was imported into PostGIS with a new immutable checksum, and
  NRT–SFO now calculates with suggested runways plus an explicit disconnected
  terminal warning rather than failing catalogue lookup.
- migration `0006_navigation_snapshots` persists a dedicated immutable AIRAC
  snapshot per run; a verified DXB–MAD row stores cycle `2606`, 58 navigation
  points, SID `SENP3G`, and STAR `RIDA3A`;
- optional Open-Meteo 10 m wind influences runway ranking. A live Madrid query
  selected `36L` from a 2.4 kt wind at 014° and exposed headwind/crosswind
  components while retaining NOTAM/runway-condition/ATC limitations;
- live MAD–JFK, JFK–MAD, DXB–MAD, and NRT–SFO scenarios all return compatible
  runways and real terminal identifiers; non-continuous airway joins remain
  explicit `DCT` legs.

Deferred to Phase 13 hardening/generalization:

- progressive cold-load delivery and prefetch for large AIRAC graphs;
- replacement of remaining `DCT` legs only when a versioned source proves
  connectivity; existing degraded output remains the safe fallback.

Current Phase 10 verification: API 53 passed and 1 skipped, web 13 unit/component
tests, 6 mocked Playwright journeys, 1 real-stack Playwright journey, contracts
4 tests, data 5 tests, generated-client freshness, production build, all four
live terminal scenarios, and persisted navigation-snapshot inspection passed.

This checkpoint compares the current eight-repository workspace with HLD phases
0 through 10. A phase is marked complete only when its implementation and its
acceptance evidence are both present. Later work does not implicitly close an
earlier phase.

## Executive status

The product has a complete Phase 9 user journey and a complete Version 6 Phase
10 terminal-navigation slice over the deterministic API and database stack.
Phase 0 governance and the optional Phase 8/8B model work remain independently
open; they do not block beginning Phase 11 domain implementation.

| Phase | Status | Implemented evidence | Remaining acceptance work |
| --- | --- | --- | --- |
| 0. Governance and skeleton | Partial | Eight repositories, boundaries, READMEs, AGENTS files, lock files, Compose, release manifest and local harness exist. Standard checks, CI workflows, CONTRIBUTING guides, CODEOWNERS and PR templates now exist in every repository. | Select and add the organization license, then verify GitHub branch protection, required checks and tracking issues outside the repositories. |
| 1. Pure domain foundations | Complete | SI units, WGS84 geodesy, normalization, wind vectors and pure tests live in `aeroroute-optimizer`. | Keep numerical fixtures reviewed when algorithms change. |
| 2. Database and airport catalogue | Complete | PostGIS migrations, immutable bundle import, airport search, idempotency and spatial tests pass. The public-domain bundle now contains 37 airports including RJAA and KSFO. AIRAC runways, procedures, fixes, airway graphs and cycle-versioned navigation snapshots support terminal assembly without fabricated identifiers. | Progressive first-load graph delivery and broader airport coverage continue in Phase 13. |
| 3. Aircraft performance abstraction | Complete | The provider port supports curated and optional OpenAP 2.5 adapters, explicit package provenance, strict SI conversion, fixed climb/descent estimates and adapter contract tests. Aircraft-specific profiles and mass assumptions cover A320, B738, B77W, B788, A359 and A388; real OpenAP calls were verified locally for all six types. | Keep OpenAP optional and review its LGPL-3.0 dependency obligations before distribution. |
| 4. Still-air optimizer and solver | Complete | The bounded lattice, exhaustive oracle, layered label-setting solver, alternatives, budgets, diagnostics and golden fixtures now run inside a pure production use case with three-pass mass/fuel convergence, monotonically decreasing representative mass, fixed terminal phases and a complete normalized objective breakdown. | Keep algorithm-versioned golden review mandatory when numerical assumptions change. |
| 5. Weather integration | Complete | The API builds ordered route snapshots from batched Open-Meteo coordinates, three pressure levels and adjacent forecast hours, with vector/time/geopotential interpolation, retries, cache/stale policy and explicit still-air fallback. The optimizer consumes the resulting wind field per layer and records tailwind components. A read-only dynamic corridor endpoint also exposes 40 real east/north wind vectors around the requested route endpoints at the selected forecast hour and cruise pressure level for MVP visualization. Zero-wind, tailwind, headwind, reverse-route and longer-tailwind-corridor scenarios pass; live Open-Meteo MAD-JFK and DXB-MAD field requests were verified. | Keep provider fixtures synchronized with documented Open-Meteo response changes, retain offline default tests, and do not present the coarse MVP field as operational meteorology. |
| 6. Application use case and API | Complete | Typed request/response, OpenAPI, canonical request hashing, idempotent reuse, history/detail and effective provider health now run with explicit `running`, `completed`, and `failed` short transactions. External calculation occurs after the running commit; concurrency, queue and deadline guards map to stable public errors. Migration 0004 upgrades historical snapshots, and isolated PostGIS verifies the lifecycle and immutable input. | Keep capacity/deadline defaults tuned from measured workloads and preserve the no-long-transaction boundary as orchestration grows. |
| 7. Deterministic explanation | Complete | The fact mapper reads only versioned result snapshots, distinguishes modeled trip fuel from phase/reserve assumptions, renders stable positive, negative and negligible deltas, propagates degraded-data warnings and retains the non-operational disclaimer. Migration 0005 persists one idempotent template or MLX explanation and its facts per completed run. | Keep wording changes golden-reviewed and never permit the explanation layer to recalculate authoritative route values. |
| 8. MLX prompt-only service | Partial, 4B validated | The separate service now has a pinned-manifest validator, lazy MLX-LM lifecycle, JSON-only constrained prompt, numeric and operational-claim validation, bounded timeout and deterministic fallback. Gemma 3 4B revision `4f665a4c50ecfe4ecdc34056ab52fe3e3c4abf9e` passed 3/3 native contract runs on the M4 Mac: 6.015 s cold, 1.335/1.322 s warm and 2,202.4 MB peak RSS. A live B788 API-to-MLX-to-PostGIS run persisted an MLX explanation in 7.31 s and reread it in 13 ms without regeneration. | Complete and benchmark the 12B checkpoint, record Gemma terms acceptance, run the larger repeated quality corpus and document the challenger bake-off before selecting a default model. |
| 8B. QLoRA training | Partial, pre-training | Deterministic records, grouped split, evaluation metrics, promotion logic and example configs exist. | No smoke training, adapter save/load, gold-set comparison, cards, compatibility report, checksums or promoted artifact exist. This remains optional until Phase 8 baselines are measured. |
| 9. Frontend vertical slices | Complete | Generated OpenAPI types, React Hook Form/Zod, 37-airport autocomplete, six aircraft types, TanStack Query, deterministic results, Storybook and MapLibre/OSM views exist. AIRAC and synthetic geometries, wind field, named fixes, airway/`DCT`, editable wind-ranked runways, SID/STAR provenance, technical navlog and full-screen map are visually distinct and accessible. | Retain the non-operational warning and extend the same component system for Phase 11 fuel and alternate planning. |
| 10. Terminal navigation | Complete | AIRAC runway catalogue, advisory surface-wind ranking, editable runway inputs, SID/STAR selection, connected or explicit degraded `DCT` assembly, cycle snapshots, full-screen map and four live reference scenarios. | Preserve the non-operational boundary; progressive graph loading and reducing sourced `DCT` gaps continue in Phase 13. |

## Verification evidence

All commands were run from the current workspace with dependency environments
outside the external volume to avoid AppleDouble metadata interference.

| Repository | Result |
| --- | --- |
| `aeroroute-optimizer` | Ruff, mypy, 47 tests and 89.57% coverage passed; OpenAP 2.5.0 was exercised directly for A320, B738, B77W, B788, A359 and A388. |
| `aeroroute-api` | Ruff, 54 collected tests including real PostGIS migration/import/lifecycle/explanation coverage, AIRAC runway/procedure parsing, connected and segmented terminal assembly, advisory surface wind, navigation snapshots, request-version hashing, weather orchestration, idempotency and stable errors; Alembic through revision 0006, sdist and wheel passed. |
| `aeroroute-data` | Ruff, 5 tests, deterministic 37-airport bundle, sdist and wheel passed. |
| `aeroroute-mlx` | Ruff, 12 tests, sdist and wheel passed. MLX 0.31.2 and MLX-LM 0.31.3 loaded the local Gemma 3 4B checkpoint; 3/3 native generations passed schema, numeric and operational-claim validation. |
| `aeroroute-mlx-training` | Ruff, 6 tests, sdist and wheel passed. No training run was performed. |
| `aeroroute-web` | ESLint/Prettier, TypeScript, generated-client freshness, 13 unit/component tests, production build, Storybook build, 6 mocked Playwright tests and 1 real-stack Playwright test passed. |
| `aeroroute-contracts` | Four standard-library tests, four validated JSON/OpenAPI documents and a versioned ZIP build passed. |
| `aeroroute-platform` | Ruff, 2 tests, Compose configuration and release-manifest validation passed through the reproducible `make check` command. |

Total automated tests observed: 150.

## Required closure sequence

1. Close Phase 0 reproducibility: governance files, standard commands, declared
   platform dependencies and repository-local CI.
2. Record native Phase 8 baselines. Keep Phase 8B unpromoted unless those
   baselines justify training.
3. Keep the completed Phase 9/10 real-stack journeys in release verification.
4. Implement Phase 11 fuel, destination alternate and en-route diversions next;
   retain Phase 14 for final hardening.

## Git hygiene decision

`core.filemode=false` is configured locally in all eight repositories because
the external volume reports regular source files as executable. `.DS_Store`,
AppleDouble `._*`, and `.AppleDouble/` remain ignored. Generated build and test
artifacts are excluded from commits.
