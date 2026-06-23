#!/usr/bin/env bash
set -euo pipefail

workspace="${AEROROUTE_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
for repository in aeroroute-platform aeroroute-contracts aeroroute-optimizer aeroroute-api aeroroute-data aeroroute-mlx aeroroute-mlx-training aeroroute-web; do
  test -d "$workspace/$repository" || {
    echo "Missing sibling repository: $workspace/$repository" >&2
    exit 1
  }
done
echo "AeroRoute sibling workspace is ready at $workspace"
