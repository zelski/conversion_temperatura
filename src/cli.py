"""Interfaz de línea de comandos. Uso: python src/cli.py VALOR CLAVE | python src/cli.py --listar"""

import argparse
import sys
from typing import Optional, Sequence

from conversor import CONVERSIONES, ErrorConversion, convertir

# Códigos de salida que devuelve main()
SALIDA_OK = 0
SALIDA_ERROR_CONVERSION = 1
SALIDA_ERROR_USO = 2


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="conversor",
        description="Conversor de unidades de línea de comandos",
    )
    parser.add_argument(
        "valor",
        nargs="?",
        type=float,
        help="Valor numérico a convertir",
    )
    parser.add_argument(
        "clave",
        nargs="?",
        help="Clave de conversión (ej. c2f, km2mi). Usa --listar para verlas todas",
    )
    parser.add_argument(
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


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Ejecuta la CLI y devuelve un código de salida SALIDA_* en lugar de terminar el proceso."""
    parser = construir_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as salida:
        # argparse ya imprimió la ayuda o el error; solo devolvemos su código
        return salida.code

    if args.listar:
        listar_conversiones()
        return SALIDA_OK

    # Sin --listar se requieren ambos argumentos posicionales
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
