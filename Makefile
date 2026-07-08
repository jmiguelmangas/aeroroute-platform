.PHONY: bootstrap format lint typecheck test build check dev-up dev-down integration e2e release-verify route-coverage operational-readiness verify-live performance-live phase14-release sbom

bootstrap:
	uv sync --all-groups

format:
	uv run ruff format scripts tests

lint:
	uv run ruff check scripts tests

typecheck:
	@echo "No typed runtime package in aeroroute-platform."

test:
	uv run pytest

build:
	docker compose -f compose.yaml -f compose.profiles.yaml config --quiet

dev-up:
	docker compose -f compose.yaml -f compose.profiles.yaml --profile core-linux up -d

dev-down:
	docker compose -f compose.yaml -f compose.profiles.yaml down

integration:
	./scripts/verify-local-stack.sh

e2e:
	@echo "Browser E2E is owned by aeroroute-web."

release-verify:
	uv run python scripts/validate_releases.py RELEASES.yaml

route-coverage:
	uv run python scripts/validate_route_coverage.py

operational-readiness:
	uv run python scripts/validate_operational_readiness.py

verify-live:
	uv run python scripts/verify_live_release.py

performance-live:
	uv run python scripts/check_http_budget.py

phase14-release:
	uv run python scripts/verify_phase14_release.py

sbom:
	./scripts/generate_sbom.sh

check: lint typecheck test build release-verify route-coverage operational-readiness phase14-release
