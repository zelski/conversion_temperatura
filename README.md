# Conversor de unidades

Herramienta de línea de comandos en Python puro (solo biblioteca estándar) para convertir
unidades de temperatura, distancia y masa.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python src/cli.py 100 c2f      # 212.0
python src/cli.py --listar     # muestra las conversiones disponibles
```

## Pruebas

```bash
python -m pytest
python -m pytest --cov                        # con reporte de cobertura (sentencias y ramas)
python -m pytest --cov --cov-report=html      # reporte navegable en htmlcov/index.html
```

## Documentación

- [Arquitectura y estructura del proyecto](docs/arquitectura.md)
