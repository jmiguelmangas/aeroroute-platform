# AeroRoute MLX implementation checkpoint

Date: 2026-06-27

> Historical checkpoint: this report assessed the Version 5 trajectory-simulator
> scope. Version 6 expands the MVP with terminal navigation, complete fuel
> planning, alternates, diversions, and OFP presentation. Version 6 therefore
> assigns Phase 10 to terminal navigation and moves hardening to Phase 14; see
> `docs/HLD.md` for the current source of truth and progress baseline.

## Version 6 delivery update — 29 June 2026

Expanded-MVP progress is **100%** for release `1.0.0-mvp`. Phases 10 through 14
are complete. Organization license selection and GitHub branch-protection
settings remain external governance actions, not missing MVP implementation.

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
- `easa_simplified_v1` now reconciles taxi, trip, 5% contingency,
  destination-alternate, 30-minute final reserve, extra, take-off and block
  fuel. A bounded outer iteration feeds non-trip fuel back into solver mass;
  live MAD–JFK B77W converged in two passes within 50 kg;
- destination alternates are user-selectable or deterministically suggested
  from the versioned airport catalogue and require a published AIRAC runway
  meeting the aircraft threshold. Incompatible manual choices remain visible
  and degraded rather than being silently replaced;
- the catalogue contains 42 airports after adding BIKF, CYQX, CYYT, EINN and
  LPLA. Live MAD–JFK selected CYYZ and exposed CYQX and LPLA as informational
  en-route diversion candidates with AIRAC 2606 provenance;
- the frontend accepts an optional destination alternate and extra fuel, and
  renders dedicated fuel-plan and alternate/diversion views with the
  non-operational boundary and mass-convergence status.
- migration `0007_flight_plans` persists an immutable OFP request/output
  snapshot linked to its optimization run. Canonical hashing makes repeated
  creation idempotent while `GET /flight-plans/{id}` never rebuilds from live
  providers;
- payload mass now feeds `operating empty mass + payload` into the optimizer
  rather than being display-only. Callsign and all planning inputs remain in
  the immutable request snapshot;
- the OFP screen renders route encoding, map, terminal procedures, navlog,
  fuel/mass, alternates, diversions and sources. Saved plans have their own
  history and reload route;
- JSON and A4 PDF exports use the stored snapshot. The two-page live B77W PDF
  was rendered to PNG and visually checked for readable repeated headers,
  pagination, footer, warning banner and mandatory disclaimer.
- airport reads now select only the most recently imported immutable airport
  snapshot. Historical rows remain available without duplicating search or
  route-planning results;
- the bundle contains 45 airports after adding PANC, PAFA and PHNL for Pacific
  coverage. Its checksum is frozen in the reference-scenario manifest;
- AIRAC caches expire after six hours, record observed cycles, load corridor
  data on demand and enforce configurable request concurrency and timeout.
  Navigation snapshots persist source, cycles, route status and loading mode;
- `reference/flight-plan-scenarios-2026-06-29.json` freezes MAD-JFK, JFK-MAD,
  DXB-MAD and NRT-SFO with real terminal identifiers, alternates and diversion
  minima. DXB-MAD is connected; oceanic gaps remain explicit degraded `DCT`;
- infeasible NRT-SFO B788 payload/fuel returns stable
  `422 aircraft_mass_outside_profile`; a feasible payload produces a traced OFP
  with GULBO2, STINS4, KLAX and CYVR.
- HTTP middleware emits redacted JSON request events with `X-Request-ID`, route
  templates, status and duration; `/metrics` exposes low-cardinality counters
  and duration sums, while provider health reports observed AIRAC cycles and
  cache policy;
- 1 MiB request limits, per-client fixed-window rate limiting, bounded AIRAC
  concurrency/timeouts and defensive response headers are tested;
- 30-second active-catalogue caching and 128-entry immutable OFP caching reduce
  local P95 to 8.86 ms for airport search and 9.38 ms for OFP reads, below 150
  ms and 200 ms budgets respectively;
- `make verify-live` passes all four frozen OFPs, snapshot reloads and PDF
  signatures. `make performance-live` enforces the local budgets;
- six normalized CycloneDX SBOMs and the frontend production-license inventory
  reproduce byte-for-byte. Python `pip-audit` and npm production audit report
  no known vulnerabilities;
- `docs/OPERATIONS_RUNBOOK.md` covers startup, backup, restore drill, provider
  degradation, dependency review and request-ID incident triage.

Deferred to Phase 13 hardening/generalization:

- progressive cold-load delivery and prefetch for large AIRAC graphs;
- replacement of remaining `DCT` legs only when a versioned source proves
  connectivity; existing degraded output remains the safe fallback.

Current Phase 14 verification: optimizer 60 tests with 90.19% coverage, API 68
collected tests (67 passed, 1 skipped), web 14 unit/component tests, 7
mocked Playwright journeys, 1 real-stack journey, contracts 4 tests, and data 5
tests. Platform has 8 tests covering release fixtures, live validation helpers,
performance math, SBOM normalization and release manifests. Generated-client
freshness, production/Storybook builds, migration 0007, PDF visual review,
security audits, live release verification and performance budgets passed.

