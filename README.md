# Benchmark SQL-Backend (Miembro 2)

```
case1_pagila/ case2_northwind/ case3_synthetic/   # schema_defective.sql, schema_ground_truth.sql, seeds, defects_manifest.json
backend_defensive/    # FastAPI + asyncpg sobre esquema defectuoso (código defensivo marcado con DEFENSIVE-BEGIN/END)
backend_normalized/   # mismo contrato de API sobre esquema normalizado (línea de comparación para el Miembro 5)
tests/                # pruebas de contrato (corren contra ambos backends)
tools/                # generate_seeds.py, build_manifests.py, validate_benchmark.py, measure_defensive.py
scripts/ docker/      # setup_databases.sh, docker-compose.yml
docs/Ficha_Tecnica_Benchmark.md
```

## Uso rápido
```bash
docker compose up -d                       # PG16 en :5432 (postgres/postgres) con las 6 BD cargadas
# o, con un PG propio:
PGHOST=127.0.0.1 PGUSER=postgres PGPASSWORD=postgres bash scripts/setup_databases.sh

pip install -r backend_defensive/requirements.txt pytest httpx radon
python tools/validate_benchmark.py --dsn-base postgresql://postgres:postgres@127.0.0.1:5432
BACKEND_DIR=backend_defensive  pytest      # y luego backend_normalized
cd backend_defensive && uvicorn app.main:app --reload
python tools/measure_defensive.py
```
Bases creadas: `pagila_*`, `northwind_*`, `synthetic_*` con sufijo `_defective` / `_ground_truth`.
Si cambias datos: edita `tools/generate_seeds.py` y vuelve a ejecutarlo (no edites los `seed_*.sql`).
