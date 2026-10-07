# Conversor de unidades

Herramienta de línea de comandos para convertir unidades de temperatura, distancia y masa.
Está escrita en Python puro: no necesita ninguna dependencia para funcionar.

```console
$ python src/cli.py 100 c2f
212.0
```

## Requisitos

- Python 3.10 o superior.
- Solo para desarrollo: pytest y pytest-cov (en `requirements.txt`).

## Instalación

No hay que instalar nada para usar el conversor: basta con clonar el repositorio. Para
ejecutar las pruebas, conviene instalar las dependencias de desarrollo en un entorno
virtual:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS
pip install -r requirements.txt
```

## Uso

```bash
python src/cli.py VALOR CLAVE    # convierte VALOR usando la conversión CLAVE
python src/cli.py --listar       # muestra las conversiones disponibles
python src/cli.py --help         # muestra la ayuda
```

### Conversiones disponibles

| Clave | Conversión | Límite físico |
|---|---|---|
| `c2f` | Celsius → Fahrenheit | ≥ -273.15 °C (cero absoluto) |
| `f2c` | Fahrenheit → Celsius | ≥ -459.67 °F (cero absoluto) |
| `km2mi` | Kilómetros → millas | ≥ 0 |
| `mi2km` | Millas → kilómetros | ≥ 0 |
| `kg2lb` | Kilogramos → libras | ≥ 0 |
| `lb2kg` | Libras → kilogramos | ≥ 0 |

Los resultados se redondean a 4 decimales.

### Ejemplos

```console
$ python src/cli.py -40 f2c
-40.0

$ python src/cli.py 10 km2mi
6.2137

$ python src/cli.py -1 km2mi
Error: La distancia no puede ser negativa (mínimo permitido: 0): -1.0

$ python src/cli.py 5 xyz
Error: Conversión no soportada: xyz. Usa una de: c2f, f2c, kg2lb, km2mi, lb2kg, mi2km

$ python src/cli.py abc c2f
uso: python src/cli.py [-h] [--listar] [VALOR] [CLAVE]
Error: el valor debe ser un número: 'abc'
```

### Códigos de salida

| Código | Significado |
|---|---|
| 0 | Conversión correcta (o `--listar` / `--help`) |
| 1 | Error de conversión: valor fuera del límite físico, `nan`/`inf`, resultado demasiado grande o clave inexistente |
| 2 | Error de uso: faltan argumentos, el valor no es un número o hay argumentos no reconocidos |

Los mensajes de error se escriben en la salida de error (stderr).

## Desarrollo

```bash
python -m pytest            # ejecuta las pruebas
python -m pytest --cov      # con reporte de cobertura (debe ser 100 %)
```

- [Guía de contribución](CONTRIBUTING.md): flujo de trabajo y convenciones.
- [Historial de cambios](CHANGELOG.md).

## Documentación

El índice completo está en [docs/README.md](docs/README.md):

- [Arquitectura](docs/arquitectura.md): estructura, flujo de una conversión y decisiones de
  diseño.
- [Pruebas](docs/pruebas.md): cómo ejecutar y escribir pruebas, bugs conocidos y cobertura.