This checkpoint compares the current eight-repository workspace with HLD phases
0 through 10. A phase is marked complete only when its implementation and its
acceptance evidence are both present. Later work does not implicitly close an
earlier phase.

## Executive status

The product has a complete Phase 9 user journey and a complete Version 6 Phase
10 terminal-navigation slice over the deterministic API and database stack.
Phase 0 governance and the optional Phase 8/8B model work remain independently
open as optional model/governance tracks; they do not block the completed MVP.

| Phase | Status | Implemented evidence | Remaining acceptance work |
| --- | --- | --- | --- |
| 0. Governance and skeleton | Partial | Eight repositories, boundaries, READMEs, AGENTS files, lock files, Compose, release manifest and local harness exist. Standard checks, CI workflows, CONTRIBUTING guides, CODEOWNERS and PR templates now exist in every repository. | Select and add the organization license, then verify GitHub branch protection, required checks and tracking issues outside the repositories. |
| 1. Pure domain foundations | Complete | SI units, WGS84 geodesy, normalization, wind vectors and pure tests live in `aeroroute-optimizer`. | Keep numerical fixtures reviewed when algorithms change. |
| 2. Database and airport catalogue | Complete | PostGIS migrations, active immutable snapshot selection, airport search, idempotency and spatial tests pass. The public-domain bundle contains 45 airports including Atlantic and Pacific diversion references. AIRAC runways, procedures, fixes, airway graphs and cycle-versioned navigation manifests support terminal assembly without fabricated identifiers. | Broader catalogue coverage remains a post-MVP data operation. |
| 3. Aircraft performance abstraction | Complete | The provider port supports curated and optional OpenAP 2.5 adapters, explicit package provenance, strict SI conversion, fixed climb/descent estimates and adapter contract tests. Aircraft-specific profiles and mass assumptions cover A320, B738, B77W, B788, A359 and A388; real OpenAP calls were verified locally for all six types. | Keep OpenAP optional and review its LGPL-3.0 dependency obligations before distribution. |
| 4. Still-air optimizer and solver | Complete | The bounded lattice, exhaustive oracle, layered label-setting solver, alternatives, budgets, diagnostics and golden fixtures now run inside a pure production use case with three-pass mass/fuel convergence, monotonically decreasing representative mass, fixed terminal phases and a complete normalized objective breakdown. | Keep algorithm-versioned golden review mandatory when numerical assumptions change. |
| 5. Weather integration | Complete | The API builds ordered route snapshots from batched Open-Meteo coordinates, three pressure levels and adjacent forecast hours, with vector/time/geopotential interpolation, retries, cache/stale policy and explicit still-air fallback. The optimizer consumes the resulting wind field per layer and records tailwind components. A read-only dynamic corridor endpoint also exposes 40 real east/north wind vectors around the requested route endpoints at the selected forecast hour and cruise pressure level for MVP visualization. Zero-wind, tailwind, headwind, reverse-route and longer-tailwind-corridor scenarios pass; live Open-Meteo MAD-JFK and DXB-MAD field requests were verified. | Keep provider fixtures synchronized with documented Open-Meteo response changes, retain offline default tests, and do not present the coarse MVP field as operational meteorology. |
| 6. Application use case and API | Complete | Typed request/response, OpenAPI, canonical request hashing, idempotent reuse, history/detail and effective provider health now run with explicit `running`, `completed`, and `failed` short transactions. External calculation occurs after the running commit; concurrency, queue and deadline guards map to stable public errors. Migration 0004 upgrades historical snapshots, and isolated PostGIS verifies the lifecycle and immutable input. | Keep capacity/deadline defaults tuned from measured workloads and preserve the no-long-transaction boundary as orchestration grows. |
| 7. Deterministic explanation | Complete | The fact mapper reads only versioned result snapshots, distinguishes modeled trip fuel from phase/reserve assumptions, renders stable positive, negative and negligible deltas, propagates degraded-data warnings and retains the non-operational disclaimer. Migration 0005 persists one idempotent template or MLX explanation and its facts per completed run. | Keep wording changes golden-reviewed and never permit the explanation layer to recalculate authoritative route values. |
| 8. MLX prompt-only service | Partial, 4B validated | The separate service now has a pinned-manifest validator, lazy MLX-LM lifecycle, JSON-only constrained prompt, numeric and operational-claim validation, bounded timeout and deterministic fallback. Gemma 3 4B revision `4f665a4c50ecfe4ecdc34056ab52fe3e3c4abf9e` passed 3/3 native contract runs on the M4 Mac: 6.015 s cold, 1.335/1.322 s warm and 2,202.4 MB peak RSS. A live B788 API-to-MLX-to-PostGIS run persisted an MLX explanation in 7.31 s and reread it in 13 ms without regeneration. | Complete and benchmark the 12B checkpoint, record Gemma terms acceptance, run the larger repeated quality corpus and document the challenger bake-off before selecting a default model. |
| 8B. QLoRA training | Partial, pre-training | Deterministic records, grouped split, evaluation metrics, promotion logic and example configs exist. | No smoke training, adapter save/load, gold-set comparison, cards, compatibility report, checksums or promoted artifact exist. This remains optional until Phase 8 baselines are measured. |
| 9. Frontend vertical slices | Complete | Generated OpenAPI types, React Hook Form/Zod, 42-airport autocomplete, six aircraft types, TanStack Query, deterministic results, Storybook and MapLibre/OSM views exist. AIRAC and synthetic geometries, wind field, named fixes, airway/`DCT`, editable wind-ranked runways, SID/STAR provenance, technical navlog, fuel/alternate views and full-screen map are visually distinct and accessible. | Retain the non-operational warning while Phase 12 adds the complete OFP workflow and exports. |
| 10. Terminal navigation | Complete | AIRAC runway catalogue, advisory surface-wind ranking, editable runway inputs, SID/STAR selection, connected or explicit degraded `DCT` assembly, cycle snapshots, full-screen map and four live reference scenarios. | Preserve the non-operational boundary; progressive graph loading and reducing sourced `DCT` gaps continue in Phase 13. |
| 11. Fuel, alternates and diversions | Complete | Versioned simplified EASA arithmetic, bounded full-mass reconciliation, editable/suggested runway-compatible destination alternate, AIRAC-sourced diversion candidates, additive OpenAPI fields, persistence and frontend review views pass unit and real-stack verification. | The direct-distance alternate estimate remains educational. Weather minima, NOTAM, airport status, ETOPS/EDTO and dispatch approval remain explicitly outside scope. |
| 12. OFP workflow and frontend | Complete | Immutable flight-plan snapshots, callsign/payload-aware creation, coded route, navlog, fuel/mass, terminal navigation, alternates/diversions, saved-plan history, map and non-operational JSON/PDF exports pass mocked and real-stack verification. | Exports are educational artifacts only and intentionally cannot be submitted as ICAO FPL. |
| 13. Supported-route generalization | Complete | Active catalogue snapshots, bounded on-demand AIRAC loading, cycle/status manifests, stable mass errors and four frozen live reference routes cover the supported MVP catalogue with complete or explicit degraded output. | Expanding beyond the 45-airport catalogue remains post-MVP; no invented identifiers or silent fallback are permitted. |
| 14. Observability, security and hardening | Complete | Structured correlated logs, metrics, provider manifests, request/rate limits, defensive headers, immutable read caches, measured P95 budgets, live four-route verification, reproducible SBOMs, clean dependency audits and operations runbook support release `1.0.0-mvp`. | Continue dependency review, restore drills and performance observation after every release; this does not grant operational approval. |

