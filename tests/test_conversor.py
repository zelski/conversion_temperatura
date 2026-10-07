# test_conversor.py
# Pruebas de las funciones de conversión y del punto de entrada convertir().
# Las pruebas marcadas con xfail estricto documentan bugs conocidos: el PR que corrige
# cada bug debe quitar su marca.

import math

import pytest

from conversor import CONVERSIONES, convertir

BUG_FAHRENHEIT = pytest.mark.xfail(
    strict=True, reason="Bug #1: fahrenheit_a_celsius usa 9/5 y valida el resultado"
)
BUG_NO_FINITOS = pytest.mark.xfail(strict=True, reason="Bug #2: nan e inf no se rechazan")
BUG_CERO_NEGATIVO = pytest.mark.xfail(strict=True, reason="Bug #9: se devuelve -0.0")

PARES_INVERSOS = [("c2f", "f2c"), ("km2mi", "mi2km"), ("kg2lb", "lb2kg")]


def _ida_y_vuelta():
    # Cada par en ambos sentidos; los que pasan por f2c dependen del bug #1
    return [
        pytest.param(ida, vuelta, marks=[BUG_FAHRENHEIT] if "f2c" in (ida, vuelta) else [])
        for ida, vuelta in PARES_INVERSOS + [(b, a) for a, b in PARES_INVERSOS]
    ]


@pytest.mark.parametrize(
    "clave, valor, esperado",
    [
        ("c2f", 100, 212),
        ("c2f", 0, 32),
        ("c2f", -40, -40),
        pytest.param("f2c", 212, 100, marks=BUG_FAHRENHEIT),
        ("f2c", 32, 0),
        pytest.param("f2c", -40, -40, marks=BUG_FAHRENHEIT),
        ("km2mi", 10, 6.2137),
        ("mi2km", 6.21371, 10),
        ("kg2lb", 1, 2.2046),
        ("lb2kg", 2.20462, 1),
    ],
)
def test_convertir_valores_conocidos(clave, valor, esperado):
    assert convertir(valor, clave) == pytest.approx(esperado)


@pytest.mark.parametrize("ida, vuelta", _ida_y_vuelta())
@pytest.mark.parametrize("valor", [1, 37.5, 1000])
def test_ida_y_vuelta_recupera_el_valor(ida, vuelta, valor):
    funcion_ida, _ = CONVERSIONES[ida]
    funcion_vuelta, _ = CONVERSIONES[vuelta]
    assert funcion_vuelta(funcion_ida(valor)) == pytest.approx(valor)


@pytest.mark.parametrize(
    "clave, valor",
    [
        ("c2f", -273.16),
        ("f2c", -459.68),
        ("km2mi", -1),
        ("mi2km", -1),
        ("kg2lb", -1),
        ("lb2kg", -1),
    ],
)
def test_convertir_rechaza_valores_fisicamente_imposibles(clave, valor):
    with pytest.raises(ValueError):
        convertir(valor, clave)


@pytest.mark.parametrize(
    "clave, valor",
    [
        ("c2f", -273.15),
        pytest.param("f2c", -459.67, marks=BUG_FAHRENHEIT),
        ("km2mi", 0),
    ],
)
def test_convertir_acepta_el_limite_fisico_exacto(clave, valor):
    convertir(valor, clave)


@pytest.mark.parametrize(
    "valor",
    [
        pytest.param(math.nan, marks=BUG_NO_FINITOS, id="nan"),
        pytest.param(math.inf, marks=BUG_NO_FINITOS, id="inf"),
        pytest.param(-math.inf, id="-inf"),
    ],
)
def test_convertir_rechaza_valores_no_finitos(valor):
    with pytest.raises(ValueError):
        convertir(valor, "km2mi")


def test_convertir_clave_invalida():
    # Una clave inexistente debe producir un KeyError que mencione la clave
    with pytest.raises(KeyError, match="leguas2parsecs"):
        convertir(5, "leguas2parsecs")


@BUG_CERO_NEGATIVO
def test_convertir_no_devuelve_cero_negativo():
    assert math.copysign(1, convertir(-0.0, "km2mi")) == 1
