# AeroRoute MVP operations runbook

## Scope

This runbook covers the local educational MVP. It does not make the service an
operational flight-planning system.

## Start and verify

1. Start PostGIS with `docker compose up -d postgis`.
2. Run `uv run alembic upgrade head` in `aeroroute-api`.
3. Start the API with Uvicorn and access logs disabled; structured application
   logs already include request ID, route template, status and duration.
4. Start the Vite frontend.
5. Run `make verify-live` and `make performance-live` in
   `aeroroute-platform`.

## Backup

Create a PostgreSQL custom-format backup without embedding credentials in the
file name or command history:

```bash
docker exec aeroroute-platform-postgis-1 pg_dump \
  --username aeroroute --dbname aeroroute --format custom \
  --file /tmp/aeroroute.dump
docker cp aeroroute-platform-postgis-1:/tmp/aeroroute.dump ./aeroroute.dump
```

Store the dump outside the repository with restricted permissions. Record the
release manifest, airport-bundle SHA-256 and AIRAC cycles alongside it.

## Restore drill

Restore only into a fresh database. Never overwrite the sole working copy.

```bash
createdb aeroroute_restore
pg_restore --exit-on-error --clean --if-exists \
  --dbname aeroroute_restore aeroroute.dump
```

Point a temporary API instance at the restored database, run migrations, then
verify:

- `alembic_version` equals the expected release revision;
- counts for `optimization_runs`, `flight_plans`, and `navigation_snapshots`;
- a stored OFP reloads with the same coded route and fuel block;
- its PDF starts with `%PDF` and retains the disclaimer.

## Provider degradation

- AIRAC outage: explicit runway selections return a stable 503; enrichment
  retains sourced terminal data already available or marks the route degraded.
- Weather outage: optimization uses the documented still-air fallback and adds
  `WEATHER_FALLBACK` or `WEATHER_STILL_AIR`.
- MLX outage: explanation falls back to deterministic text; route and fuel are
  never recalculated by the language model.
- No runway-compatible alternate or diversion: the OFP remains visible with a
  warning; no airport is fabricated.

## Security and dependency review

Generate inventories with `scripts/generate_sbom.sh`. Review CycloneDX and web
license output before a release, then run the repository's configured GitHub
dependency and secret scanning. Do not commit database dumps, environment
files, credentials, provider tokens, or model-license acceptance records.

## Incident triage

Use `X-Request-ID` to correlate the public response with the JSON HTTP log.
Inspect `/metrics` for route/status counts and duration sums. Preserve the
immutable optimization, navigation, and flight-plan snapshots when reporting a
reproducibility defect.
