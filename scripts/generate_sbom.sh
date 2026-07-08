#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
OUTPUT="$ROOT/aeroroute-platform/sbom"
mkdir -p "$OUTPUT"

for repo in aeroroute-api aeroroute-optimizer aeroroute-data aeroroute-mlx aeroroute-mlx-training aeroroute-platform; do
  (
    cd "$ROOT/$repo"
    COPYFILE_DISABLE=1 uv export --preview-features sbom-export \
      --format cyclonedx1.5 --no-dev --frozen \
      --output-file "$OUTPUT/$repo.cdx.json" >/dev/null
  )
done

(
  cd "$ROOT/aeroroute-web"
  pnpm licenses list --prod --json > "$OUTPUT/aeroroute-web-licenses.json"
)

find "$OUTPUT" -name '._*' -type f -delete
python3 "$ROOT/aeroroute-platform/scripts/normalize_sbom.py" "$OUTPUT"

printf 'Generated SBOM inventory in %s\n' "$OUTPUT"
