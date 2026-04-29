# AGENTS.md

## Repo Basics
- Python project managed with `uv`; `pyproject.toml` requires Python `>=3.14` and `uv.lock` is committed.
- There is no package directory or console script yet; current executable/schema/CLI entrypoint is root `main.py`.
- `README.md` is empty, and there are no tests or CI workflows currently in the repo.
- Runtime env is loaded by `load_dotenv()` in `main.py`; keep secrets in `.env` and mirror required keys in `.env.example`.
- After meaningful repo changes, review this file and update any stale commands, entrypoints, schemas, or workflow notes.

## Commands
- Install/sync dependencies with `uv sync`.
- Run the current app with `uv run main.py transcripts/ts-1.txt`; use `uv run main.py --help` for CLI usage.
- Run repo checks with `make check`; this runs `uv run ruff check --fix --unsafe-fixes && uv run basedpyright` and may edit files.
- Run tests with `uv run pytest`; pre-commit always runs pytest even though no tests exist yet.
- Pre-commit also runs `ruff-check --fix`, `ruff-format`, and `basedpyright`.

## Current Code Shape
- Defines the Pydantic v2 structured-output models: `AbstainEvaluation`, generic `ExtractedAttribute[T]`, `Stage`, `AgentExtraction`, and `Opportunity`.
- Preserve the schema constraints unless explicitly changing the task: `extra="forbid"`, confidence/value bounds `0..1`, and justification/summary max lengths.
- Scalar extracted fields use one `ExtractedAttribute[...]`; repeated fields use `list[ExtractedAttribute[...]]` with non-null inner values and an empty list when absent.
- `transcripts/` contains sample inputs (i.e. `ts-1.txt`, `ts-2.txt`); the CLI accepts which transcript file to process and an optional `--threshold`.

## CLI Flow
- The CLI is built with Typer, LangChain/LangGraph, and Together AI; graph execution and agent calls use async `ainvoke`.
- First agent uses `openai/gpt-oss-120b` structured output to produce `AbstainEvaluation`.
- Compute `value_index = transcript_value * confidence`; start with abstain threshold `0.6`.
- If `value_index < threshold` (default `0.6`), use the summary agent for a brief last-touch summary, then print abstention, scores, justification, and summary.
- If `value_index >= 0.6`, use `zai-org/GLM-5.1` structured output to produce `AgentExtraction`.
- Consolidate an `Opportunity` by averaging extraction confidence scores, then call the smaller model for the final last-touch summary.
- Final non-abstained CLI output should be JSON matching the `Opportunity` schema.

## Environment
- Together access uses `TOGETHER_API_KEY` from `.env`/environment.
- LangSmith tracing keys are documented in `.env.example`: `LANGSMITH_TRACING`, `LANGSMITH_ENDPOINT`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`.
