# test_cli.py
# Pruebas de la interfaz de línea de comandos a través de main(argv).
# Las pruebas marcadas con xfail estricto documentan bugs conocidos: el PR que corrige
# cada bug debe quitar su marca.

import pytest

from cli import SALIDA_ERROR_CONVERSION, SALIDA_ERROR_USO, SALIDA_OK, main
import cli
from conversor import CONVERSIONES


@pytest.mark.parametrize(
    "argv, esperado",
    [(["100", "c2f"], "212.0"), (["-40", "c2f"], "-40.0")],
)
def test_conversion_exitosa_imprime_resultado(capsys, argv, esperado):
    assert main(argv) == SALIDA_OK
    assert capsys.readouterr().out.strip() == esperado


def test_listar_muestra_todas_las_claves(capsys):
    assert main(["--listar"]) == SALIDA_OK
    salida = capsys.readouterr().out
    assert all(clave in salida for clave in CONVERSIONES)


@pytest.mark.parametrize("argv", [["5", "xyz"], ["-1", "km2mi"], ["nan", "c2f"]])
def test_error_de_conversion_devuelve_1(capsys, argv):
    assert main(argv) == SALIDA_ERROR_CONVERSION
    assert capsys.readouterr().err.startswith("Error: ")


def test_mensaje_de_clave_invalida_sin_comillas(capsys):
    main(["5", "xyz"])
    assert capsys.readouterr().err.startswith("Error: Conversión no soportada: xyz.")


@pytest.mark.parametrize("argv", [[], ["5"], ["abc", "c2f"]])
def test_error_de_uso_devuelve_2_sin_lanzar(capsys, argv):
    assert main(argv) == SALIDA_ERROR_USO


def test_ayuda_devuelve_0_sin_lanzar(capsys):
    assert main(["--help"]) == SALIDA_OK
    assert "uso:" in capsys.readouterr().out


@pytest.mark.parametrize("argv", [[], ["5"], ["abc", "c2f"], ["5", "c2f", "-x"]])
def test_error_de_uso_escribe_solo_en_stderr(capsys, argv):
    main(argv)
    salida = capsys.readouterr()
    assert salida.out == ""
    assert salida.err != ""


@pytest.mark.parametrize(
    "argv, mensaje",
    [
        (["abc", "c2f"], "Error: el valor debe ser un número: 'abc'"),
        (["5", "c2f", "-x"], "Error: argumentos no reconocidos: -x"),
        (["--listar=1"], "Error: argumentos inválidos"),
    ],
)
def test_errores_de_uso_en_espanol(capsys, argv, mensaje):
    assert main(argv) == SALIDA_ERROR_USO
    error = capsys.readouterr().err
    assert error.startswith("uso: ")
    assert mensaje in error


def test_ayuda_en_espanol(capsys):
    main(["--help"])
    ayuda = capsys.readouterr().out
    assert ayuda.startswith("uso: ")
    assert "opciones:" in ayuda and "Muestra esta ayuda" in ayuda
    assert not any(texto in ayuda for texto in ("usage", "options", "show this help"))


def test_ayuda_muestra_el_comando_real(capsys):
    main(["--help"])
    assert capsys.readouterr().out.startswith("uso: python src/cli.py ")


@pytest.mark.parametrize("codigo, esperado", [(0, 0), (2, 2), ("mensaje", 2), (None, 2)])
def test_main_normaliza_el_codigo_de_systemexit(monkeypatch, codigo, esperado):
    # SystemExit.code puede ser int, str o None; main() siempre devuelve un int
    class ParserQueTermina:
        def parse_known_args(self, argv):
            raise SystemExit(codigo)

    monkeypatch.setattr(cli, "construir_parser", ParserQueTermina)
    assert main([]) == esperado
