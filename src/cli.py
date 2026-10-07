"""Interfaz de línea de comandos. Uso: python src/cli.py VALOR CLAVE | python src/cli.py --listar"""

import argparse
import io
import math
import sys
import traceback
from collections.abc import Sequence
from typing import NoReturn

from conversor import CONVERSIONES, ErrorConversion, convertir

# Códigos de salida que devuelve main(); SALIDA_ERROR_INTERNO solo lo usa
# ejecutar_desde_consola() ante una excepción inesperada (un bug)
SALIDA_OK = 0
SALIDA_ERROR_CONVERSION = 1
SALIDA_ERROR_USO = 2
SALIDA_ERROR_INTERNO = 3

# Textos que float() interpreta como infinito; cualquier otro valor infinito es un desbordamiento
_TEXTOS_INFINITO = {"inf", "infinity"}

# Nombre con el que se ejecuta la CLI, tal como lo documenta el README
PROGRAMA = "python src/cli.py"


class _ParserEnEspanol(argparse.ArgumentParser):
    """ArgumentParser con los textos fijos de argparse traducidos al español."""

    def format_usage(self) -> str:
        return super().format_usage().replace("usage: ", "uso: ", 1)

    def format_help(self) -> str:
        return super().format_help().replace("usage: ", "uso: ", 1)

    def error(self, message: str) -> NoReturn:
        # argparse llama a error() con mensajes en inglés solo en casos raros que main() no
        # valida por su cuenta (por ejemplo, --listar=1), así que se sustituyen por uno genérico
        self.print_usage(sys.stderr)
        self.exit(SALIDA_ERROR_USO, "Error: argumentos inválidos; usa --help para ver el uso\n")


def construir_parser() -> argparse.ArgumentParser:
    """Define los argumentos de la CLI: VALOR y CLAVE opcionales, y la bandera --listar.

    VALOR se recibe como texto y main() lo convierte a número, para que el error de un
    valor no numérico salga en español.
    """
    parser = _ParserEnEspanol(
        prog=PROGRAMA,
        description="Conversor de unidades de línea de comandos",
        add_help=False,
    )
    argumentos = parser.add_argument_group("argumentos")
    argumentos.add_argument("valor", nargs="?", metavar="VALOR", help="Valor numérico a convertir")
    argumentos.add_argument(
        "clave",
        nargs="?",
        metavar="CLAVE",
        help="Clave de conversión (ej. c2f, km2mi). Usa --listar para verlas todas",
    )
    opciones = parser.add_argument_group("opciones")
    opciones.add_argument("-h", "--help", action="help", help="Muestra esta ayuda y sale")
    opciones.add_argument(
        "--listar",
        action="store_true",
        help="Muestra las conversiones disponibles",
    )
    return parser


def listar_conversiones() -> None:
    """Imprime la tabla de conversiones disponibles."""
    print("Conversiones disponibles:")
    for clave, conversion in sorted(CONVERSIONES.items()):
        print(f"  {clave:8s} {conversion.descripcion}")


def _error_de_uso(parser: argparse.ArgumentParser, mensaje: str) -> int:
    """Imprime la línea de uso y el error en stderr, y devuelve SALIDA_ERROR_USO."""
    parser.print_usage(sys.stderr)
    print(f"Error: {mensaje}", file=sys.stderr)
    return SALIDA_ERROR_USO


def _es_numero(texto: str) -> bool:
    """Indica si float() acepta el texto."""
    try:
        float(texto)
    except ValueError:
        return False
    return True


def _mensaje_de_valor_invalido(texto: str) -> str:
    """Explica por qué VALOR no es un número y, si usó coma decimal, sugiere el punto."""
    mensaje = f"el valor debe ser un número: {texto!r}"
    # No se acepta la coma porque "1,000" es ambiguo (¿mil o uno?), pero se sugiere el punto
    con_punto = texto.replace(",", ".")
    if texto.count(",") == 1 and _es_numero(con_punto):
        mensaje += f" (usa punto decimal, por ejemplo {con_punto})"
    return mensaje


def main(argv: Sequence[str] | None = None) -> int:
    """Ejecuta la CLI y devuelve un código de salida SALIDA_* en lugar de terminar el proceso."""
    parser = construir_parser()
    try:
        args, no_reconocidos = parser.parse_known_args(argv)
    except SystemExit as fin_de_argparse:
        # argparse ya imprimió la ayuda o el error. SystemExit.code puede ser int, str o
        # None; se normaliza para cumplir el tipo de retorno
        if isinstance(fin_de_argparse.code, int):
            return fin_de_argparse.code
        return SALIDA_ERROR_USO

    if no_reconocidos:
        # argparse solo reconoce negativos como -40 o -4.5; -1e5, -5. o -inf los toma por
        # opciones desconocidas, así que se explica cómo escribirlos
        negativo = next((texto for texto in no_reconocidos if _es_numero(texto)), None)
        if negativo is not None:
            return _error_de_uso(
                parser,
                f"'{negativo}' parece un número negativo; escríbelo después de --, "
                f"por ejemplo: {PROGRAMA} -- {negativo} CLAVE",
            )
        return _error_de_uso(parser, f"argumentos no reconocidos: {' '.join(no_reconocidos)}")

    if args.listar:
        listar_conversiones()
        return SALIDA_OK

    # Sin --listar se requieren ambos argumentos posicionales
    if args.valor is None or args.clave is None:
        return _error_de_uso(parser, "se requieren VALOR y CLAVE (o usa --listar)")

    try:
        valor = float(args.valor)
    except ValueError:
        return _error_de_uso(parser, _mensaje_de_valor_invalido(args.valor))

    # float("1e400") se desborda a inf sin error; se informa el texto que escribió el usuario
    if math.isinf(valor) and args.valor.strip().lstrip("+-").lower() not in _TEXTOS_INFINITO:
        print(f"Error: el valor está fuera del rango representable: {args.valor!r}", file=sys.stderr)
        return SALIDA_ERROR_CONVERSION

    try:
        resultado = convertir(valor, args.clave.strip().lower())
    except ErrorConversion as error:
        print(f"Error: {error}", file=sys.stderr)
        return SALIDA_ERROR_CONVERSION

    print(resultado)
    return SALIDA_OK


def ejecutar_desde_consola(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada de la consola: prepara la salida y atrapa fallos inesperados.

    A diferencia de main(), convierte cualquier excepción no prevista (un bug) en
    SALIDA_ERROR_INTERNO, conservando el traceback para depurar, de modo que un script que
    use la CLI pueda distinguir un bug de un error de conversión.
    """
    for flujo in (sys.stdout, sys.stderr):
        # Si la consola no admite algún carácter (por ejemplo 'ó' en ASCII), se escribe '?'
        # en lugar de fallar con UnicodeEncodeError
        if isinstance(flujo, io.TextIOWrapper):
            flujo.reconfigure(errors="replace")
    try:
        return main(argv)
    except Exception:
        traceback.print_exc()
        print("Error interno inesperado; por favor reporta este fallo", file=sys.stderr)
        return SALIDA_ERROR_INTERNO


if __name__ == "__main__":
    raise SystemExit(ejecutar_desde_consola())
