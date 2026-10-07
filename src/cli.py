"""Interfaz de línea de comandos. Uso: python src/cli.py VALOR CLAVE | python src/cli.py --listar"""

import argparse
import sys
from collections.abc import Sequence
from typing import NoReturn

from conversor import CONVERSIONES, ErrorConversion, convertir

# Códigos de salida que devuelve main()
SALIDA_OK = 0
SALIDA_ERROR_CONVERSION = 1
SALIDA_ERROR_USO = 2

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
        return _error_de_uso(parser, f"el valor debe ser un número: {args.valor!r}")

    try:
        resultado = convertir(valor, args.clave)
    except ErrorConversion as error:
        print(f"Error: {error}", file=sys.stderr)
        return SALIDA_ERROR_CONVERSION

    print(resultado)
    return SALIDA_OK


if __name__ == "__main__":
    raise SystemExit(main())
