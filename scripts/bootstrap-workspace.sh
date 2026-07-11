#!/usr/bin/env bash
# Clone (or verify) the AeroRoute sibling repositories next to this one, and
# optionally bootstrap each one. See docs/HLD.md section 21.6.
#
# Usage:
#   ./scripts/bootstrap-workspace.sh                    # clone missing siblings only
#   ./scripts/bootstrap-workspace.sh --mode development  # also run `make bootstrap` in each
#
# Env overrides:
#   AEROROUTE_WORKSPACE    workspace dir siblings are cloned into (default: parent of this repo)
#   AEROROUTE_GITHUB_ORG   GitHub org/user siblings are cloned from (default: jmiguelmangas)
#   AEROROUTE_GIT_PROTOCOL "https" (default) or "ssh"
set -euo pipefail

mode="ci"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      mode="$2"
      shift 2
      ;;
    --mode=*)
      mode="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

workspace="${AEROROUTE_WORKSPACE:-$(cd "$(dirname "$0")/../.." && pwd)}"
org="${AEROROUTE_GITHUB_ORG:-jmiguelmangas}"
protocol="${AEROROUTE_GIT_PROTOCOL:-https}"

repositories=(
  aeroroute-contracts
  aeroroute-optimizer
  aeroroute-api
  aeroroute-data
  aeroroute-mlx
  aeroroute-mlx-training
  aeroroute-platform
  aeroroute-web
)

clone_url() {
  local repository="$1"
  if [ "$protocol" = "ssh" ]; then
    echo "git@github.com:${org}/${repository}.git"
  else
    echo "https://github.com/${org}/${repository}.git"
  fi
}

for repository in "${repositories[@]}"; do
  repo_dir="$workspace/$repository"
  if [ -d "$repo_dir/.git" ]; then
    echo "OK (already cloned): $repo_dir"
    continue
  fi
  if [ -e "$repo_dir" ]; then
    echo "Refusing to clone over existing non-git path: $repo_dir" >&2
    exit 1
  fi
  url="$(clone_url "$repository")"
  echo "Cloning $repository from $url ..."
  git clone "$url" "$repo_dir"
done

if [ "$mode" = "development" ]; then
  for repository in "${repositories[@]}"; do
    repo_dir="$workspace/$repository"
    if [ -f "$repo_dir/Makefile" ] && grep -q '^bootstrap:' "$repo_dir/Makefile"; then
      echo "Bootstrapping $repository (make bootstrap) ..."
      make -C "$repo_dir" bootstrap
    fi
  done
fi

echo "AeroRoute sibling workspace is ready at $workspace"
