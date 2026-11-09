# Ficha Técnica del Benchmark — Miembro 2 (Dataset y Benchmark SQL-Backend)

> RDBMS único: **PostgreSQL 16/17**. Todos los datos de esta ficha fueron verificados contra una instancia real
> (`tools/validate_benchmark.py`, `pytest tests/` sobre ambos backends).

## 1. Tabla resumen

| Caso | Nombre | Tablas (defectuoso → normalizado) | Defectos inyectados | DDL defectuoso | DDL corregido |
|---|---|---|---|---|---|
| 1 | Pagila (Sakila PostgreSQL), núcleo OLTP de alquileres/inventario | 15 → 16 | 10 (1 de 1FN, 2 de 2FN, 2 de 3FN, 5 de FK) | `case1_pagila/schema_defective.sql` | `case1_pagila/schema_ground_truth.sql` |
| 2 | Northwind-PostgreSQL (órdenes, detalle, clientes) | 14 → 15 | 10 (1, 2, 1, 6) | `case2_northwind/schema_defective.sql` | `case2_northwind/schema_ground_truth.sql` |
| 3 | Sintético de Control PG (mutaciones aisladas, estilo DNBench) | 5 → 7 | 8 (1, 2, 1, 4) | `case3_synthetic/schema_defective.sql` | `case3_synthetic/schema_ground_truth.sql` |
| | **Total** | | **28 instancias** (3 de 1FN, 6 de 2FN, 4 de 3FN, 15 de FK) | | |

Cada caso incluye `defects_manifest.json` (verdad de terreno legible por máquina para Precision/Recall/F1) y
`seed_defective.sql` / `seed_ground_truth.sql` (datos semilla).

## 2. Ubicación exacta de cada defecto

### Caso 1 — Pagila
| ID | Tipo | Tabla.columna | Descripción / dependencia | Corrección en el GT | Endpoint que lo sufre |
|---|---|---|---|---|---|
| D1-01 | 1FN | `film.special_features` | Lista CSV (`Trailers,Deleted Scenes`) en TEXT | tabla `film_special_feature(film_id, feature)` | — |
| D2-01 | 2FN | `film_actor.actor_full_name` | `actor_id → nombre` (PK `actor_id, film_id`) | columna eliminada | — |
| D2-02 | 2FN | `film_category.category_name` | `category_id → nombre` (PK `film_id, category_id`) | columna eliminada | — |
| D3-01 | 3FN | `inventory.film_title` | `inventory_id → film_id → title` | columna eliminada (JOIN `film`) | `PUT /inventario` |
| D3-02 | 3FN | `address.city_name` | `address_id → city_id → city` | columna eliminada (JOIN `city`) | — |
| D4-01 | FK | `inventory.film_id` | sin FK → `film` | FK `ON DELETE RESTRICT` | `PUT /inventario` |
| D4-02 | FK | `inventory.store_id` | sin FK → `store` | FK `ON DELETE RESTRICT` | `PUT /inventario` |
| D4-03 | FK | `rental.inventory_id` | sin FK → `inventory` | FK `ON DELETE RESTRICT` | `DELETE /inventario` |
| D4-04 | FK | `rental.customer_id` | sin FK → `customer` | FK `ON DELETE RESTRICT` | — |
| D4-05 | FK | `payment.rental_id` | sin FK → `rental` | FK `ON DELETE RESTRICT` | — |

### Caso 2 — Northwind-PG
| ID | Tipo | Tabla.columna | Descripción / dependencia | Corrección en el GT | Endpoint que lo sufre |
|---|---|---|---|---|---|
| D1-01 | 1FN | `customers.phones` | teléfonos separados por coma (reemplaza a `phone`) | tabla `customer_phones(customer_id, phone)` | `POST /clientes` |
| D2-01 | 2FN | `order_details.product_name` | `product_id → product_name` (PK `order_id, product_id`) | columna eliminada | `POST /pedidos` |
| D2-02 | 2FN | `order_details.quantity_per_unit` | `product_id → quantity_per_unit` | columna eliminada | `POST /pedidos` |
| D3-01 | 3FN | `orders.shipper_name` | `order_id → ship_via → company_name` | columna eliminada (JOIN `shippers`) | `POST /pedidos` |
| D4-01 | FK | `orders.customer_id` | sin FK → `customers` | FK `RESTRICT` | `POST /pedidos` |
| D4-02 | FK | `orders.ship_via` | sin FK → `shippers` | FK `RESTRICT` | `POST /pedidos` |
| D4-03 | FK | `order_details.order_id` | sin FK → `orders` | FK `CASCADE` | `POST /pedidos` |
| D4-04 | FK | `order_details.product_id` | sin FK → `products` | FK `RESTRICT` | `POST /pedidos` |
| D4-05 | FK | `products.category_id` | sin FK → `categories` | FK `RESTRICT` | — |
| D4-06 | FK | `products.supplier_id` | sin FK → `suppliers` | FK `RESTRICT` | — |

