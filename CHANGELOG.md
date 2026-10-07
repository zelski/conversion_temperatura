# Historial de cambios

Cambios relevantes del proyecto, del más reciente al más antiguo. El formato se basa en
[Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). El proyecto todavía no publica
versiones numeradas, así que los cambios se agrupan por fecha y enlazan al PR que los
introdujo.

Los cambios marcados con **⚠️ Rompe el contrato** pueden requerir ajustes en el código que
usa `conversor.py` o en los scripts que llaman a la CLI.

## 2026-10-06

### Agregado

- Código de salida `3` (`SALIDA_ERROR_INTERNO`) para fallos inesperados: antes un bug salía
  con código 1, igual que un error de conversión. Se sigue mostrando el traceback.
  ([#21](https://github.com/zelski/conversion_temperatura/pull/21))
- La clave de conversión no distingue mayúsculas ni espacios en la CLI (`C2F`, ` c2f `).
  ([#21](https://github.com/zelski/conversion_temperatura/pull/21))

### Corregido

- Mensajes más claros en tres errores frecuentes de la CLI
  ([#21](https://github.com/zelski/conversion_temperatura/pull/21)):
  - `-1e5 c2f` decía "argumentos no reconocidos"; ahora explica que los negativos con
    exponente van después de `--`.
  - `36,6 c2f` sugiere usar punto decimal.
  - `1e400 c2f` decía "número finito: inf"; ahora dice que el valor está fuera del rango
    representable.
- La CLI fallaba con `UnicodeEncodeError` si la salida no admitía acentos (por ejemplo,
  `PYTHONIOENCODING=ascii`); ahora sustituye esos caracteres por `?`.
  ([#21](https://github.com/zelski/conversion_temperatura/pull/21))

- **⚠️ Rompe el contrato** (salida de la CLI): los mensajes que generaba argparse salían en
  inglés (`usage:`, `invalid float value`, `unrecognized arguments`, `show this help…`).
  Ahora toda la CLI está en español: `uso:`, `Error: el valor debe ser un número: 'abc'`,
  `Error: argumentos no reconocidos: -x` y la ayuda con secciones `argumentos` y `opciones`.
  Los códigos de salida no cambian.
  ([#20](https://github.com/zelski/conversion_temperatura/pull/20))
- La ayuda anunciaba un comando `conversor` que no existe desde el PR #3; ahora muestra
  `python src/cli.py`. ([#20](https://github.com/zelski/conversion_temperatura/pull/20))
- Cuando faltaban argumentos, la línea de uso salía por stdout y el error por stderr. Ahora
  todos los errores de uso van solo a stderr.
  ([#20](https://github.com/zelski/conversion_temperatura/pull/20))

- Un valor finito muy grande podía desbordarse a `inf` al convertir: `1e308 c2f` imprimía
  `inf` con código 0. Ahora se rechaza con `ErrorConversion` (código 1).
  ([#19](https://github.com/zelski/conversion_temperatura/pull/19))
- Las funciones de conversión públicas (`celsius_a_fahrenheit`, …) aceptaban `nan` e `inf`
  cuando se llamaban sin pasar por `convertir()`. Ahora todas rechazan valores no finitos.
  ([#19](https://github.com/zelski/conversion_temperatura/pull/19))

- Las conversiones de distancia y masa usaban factores truncados (`0.621371` y `2.20462`) que
  alteraban los decimales mostrados con valores grandes: `1000 kg2lb` daba `2204.62` en lugar
  de `2204.6226`. Ahora se usan las definiciones exactas (1 mi = 1.609344 km,
  1 lb = 0.45359237 kg). **⚠️ Rompe el contrato**: las constantes `FACTOR_KM_A_MILLAS` y
  `FACTOR_KG_A_LIBRAS` pasan a ser `KM_POR_MILLA` y `KG_POR_LIBRA`, y los parámetros `km` y
  `kg` pasan a llamarse `kilometros` y `kilogramos`.
  ([#18](https://github.com/zelski/conversion_temperatura/pull/18))
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

- Los mensajes de error incluyen el valor que falló y, si aplica, el límite físico:
  `La distancia no puede ser negativa (mínimo permitido: 0): -1.0`. `convertir()` valida la
  clave antes que el valor, así que con ambos inválidos informa la clave. Las excepciones
  exponen los datos sin necesidad de interpretar el texto: `ErrorConversion.valor` y
  `.minimo`, y `ConversionNoSoportada.clave` y `.disponibles`. Los tipos de excepción y los
  códigos de salida no cambian; solo el texto de los mensajes.
  ([#19](https://github.com/zelski/conversion_temperatura/pull/19))
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
