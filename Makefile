.PHONY: dev-up dev-down lint security-check compose-config

dev-up:
	./scripts/dev-up.sh

dev-down:
	docker compose down

dev-proxy:
	docker compose --profile proxy up -d

lint:
	ruff check app scripts client/main.py

security-check:
	./scripts/security-check.sh

compose-config:
	docker compose config
