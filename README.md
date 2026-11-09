<<<<<<< HEAD
# Agente Autónomo MCP y Validación *Dry-Run* para PostgreSQL (`agente-mcp-normalizacion`)

> **Alcance de la Rama:** Diseño experimental e infraestructura determinista para comparar estrategias de Inteligencia Artificial de **Nivel 2 (Zero-Shot y Chain-of-Thought estático)** frente a **Nivel 3 (Agente Autónomo con MCP Server, Skill procedimental y validación transaccional *Dry-Run*)** sobre 9 corridas (`EXP-01`–`EXP-09`), respondiendo $RQ_2$ y validando $H_2$.
=======
# Métricas Estructurales de Calidad Backend e ISO/IEC 25010 (`metricas-calidad-backend`)

> **Alcance de la Rama:** Formalización matemática e instrumentación estática determinista sobre AST de Python 3.12 (`metrics_quality/measure_quality.py`) para cuantificar el impacto de la normalización PostgreSQL en la Complejidad Ciclomática ($CC$), Código Defensivo ($SLOC_{def}$) y Consultas Previas ($Q_{prev}$), respondiendo $RQ_3$ y contrastando $H_3$.
>>>>>>> metricas-calidad-backend

---

## 1. Propósito Metodológico

<<<<<<< HEAD
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
=======
Esta rama aísla la capa de **evaluación cuantitativa del software *backend*** sobre el par funcionalmente equivalente `backend_defensive/` vs. `backend_normalized/`:
1. **Instrumentación AST Nativa (`metrics_quality/measure_quality.py`):** Recorre exclusivamente los rangos `[start_line, end_line]` de cada nodo `FunctionDef` / `AsyncFunctionDef` (evitando falsos positivos por *docstrings* o estilo), calibrada contra `radon` v6.0+ sobre `metrics_quality/test_sample_backend.py`.
2. **Métricas Formalizadas:**
   - **Complejidad Ciclomática de McCabe ($CC = E - N + 2P = 1 + \sum \pi_i$):** Clasificada en rangos de riesgo de Radon (A: 1–5, B: 6–10, C–F: >10).
   - **Líneas Lógicas Defensivas ($SLOC_{def}$):** Código añadido para compensar 1FN/2FN/3FN o ausencia de FKs (`# >>> DEFENSIVE-BEGIN/END`).
   - **Consultas Previas ($Q_{prev}$):** Sentencias `SELECT COUNT(*) / EXISTS / 1` antes de mutar datos.
   - **Alineación ISO/IEC 25010:** Mantenibilidad (*Analizabilidad*, *Modificabilidad*, *Modularidad*) y Fiabilidad (*Tolerancia a fallos*, mitigación de condiciones de carrera TOCTOU vía motor ACID).

---

## 2. Resumen de Resultados Verificados

| Indicador Global (`backend_defensive` $\to$ `backend_normalized`) | Inicial | Final | Diferencial ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **$\sum CC$ en los 7 *endpoints* (`app/routers/`)** | **29** ($\bar{x}=4.14$) | **20** ($\bar{x}=2.86$) | **-31.03%** |
| **$\sum CC$ en los 4 *endpoints* con variación** (`crear_cliente` **-57.1%**, `obtener_cliente` **-50.0%**) | **21** ($\bar{x}=5.25$) | **12** ($\bar{x}=3.00$) | **-42.86%** |
| **$\sum SLOC_{def}$ en controladores** *(corregido `31` $\to$ `24` por auditoría AST)* | **24 líneas** | **0 líneas** | **-100.0%** |
| **$\sum Q_{prev}$ previas a mutación** *(elimina bucle $O(N)$ en `crear_pedido`)* | **6 ($+O(N)$)** | **0 consultas** | **-100.0%** |
| **Distribución de Rango Radon** | 2 en Rango B, 5 en Rango A | **7/7 (100%) en Rango A** | **Cero Rango B** |

**Dictamen sobre $H_3$:** **Parcialmente Confirmada** — erradicación del `100%` en $SLOC_{def}$ y $Q_{prev}$ con picos de `-57.1%` en $CC$, mientras rutas mixtas conservan respuestas HTTP legítimas (`404`/`409`/`422`). Ver detalles en [`metrics_quality/docs/Resultados_Calidad_Backend.md`](metrics_quality/docs/Resultados_Calidad_Backend.md).

---

## 3. Reproducción Rápida

```bash
# 1. Calibración sobre ejemplo controlado síncrono
python metrics_quality/measure_quality.py metrics_quality/test_sample_backend.py

# 2. Auditoría comparativa real sobre el benchmark FastAPI
python metrics_quality/measure_quality.py \
  backend_defensive/app/routers \
  --compare backend_normalized/app/routers \
  --json metrics_quality/results/metricas_m2_audit.json \
  --md metrics_quality/results/tabla_m2_audit.md

# 3. Verificación global del paquete app/ con Radon (opcional)
pip install -r metrics_quality/requirements.txt
python tools/measure_defensive.py
```

---

## 4. Estructura Específica Añadida en la Rama

```text
├── README.md                                          # Documentación específica de esta rama
└── metrics_quality/
    ├── measure_quality.py                             # Analizador AST determinista (CC, SLOC_def, Q_prev, Δ%)
    ├── test_sample_backend.py                         # Módulo de calibración síncrona
    ├── requirements.txt                               # radon, black, pytest
    ├── docs/
    │   ├── Marco_Metrico_y_Formalizacion.md           # Fórmulas matemáticas e ISO/IEC 25010
    │   └── Resultados_Calidad_Backend.md              # Tablas verificadas, auditoría y dictamen H3
    └── results/
        ├── metrics_test_result.json / metrics_test_table.md
        └── metricas_m2_audit.json / tabla_m2_audit.md
>>>>>>> metricas-calidad-backend
```
