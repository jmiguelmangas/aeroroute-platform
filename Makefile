.PHONY: dev-up dev-down integration e2e release-verify check

dev-up:
	docker compose -f compose.yaml -f compose.profiles.yaml --profile core-linux up -d

dev-down:
	docker compose -f compose.yaml -f compose.profiles.yaml down

integration:
	./scripts/verify-local-stack.sh

e2e:
	@echo "Browser E2E is owned by aeroroute-web."

release-verify:
	python3 scripts/validate_releases.py RELEASES.yaml

check: release-verify
