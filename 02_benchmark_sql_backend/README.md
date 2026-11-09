# 02 — Dataset Relacional PostgreSQL 16 y Backend Dual FastAPI

> **Rama Estandarizada Asociada:** `benchmark-sql-backend` (respaldada históricamente bajo `backup/pre-reorg-main`).  
> **Propósito:** Proveer el banco de pruebas reproducible en un único motor (**PostgreSQL 16/17**): 3 esquemas con **28 defectos relacionales inyectados**, sus *Ground Truth* normalizados, semillas con anomalías deliberadas y dos microservicios FastAPI funcionalmente equivalentes para medir $RQ_3$.

---

## 1. Corpus Relacional (3 Esquemas, 28 Defectos)

| Caso | Dominio | Tablas (`Def -> GT`) | Defectos (`D1/D2/D3/D4`) | Archivos Clave |
| :--- | :--- | :---: | :---: | :--- |
| **Caso 1: Pagila** | Puerto OLTP Sakila en PG (núcleo sin extensiones) | `15 -> 16` | **10** (`1` / `2` / `2` / `5`) | [`case1_pagila/`](case1_pagila/defects_manifest.json) |
| **Caso 2: Northwind-PG** | Ventas, pedidos, clientes y envíos (`northwind_psql`, 14 tablas) | `14 -> 15` | **10** (`1` / `2` / `1` / `6`) | [`case2_northwind/`](case2_northwind/defects_manifest.json) |
| **Caso 3: Sintético Control** | Micro-benchmark estilo *DNBench* libre de ruido heredado | `5 -> 7` | **8** (`1` / `2` / `1` / `4`) | [`case3_synthetic/`](case3_synthetic/defects_manifest.json) |
| **Total Corpus** | — | — | **28 instancias trazables** | [`Ficha_Tecnica_Benchmark.md`](Ficha_Tecnica_Benchmark.md) |

Cada carpeta de caso contiene `schema_defective.sql`, `schema_ground_truth.sql`, `seed_defective.sql` (con filas huérfanas y delimitadores mixtos para forzar el muestreo del agente), `seed_ground_truth.sql` y `defects_manifest.json` (incluyendo `known_native_smells`).

---

## 2. Arquitectura Backend Dual (FastAPI + `asyncpg`)

* [`backend_defensive/`](backend_defensive/app/routers/): Implementa **7 rutas REST** sobre Pagila (`/inventario`) y Northwind (`/clientes`, `/pedidos`) compensando **12 de los 20 defectos de esquema** mediante código defensivo delimitado con `# >>> DEFENSIVE-BEGIN` y `# <<< DEFENSIVE-END`.
* [`backend_normalized/`](backend_normalized/app/routers/): Implementa el mismo contrato de API apoyado en el esquema normalizado (JOINs, `array_agg`, `FOREIGN KEY`, manejo de `ForeignKeyViolationError`).
* [`tests/test_contract.py`](tests/test_contract.py): **10 pruebas agnósticas de contrato** en `pytest` que certifican equivalencia funcional exacta entre ambos backends (`201`, `200`, `204`, `404`, `409`, `422`).

---

## 3. Estructura y Comandos de Verificación

```text
02_benchmark_sql_backend/
├── Ficha_Tecnica_Benchmark.md       # Detalle por defecto, cobertura 12/20 y notas de diseño
├── pytest.ini                       # Configuración de pruebas de contrato
├── case1_pagila/                    # DDL, semillas y manifiesto JSON (Pagila)
├── case2_northwind/                 # DDL, semillas y manifiesto JSON (Northwind-PG)
├── case3_synthetic/                 # DDL, semillas y manifiesto JSON (Sintético)
├── backend_defensive/               # Microservicio FastAPI con código defensivo
├── backend_normalized/              # Microservicio FastAPI sobre esquema normalizado
├── docker/init.sh                   # Script de inicialización invocado por ../docker-compose.yml
├── scripts/setup_databases.sh       # Provisiona las 6 bases de datos en PostgreSQL 16
├── tests/                           # 10 pruebas de contrato compartidas
└── tools/                           # build_manifests.py, generate_seeds.py, measure_defensive.py, validate_benchmark.py
```

### Ejecución Local
```bash
# Desde la raíz del repositorio: levantar las 6 bases en PostgreSQL 16
docker compose up -d

# Desde esta carpeta (02_benchmark_sql_backend/): validar catálogo real y contratos API
cd 02_benchmark_sql_backend
python -m pip install -r backend_defensive/requirements.txt
python tools/validate_benchmark.py --dsn-base postgresql://postgres:postgres@127.0.0.1:5432
BACKEND_DIR=backend_defensive pytest tests -v
BACKEND_DIR=backend_normalized pytest tests -v
```
