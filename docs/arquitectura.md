# Arquitectura

## Estructura del proyecto

```text
.
├── docs/                       # Documentación
│   └── arquitectura.md
├── src/                        # Código fuente (layout "src")
│   └── conversor_unidades/
│       ├── __init__.py
│       ├── __main__.py         # Permite: python -m conversor_unidades
│       ├── cli.py              # Interfaz de línea de comandos (argparse)
│       └── conversor.py        # Lógica de conversión y registro CONVERSIONES
├── tests/                      # Pruebas con pytest
│   └── test_conversor.py
├── pyproject.toml              # Metadatos del paquete y configuración de pytest
└── requirements.txt
```

Se usa el *layout* `src` para que las pruebas se ejecuten contra el paquete y no contra
archivos sueltos de la raíz: nada se puede importar por accidente desde el directorio de
trabajo. `pyproject.toml` agrega `src` al `pythonpath` de pytest, así que las pruebas
funcionan sin instalar el paquete.

## Módulos

- **`conversor.py`**: cada conversión es una función independiente que valida los límites
  físicos (cero absoluto, distancias o masas negativas) lanzando `ValueError`. El diccionario
  `CONVERSIONES` es el registro central que asocia una clave corta (`c2f`, `km2mi`, …) con
  `(función, descripción)`. `convertir(valor, clave)` es el punto de entrada único: lanza
  `KeyError` para claves desconocidas y redondea el resultado a 4 decimales.
- **`cli.py`**: interfaz con `argparse`. `main(argv=None)` devuelve un código de salida
  (0 correcto, 1 error de conversión, 2 faltan argumentos) en lugar de llamar a `sys.exit`,
  para poder probarla pasando `argv`. `--listar` lee las descripciones de `CONVERSIONES`.

## Agregar una conversión

1. Escribe la función en `src/conversor_unidades/conversor.py`.
2. Regístrala en `CONVERSIONES`.

La CLI y `--listar` la detectan automáticamente.