## Verification evidence

All commands were run from the current workspace with dependency environments
outside the external volume to avoid AppleDouble metadata interference.

| Repository | Result |
| --- | --- |
| `aeroroute-optimizer` | Ruff, mypy, 60 tests and 90.18% coverage passed, including simplified EASA fuel arithmetic and aircraft planning assumptions. |
| `aeroroute-api` | Ruff, 68 collected tests including observability, security headers, rate/request limits, active snapshots, TTL/cycle AIRAC cache, immutable flight plans, PDF rendering, PostGIS lifecycle and stable errors; 67 passed and 1 optional integration test skipped. |
| `aeroroute-data` | Ruff, 5 tests and deterministic 45-airport bundle passed. |
| `aeroroute-mlx` | Ruff, 12 tests, sdist and wheel passed. MLX 0.31.2 and MLX-LM 0.31.3 loaded the local Gemma 3 4B checkpoint; 3/3 native generations passed schema, numeric and operational-claim validation. |
| `aeroroute-mlx-training` | Ruff, 6 tests, sdist and wheel passed. No training run was performed. |
| `aeroroute-web` | ESLint/Prettier, TypeScript, generated-client freshness, 14 unit/component tests, production build, Storybook build, 7 mocked Playwright tests and 1 real-stack Playwright test passed. |
| `aeroroute-contracts` | Four standard-library tests, four validated JSON/OpenAPI documents and a versioned ZIP build passed. |
| `aeroroute-platform` | Ruff, 8 tests, four-route live verifier, P95 budget runner, reproducible SBOM inventory, operations runbook, Compose and release-manifest validation passed. |

Total automated checks observed: 185, including 8 Playwright journeys.

## Required closure sequence

1. Close Phase 0 reproducibility: governance files, standard commands, declared
   platform dependencies and repository-local CI.
2. Record native Phase 8 baselines. Keep Phase 8B unpromoted unless those
   baselines justify training.
3. Keep the completed Phase 9/10 real-stack journeys in release verification.
4. Preserve the frozen scenarios and non-operational boundary for every future
   change; treat broader data coverage and operational certification as new
   product scopes, not silent extensions of this MVP.

## Git hygiene decision

`core.filemode=false` is configured locally in all eight repositories because
the external volume reports regular source files as executable. `.DS_Store`,
AppleDouble `._*`, and `.AppleDouble/` remain ignored. Generated build and test
artifacts are excluded from commits.
