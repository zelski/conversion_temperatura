# Arquitectura

## Estructura del proyecto

```text
.
├── docs/                       # Documentación
│   └── arquitectura.md
├── src/                        # Código fuente
│   ├── cli.py                  # Interfaz de línea de comandos (argparse)
│   └── conversor.py            # Lógica de conversión y registro CONVERSIONES
├── tests/                      # Pruebas con pytest
│   └── test_conversor.py
├── pyproject.toml              # Configuración de pytest
└── requirements.txt
```

El código vive en `src/` como módulos planos, separado de las pruebas y la documentación.
`pyproject.toml` agrega `src` al `pythonpath` de pytest, así que las pruebas importan
`conversor` directamente sin instalar nada. Al ejecutar `python src/cli.py`, Python agrega
`src/` al `sys.path` por ser la carpeta del script, por lo que `cli.py` encuentra a
`conversor.py`.

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

1. Escribe la función en `src/conversor.py`.
2. Regístrala en `CONVERSIONES`.

La CLI y `--listar` la detectan automáticamente.
