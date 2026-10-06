# Conversor de unidades

Herramienta de línea de comandos en Python puro (solo biblioteca estándar) para convertir
unidades de temperatura, distancia y masa.

## Instalación

```bash
pip install -e ".[dev]"
```

## Uso

```bash
conversor 100 c2f          # 212.0
conversor --listar         # muestra las conversiones disponibles
python -m conversor_unidades 100 c2f   # alternativa sin el comando instalado
```

## Pruebas

```bash
python -m pytest
```

## Documentación

- [Arquitectura y estructura del proyecto](docs/arquitectura.md)
