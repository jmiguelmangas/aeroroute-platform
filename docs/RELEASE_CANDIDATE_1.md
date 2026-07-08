# AeroRoute MLX system-v1.0.0-rc1

Generated: 2026-07-08T20:07:36Z

This release candidate freezes the completed educational pre-operational OFP
MVP. It is not an operational flight-planning release, is not ICAO-fileable, and
must not be used for ATC filing or safety-critical decisions.

## Coordinated Tag

Use the coordinated tag `system-v1.0.0-rc1` in every AeroRoute repository. The
platform repository tag is the authoritative system release-candidate pointer
and carries this evidence document.

## Component Snapshot

| Repository | RC commit |
| --- | --- |
| `aeroroute-api` | `14b9c04cc4cbd6fc68cfa92ec3de30b9eea7ccc0` |
| `aeroroute-web` | `e3182000d456981905120834beeb825328de6ce5` |
| `aeroroute-platform` | resolved by tag `system-v1.0.0-rc1` |
| `aeroroute-contracts` | `822d0012acdcc242f3aa567dd1ca34743ddb5bdc` |
| `aeroroute-data` | `6e8d50a35d39ffb3d424ae970c93b42f1493632b` |
| `aeroroute-optimizer` | `000b3c662d26d50899e9c2efa41968d5e02d4197` |
| `aeroroute-mlx` | `37fe4d34d172579f15bb9681589e76dc6b38aa2b` |
| `aeroroute-mlx-training` | `a85f5d433091777480f20adf582ba328e2835791` |

## Release Evidence

Local gates passed on the RC workspace:

| Area | Evidence |
| --- | --- |
| API | `make check`: 77 passed, 1 skipped; wheel/sdist built for `aeroroute-api 0.6.0`. |
| Web | `pnpm check`: lint, typecheck, generated client check, 14 unit tests, production build, Storybook build. |
| Platform | `make check`: 16 tests, Compose config, release manifest, route coverage and Phase 14 gate. |
| Live release | `make verify-live`: MAD-JFK, JFK-MAD, DXB-MAD and NRT-SFO OFPs reproduced against local API/PostGIS. |
| Performance | `make performance-live`: airport search P95 4.14 ms against 150 ms budget; flight-plan read P95 2.88 ms against 200 ms budget. |
| Browser simulation | `pnpm e2e -- e2e/simulation.spec.ts`: 7 Playwright tests passed, including fullscreen map, layers, stored OFP, API degradation and WCAG serious/critical scan. |
| Browser real stack | `pnpm e2e:real`: live MAD-JFK optimization through API and database passed. |
| Contracts | `make check`: 4 contract documents validated, 4 tests passed, release zip built. |
| Data | `make check`: 5 tests passed, airport data wheel/sdist built. |
| Optimizer | `make check`: 60 tests passed, 90.19% coverage, wheel/sdist built. |
| MLX service | `make check`: 12 tests passed, wheel/sdist built. |
| MLX training | `make check`: 6 tests passed, wheel/sdist built. |

Latest GitHub Actions CI was green for all eight repositories at their RC
commits before tag creation.

## Demo Baseline

The local RC demo uses:

- frontend: `http://127.0.0.1:5173/`;
- API: `http://127.0.0.1:8000`;
- PostGIS: `aeroroute-platform-postgis-1` on port `55432`;
- airport bundle: `aeroroute-data/bundles/mvp-airports-2026.06.27`;
- AIRAC cycle: `2606` as frozen in `RELEASES.yaml`;
- reference route pairs: `MAD-JFK`, `JFK-MAD`, `DXB-MAD`, `NRT-SFO`.

Before a live demo, run:

```bash
cd aeroroute-platform
make dev-up
cd ../aeroroute-api
uv run alembic upgrade head
uv run aeroroute import-airports --bundle ../aeroroute-data/bundles/mvp-airports-2026.06.27
cd ../aeroroute-platform
make verify-live
make performance-live
```

## RC1 Scope

Included:

- educational OFP generation with real airport identifiers, runway selection,
  SID/STAR enrichment, route status and explicit degraded `DCT` segments;
- destination alternate, en-route diversions, simplified configurable EASA fuel
  components and PDF/JSON export;
- interactive map with fullscreen mode, route layers, navigation points and
  wind-field overlay where available;
- reproducible release manifest, route coverage report, SBOM/license inventory,
  runbook, live verifier and performance budget checks.

Still outside scope:

- ICAO FPL filing;
- NOTAM/RAD/ATC route validation;
- overflight permissions;
- MEL/CDL effects;
- ETOPS/EDTO approval;
- operational certification or dispatch authorization.

## RC1 Risks To Review Manually

- Map and wind overlays are suitable for demo and education, but not operational
  meteorology.
- Supported route coverage is intentionally limited to the MVP catalogue and
  four frozen reference pairs.
- AIRAC enrichment is on-demand and may degrade when the provider or source
  graph is incomplete.
- The web production build emits large chunk warnings; this is acceptable for
  RC1 but should be handled with code splitting post-MVP.
