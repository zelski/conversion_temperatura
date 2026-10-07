"""Funciones de conversión de unidades y registro de conversiones disponibles."""

import math
from collections.abc import Callable
from typing import NamedTuple

# Definiciones exactas del acuerdo internacional de 1959 sobre la yarda y la libra
KM_POR_MILLA = 1.609344
KG_POR_LIBRA = 0.45359237

# Límite físico inferior para temperaturas (cero absoluto) en cada escala
CERO_ABSOLUTO_C = -273.15
CERO_ABSOLUTO_F = -459.67

# Decimales a los que convertir() redondea el resultado
DECIMALES = 4

# Mensajes de error compartidos por las validaciones
MENSAJE_CERO_ABSOLUTO = "Temperatura por debajo del cero absoluto"
MENSAJE_DISTANCIA_NEGATIVA = "La distancia no puede ser negativa"
MENSAJE_MASA_NEGATIVA = "La masa no puede ser negativa"
MENSAJE_NO_FINITO = "El valor debe ser un número finito"
MENSAJE_DESBORDAMIENTO = "El resultado excede el rango representable"


class ErrorConversion(ValueError):
    """Error de dominio del conversor (valor inválido o conversión inexistente).

    Hereda de ValueError para no romper a quien ya capturaba ValueError. Expone el
    valor que provocó el error y, si se violó un límite físico, el mínimo permitido;
    ambos son None cuando no aplican.
    """

    def __init__(
        self, mensaje: str, *, valor: float | None = None, minimo: float | None = None
    ) -> None:
        super().__init__(mensaje)
        self.valor = valor
        self.minimo = minimo


class ConversionNoSoportada(ErrorConversion):
    """La clave de conversión solicitada no está registrada.

    Expone la clave pedida y las claves disponibles, ordenadas.
    """

    def __init__(
        self, mensaje: str, *, clave: str | None = None, disponibles: tuple[str, ...] = ()
    ) -> None:
        super().__init__(mensaje)
        self.clave = clave
        self.disponibles = disponibles


class Conversion(NamedTuple):
    """Entrada del registro: la función que convierte y su descripción legible."""

    funcion: Callable[[float], float]
    descripcion: str


def _validar(valor: float, minimo: float, mensaje: str) -> None:
    """Lanza ErrorConversion si el valor no es finito o está por debajo del límite físico.

    Toda función de conversión debe llamarla antes de calcular.
    """
    # nan e inf positivo pasarían la comparación con el mínimo, así que se rechazan antes
    if not math.isfinite(valor):
        raise ErrorConversion(f"{MENSAJE_NO_FINITO}: {valor}", valor=valor)
    if valor < minimo:
        raise ErrorConversion(
            f"{mensaje} (mínimo permitido: {minimo}): {valor}", valor=valor, minimo=minimo
        )


def celsius_a_fahrenheit(celsius: float) -> float:
    """°F = °C × 9/5 + 32. Rechaza temperaturas por debajo del cero absoluto."""
    _validar(celsius, CERO_ABSOLUTO_C, MENSAJE_CERO_ABSOLUTO)
    return celsius * 9 / 5 + 32


def fahrenheit_a_celsius(fahrenheit: float) -> float:
    """°C = (°F - 32) × 5/9. Rechaza temperaturas por debajo del cero absoluto."""
    _validar(fahrenheit, CERO_ABSOLUTO_F, MENSAJE_CERO_ABSOLUTO)
    return (fahrenheit - 32) * 5 / 9


def km_a_millas(kilometros: float) -> float:
    """mi = km / KM_POR_MILLA. Rechaza distancias negativas."""
    _validar(kilometros, 0, MENSAJE_DISTANCIA_NEGATIVA)
    return kilometros / KM_POR_MILLA


def millas_a_km(millas: float) -> float:
    """km = mi × KM_POR_MILLA. Rechaza distancias negativas."""
    _validar(millas, 0, MENSAJE_DISTANCIA_NEGATIVA)
    return millas * KM_POR_MILLA


def kg_a_libras(kilogramos: float) -> float:
    """lb = kg / KG_POR_LIBRA. Rechaza masas negativas."""
    _validar(kilogramos, 0, MENSAJE_MASA_NEGATIVA)
    return kilogramos / KG_POR_LIBRA


def libras_a_kg(libras: float) -> float:
    """kg = lb × KG_POR_LIBRA. Rechaza masas negativas."""
    _validar(libras, 0, MENSAJE_MASA_NEGATIVA)
    return libras * KG_POR_LIBRA


CONVERSIONES: dict[str, Conversion] = {
    "c2f": Conversion(celsius_a_fahrenheit, "Celsius a Fahrenheit"),
    "f2c": Conversion(fahrenheit_a_celsius, "Fahrenheit a Celsius"),
    "km2mi": Conversion(km_a_millas, "Kilómetros a millas"),
    "mi2km": Conversion(millas_a_km, "Millas a kilómetros"),
    "kg2lb": Conversion(kg_a_libras, "Kilogramos a libras"),
    "lb2kg": Conversion(libras_a_kg, "Libras a kilogramos"),
}


def convertir(valor: float, clave: str) -> float:
    """Punto de entrada único: valida, convierte y redondea a DECIMALES.

    Lanza ConversionNoSoportada si la clave no está en CONVERSIONES, y ErrorConversion
    si el valor no es finito, viola un límite físico o el resultado se desborda.
    """
    # La clave se valida primero: no depende del valor y da el mensaje más útil
    if clave not in CONVERSIONES:
        disponibles = tuple(sorted(CONVERSIONES))
        raise ConversionNoSoportada(
            f"Conversión no soportada: {clave}. Usa una de: {', '.join(disponibles)}",
            clave=clave,
            disponibles=disponibles,
        )
    resultado = CONVERSIONES[clave].funcion(valor)
    # Un valor finito muy grande puede desbordarse a inf al aplicar la fórmula
    if not math.isfinite(resultado):
        raise ErrorConversion(f"{MENSAJE_DESBORDAMIENTO}: {valor}", valor=valor)
    # "+ 0.0" normaliza -0.0 a 0.0 (por ejemplo, al convertir -0.0 o al redondear -0.00001)
    return round(resultado, DECIMALES) + 0.0
