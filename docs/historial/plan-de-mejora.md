# Plan de mejora: corrección de bugs y mejoras de la auditoría

> **Estado (2026-10-06): completado.** Los 9 PRs del plan se fusionaron en `main` como
> PRs #4 a #12 de GitHub. La suite final tiene **61 pruebas pasando y ningún `xfail`**
> (58 previstas + `--help`, jerarquía de excepciones y un segundo caso de `-0.0`).
>
> | PR del plan | Hallazgo | PR en GitHub |
> |---|---|---|
> | 1 | #3 Cobertura | [#4](https://github.com/zelski/conversion_temperatura/pull/4) |
> | 2 | #1 Fahrenheit → Celsius | [#5](https://github.com/zelski/conversion_temperatura/pull/5) |
> | 3 | #2 Valores no finitos | [#6](https://github.com/zelski/conversion_temperatura/pull/6) |
> | 4 | #4 Excepciones de dominio | [#7](https://github.com/zelski/conversion_temperatura/pull/7) |
> | 5 | #5 `SystemExit` | [#8](https://github.com/zelski/conversion_temperatura/pull/8) |
> | 6 | #6 DRY | [#9](https://github.com/zelski/conversion_temperatura/pull/9) |
> | 7 | #7 `NamedTuple` | [#10](https://github.com/zelski/conversion_temperatura/pull/10) |
> | 8 | #8 Type hints y docstrings | [#11](https://github.com/zelski/conversion_temperatura/pull/11) |
> | 9 | #9 `-0.0` | [#12](https://github.com/zelski/conversion_temperatura/pull/12) |
>
> **Documento histórico**: se conserva como registro de cómo se planificó y ejecutó la
> corrección. Las rutas y comandos reflejan el proyecto en ese momento. Para el estado
> actual, consulta la [documentación vigente](../README.md).