### Caso 3 — Sintético de control (5 tablas: `clientes`, `productos`, `pedidos`, `detalle_pedido`, `envios`)
| ID | Tipo | Tabla.columna | Descripción / dependencia | Corrección en el GT |
|---|---|---|---|---|
| D1-01 | 1FN | `clientes.telefonos` | lista CSV | tabla `clientes_telefonos` |
| D2-01 | 2FN | `detalle_pedido.nombre_producto` | `producto_id → nombre` (PK `pedido_id, producto_id`) | columna eliminada |
| D2-02 | 2FN | `detalle_pedido.categoria_producto` | `producto_id → categoría` | columna eliminada |
| D3-01 | 3FN | `clientes.ciudad` | `cliente_id → codigo_postal → ciudad` | tabla `codigos_postales` + FK |
| D4-01 | FK | `pedidos.cliente_id` | sin FK → `clientes` | FK `RESTRICT` |
| D4-02 | FK | `detalle_pedido.pedido_id` | sin FK → `pedidos` | FK `CASCADE` |
| D4-03 | FK | `detalle_pedido.producto_id` | sin FK → `productos` | FK `RESTRICT` |
| D4-04 | FK | `envios.pedido_id` | sin FK → `pedidos` | FK `CASCADE` |

El Caso 3 no tiene backend: es el control para medir Precision/Recall/F1 del LLM sin ruido de dominio.

## 3. Cobertura defecto → backend (honestidad experimental)

`backend_defensive/` ejercita **4 de 10** defectos de Pagila y **8 de 10** de Northwind. El resto son *solo de esquema*
(los detectan los LLM/linters, pero no generan código defensivo medible). Los defectos de 1FN, 2FN y 3FN de Pagila
no se ejercitan (el único endpoint de Pagila es `/inventario`). Si el equipo quiere cubrir 1FN en Pagila, bastaría
un `GET /peliculas?feature=Trailers` que parsee el CSV (no incluido: los 3 endpoints pedidos son el alcance).

## 4. Qué consume cada miembro

| Miembro | Archivos |
|---|---|
| 1 (SLR) | esta ficha + `defects_manifest.json` (citar taxonomía y conteos) |
| 3 (linters) | `case*/schema_defective.sql`. Ejecución documentada en `m3/Analisis de Resultados.md`: SQLFluff no emitió errores `PRS`/`LXR`/`TMP` y registró `CP03`, `CP05`, `LT01`, `LT02` y `RF04`; SonarQube registró tres `SQLCC:C030`. Ningún hallazgo correspondió a los 28 defectos relacionales del manifiesto. |
| 4 (agente MCP) | `docker-compose.yml` o `scripts/setup_databases.sh` → BD `*_defective` pobladas; `defects_manifest.json` como verdad de terreno; `known_native_smells` para no contar falsos positivos |
| 5 (métricas) | `backend_defensive/` vs `backend_normalized/` (mismo contrato de API); marcadores `DEFENSIVE-BEGIN/END`; `tools/measure_defensive.py` |

## 5. Resultado de verificación

- `tools/validate_benchmark.py`: los 28 defectos presentes en el DDL defectuoso y ausentes/corregidos en el GT (`OK` en todos).
- Los 6 DDL + 6 semillas cargan sin errores en PostgreSQL 16.
- `pytest tests/` (10 pruebas de contrato) pasa contra **ambos** backends.
- Medición preliminar (`tools/measure_defensive.py`, radon, suma de CC por función):

| Backend | SLOC | SLOC_def | CC total |
|---|---|---|---|
| defensive | 170 | 31 (18.2 %) | 45 |
| normalized | 162 | 0 | 35 |

  ΔCC ≈ 22 %. Es una cifra de referencia para un backend mínimo; la medición oficial es del Miembro 5.

## 6. Decisiones de diseño y discrepancias con los documentos del equipo

1. **Northwind tiene 14 tablas, no 13.** El `northwind.sql` de `pthom/northwind_psql` crea 14 (incluye `us_states`). Se usaron las 14; conviene corregir "13 tablas" en *Contexto General* (§3 y diagrama).
2. **Pagila = núcleo de 15 tablas.** El repo oficial tiene además `film_embedding` (pgvector), `uuidv7()`, `tsvector` y 59 particiones de `payment`. Se omitieron para que el DDL corra en cualquier PG 16/17 sin extensiones. Se mantienen tipos (`TEXT`, `TIMESTAMPTZ`, `IDENTITY`) y relaciones originales.
3. **El GT corrige solo lo inyectado.** Northwind y Sakila tienen *smells* nativos (p. ej. `postal_code → city` en `customers`). Se listan en `known_native_smells` de cada manifiesto; se sugiere no puntuarlos como falsos positivos. Si el docente exige un GT "perfecto", habría que normalizarlos también.
4. **Adaptación de Northwind:** `orders.order_id` usa `IDENTITY` (el original asigna IDs a mano) para no introducir un quinto defecto.
5. **Los datos semilla defectuosos contienen anomalías deliberadas** (huérfanos, nombres obsoletos, CSV con separadores mixtos) para que el muestreo `LIMIT 5` del agente tenga qué encontrar. El GT no las tiene.
6. **Endpoints extra:** `GET` y `DELETE /inventario/{id}` (el `DELETE` ejerce el `COUNT(*)` previo al borrado que pide la guía).
7. **Defensivo ≠ inseguro por diseño:** el código defensivo verifica y luego escribe; entre ambos pasos hay una ventana de *race condition* (TOCTOU) que el esquema normalizado elimina. Es un argumento útil para la discusión del paper.
8. **Referencias del documento de Contexto a verificar (Miembro 1):** `arXiv:2609.xxxxx` (DNBench) es un marcador de posición, y la cita *Sharma et al. (2018) "Database Smells: A Survey and Taxonomy"* no coincide con lo que recuerdo del trabajo de Sharma et al. sobre *smells* de esquemas (ICSE-SEIP 2018, "Smelly relations"); conviene confirmarla antes de enviar el manuscrito.
