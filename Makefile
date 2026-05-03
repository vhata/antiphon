## Antiphon canonical commands.
##
## Stable named entrypoints for the common workflows. The underlying
## tool may change; the names here do not.
##
## Run `make` (no target) for the list.

.PHONY: help install check format lint typecheck test clean profile gems

help: ## Show this help
	@grep -E '^[a-zA-Z][a-zA-Z0-9_-]*:.*?##' $(MAKEFILE_LIST) \
		| awk -F ':.*?##' '{printf "  \033[1m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install dev dependencies via uv
	uv sync

check: ## Format-check + lint + typecheck + tests
	uv run ruff format --check . && uv run ruff check . && uv run mypy . && uv run pytest

format: ## Auto-format
	uv run ruff format .

lint: ## Lint
	uv run ruff check .

typecheck: ## mypy
	uv run mypy .

test: ## Unit tests
	uv run pytest

clean: ## Remove cache directories
	rm -rf .pytest_cache .mypy_cache .ruff_cache .venv

# Project-specific entry points

profile: ## Print the listening-shape profile (needs .env loaded)
	uv run python -m scripts.profile

gems: ## Print forgotten gems (needs .env loaded)
	uv run python -m scripts.forgotten_gems

mood: ## Print a mood's picks as Spotify links (NAME='small hours')
	uv run python -m scripts.mood "$(NAME)"

reject: ## Append to dislikes.md (LABEL='X' REASON='Y' [CATEGORY='Artists'])
	uv run python -m scripts.reject "$(LABEL)" "$(REASON)" "$(CATEGORY)"

validate: ## Promote a candidate to validated (MOOD='X' PICK='Y')
	uv run python -m scripts.validate "$(MOOD)" "$(PICK)"

recent: ## Last N days of scrobbles ([N=7])
	uv run python -m scripts.recent "$(N)"

similar: ## Similar artists w/ library overlap (ARTIST='X' [N=20])
	uv run python -m scripts.similar "$(ARTIST)" "$(N)"

stats: ## Library coverage diagnostic
	uv run python -m scripts.stats

.DEFAULT_GOAL := help
