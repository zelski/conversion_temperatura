# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A small command-line unit converter in pure Python (standard library only; `pytest` is the sole dependency). All code, comments, identifiers, user-facing messages, and test names are in **Spanish** — keep new code consistent with that.

## Commands

```bash
pip install -r requirements.txt              # installs pytest
python -m pytest                             # run all tests
python -m pytest tests/test_conversor.py::test_convertir_clave_invalida   # single test
python cli.py 100 c2f                        # run a conversion
python cli.py --listar                       # list available conversion keys
```

The root `conftest.py` exists so pytest puts the project root on `sys.path`; tests import `conversor` directly without installing the package. There is no linter or build step configured.

## Architecture

- `conversor.py` — conversion logic. Each conversion is a standalone function that validates physical limits (below absolute zero, negative distance/mass) by raising `ValueError`. The `CONVERSIONES` dict is the central registry mapping a short key (e.g. `c2f`, `km2mi`) to `(function, description)`. `convertir(valor, clave)` is the single entry point: it raises `KeyError` for unknown keys and rounds results to 4 decimals.
- `cli.py` — argparse front end. `main(argv=None)` returns an exit code (0 ok, 1 conversion error, 2 missing arguments) instead of calling `sys.exit` directly, so it can be tested by passing `argv`. `--listar` reads descriptions straight from `CONVERSIONES`.

To add a conversion: write the function in `conversor.py` and register it in `CONVERSIONES`; the CLI and `--listar` pick it up automatically.

## Tests

`tests/test_conversor.py` is explicitly partial — it covers only `celsius_a_fahrenheit`, `km_a_millas`, and the invalid-key path of `convertir`. The other conversions and `cli.py` are untested.
