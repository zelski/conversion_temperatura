# Arquitectura

## Estructura del proyecto

```text
.
├── .claude/
│   └── settings.json           # Configuración de Claude Code (archivos que no debe leer)
├── docs/                       # Documentación (índice en docs/README.md)
├── src/                        # Código fuente
│   ├── cli.py                  # Interfaz de línea de comandos (argparse)
│   └── conversor.py            # Lógica de conversión y registro CONVERSIONES
├── tests/                      # Pruebas con pytest (ver docs/pruebas.md)
│   ├── test_cli.py
│   └── test_conversor.py
├── CHANGELOG.md                # Historial de cambios
├── CLAUDE.md                   # Instrucciones para Claude Code
├── CONTRIBUTING.md             # Cómo contribuir
├── pyproject.toml              # Configuración de pytest y coverage
├── README.md
└── requirements.txt            # Dependencias de desarrollo (pytest, pytest-cov)
```

El código vive en `src/` como módulos planos, sin subpaquetes, separado de las pruebas y la
documentación. No hay paquete instalable:

- Al ejecutar `python src/cli.py`, Python agrega `src/` al `sys.path` por ser la carpeta del
  script, así que `cli.py` puede importar `conversor`.
- En las pruebas, `pyproject.toml` agrega `src/` al `pythonpath` de pytest.

## Flujo de una conversión

```text
python src/cli.py 100 c2f
        │
        ▼
cli.main(argv) ──── argparse valida los argumentos ──── error ──► código 2 (SALIDA_ERROR_USO)
        │
        ▼
conversor.convertir(100.0, "c2f")
        │  1. busca la clave en CONVERSIONES              ──► ConversionNoSoportada
        │  2. llama a celsius_a_fahrenheit(100.0)
        │       └─ _validar(): valor finito y límite físico ──► ErrorConversion
        │  3. comprueba que el resultado no se desborde   ──► ErrorConversion
        │  4. redondea a DECIMALES y normaliza -0.0
        ▼
212.0 ──► se imprime, código 0 (SALIDA_OK)

ErrorConversion (o subclase) ──► "Error: <mensaje>" en stderr, código 1 (SALIDA_ERROR_CONVERSION)
```

## Módulos

### `conversor.py`

- **Funciones de conversión** (`celsius_a_fahrenheit`, `km_a_millas`, …): cada una valida su
  entrada con `_validar()` (que rechaza valores no finitos y fuera del límite físico) y aplica
  su fórmula. Como son públicas, dan la misma garantía si se llaman sin pasar por
  `convertir()`. Los factores y límites son
  constantes con nombre (`KM_POR_MILLA`, `CERO_ABSOLUTO_C`, …). Los factores de distancia y
  masa guardan las definiciones exactas (1 mi = 1.609344 km, 1 lb = 0.45359237 kg) y cada
  par de funciones inversas multiplica o divide por la misma constante.
- **Registro `CONVERSIONES`**: asocia una clave corta (`c2f`, `km2mi`, …) con una
  `Conversion(funcion, descripcion)`, que es un `NamedTuple`. Es la única fuente de verdad
  sobre qué conversiones existen.
- **`convertir(valor, clave)`**: punto de entrada único. Valida primero la clave (no depende
  del valor y da el mensaje más útil), convierte, rechaza resultados que se desbordan a `inf`
  y redondea a `DECIMALES` (4) decimales.
- **Errores de dominio**:

  ```text
  ValueError
  └── ErrorConversion           # valor no finito, fuera del límite físico o desbordamiento
      └── ConversionNoSoportada # la clave no está en CONVERSIONES
  ```

  Capturar `ErrorConversion` cubre todos los errores del conversor. Como hereda de
  `ValueError`, el código que ya capturaba `ValueError` sigue funcionando.

  Además del mensaje, las excepciones exponen datos para quien las capture sin tener que
  interpretar el texto (`None` cuando no aplican):

  | Excepción | Atributos |
  |---|---|
  | `ErrorConversion` | `valor` (la entrada que falló) y `minimo` (el límite físico violado) |
  | `ConversionNoSoportada` | `clave` (la pedida) y `disponibles` (tupla ordenada de claves válidas) |

  Los mensajes incluyen el valor y, si aplica, el límite: `Temperatura por debajo del cero
  absoluto (mínimo permitido: -459.67): -500.0`.

### `cli.py`

Interfaz con `argparse`. `main(argv=None)` **devuelve** un código de salida en lugar de
terminar el proceso, para poder probarla pasando `argv`:

| Constante | Código | Cuándo |
|---|---|---|
| `SALIDA_OK` | 0 | Conversión correcta, `--listar` o `--help` |
| `SALIDA_ERROR_CONVERSION` | 1 | `convertir()` lanzó `ErrorConversion` |
| `SALIDA_ERROR_USO` | 2 | Faltan argumentos o son inválidos |

`main()` también captura el `SystemExit` que lanza argparse ante argumentos inválidos o
`--help`, y devuelve su código. `--listar` lee las descripciones directamente de
`CONVERSIONES`.

## Agregar una conversión

1. Escribe la función en `src/conversor.py`: valida la entrada con `_validar()` antes de
   calcular y documenta la fórmula en su docstring.
2. Regístrala en `CONVERSIONES` con una clave corta y una descripción.
3. Agrega sus casos a las pruebas parametrizadas de `tests/test_conversor.py` (ver
   [pruebas.md](pruebas.md#agregar-pruebas)).

La CLI y `--listar` la detectan automáticamente.

## Decisiones de diseño

- **Una función por conversión en lugar de una fábrica genérica**: las fórmulas se leen
  directamente en el código (KISS). Ver
  [PR #9](https://github.com/zelski/conversion_temperatura/pull/9).
- **Excepciones propias en lugar de `KeyError`/`ValueError` sueltos**: la CLI captura un único
  tipo y los mensajes no necesitan limpieza. Ver
  [PR #7](https://github.com/zelski/conversion_temperatura/pull/7).
- **`main()` devuelve el código en lugar de llamar a `sys.exit()`**: permite probar la CLI
  sin lanzar procesos. Se descartó `exit_on_error=False` de argparse porque no cubre
  `--help`. Ver [PR #8](https://github.com/zelski/conversion_temperatura/pull/8).
