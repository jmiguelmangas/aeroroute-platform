.PHONY: dev-up dev-down integration e2e release-verify check

dev-up:
	docker compose -f compose.yaml -f compose.profiles.yaml --profile core-linux up -d

dev-down:
	docker compose -f compose.yaml -f compose.profiles.yaml down

integration e2e:
	@echo "Integration harness skeleton: release artifacts are required."

release-verify:
	python3 scripts/validate_releases.py RELEASES.yaml

check: release-verify
