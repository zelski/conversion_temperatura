# test_conversor.py
# Pruebas de las funciones de conversión y del punto de entrada convertir().
# Las pruebas marcadas con xfail estricto documentan bugs conocidos: el PR que corrige
# cada bug debe quitar su marca.

import math

import pytest

from conversor import CONVERSIONES, ConversionNoSoportada, ErrorConversion, convertir

PARES_INVERSOS = [("c2f", "f2c"), ("km2mi", "mi2km"), ("kg2lb", "lb2kg")]


@pytest.mark.parametrize(
    "clave, valor, esperado",
    [
        ("c2f", 100, 212),
        ("c2f", 0, 32),
        ("c2f", -40, -40),
        ("f2c", 212, 100),
        ("f2c", 32, 0),
        ("f2c", -40, -40),
        ("km2mi", 10, 6.2137),
        ("mi2km", 6.21371, 10),
        ("kg2lb", 1, 2.2046),
        ("lb2kg", 2.20462, 1),
    ],
)
def test_convertir_valores_conocidos(clave, valor, esperado):
    assert convertir(valor, clave) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "clave, valor, esperado",
    [
        # Definiciones exactas: 1 mi = 1.609344 km y 1 lb = 0.45359237 kg
        ("mi2km", 1000, 1609.344),
        ("km2mi", 1000, 621.3712),
        ("lb2kg", 1000, 453.5924),
        ("kg2lb", 1000, 2204.6226),
    ],
)
def test_convertir_es_exacto_hasta_el_ultimo_decimal(clave, valor, esperado):
    # Con valores grandes, un factor truncado altera los 4 decimales que se muestran
    assert convertir(valor, clave) == pytest.approx(esperado, abs=1e-9)


@pytest.mark.parametrize("ida, vuelta", PARES_INVERSOS + [(b, a) for a, b in PARES_INVERSOS])
@pytest.mark.parametrize("valor", [0, 1, 37.5, 1000])
def test_ida_y_vuelta_recupera_el_valor(ida, vuelta, valor):
    intermedio = CONVERSIONES[ida].funcion(valor)
    assert CONVERSIONES[vuelta].funcion(intermedio) == pytest.approx(valor)


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
    with pytest.raises(ErrorConversion):
        convertir(valor, clave)


@pytest.mark.parametrize(
    "clave, valor",
    [
        ("c2f", -273.15),
        ("f2c", -459.67),
        ("km2mi", 0),
    ],
)
def test_convertir_acepta_el_limite_fisico_exacto(clave, valor):
    convertir(valor, clave)


@pytest.mark.parametrize("valor", [math.nan, math.inf, -math.inf])
def test_convertir_rechaza_valores_no_finitos(valor):
    with pytest.raises(ErrorConversion):
        convertir(valor, "km2mi")


def test_convertir_clave_invalida():
    # Una clave inexistente debe producir ConversionNoSoportada que mencione la clave
    with pytest.raises(ConversionNoSoportada, match="leguas2parsecs"):
        convertir(5, "leguas2parsecs")


def test_errores_de_dominio_son_value_error():
    # Compatibilidad: quien capturaba ValueError sigue capturando los errores del conversor
    assert issubclass(ConversionNoSoportada, ErrorConversion)
    assert issubclass(ErrorConversion, ValueError)


@pytest.mark.parametrize("clave, valor", [("km2mi", -0.0), ("c2f", -17.77778)])
def test_convertir_no_devuelve_cero_negativo(clave, valor):
    # -17.77778 °C da -0.000004 °F, que al redondear quedaría en -0.0
    assert math.copysign(1, convertir(valor, clave)) == 1
