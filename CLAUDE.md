# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A small command-line unit converter in pure Python (standard library only; `pytest` is the sole dependency). All code, comments, identifiers, user-facing messages, and test names are in **Spanish** — keep new code consistent with that.

## Commands

```bash
pip install -r requirements.txt              # installs pytest
python -m pytest                             # run all tests
python -m pytest tests/test_conversor.py::test_convertir_clave_invalida   # single test
python src/cli.py 100 c2f                    # run a conversion
python src/cli.py --listar                   # list available conversion keys
```

Code lives as flat modules in `src/` (no subpackages), tests in `tests/`, docs in `docs/`. `pyproject.toml` only configures pytest: `pythonpath = ["src"]` lets tests import `conversor` directly without installing anything. There is no linter or build step configured.

## Architecture

- `src/conversor.py` — conversion logic. Each conversion is a standalone function that validates physical limits (below absolute zero, negative distance/mass) by raising `ValueError`. The `CONVERSIONES` dict is the central registry mapping a short key (e.g. `c2f`, `km2mi`) to `(function, description)`. `convertir(valor, clave)` is the single entry point: it raises `ValueError` for non-finite values (`nan`, `inf`), `KeyError` for unknown keys, and rounds results to 4 decimals.
- `src/cli.py` — argparse front end. `main(argv=None)` returns an exit code (0 ok, 1 conversion error, 2 missing arguments) instead of calling `sys.exit` directly, so it can be tested by passing `argv`. `--listar` reads descriptions straight from `CONVERSIONES`.
To add a conversion: write the function in `src/conversor.py` and register it in `CONVERSIONES`; the CLI and `--listar` pick it up automatically.

## Tests

- `tests/test_conversor.py` — known values, round trips, physical limits, non-finite values and invalid keys for every conversion, through `convertir()` and `CONVERSIONES`.
- `tests/test_cli.py` — exercises `main(argv)` and its exit codes, using `capsys` for output.

Known bugs are documented as tests marked `pytest.mark.xfail(strict=True, reason="Bug #N: ...")`; they show as `XFAIL` while the bug exists. A PR that fixes a bug must remove its `xfail` mark in the same change — otherwise the test reports `XPASS(strict)` and the suite fails.
