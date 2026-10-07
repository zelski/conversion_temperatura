# test_cli.py
# Pruebas de la interfaz de línea de comandos a través de main(argv).
# Las pruebas marcadas con xfail estricto documentan bugs conocidos: el PR que corrige
# cada bug debe quitar su marca.

import io
import os
import pathlib
import subprocess
import sys

import pytest

import cli
from cli import SALIDA_ERROR_CONVERSION, SALIDA_ERROR_USO, SALIDA_OK, main
from conversor import CONVERSIONES

RUTA_CLI = pathlib.Path(__file__).resolve().parent.parent / "src" / "cli.py"


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


@pytest.mark.parametrize("valor", ["-1e5", "-5.", "-inf"])
def test_negativo_especial_sugiere_doble_guion(capsys, valor):
    assert main([valor, "c2f"]) == SALIDA_ERROR_USO
    error = capsys.readouterr().err
    assert f"'{valor}' parece un número negativo" in error
    assert f"python src/cli.py -- {valor} CLAVE" in error


def test_coma_decimal_sugiere_punto(capsys):
    assert main(["36,6", "c2f"]) == SALIDA_ERROR_USO
    assert "usa punto decimal, por ejemplo 36.6" in capsys.readouterr().err


def test_valor_que_desborda_float_se_reporta_tal_cual(capsys):
    assert main(["1e400", "c2f"]) == SALIDA_ERROR_CONVERSION
    assert "fuera del rango representable: '1e400'" in capsys.readouterr().err


def test_error_interno_devuelve_codigo_propio(monkeypatch, capsys):
    def falla(valor, clave):
        raise RuntimeError("fallo interno simulado")

    monkeypatch.setattr(cli, "convertir", falla)
    assert cli.ejecutar_desde_consola(["5", "c2f"]) == cli.SALIDA_ERROR_INTERNO
    error = capsys.readouterr().err
    assert "RuntimeError: fallo interno simulado" in error  # se conserva el traceback
    assert "Error interno inesperado" in error


def test_salida_sin_unicode_no_falla():
    entorno = {**os.environ, "PYTHONIOENCODING": "ascii"}
    proceso = subprocess.run(
        [sys.executable, str(RUTA_CLI), "--listar"], capture_output=True, text=True, env=entorno
    )
    assert proceso.returncode == SALIDA_OK
    assert "Kil?metros a millas" in proceso.stdout


@pytest.mark.parametrize("clave", ["C2F", " c2f ", "C2f"])
def test_clave_ignora_mayusculas_y_espacios(capsys, clave):
    assert main(["100", clave]) == SALIDA_OK
    assert capsys.readouterr().out.strip() == "212.0"


def test_ejecutar_desde_consola_tolera_flujos_sin_reconfigure(monkeypatch):
    # Si stdout/stderr fueron reemplazados por objetos sin reconfigure(), no debe fallar
    salida, errores = io.StringIO(), io.StringIO()
    monkeypatch.setattr(sys, "stdout", salida)
    monkeypatch.setattr(sys, "stderr", errores)
    assert cli.ejecutar_desde_consola(["100", "c2f"]) == SALIDA_OK
    assert salida.getvalue().strip() == "212.0"
