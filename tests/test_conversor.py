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


@pytest.mark.parametrize("clave", sorted(CONVERSIONES))
@pytest.mark.parametrize("valor", [math.nan, math.inf])
def test_funciones_de_conversion_rechazan_valores_no_finitos(clave, valor):
    # Las funciones son públicas: deben dar la misma garantía que convertir()
    with pytest.raises(ErrorConversion):
        CONVERSIONES[clave].funcion(valor)


@pytest.mark.parametrize(
    "clave, valor",
    [("c2f", 1e308), ("f2c", 1.7e308), ("mi2km", 1.5e308), ("kg2lb", 1e308)],
)
def test_convertir_rechaza_resultados_que_se_desbordan(clave, valor):
    with pytest.raises(ErrorConversion, match="excede el rango representable") as error:
        convertir(valor, clave)
    assert error.value.valor == valor


def test_convertir_valida_la_clave_antes_que_el_valor():
    # Con dos errores a la vez se informa la clave, que no depende del valor
    with pytest.raises(ConversionNoSoportada):
        convertir(math.nan, "xyz")


@pytest.mark.parametrize(
    "clave, valor, minimo",
    [("c2f", -300, -273.15), ("f2c", -500, -459.67), ("km2mi", -1, 0), ("lb2kg", -2.5, 0)],
)
def test_error_de_limite_informa_valor_y_minimo(clave, valor, minimo):
    with pytest.raises(ErrorConversion) as error:
        convertir(valor, clave)
    assert (error.value.valor, error.value.minimo) == (valor, minimo)
    assert str(valor) in str(error.value) and str(minimo) in str(error.value)


def test_error_de_valor_no_finito_informa_el_valor():
    with pytest.raises(ErrorConversion, match="finito: inf") as error:
        convertir(math.inf, "c2f")
    assert error.value.valor == math.inf
    assert error.value.minimo is None


def test_conversion_no_soportada_informa_clave_y_disponibles():
    with pytest.raises(ConversionNoSoportada) as error:
        convertir(5, "xyz")
    assert error.value.clave == "xyz"
    assert error.value.disponibles == tuple(sorted(CONVERSIONES))


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
