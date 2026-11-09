# Corpus Experimental SQL-Backend en PostgreSQL 16 (`benchmark-sql-backend`)

> **Alcance de la Rama:** Construcción del banco de pruebas relacional unificado en **PostgreSQL 16** (3 esquemas, 28 defectos inyectados) y del servicio *backend* dual equivalente en **Python 3.12 + FastAPI + `asyncpg`** (`backend_defensive/` vs. `backend_normalized/`).

---

## 1. Propósito Metodológico

Esta rama provee la materia prima experimental controlada para evaluar la cadena causal desde el diseño del esquema relacional hasta la complejidad estructural del código de aplicación:
- **Esquemas defectuosos sintácticamente válidos (`schema_defective.sql`):** Compilan al 100% en PostgreSQL 16 para probar la ceguera semántica de linters AST y exigir introspección real de catálogo/datos a los agentes de IA.
- **Esquemas de referencia (*Ground Truth*, `schema_ground_truth.sql`):** Modelos normalizados a Tercera Forma Normal (3FN) con claves foráneas declarativas (`ON DELETE RESTRICT` / `CASCADE`).
- **Backend Dual Funcionalmente Equivalente:** Demuestra el costo estructural de suplir invariantes relacionales ausentes mediante código defensivo frente a delegar la integridad declarativa en PostgreSQL.

---

## 2. Corpus Experimental (3 Esquemas, 28 Defectos)

| Caso | Dominio | Tablas (Def $\to$ GT) | Defectos (1FN / 2FN / 3FN / FK) | Semillas Contaminadas (Deliberadas) |
| :--- | :--- | :---: | :---: | :--- |
| **`case1_pagila/`** | Alquileres OLTP e inventario (puerto Sakila PG, núcleo puro) | $15 \to 16$ | **10** (`1` / `2` / `2` / `5`) | Lista CSV en `film.special_features` y tuplas huérfanas (`film_id = 999`, `inventory_id = 999`). |
| **`case2_northwind/`** | Órdenes, clientes y proveedores (`northwind_psql` con `us_states`) | $14 \to 15$ | **10** (`1` / `2` / `1` / `6`) | Delimitadores mixtos `[,;/]` en `customers.phones` y huérfanos (`'ZZZZZ'`, `ship_via = 99`, `product_id = 999`). |
| **`case3_synthetic/`** | Micro-benchmark e-commerce controlado (estilo *DNBench*) | $5 \to 7$ | **8** (`1` / `2` / `1` / `4`) | Delimitadores `[,;]` en `clientes.telefonos`, transitiva `codigo_postal -> ciudad` y huérfano `pedido_id = 999`. |

Cada caso incluye `defects_manifest.json` como verdad de terreno legible por máquina (descontando particularidades heredadas originales en `known_native_smells`).

---

## 3. Backend Dual Equivalente y Validación de Contrato

* **`backend_defensive/`:** Implementa **7 endpoints** REST (`crear_cliente`, `obtener_cliente`, `poner_inventario`, `obtener_inventario`, `borrar_inventario`, `crear_pedido`, `obtener_pedido`) que ejercitan **12 de los 20 defectos** de Pagila y Northwind. Toda lógica compensatoria (`re.split`, `SELECT COUNT(*)` previos, sincronización manual 2FN/3FN) se delimita entre marcadores `# >>> DEFENSIVE-BEGIN` y `# <<< DEFENSIVE-END`.
* **`backend_normalized/`:** Reemplaza las compensaciones por inserciones transaccionales directas, consultas `JOIN` / `array_agg` y manejo nativo de excepciones PostgreSQL (`asyncpg.ForeignKeyViolationError`).
* **Equivalencia Garantizada (`tests/test_contract.py`):** Ambas versiones superan exactamente la misma suite de **10 pruebas agnósticas de contrato en `pytest`** (`201`, `200`, `204`, `404`, `409`, `422`).

---

## 4. Reproducción y Verificación

```bash
# 1. Levantar las 6 bases precargadas en PostgreSQL 16 Docker
docker compose up -d

# 2. Verificar que los 28 defectos existen en _defective y están resueltos en _ground_truth
python tools/validate_benchmark.py --dsn-base postgresql://postgres:postgres@127.0.0.1:5432

# 3. Ejecutar las 10 pruebas de contrato en ambos backends
BACKEND_DIR=backend_defensive pytest tests
BACKEND_DIR=backend_normalized pytest tests
```

---

## 5. Estructura de la Rama

```text
├── README.md                     # Documentación específica de esta rama
├── Ficha_Tecnica_Benchmark.md    # Detalle de los 28 defectos, semillas y cobertura
├── docker-compose.yml / docker/  # PostgreSQL 16 precargado con 6 bases de datos
├── scripts/setup_databases.sh    # Carga idempotente DDL + seeds
├── case1_pagila/                 # Esquemas, semillas y manifiesto Caso 1
├── case2_northwind/              # Esquemas, semillas y manifiesto Caso 2
├── case3_synthetic/              # Esquemas, semillas y manifiesto Caso 3
├── backend_defensive/            # Servicio FastAPI con código defensivo delimitado
├── backend_normalized/           # Servicio FastAPI limpio sobre esquema 3FN
├── tests/test_contract.py        # 10 pruebas de equivalencia funcional HTTP
└── tools/                        # build_manifests.py, generate_seeds.py, validate_benchmark.py, measure_defensive.py
```
