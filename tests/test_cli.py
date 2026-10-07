# test_cli.py
# Pruebas de la interfaz de línea de comandos a través de main(argv).
# Las pruebas marcadas con xfail estricto documentan bugs conocidos: el PR que corrige
# cada bug debe quitar su marca.

import pytest

from cli import main
from conversor import CONVERSIONES

BUG_SYSTEMEXIT = pytest.mark.xfail(
    strict=True, reason="Bug #5: main() lanza SystemExit en vez de devolver el código"
)


@pytest.mark.parametrize(
    "argv, esperado",
    [(["100", "c2f"], "212.0"), (["-40", "c2f"], "-40.0")],
)
def test_conversion_exitosa_imprime_resultado(capsys, argv, esperado):
    assert main(argv) == 0
    assert capsys.readouterr().out.strip() == esperado


def test_listar_muestra_todas_las_claves(capsys):
    assert main(["--listar"]) == 0
    salida = capsys.readouterr().out
    assert all(clave in salida for clave in CONVERSIONES)


@pytest.mark.parametrize("argv", [["5", "xyz"], ["-1", "km2mi"], ["nan", "c2f"]])
def test_error_de_conversion_devuelve_1(capsys, argv):
    assert main(argv) == 1
    assert capsys.readouterr().err.startswith("Error: ")


def test_mensaje_de_clave_invalida_sin_comillas(capsys):
    main(["5", "xyz"])
    assert capsys.readouterr().err.startswith("Error: Conversión no soportada: xyz.")


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["5"],
        pytest.param(["abc", "c2f"], marks=BUG_SYSTEMEXIT),
    ],
)
def test_error_de_uso_devuelve_2_sin_lanzar(capsys, argv):
    assert main(argv) == 2
