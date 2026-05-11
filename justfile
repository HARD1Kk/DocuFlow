fmt:
    @uv run ruff format .  && uv run ruff check --fix && uv run ruff format .

go:
    @uv run python -m docuflow.main

install:
    @uv pip install -e .

check:
    @uv run mypy .
    @uv run ty check

test:
    @uv run pytest -s
dead:
    @uv run vulture . --exclude .venv

clean:
	rm -f *.md