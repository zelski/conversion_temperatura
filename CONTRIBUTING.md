# Guía de contribución

## Idioma

Todo va en **español**: código, identificadores, comentarios, mensajes al usuario, nombres de
pruebas, commits, PRs y documentación. La única excepción es `CLAUDE.md`, que son
instrucciones para Claude Code.

## Flujo de trabajo

1. Crea una rama desde `main` actualizado, con un nombre descriptivo en español y guiones:
   `corrige-fahrenheit-a-celsius`, `agrega-conversion-de-volumen`.
2. Haz **un cambio por PR**: una corrección, una mejora o una refactorización. Así cada
   cambio se revisa por sí mismo.
3. Abre el PR contra `main`. Se fusiona con un merge commit cuando no tiene conflictos y la
   suite pasa.

`main` debe estar siempre en verde: ningún PR se fusiona con pruebas fallando.

## Corregir un bug

1. Escribe primero una prueba que describa el comportamiento correcto y comprueba que
   **falla** con el código actual.
2. Si el bug no se corrige en el mismo PR, marca la prueba con
   `@pytest.mark.xfail(strict=True, reason="Bug #N: ...")`. Ver
   [docs/pruebas.md](docs/pruebas.md#bugs-conocidos-xfail-estricto).
3. El PR que corrige el bug quita la marca `xfail` en el mismo cambio.

## Estilo de código

- Python puro, solo biblioteca estándar. pytest y pytest-cov son dependencias de
  desarrollo; no agregues dependencias de ejecución.
- Type hints en todas las funciones y docstrings en las funciones y clases públicas.
- Constantes con nombre en lugar de números o cadenas mágicas.
- Los errores del dominio se lanzan como `ErrorConversion` o sus subclases, nunca como
  `ValueError` o `KeyError` sueltos.

## Commits y PRs

- **Mensaje de commit**: una primera línea en imperativo (`Corrige…`, `Agrega…`), y después un
  párrafo que explique **por qué** se hace el cambio.
- **Descripción del PR**: propósito, cambios, impacto en el contrato y cómo verificarlo. Si el
  cambio rompe el contrato, indícalo con **⚠️**.

## Lista de verificación del PR

- [ ] La rama sale de `main` actualizado.
- [ ] `python -m pytest` pasa completo.
- [ ] `python -m pytest --cov` mantiene la cobertura en 100 %.
- [ ] Si corrige un bug, su prueba fallaba antes del cambio.
- [ ] La documentación afectada está actualizada en el mismo PR: `README.md`, `docs/`,
      `CLAUDE.md`.
- [ ] Los cambios visibles para el usuario están en [CHANGELOG.md](CHANGELOG.md).
