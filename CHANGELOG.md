# Historial de cambios

Cambios relevantes del proyecto, del más reciente al más antiguo. El formato se basa en
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). El proyecto todavía no publica
versiones numeradas, así que los cambios se agrupan por fecha y enlazan al PR que los
introdujo.

Los cambios marcados con **⚠️ Rompe el contrato** pueden requerir ajustes en el código que
usa `conversor.py` o en los scripts que llaman a la CLI.

## 2026-10-06

### Corregido

- `fahrenheit_a_celsius` multiplicaba por 9/5 en lugar de 5/9 (`212 °F` daba `324`) y
  rechazaba temperaturas válidas porque validaba el resultado en vez de la entrada.
  ([#5](https://github.com/zelski/conversion_temperatura/pull/5))
- **⚠️ Rompe el contrato**: `nan` e `inf` pasaban todas las validaciones y la CLI imprimía
  `nan` con código 0. Ahora `convertir()` los rechaza con un error.
  ([#6](https://github.com/zelski/conversion_temperatura/pull/6))
- `main()` lanzaba `SystemExit` ante argumentos inválidos (`abc c2f`) o `--help` en lugar de
  devolver el código de salida. ([#8](https://github.com/zelski/conversion_temperatura/pull/8))
- `convertir()` podía devolver `-0.0` (por ejemplo, con `-17.77778 c2f`).
  ([#12](https://github.com/zelski/conversion_temperatura/pull/12))

### Cambiado

- **⚠️ Rompe el contrato**: `convertir()` lanza `ConversionNoSoportada` en lugar de `KeyError`
  para claves desconocidas. Los errores de validación pasan a ser `ErrorConversion`, que
  hereda de `ValueError`, así que el código que capturaba `ValueError` sigue funcionando.
  ([#7](https://github.com/zelski/conversion_temperatura/pull/7))
- El registro `CONVERSIONES` guarda `Conversion(funcion, descripcion)` (`NamedTuple`) en lugar
  de tuplas sin nombre. Sigue siendo compatible con el desempaquetado por posición.
  ([#10](https://github.com/zelski/conversion_temperatura/pull/10))
- Validaciones sin duplicar, type hints, docstrings y constantes con nombre (`DECIMALES`,
  `SALIDA_*`), sin cambios de comportamiento.
  ([#9](https://github.com/zelski/conversion_temperatura/pull/9),
  [#11](https://github.com/zelski/conversion_temperatura/pull/11))

### Agregado

- Suite de pruebas ampliada de 4 a 61 pruebas, con `tests/test_cli.py` y la convención de
  `xfail` estricto para documentar bugs conocidos.
  ([#4](https://github.com/zelski/conversion_temperatura/pull/4))
- Medición de cobertura con pytest-cov, al 100 % de sentencias y ramas.
  ([#14](https://github.com/zelski/conversion_temperatura/pull/14))
- Documentación reorganizada en `docs/`, con guía de contribución y este historial.

## 2026-10-05

### Cambiado

- **⚠️ Rompe el contrato**: el código se mueve a `src/` y las pruebas a `tests/`. La CLI pasa
  de ejecutarse con `python cli.py` a `python src/cli.py`.
  ([#2](https://github.com/zelski/conversion_temperatura/pull/2),
  [#3](https://github.com/zelski/conversion_temperatura/pull/3))

### Agregado

- Código inicial del conversor: 6 conversiones de temperatura, distancia y masa, y CLI con
  `--listar`. ([#1](https://github.com/zelski/conversion_temperatura/pull/1))
