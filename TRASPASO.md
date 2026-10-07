# Traspaso de sesión: auditoría del conversor de unidades

Este archivo resume una sesión previa de Claude (Cowork) para continuarla en Claude Code.
**No debe incluirse en ningún commit** (ver paso 0).

## Rol acordado

Actúa como programador senior de Python especializado en arquitectura y buenas prácticas
(clean code, SOLID, KISS, DRY). Todo el código, comentarios, identificadores, mensajes y
nombres de tests van en **español** (ver `CLAUDE.md`).

## Estado actual

- El código de esta carpeta está **sin modificar** (versión original).
- La suite original pasa (4/4), pero **no cubre el bug crítico** descrito abajo.
- El usuario ya creó en GitHub el repo **privado** `zelski/conversion_temperatura`.
  Si al crearlo marcó "Add README", hay que integrar ese commit antes de hacer push.
- Ninguna sesión previa ha hecho push ni ha abierto PRs todavía.

## Siguiente paso: subir el código original a GitHub mediante un PR

**Pide confirmación al usuario antes de cada acción que envíe algo a GitHub.**

0. Excluir este archivo del control de versiones sin tocar `.gitignore`:
   `git init -b main` y después agregar `TRASPASO.md` a `.git/info/exclude`.
1. `main`: un commit vacío `Inicializa el repositorio` (`git commit --allow-empty`).
   Si el repo remoto ya tiene un README, en su lugar haz `git pull origin main` y parte de ahí.
2. Crear la rama `codigo-inicial` y agregar los 7 archivos **sin cambios**: `.gitignore`, `CLAUDE.md`,
   `cli.py`, `conftest.py`, `conversor.py`, `requirements.txt`, `tests/test_conversor.py`.
   El commit se llama `Agrega el código inicial del conversor de unidades`.
3. Hacer push de ambas ramas a `https://github.com/zelski/conversion_temperatura.git`.
4. Abrir el PR `codigo-inicial` → `main` con el título y la descripción de abajo (ya aprobados por el usuario).

### Título del PR

Código inicial del conversor de unidades

### Descripción del PR

```markdown
## Propósito

Este PR incorpora el código existente del conversor de unidades **tal como está hoy**, sin modificaciones. El objetivo es tener una línea base visible sobre la cual proponer y revisar las correcciones y mejoras en PRs posteriores.

## Qué hace el proyecto

Es una herramienta de línea de comandos en Python puro (solo biblioteca estándar) para convertir unidades de temperatura, distancia y masa:

| Clave | Conversión |
|---|---|
| `c2f` / `f2c` | Celsius ↔ Fahrenheit |
| `km2mi` / `mi2km` | Kilómetros ↔ millas |
| `kg2lb` / `lb2kg` | Kilogramos ↔ libras |

- **`conversor.py`**: funciones de conversión que validan límites físicos (cero absoluto, distancias o masas negativas). Un registro central `CONVERSIONES` asocia cada clave con su función, y `convertir()` es el punto de entrada único (redondea a 4 decimales).
- **`cli.py`**: interfaz con `argparse`. `main()` devuelve un código de salida (0 ok, 1 error de conversión, 2 faltan argumentos) para poder probarlo.
- **`tests/`**: suite de pytest **parcial**, con 4 pruebas.

## Uso

    pip install -r requirements.txt
    python cli.py 100 c2f        # 212.0
    python cli.py --listar
    python -m pytest

## Estado

- ✅ `python -m pytest`: 4/4 pruebas pasan.
- ℹ️ Se subió sin cambios a propósito. Una auditoría de código ya identificó hallazgos (incluido un error en la conversión Fahrenheit → Celsius) que se atenderán en PRs separados para que cada cambio sea revisable por sí mismo.
```

## Después: hallazgos de la auditoría y plan de corrección

