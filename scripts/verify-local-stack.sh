#!/usr/bin/env bash
set -euo pipefail

workspace="$(cd "$(dirname "$0")/../.." && pwd)"
data_repo="$workspace/aeroroute-data"
api_repo="$workspace/aeroroute-api"
mlx_repo="$workspace/aeroroute-mlx"
bundle_dir="${TMPDIR:-/tmp}/aeroroute-platform-airport-bundle"
mlx_port=8765

docker compose -f "$workspace/aeroroute-platform/compose.yaml" \
  -f "$workspace/aeroroute-platform/compose.profiles.yaml" \
  --profile core-linux up -d

uv --directory "$api_repo" run alembic -c alembic.ini upgrade head
uv --directory "$data_repo" run aeroroute-data build-airports \
  --source tests/fixtures/airports.csv \
  --output "$bundle_dir" \
  --version 2026.06.1
uv --directory "$api_repo" run aeroroute import-airports --bundle "$bundle_dir"
uv --directory "$mlx_repo" run uvicorn aeroroute_mlx.main:app \
  --host 127.0.0.1 --port "$mlx_port" >/tmp/aeroroute-mlx-integration.log 2>&1 &
mlx_pid=$!
trap 'kill "$mlx_pid" 2>/dev/null || true' EXIT
for _ in $(seq 1 20); do
  if curl --fail --silent "http://127.0.0.1:$mlx_port/health" >/dev/null; then
    break
  fi
  sleep 0.25
done
curl --fail --silent "http://127.0.0.1:$mlx_port/health" >/dev/null
MLX_SERVICE_URL="http://127.0.0.1:$mlx_port" uv --directory "$api_repo" run python -c '
from fastapi.testclient import TestClient
from aeroroute_api.main import app

with TestClient(app) as client:
    result = client.post(
        "/api/v1/optimizations",
        json={
            "origin_icao": "LEMD",
            "destination_icao": "KJFK",
            "aircraft_type": "A320",
            "profile": "minimum_fuel",
        },
    )
    assert result.status_code == 200, result.text
    run_id = result.json()["run_id"]
    explanation = client.get(f"/api/v1/optimizations/{run_id}/explanation")
    assert explanation.status_code == 200, explanation.text
    assert explanation.json()["provider"] == "template"
print(f"integration_run_id={run_id}")
'
