## Antiphon canonical commands.
##
## Stable named entrypoints for the common workflows. The underlying
## tool may change; the names here do not.
##
## Run `make` (no target) for the list.

# Make has no native support for positional args; this captures any
# extra command-line goals (after the first) as $(POSITIONAL_ARGS) and
# short-circuits Make's attempt to build them as real targets. Targets
# that take args may use POSITIONAL_ARGS as a fallback when their named
# variables (NAME=, MOOD=, etc.) are not set.
#
# The ARG_TAKING_TARGETS list activates a catch-all `%:` rule that
# no-ops any unmatched goal — needed so that multi-word positional args
# (which Make sees as separate goals after shell quoting) don't blow up
# with "No rule to make target ...". Pattern rules don't shadow
# explicit rules, so this is safe for the targets we know about.
ARG_TAKING_TARGETS := mood add-mood populate-mood similar
ifneq ($(filter $(ARG_TAKING_TARGETS),$(firstword $(MAKECMDGOALS))),)
  POSITIONAL_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  %:
	@true
endif

.PHONY: help install check format lint typecheck test clean profile gems setup mood reject validate add-mood recent similar stats

help: ## Show this help
	@grep -E '^[a-zA-Z][a-zA-Z0-9_-]*:.*?##' $(MAKEFILE_LIST) \
		| awk -F ':.*?##' '{printf "  \033[1m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Interactive first-time setup wizard (stdlib-only, no uv needed)
	python3 scripts/setup.py

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

# Project-specific entry points.
#
# All arg-taking targets accept either NAMED args (NAME='X' DESC='Y') or
# positional args (`make add-mood feisty 'description here'`). When both
# are given, NAMED wins. With positional, the first word is the primary
# arg and remaining words join into the second.

profile: ## Print the listening-shape profile
	uv run python -m scripts.profile

gems: ## Print forgotten gems
	uv run python -m scripts.forgotten_gems

mood: ## Print a mood's picks (NAME='X' or positional). No arg lists all.
	uv run python -m scripts.mood "$(or $(NAME),$(POSITIONAL_ARGS))"

reject: ## Append to dislikes.md (LABEL='X' REASON='Y' [CATEGORY='...'])
	@if [ -z "$(LABEL)" ] || [ -z "$(REASON)" ]; then \
		echo "usage: make reject LABEL='<label>' REASON='<reason>' [CATEGORY='<cat>']"; \
		echo "   (multi-word args make NAMED form mandatory; quote freely)"; \
		exit 64; \
	fi; \
	uv run python -m scripts.reject "$(LABEL)" "$(REASON)" "$(CATEGORY)"

validate: ## Promote a candidate to validated (MOOD='X' PICK='Y')
	@if [ -z "$(MOOD)" ] || [ -z "$(PICK)" ]; then \
		echo "usage: make validate MOOD='<mood>' PICK='<pick substring>'"; \
		echo "   (multi-word args make NAMED form mandatory; quote freely)"; \
		exit 64; \
	fi; \
	uv run python -m scripts.validate "$(MOOD)" "$(PICK)"

add-mood: ## Add a new mood scaffold (NAME='X' [DESC='Y']  or  positional)
	@if [ -n "$(NAME)" ]; then \
		uv run python -m scripts.add_mood "$(NAME)" "$(DESC)"; \
	elif [ -n "$(POSITIONAL_ARGS)" ]; then \
		uv run python -m scripts.add_mood "$(firstword $(POSITIONAL_ARGS))" "$(wordlist 2,99,$(POSITIONAL_ARGS))"; \
	else \
		echo "usage: make add-mood NAME='<name>' [DESC='<description>']"; \
		echo "   or: make add-mood <name> [<description...>]"; \
		exit 64; \
	fi

populate-mood: ## Use Claude to propose candidates for a mood (NAME='X' [N=5])
	@_name="$(or $(NAME),$(firstword $(POSITIONAL_ARGS)))"; \
	if [ -z "$$_name" ]; then \
		echo "usage: make populate-mood NAME='<mood>' [N=5]"; \
		echo "   or: make populate-mood <mood> [N]"; \
		exit 64; \
	fi; \
	uv run python -m scripts.populate_mood "$$_name" "$(N)"

recent: ## Last N days of scrobbles ([N=7])
	uv run python -m scripts.recent "$(N)"

similar: ## Similar artists w/ library overlap (ARTIST='X' [N=20])
	@if [ -z "$(ARTIST)" ] && [ -z "$(POSITIONAL_ARGS)" ]; then \
		echo "usage: make similar ARTIST='<artist>' [N=20]"; \
		echo "   or: make similar <artist...>"; \
		exit 64; \
	fi; \
	uv run python -m scripts.similar "$(or $(ARTIST),$(POSITIONAL_ARGS))" "$(N)"

stats: ## Library coverage diagnostic
	uv run python -m scripts.stats

log-rec: ## Log a rec to session.log.md (PICK='Artist — Album' [SOURCE='mood'])
	@if [ -z "$(PICK)" ]; then \
		echo "usage: make log-rec PICK='<artist — album>' [SOURCE='<mood-or-mode>']"; \
		exit 64; \
	fi; \
	uv run python -m scripts.log_rec "$(PICK)" "$(SOURCE)"

cooldown: ## Show recs from the last N days ([DAYS=7])
	uv run python -m scripts.cooldown "$(DAYS)"

.DEFAULT_GOAL := help