Cada corrección (o grupo pequeño de correcciones) va en **su propio PR** desde `main`, para dar visibilidad a cada cambio.
El orden de ejecución recomendado es: **tests primero** (#3) y comprobar que fallan con el código original; después #1, #2, #4, #5 y finalmente #6 a #9.

| # | Severidad | Hallazgo | Solución | ¿Rompe contrato? |
|---|---|---|---|---|
| 1 | Crítico | `fahrenheit_a_celsius` usa `* 9 / 5` en lugar de `* 5 / 9` (212 °F → 324). Además valida el *resultado* en vez de la *entrada*. | Corregir la fórmula y validar la entrada contra `CERO_ABSOLUTO_F = -459.67`. | No |
| 2 | Alto | `nan` e `inf` pasan todas las validaciones (`cli.py nan c2f` imprime `nan` con código 0). | Agregar `math.isfinite` en `convertir()`. | Sí |
| 3 | Alto | Cobertura mínima: 4 conversiones, los errores y la CLI no tienen tests. | Tests parametrizados, ida y vuelta, límites exactos y `tests/test_cli.py`. | — |
| 4 | Medio | `KeyError` usado como error de dominio, lo que obliga al truco `strip(chr(39))` en `cli.py`. | Excepciones `ErrorConversion(ValueError)` y `ConversionNoSoportada`. | Sí (`KeyError` → `ConversionNoSoportada`) |
| 5 | Medio | `main()` lanza `SystemExit` con `abc c2f` en lugar de devolver un código. | Envolver `parse_args` y devolver `salida.code`. Se descartó `exit_on_error=False` porque se comporta distinto según la versión de Python y no cubre `--help`. | No |
| 6 | Bajo | Validación duplicada (DRY). | Helper `_exigir_minimo` y mensajes como constantes. Se descartó la fábrica de conversiones lineales (KISS). | No |
| 7 | Bajo | El registro guarda tuplas posicionales `(funcion, descripcion)`. | `NamedTuple Conversion`. | No |
| 8 | Bajo | Sin type hints; comentarios en lugar de docstrings; números mágicos. | Type hints, docstrings, `DECIMALES` y constantes `SALIDA_*`. | No |
| 9 | Cosmético | Se imprime `-0.0`. | Sumar `+ 0.0` tras redondear. | No |

### Código final validado

Este es el código final con todas las correcciones aplicadas. Se probó en una copia aparte con Python 3.10 y pytest 9.1.1: **58 tests pasan**.
Para los PRs incrementales, aplícalo por partes según el plan de arriba.

#### `conversor.py`

```python
"""Funciones de conversión de unidades y registro de conversiones disponibles."""

import math
from typing import Callable, NamedTuple

FACTOR_KM_A_MILLAS = 0.621371
FACTOR_KG_A_LIBRAS = 2.20462

CERO_ABSOLUTO_C = -273.15
CERO_ABSOLUTO_F = -459.67

DECIMALES = 4

MENSAJE_CERO_ABSOLUTO = "Temperatura por debajo del cero absoluto"
MENSAJE_DISTANCIA_NEGATIVA = "La distancia no puede ser negativa"
MENSAJE_MASA_NEGATIVA = "La masa no puede ser negativa"


class ErrorConversion(ValueError):
    """Error de dominio del conversor (valor inválido o conversión inexistente)."""


class ConversionNoSoportada(ErrorConversion):
    """La clave de conversión solicitada no está registrada."""


class Conversion(NamedTuple):
    funcion: Callable[[float], float]
    descripcion: str


def _exigir_minimo(valor: float, minimo: float, mensaje: str) -> None:
    """Lanza ErrorConversion si el valor está por debajo del límite físico."""
    if valor < minimo:
        raise ErrorConversion(mensaje)


def celsius_a_fahrenheit(celsius: float) -> float:
    _exigir_minimo(celsius, CERO_ABSOLUTO_C, MENSAJE_CERO_ABSOLUTO)
    return celsius * 9 / 5 + 32


def fahrenheit_a_celsius(fahrenheit: float) -> float:
    _exigir_minimo(fahrenheit, CERO_ABSOLUTO_F, MENSAJE_CERO_ABSOLUTO)
    return (fahrenheit - 32) * 5 / 9


def km_a_millas(km: float) -> float:
    _exigir_minimo(km, 0, MENSAJE_DISTANCIA_NEGATIVA)
    return km * FACTOR_KM_A_MILLAS


def millas_a_km(millas: float) -> float:
    _exigir_minimo(millas, 0, MENSAJE_DISTANCIA_NEGATIVA)
    return millas / FACTOR_KM_A_MILLAS


def kg_a_libras(kg: float) -> float:
    _exigir_minimo(kg, 0, MENSAJE_MASA_NEGATIVA)
    return kg * FACTOR_KG_A_LIBRAS


def libras_a_kg(libras: float) -> float:
    _exigir_minimo(libras, 0, MENSAJE_MASA_NEGATIVA)
    return libras / FACTOR_KG_A_LIBRAS


CONVERSIONES: dict[str, Conversion] = {
    "c2f": Conversion(celsius_a_fahrenheit, "Celsius a Fahrenheit"),
    "f2c": Conversion(fahrenheit_a_celsius, "Fahrenheit a Celsius"),
    "km2mi": Conversion(km_a_millas, "Kilómetros a millas"),
    "mi2km": Conversion(millas_a_km, "Millas a kilómetros"),
    "kg2lb": Conversion(kg_a_libras, "Kilogramos a libras"),
    "lb2kg": Conversion(libras_a_kg, "Libras a kilogramos"),
}


def convertir(valor: float, clave: str) -> float:
    """Punto de entrada único: valida, convierte y redondea a DECIMALES."""
    if not math.isfinite(valor):
        raise ErrorConversion("El valor debe ser un número finito")
    try:
        conversion = CONVERSIONES[clave]
    except KeyError:
        disponibles = ", ".join(sorted(CONVERSIONES))
        raise ConversionNoSoportada(
            f"Conversión no soportada: {clave}. Usa una de: {disponibles}"
        ) from None
    # "+ 0.0" normaliza -0.0 a 0.0
    return round(conversion.funcion(valor), DECIMALES) + 0.0
```

#### `cli.py`

```python
"""Interfaz de línea de comandos. Uso: python cli.py VALOR CLAVE | python cli.py --listar"""

import argparse
import sys
from typing import Optional, Sequence

from conversor import CONVERSIONES, ErrorConversion, convertir

SALIDA_OK = 0
SALIDA_ERROR_CONVERSION = 1
SALIDA_ERROR_USO = 2


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="conversor",
        description="Conversor de unidades de línea de comandos",
    )
    parser.add_argument("valor", nargs="?", type=float, help="Valor numérico a convertir")
    parser.add_argument(
        "clave",
        nargs="?",
        help="Clave de conversión (ej. c2f, km2mi). Usa --listar para verlas todas",
    )
    parser.add_argument("--listar", action="store_true", help="Muestra las conversiones disponibles")
    return parser


def listar_conversiones() -> None:
    print("Conversiones disponibles:")
    for clave, conversion in sorted(CONVERSIONES.items()):
        print(f"  {clave:8s} {conversion.descripcion}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = construir_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as salida:
        # argparse ya imprimió la ayuda o el error; solo devolvemos su código
        return salida.code

    if args.listar:
        listar_conversiones()
        return SALIDA_OK

    if args.valor is None or args.clave is None:
        parser.print_usage()
        print("Error: se requieren VALOR y CLAVE (o usa --listar)", file=sys.stderr)
        return SALIDA_ERROR_USO

    try:
        resultado = convertir(args.valor, args.clave)
    except ErrorConversion as error:
        print(f"Error: {error}", file=sys.stderr)
        return SALIDA_ERROR_CONVERSION

    print(resultado)
    return SALIDA_OK


if __name__ == "__main__":
    raise SystemExit(main())
```

#### `tests/test_conversor.py`

```python
import math

import pytest

from conversor import CONVERSIONES, ConversionNoSoportada, ErrorConversion, convertir

PARES_INVERSOS = [("c2f", "f2c"), ("km2mi", "mi2km"), ("kg2lb", "lb2kg")]


@pytest.mark.parametrize(
    "clave, valor, esperado",
    [
        ("c2f", 100, 212), ("c2f", 0, 32), ("c2f", -40, -40),
        ("f2c", 212, 100), ("f2c", 32, 0), ("f2c", -40, -40),
        ("km2mi", 10, 6.2137), ("mi2km", 6.21371, 10),
        ("kg2lb", 1, 2.2046), ("lb2kg", 2.20462, 1),
    ],
)
def test_convertir_valores_conocidos(clave, valor, esperado):
    assert convertir(valor, clave) == pytest.approx(esperado)


@pytest.mark.parametrize("ida, vuelta", PARES_INVERSOS + [(b, a) for a, b in PARES_INVERSOS])
@pytest.mark.parametrize("valor", [0, 1, 37.5, 1000])
def test_ida_y_vuelta_recupera_el_valor(ida, vuelta, valor):
    intermedio = CONVERSIONES[ida].funcion(valor)
    assert CONVERSIONES[vuelta].funcion(intermedio) == pytest.approx(valor)


@pytest.mark.parametrize(
    "clave, valor",
    [("c2f", -273.16), ("f2c", -459.68), ("km2mi", -1), ("mi2km", -1), ("kg2lb", -1), ("lb2kg", -1)],
)
def test_convertir_rechaza_valores_fisicamente_imposibles(clave, valor):
    with pytest.raises(ErrorConversion):
        convertir(valor, clave)


@pytest.mark.parametrize("clave, valor", [("c2f", -273.15), ("f2c", -459.67), ("km2mi", 0)])
def test_convertir_acepta_el_limite_fisico_exacto(clave, valor):
    convertir(valor, clave)


@pytest.mark.parametrize("valor", [math.nan, math.inf, -math.inf])
def test_convertir_rechaza_valores_no_finitos(valor):
    with pytest.raises(ErrorConversion):
        convertir(valor, "km2mi")


def test_convertir_clave_invalida():
    with pytest.raises(ConversionNoSoportada, match="leguas2parsecs"):
        convertir(5, "leguas2parsecs")


def test_convertir_no_devuelve_cero_negativo():
    assert math.copysign(1, convertir(-0.0, "km2mi")) == 1
```

#### `tests/test_cli.py`

```python
import pytest

from cli import SALIDA_ERROR_CONVERSION, SALIDA_ERROR_USO, SALIDA_OK, main
from conversor import CONVERSIONES


@pytest.mark.parametrize("argv, esperado", [(["100", "c2f"], "212.0"), (["-40", "c2f"], "-40.0")])
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
```