Plan para atender los hallazgos de la auditoría del conversor de unidades. Parte de `main`
en `82b0f9f` (después de fusionar el PR #3): el código vive en `src/` y las pruebas en `tests/`.

## Principios

- **Un PR por hallazgo**, cada uno en su propia rama creada desde `main`, para que cada
  cambio se pueda revisar por separado. Se abre el siguiente cuando se fusiona el anterior.
- **`main` siempre en verde**: ningún PR se fusiona con pruebas fallando.
- **Cada corrección trae su prueba de regresión** y se demuestra que esa prueba fallaba antes.
- Todo en español (código, mensajes, nombres de pruebas, commits y PRs).
- Si un cambio altera el comportamiento documentado, se actualizan en el mismo PR
  `README.md`, `docs/arquitectura.md` y `CLAUDE.md`.

## Estrategia de pruebas: `xfail` estricto

Las pruebas van primero (PR 1), pero no pueden fusionarse fallando. Por eso las pruebas que
describen un bug conocido se marcan con:

```python
@pytest.mark.xfail(strict=True, reason="Bug #1: fórmula f2c invertida")
```

- Con el código original aparecen como `XFAIL`, lo que **demuestra que el bug existe**.
- `strict=True` hace que, si el bug se corrige y la marca sigue ahí, la prueba aparezca como
  `XPASS(strict)` y la suite falle. Así nadie olvida quitar la marca.
- El PR que corrige cada bug **solo quita su marca `xfail`** y cambia el código.

Las pruebas que dependen de una API que todavía no existe (por ejemplo `ErrorConversion`)
se agregan en el PR que crea esa API.

Verificación local:

```bash
.venv\Scripts\python -m pytest -v
.venv\Scripts\python src/cli.py 100 c2f
```

## Hallazgos de la auditoría

| # | Severidad | Hallazgo | ¿Rompe contrato? |
|---|---|---|---|
| 1 | Crítico | `fahrenheit_a_celsius` usa `* 9 / 5` en lugar de `* 5 / 9` (212 °F → 324) y valida el *resultado* en vez de la *entrada*. | No |
| 2 | Alto | `nan` e `inf` pasan todas las validaciones (`cli.py nan c2f` imprime `nan` con código 0). | Sí |
| 3 | Alto | Cobertura mínima: 4 pruebas; los errores y la CLI no tienen pruebas. | — |
| 4 | Medio | `KeyError` usado como error de dominio, lo que obliga al truco `strip(chr(39))` en `cli.py`. | Sí |
| 5 | Medio | `main()` lanza `SystemExit` con `abc c2f` en lugar de devolver un código. | No |
| 6 | Bajo | Validación duplicada en cada función (DRY). | No |
| 7 | Bajo | El registro guarda tuplas posicionales `(funcion, descripcion)`. | No |
| 8 | Bajo | Sin type hints; comentarios en lugar de docstrings; números mágicos. | No |
| 9 | Cosmético | Se imprime `-0.0`. | No |

## Secuencia de PRs

### PR 1 — Amplía la cobertura de pruebas (hallazgo #3)

- **Rama:** `pruebas-cobertura`
- **Archivos:** `tests/test_conversor.py`, `tests/test_cli.py` (nuevo)
- **Cambios:**
  - Pruebas parametrizadas de valores conocidos para las 6 conversiones.
  - Ida y vuelta (`c2f`↔`f2c`, `km2mi`↔`mi2km`, `kg2lb`↔`lb2kg`) recupera el valor.
  - Rechazo de valores físicamente imposibles y aceptación del límite exacto
    (`-273.15 °C`, `-459.67 °F`, `0 km`).
  - `tests/test_cli.py`: conversión exitosa, `--listar`, errores de conversión (código 1),
    errores de uso (código 2) y mensaje de clave inválida sin comillas.
  - Marcadas `xfail(strict=True)`: `f2c` (#1), valores no finitos (#2), `SystemExit` con
    `abc c2f` (#5) y `-0.0` (#9).
- **Criterio de aceptación:** la suite pasa en `main` y las pruebas de bugs salen `XFAIL`.

### PR 2 — Corrige la conversión Fahrenheit → Celsius (hallazgo #1)

- **Rama:** `corrige-fahrenheit-a-celsius`
- **Archivos:** `src/conversor.py`, `tests/test_conversor.py`
- **Cambios:**
  - Fórmula `(fahrenheit - 32) * 5 / 9`.
  - Nueva constante `CERO_ABSOLUTO_F = -459.67`; se valida la **entrada** contra ella.
  - Quitar las marcas `xfail` de #1.
- **Criterio:** `212 °F → 100`, `32 °F → 0`, `-40 °F → -40` e ida y vuelta con `c2f`.

### PR 3 — Rechaza valores no finitos (hallazgo #2)

- **Rama:** `rechaza-valores-no-finitos`
- **Archivos:** `src/conversor.py`, `tests/test_conversor.py`, `tests/test_cli.py`
- **Cambios:** `math.isfinite(valor)` en `convertir()`; lanza `ValueError("El valor debe ser
  un número finito")`. La CLI ya lo convierte en código de salida 1.
- **Rompe contrato:** `convertir(nan, ...)` deja de devolver `nan`. Indicarlo en el PR.

### PR 4 — Excepciones de dominio propias (hallazgo #4)

- **Rama:** `excepciones-de-dominio`
- **Archivos:** `src/conversor.py`, `src/cli.py`, pruebas y documentación
- **Cambios:**
  - `class ErrorConversion(ValueError)` y `class ConversionNoSoportada(ErrorConversion)`.
  - Las validaciones lanzan `ErrorConversion`; las claves desconocidas, `ConversionNoSoportada`.
  - `cli.py` captura solo `ErrorConversion` y se elimina `strip(chr(39))`.
  - `test_convertir_clave_invalida` espera `ConversionNoSoportada`.
  - Actualizar `docs/arquitectura.md` y `CLAUDE.md`, que mencionan `KeyError` y `ValueError`.
- **Rompe contrato:** `convertir()` ya no lanza `KeyError`. `ErrorConversion` hereda de
  `ValueError`, así que el código que captura `ValueError` sigue funcionando.

### PR 5 — `main()` devuelve el código en errores de argparse (hallazgo #5)

- **Rama:** `cli-sin-systemexit`
- **Archivos:** `src/cli.py`, `tests/test_cli.py`
- **Cambios:** envolver `parser.parse_args(argv)` en `try/except SystemExit` y devolver
  `salida.code`. Se descarta `exit_on_error=False` porque cambia según la versión de Python
  y no cubre `--help`. Quitar las marcas `xfail` de #5.

### PR 6 — Elimina la validación duplicada (hallazgo #6)

- **Rama:** `validacion-sin-duplicados`
- **Cambios:** helper `_exigir_minimo(valor, minimo, mensaje)` y mensajes como constantes
  (`MENSAJE_CERO_ABSOLUTO`, `MENSAJE_DISTANCIA_NEGATIVA`, `MENSAJE_MASA_NEGATIVA`).
  Se descarta una fábrica de conversiones lineales (KISS).
- **Criterio:** sin cambios de comportamiento; la suite pasa sin modificaciones.

### PR 7 — Registro con `NamedTuple` (hallazgo #7)

- **Rama:** `registro-namedtuple`
- **Cambios:** `class Conversion(NamedTuple)` con `funcion` y `descripcion`; `convertir()` y
  `listar_conversiones()` usan los campos por nombre. Actualizar la documentación del registro.

### PR 8 — Type hints, docstrings y constantes (hallazgo #8)

- **Rama:** `type-hints-y-docstrings`
- **Cambios:** anotaciones de tipos, docstrings en lugar de comentarios de cabecera,
  `DECIMALES = 4` y `SALIDA_OK`, `SALIDA_ERROR_CONVERSION` y `SALIDA_ERROR_USO` en `cli.py`.
  Las pruebas de la CLI usan esas constantes.

### PR 9 — Evita imprimir `-0.0` (hallazgo #9)

- **Rama:** `sin-cero-negativo`
- **Cambios:** `round(...) + 0.0` en `convertir()` con un comentario que lo explique.
  Quitar la marca `xfail` de #9.

## Resultado esperado

Al terminar, el código debe coincidir con la versión final validada en [`traspaso.md`](traspaso.md)
(adaptada a `src/`) y la suite debe tener **58 pruebas pasando y ningún `xfail`**. El PR 2 recupera el valor 0
en las pruebas de ida y vuelta (se había quitado porque `c2f→f2c` con 0 coincidía por
casualidad con el bug #1). Si los PRs 4 a 9 agregan pruebas nuevas, el total crecerá.

## Lista de verificación por PR

- [ ] Rama creada desde `main` actualizado.
- [ ] La prueba de regresión falla (o sale `XFAIL`) antes del cambio y pasa después.
- [ ] `.venv\Scripts\python -m pytest` pasa completo.
- [ ] Documentación actualizada si cambia el comportamiento o el contrato.
- [ ] Descripción del PR con propósito, cambios, impacto en el contrato y cómo verificar.
