fmt:
    uv run ruff format .  && uv run ruff check --fix && uv run ruff format .

go:
    uv run src/main.py

activate:
    source .venv/bin/activate
