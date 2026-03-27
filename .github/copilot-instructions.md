# Copilot Coding Agent Instructions for eparse

## Repository Overview
- **Purpose:** eparse is a Python package and CLI tool for crawling, parsing, and extracting tabular data from Excel spreadsheets, with support for SQLite and PostgreSQL outputs.
- **Language:** Python (>=3.8)
- **Key dependencies:** click, openpyxl, lxml, pandas, peewee
- **Dev/test tools:** pytest, black, flake8, pre-commit, tox
- **CI:** GitHub Actions (`.github/workflows/ci.yml`)

## Project Structure
- Main code: `eparse/`
- CLI: `eparse/cli.py`
- Tests: `tests/`
- Docs: `docs/`
- Config: `pyproject.toml`, `setup.cfg`, `tox.ini`, `.pre-commit-config.yaml`, `Makefile`
- CI: `.github/workflows/ci.yml`

## Setup, Lint, and Test (Base Case)
**Always follow these steps in order:**

1. **Install all dependencies:**
   - `pip install -e .[test]`
2. **Lint:**
   - `make lint`
3. **Test:**
   - `make test`
4. **Pre-commit (optional, but enforced in CI):**
   - `make pre-commit`

**If using PostgreSQL output:**
- Install: `pip install psycopg2-binary`

## CI and Validation
- **CI runs on every push and PR**: runs `make lint`, `make pre-commit`, and `make test` (Python 3.10).
- **All code must pass lint and tests locally before PR.**

## Environment
- Python >=3.8 required.
- No Docker or Compose files—do not attempt Docker workflows.

## Key Files in Root
- AUTHORS.rst, CONTRIBUTING.rst, HISTORY.rst, LICENSE, MANIFEST.in, Makefile, README.rst, pyproject.toml, setup.cfg, tox.ini, .pre-commit-config.yaml, .github/, eparse/, tests/, docs/, contrib/

## Agent Guidance
- **Always use the above commands and Makefile targets.**
- **Only search for alternatives if these fail or are incomplete.**
- **Do not attempt Docker or Compose workflows—they are not present.**

## References
- See `README.rst` for usage and development details.
- See `.github/workflows/ci.yml` for CI steps.
- See `CONTRIBUTING.rst` for contribution process.
