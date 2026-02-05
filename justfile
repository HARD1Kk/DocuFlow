fmt:
    uv run ruff format . && uv run ruff check --fix && uv run ruff format .

run:
    uv run src/main.py

check:
    uv run mypy . 
