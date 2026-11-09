# Agente Autónomo MCP y Validación *Dry-Run* para PostgreSQL (`agente-mcp-normalizacion`)

> **Alcance de la Rama:** Diseño experimental e infraestructura determinista para comparar estrategias de Inteligencia Artificial de **Nivel 2 (Zero-Shot y Chain-of-Thought estático)** frente a **Nivel 3 (Agente Autónomo con MCP Server, Skill procedimental y validación transaccional *Dry-Run*)** sobre 9 corridas (`EXP-01`–`EXP-09`), respondiendo $RQ_2$ y validando $H_2$.

---

## 1. Propósito Metodológico

Cuando un LLM opera "a ciegas" sobre texto DDL crudo (*Zero-Shot* o *CoT* sin herramientas), desconoce nombres exactos del catálogo y la presencia de registros huérfanos o listas delimitadas en datos reales. Esta rama implementa una arquitectura agéntica determinista que acopla:
1. **Introspección viva vía MCP (`@modelcontextprotocol/server-postgres`):** Inspección de `information_schema` y muestreo semántico real (`SELECT ... LIMIT 5`) mediante `tools/introspect_db.py`.
2. **Skill Procedimental (`skills/postgres-schema-auditor/SKILL.md`):** Protocolo *Chain-of-Thought* en 5 pasos (Introspección $\to$ Muestreo 1FN $\to$ Inferencia de Dependencias $\to$ Clasificación Taxonómica $\to$ Emisión de DDL nativo PostgreSQL 16).
3. **Bucle Cerrado *Dry-Run* (`tools/dry_run_validator.py`):** Ejecución real del DDL dentro de transacciones revertibles `BEGIN ... ROLLBACK` vía `psycopg`, capturando códigos `SQLSTATE` (`23503`, `42830`, `42703`) como retroalimentación determinista sin alterar el servidor.
4. **Decodificación Reproducible (`config/inference_config.json`):** Modelo base **`gemini-3.8-flash`** (`reasoning_effort = high`) bajo ***Greedy Decoding*** ($T=0.0, Top\text{-}K=1, Top\text{-}P=1.0, \text{seed}=42$, penalizaciones `0.0`).

---

## 2. Resultados Experimentales (`EXP-01` al `EXP-09`)

| Condición Metodológica | Experimentos | $\Sigma TP$ | $\Sigma FP$ | $\Sigma FN$ | Precision | Recall | $F_1$-Score | Compilación DDL | Alucinación FK | Iteraciones |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Nivel 2A: LLM Crudo (Zero-Shot)** | `EXP-01, 04, 07` | 13 | 6 | 15 | 68.42% | 46.43% | **55.32%** | **0.0%** (0/3) | **43.75%** (7/16) | 1.00 |
| **Nivel 2B: CoT Estático sin MCP** | `EXP-02, 05, 08` | 28 | 0 | 0 | 100.0% | 100.0% | **100.0%** | **0.0%** (0/3) | **0.00%** (0/16) | 1.00 |
| **Nivel 3: Agente MCP + Dry-Run** | `EXP-03, 06, 09` | **28** | **0** | **0** | **100.0%** | **100.0%** | **100.0%** | **100.0%** (3/3) | **0.00%** (0/16) | **1.67** |

* **Hallazgo Clave (Paradoja del CoT sin Herramientas):** El CoT estático alcanza $100\%$ de $F_1$ conceptual en papel, pero falla en el $100\%$ de ejecuciones reales en PostgreSQL por excepción `23503` (*foreign_key_violation*) ante huérfanos preexistentes (`film_id = 999`, `'ZZZZZ'`, `pedido_id = 999`). El Agente Nivel 3 detecta estos fallos en *Dry-Run*, añade saneamiento transaccional previo y compila al **100%**.

---

## 3. Reproducción en PostgreSQL 16 (Docker)

```bash
# 1. Levantar bases defectuosas en PostgreSQL 16
docker compose up -d

# 2. Validar individualmente un DDL con Dry-Run (BEGIN ... ROLLBACK)
python tools/dry_run_validator.py --db pagila_defective --file case1_pagila/resultados_experimentos_m4/exp03_ddl_agent_optimized.sql

# 3. Ejecutar la suite completa EXP-01 a EXP-09
python tools/run_benchmark_suite.py
```

---

## 4. Estructura Específica Añadida en la Rama

```text
├── README.md                                  # Documentación específica de esta rama
├── config/
│   ├── inference_config.json                  # Greedy Decoding determinista (seed=42)
│   └── mcp_postgres.json                      # Configuración @modelcontextprotocol/server-postgres
├── skills/postgres-schema-auditor/SKILL.md    # Especificación procedimental CoT del agente
├── tools/
│   ├── introspect_db.py                       # Introspección information_schema + LIMIT 5
│   ├── dry_run_validator.py                   # Validador transaccional BEGIN...ROLLBACK (psycopg)
│   └── run_benchmark_suite.py                 # Suite maestra EXP-01..EXP-09
├── case*/resultados_experimentos_m4/          # 9 scripts DDL generados (exp01..exp09.sql)
└── docs/resultados_experimentos_m4.md         # Informe completo, matrices y logs de ejecución
```
