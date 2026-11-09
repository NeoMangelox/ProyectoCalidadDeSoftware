# 04 — Agente Autónomo MCP y Validación *Dry-Run* (Nivel 2 vs. Nivel 3)

> **Rama Estandarizada Asociada:** `agente-mcp-normalizacion` (estandarización de `rama-de-sofia`, respaldada bajo `backup/pre-reorg-rama-de-sofia`).  
> **Propósito:** Comparar experimentalmente estrategias pasivas de IA en **Nivel 2** (*Zero-Shot* y *Chain-of-Thought* sin herramientas) frente a nuestra arquitectura de **Agente Autónomo Nivel 3** dotado de PostgreSQL MCP Server, habilidad procedimental y validación transaccional determinista (`BEGIN ... ROLLBACK`) sobre **9 experimentos (`EXP-01`–`EXP-09`)**.

---

## 1. Arquitectura Experimental e Inferencia Determinista

* **Configuración Central ([`config/inference_config.json`](config/inference_config.json)):** Decodificación determinista (*Greedy Decoding*) con `model = "gemini-3.8-flash"`, `reasoning_effort = "high"`, `temperature = 0.0`, `top_k = 1`, `top_p = 1.0`, `seed = 42` y penalizaciones en `0.0`.
* **Conectividad MCP ([`config/mcp_postgres.json`](config/mcp_postgres.json)):** Servidor `@modelcontextprotocol/server-postgres` conectado a las instancias aisladas de Docker (`pagila_defective`, `northwind_defective`, `synthetic_defective`).
* **Skill Procedimental ([`skills/postgres-schema-auditor/SKILL.md`](skills/postgres-schema-auditor/SKILL.md)):** Flujo estructurado en **5 etapas cognitivas** (introspección `information_schema`, muestreo empírico `SELECT ... LIMIT 5`, inferencia $X \rightarrow Y$, clasificación D1–D4 y generación DDL PostgreSQL 15+), operacionalizado en bucle cerrado de **4 fases** con el validador *Dry-Run*.
* **Herramientas Deterministas ([`tools/`](tools/)):**
  * [`introspect_db.py`](tools/introspect_db.py): Auditoría de tablas, columnas, constraints y muestreo vivo (`LIMIT 5`).
  * [`dry_run_validator.py`](tools/dry_run_validator.py): Arnés `BEGIN ... ROLLBACK` vía `psycopg` para capturar códigos `SQLSTATE` (`23503`, `42830`, `42703`) sin alterar datos.
  * [`run_benchmark_suite.py`](tools/run_benchmark_suite.py): Ejecutor maestro de los 9 scripts DDL (`EXP-01` al `EXP-09`).

---

## 2. Resultados Consolidados (`EXP-01`–`EXP-09`)

| Condición Metodológica | Experimentos | $\Sigma TP$ | $\Sigma FP$ | $\Sigma FN$ | Precision | Recall | $F_1$-Score | Compilación DDL | Alucinación FK | Iteraciones |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Nivel 2A: LLM Crudo (Zero-Shot)** | `EXP-01, 04, 07` | 13 | 6 | 15 | 68.42% | 46.43% | **55.32%** | **0.0%** (0/3) | **43.75%** (7/16) | 1.00 |
| **Nivel 2B: CoT Estático sin MCP** | `EXP-02, 05, 08` | 28 | 0 | 0 | 100.00% | 100.00% | **100.00%** | **0.0%** (0/3) | **0.00%** (0/16) | 1.00 |
| **Nivel 3: Agente MCP + Dry-Run** | `EXP-03, 06, 09` | **28** | **0** | **0** | **100.00%** | **100.00%** | **100.00%** | **100.0%** (3/3) | **0.00%** (0/16) | **1.67** |

* **Hallazgo Crítico ("Paradoja del CoT sin Herramientas"):** Aunque CoT estático alcanza $100\%$ de $F_1$ teórico, **el `100%` de sus scripts falla en PostgreSQL con `23503` (`foreign_key_violation`)** al no inspeccionar huérfanos preexistentes (`film_id=999`, `'ZZZZZ'`, `pedido_id=999`) ni poblar tablas catálogo antes de aplicar FKs. El Agente Nivel 3 captura el fallo en Dry-Run e inyecta saneamiento transaccional previo, confirmando **$H_2$**.

Ver reporte completo y trazas de error en [`docs/resultados_experimentos_ia.md`](docs/resultados_experimentos_ia.md) y los 9 artefactos DDL en [`resultados_experimentos/`](resultados_experimentos/).

---

## 3. Ejecución del Arnés *Dry-Run*

```bash
# Levantar PostgreSQL 16 desde la raíz
docker compose up -d

# Validar un DDL individual (BEGIN ... ROLLBACK)
python 04_agente_mcp_normalizacion/tools/dry_run_validator.py \
  --db pagila_defective \
  --file 04_agente_mcp_normalizacion/resultados_experimentos/case1_pagila/exp03_ddl_agent_optimized.sql

# Correr la suite completa EXP-01 a EXP-09
python 04_agente_mcp_normalizacion/tools/run_benchmark_suite.py
```
