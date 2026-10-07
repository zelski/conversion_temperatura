# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A small command-line unit converter in pure Python (standard library only at runtime; `pytest` and `pytest-cov` are dev-only dependencies). All code, comments, identifiers, user-facing messages, test names, commits, PRs and docs are in **Spanish** — keep new work consistent with that. This file is the only English document.

## Commands

```bash
pip install -r requirements.txt              # installs pytest and pytest-cov
python -m pytest                             # run all tests
python -m pytest tests/test_conversor.py::test_convertir_clave_invalida   # single test
python -m pytest --cov                       # statement + branch coverage of src/
python src/cli.py 100 c2f                    # run a conversion
python src/cli.py --listar                   # list available conversion keys
```

Code lives as flat modules in `src/` (no subpackages, nothing installable), tests in `tests/`, docs in `docs/`. `pyproject.toml` only configures tooling: pytest's `pythonpath = ["src"]` lets tests import `conversor` directly, and `[tool.coverage.*]` measures `src/` with branch coverage (only the `if __name__ == "__main__":` guard is excluded). There is no linter or build step configured. `.claude/settings.json` denies reading generated files (`.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `htmlcov/`, `.coverage`); run tests with the system `python`, not `.venv\Scripts\python`.

## Architecture

Full details in `docs/arquitectura.md`; the essentials:

- `src/conversor.py` — each conversion is a standalone function that checks its physical limit with `_exigir_minimo()` and applies its formula. `CONVERSIONES` is the central registry mapping a short key (e.g. `c2f`, `km2mi`) to a `Conversion(funcion, descripcion)` NamedTuple — access fields by name, not by position. `convertir(valor, clave)` is the single entry point: rejects non-finite values, looks up the key, converts, rounds to `DECIMALES` (4) and normalizes `-0.0`.
- Exception hierarchy: `ConversionNoSoportada` → `ErrorConversion` → `ValueError`. Raise these domain errors, never bare `ValueError`/`KeyError`.
- `src/cli.py` — argparse front end. `main(argv=None)` returns `SALIDA_OK` (0), `SALIDA_ERROR_CONVERSION` (1) or `SALIDA_ERROR_USO` (2) instead of calling `sys.exit`; it also catches argparse's `SystemExit` and returns its code, so it is tested by passing `argv`. For conversion failures it catches only `ErrorConversion`.

To add a conversion: write the function in `src/conversor.py` (with a docstring stating the formula) and register it in `CONVERSIONES`; the CLI and `--listar` pick it up automatically. Then add its cases to the parametrized tests.

## Tests

See `docs/pruebas.md`. Key rules:

- Coverage must stay at 100% — new code comes with tests.
- Known bugs are tests marked `pytest.mark.xfail(strict=True, reason="Bug #N: ...")`. A PR that fixes a bug must remove its mark in the same change, otherwise the suite fails with `XPASS(strict)`.

## Workflow and docs

Follow `CONTRIBUTING.md`: one change per PR from an up-to-date `main`, and update the affected docs (`README.md`, `docs/`, this file) plus `CHANGELOG.md` in the same PR. `docs/historial/` holds historical records (the original handoff and the completed improvement plan) — don't treat them as current instructions or update them for later changes.
