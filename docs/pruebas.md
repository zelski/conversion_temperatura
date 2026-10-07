# Pruebas

La suite usa [pytest](https://docs.pytest.org/) y vive en `tests/`. La configuración está en
`pyproject.toml`: `pythonpath = ["src"]` permite importar `conversor` y `cli` directamente,
sin instalar el proyecto.

## Ejecutar las pruebas

```bash
python -m pytest                     # toda la suite
python -m pytest -v                  # con el nombre de cada caso
python -m pytest tests/test_cli.py   # un archivo
python -m pytest tests/test_conversor.py::test_convertir_clave_invalida   # una prueba
```

## Organización

| Archivo | Qué prueba |
|---|---|
| `tests/test_conversor.py` | `convertir()` y las funciones de `CONVERSIONES` |
| `tests/test_cli.py` | `main(argv)`: salida impresa (con `capsys`) y códigos de salida |

**`test_conversor.py`** agrupa los casos por comportamiento y los parametriza para cubrir
todas las conversiones:

- Valores conocidos (por ejemplo, `100 °C → 212 °F`).
- Ida y vuelta: convertir y deshacer la conversión recupera el valor original.
- Límites físicos: se rechaza lo imposible (por debajo del cero absoluto, distancias o masas
  negativas) y se acepta el límite exacto.
- Valores no finitos (`nan`, `inf`, `-inf`), claves inexistentes y la jerarquía de
  excepciones.
- Normalización de `-0.0`.

**`test_cli.py`** llama a `main()` con una lista de argumentos en lugar de lanzar un proceso.
Usa las constantes `SALIDA_*` de `cli.py` en vez de números literales.

## Agregar pruebas

- Nombres en español que describan el comportamiento: `test_<sujeto>_<comportamiento>`, por
  ejemplo `test_convertir_rechaza_valores_no_finitos`.
- Si el caso encaja en una prueba existente, agrégalo a su `@pytest.mark.parametrize` en
  lugar de crear una prueba nueva.
- Una conversión nueva necesita al menos un valor conocido, su par de ida y vuelta (si tiene
  inversa) y su límite físico.

## Bugs conocidos: `xfail` estricto

Un bug que todavía no se corrige se documenta con una prueba que describe el comportamiento
**correcto**, marcada así:

```python
@pytest.mark.xfail(strict=True, reason="Bug #N: descripción breve")
```

- Mientras el bug exista, la prueba aparece como `XFAIL` y la suite pasa.
- El PR que corrige el bug **debe quitar la marca**. Si la olvida, la prueba aparece como
  `XPASS(strict)` y la suite falla, así que no puede quedar una marca obsoleta.

Para listar los bugs abiertos:

```bash
python -m pytest -rx
```

Este mecanismo se usó para corregir los 9 hallazgos de la auditoría. Ver el
[plan de mejora](historial/plan-de-mejora.md).

## Cobertura

La cobertura de sentencias y ramas de `src/` se mide con pytest-cov, configurado en
`pyproject.toml`:

```bash
python -m pytest --cov                     # reporte en la terminal con líneas faltantes
python -m pytest --cov --cov-report=html   # reporte navegable en htmlcov/index.html
```

**Regla del proyecto: la cobertura debe mantenerse en 100 %.** Todo código nuevo llega con
sus pruebas.

La única exclusión es el bloque `if __name__ == "__main__":` de `cli.py`. Solo se ejecuta al
lanzar el script desde la consola y se limita a llamar a `main()`, que las pruebas ya cubren.
Agregar más exclusiones requiere justificarlas en el PR.
