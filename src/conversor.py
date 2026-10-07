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


class ErrorConversion(ValueError):
    """Error de dominio del conversor (valor inválido o conversión inexistente).

    Hereda de ValueError para no romper a quien ya capturaba ValueError.
    """


class ConversionNoSoportada(ErrorConversion):
    """La clave de conversión solicitada no está registrada."""


class Conversion(NamedTuple):
    """Entrada del registro: la función que convierte y su descripción legible."""

    funcion: Callable[[float], float]
    descripcion: str


def _exigir_minimo(valor: float, minimo: float, mensaje: str) -> None:
    """Lanza ErrorConversion si el valor está por debajo del límite físico."""
    if valor < minimo:
        raise ErrorConversion(mensaje)


def celsius_a_fahrenheit(celsius: float) -> float:
    """°F = °C × 9/5 + 32. Rechaza temperaturas por debajo del cero absoluto."""
    _exigir_minimo(celsius, CERO_ABSOLUTO_C, MENSAJE_CERO_ABSOLUTO)
    return celsius * 9 / 5 + 32


def fahrenheit_a_celsius(fahrenheit: float) -> float:
    """°C = (°F - 32) × 5/9. Rechaza temperaturas por debajo del cero absoluto."""
    _exigir_minimo(fahrenheit, CERO_ABSOLUTO_F, MENSAJE_CERO_ABSOLUTO)
    return (fahrenheit - 32) * 5 / 9


def km_a_millas(kilometros: float) -> float:
    """mi = km / KM_POR_MILLA. Rechaza distancias negativas."""
    _exigir_minimo(kilometros, 0, MENSAJE_DISTANCIA_NEGATIVA)
    return kilometros / KM_POR_MILLA


def millas_a_km(millas: float) -> float:
    """km = mi × KM_POR_MILLA. Rechaza distancias negativas."""
    _exigir_minimo(millas, 0, MENSAJE_DISTANCIA_NEGATIVA)
    return millas * KM_POR_MILLA


def kg_a_libras(kilogramos: float) -> float:
    """lb = kg / KG_POR_LIBRA. Rechaza masas negativas."""
    _exigir_minimo(kilogramos, 0, MENSAJE_MASA_NEGATIVA)
    return kilogramos / KG_POR_LIBRA


def libras_a_kg(libras: float) -> float:
    """kg = lb × KG_POR_LIBRA. Rechaza masas negativas."""
    _exigir_minimo(libras, 0, MENSAJE_MASA_NEGATIVA)
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

    Lanza ErrorConversion si el valor no es finito o viola un límite físico, y
    ConversionNoSoportada si la clave no está en CONVERSIONES.
    """
    # nan e inf positivo pasarían las validaciones de límites, así que se rechazan aquí
    if not math.isfinite(valor):
        raise ErrorConversion("El valor debe ser un número finito")
    if clave not in CONVERSIONES:
        disponibles = ", ".join(sorted(CONVERSIONES))
        raise ConversionNoSoportada(
            f"Conversión no soportada: {clave}. Usa una de: {disponibles}"
        )
    # "+ 0.0" normaliza -0.0 a 0.0 (por ejemplo, al convertir -0.0 o al redondear -0.00001)
    return round(CONVERSIONES[clave].funcion(valor), DECIMALES) + 0.0
