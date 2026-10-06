# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A small command-line unit converter in pure Python (standard library only; `pytest` is the sole dependency). All code, comments, identifiers, user-facing messages, and test names are in **Spanish** — keep new code consistent with that.

## Commands

```bash
pip install -e ".[dev]"                      # installs the package (editable) and pytest
python -m pytest                             # run all tests
python -m pytest tests/test_conversor.py::test_convertir_clave_invalida   # single test
conversor 100 c2f                            # run a conversion (after install)
python -m conversor_unidades 100 c2f         # same, without the console script
conversor --listar                           # list available conversion keys
```

Uses the `src` layout: code lives in `src/conversor_unidades/`, tests in `tests/`, docs in `docs/`. `pyproject.toml` sets pytest's `pythonpath = ["src"]`, so tests import `conversor_unidades.conversor` without installing the package. There is no linter configured.

## Architecture

- `src/conversor_unidades/conversor.py` — conversion logic. Each conversion is a standalone function that validates physical limits (below absolute zero, negative distance/mass) by raising `ValueError`. The `CONVERSIONES` dict is the central registry mapping a short key (e.g. `c2f`, `km2mi`) to `(function, description)`. `convertir(valor, clave)` is the single entry point: it raises `KeyError` for unknown keys and rounds results to 4 decimals.
- `src/conversor_unidades/cli.py` — argparse front end. `main(argv=None)` returns an exit code (0 ok, 1 conversion error, 2 missing arguments) instead of calling `sys.exit` directly, so it can be tested by passing `argv`. `--listar` reads descriptions straight from `CONVERSIONES`. It is exposed as the `conversor` console script (`pyproject.toml`) and via `__main__.py`.

To add a conversion: write the function in `src/conversor_unidades/conversor.py` and register it in `CONVERSIONES`; the CLI and `--listar` pick it up automatically.

## Tests

`tests/test_conversor.py` is explicitly partial — it covers only `celsius_a_fahrenheit`, `km_a_millas`, and the invalid-key path of `convertir`. The other conversions and `cli.py` are untested.
