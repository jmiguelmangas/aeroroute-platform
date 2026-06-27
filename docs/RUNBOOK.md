# Runbook

Use `make dev-up` to start only the local PostGIS dependency. MLX runs natively
on macOS and is intentionally not containerized. Stop the stack with
`make dev-down`.

## Native Gemma 3 4B explanation service

The model weights must already exist at
`aeroroute-mlx/models/gemma-3-text-4b-it-4bit`. Start the validated Apple
Silicon fallback with:

```bash
cd ../aeroroute-mlx
uv sync --all-groups --extra mlx
AEROROUTE_MLX_ENABLED=1 \
  AEROROUTE_MLX_MODEL_MANIFEST=./configs/gemma3-4b-smoke.json \
  uv run uvicorn aeroroute_mlx.main:app --host 127.0.0.1 --port 8765
```

Configure the API with `MLX_SERVICE_URL=http://127.0.0.1:8765` and
`MLX_TIMEOUT_S=10`. The timeout exceeds the measured six-second cold load while
remaining bounded. If the process, output schema or claim validation fails, the
API retains its deterministic template explanation.
