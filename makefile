run:
	uv run main.py

check:
	uv run ruff check --fix --unsafe-fixes && uv run basedpyright
