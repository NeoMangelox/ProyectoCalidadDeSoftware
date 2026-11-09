# Auditoría y Optimización de Esquemas PostgreSQL mediante LLMs para el Aseguramiento de la Calidad del Backend

> **Título en inglés:** *LLM-Driven Audit and Optimization of PostgreSQL Schemas for Backend Quality Assurance*  
> **Asignatura:** Calidad de Software (Ciclo 6) — Evaluación $N_2$  
> **Docente Asesor:** Mg. Gustavo Arredondo Castillo  
> **RDBMS Único:** PostgreSQL 16/17 (entorno reproducible en Docker)

---

## 1. Resumen Ejecutivo e Hipótesis Verificadas

Este repositorio consolida la infraestructura experimental, los artefactos de auditoría y los manuscritos científicos del proyecto orientado a demostrar la cadena causal completa entre **defectos relacionales en esquemas PostgreSQL** (1FN–3FN y claves foráneas ausentes) y la **deuda técnica trasladada al código backend** (programación defensiva, consultas redundantes y vulnerabilidades de concurrencia TOCTOU).

| Nivel Experimental | Instrumentación | Hallazgo Principal Medido | Dictamen Hipótesis |
| :--- | :--- | :--- | :---: |
| **Nivel 1 — Control AST** ($RQ_1$) | SQLFluff `4.5.0` (`postgres`, 79 reglas) + SonarQube `26.10` (`sonar-sql-plugin 1.4.0`) + controles positivos | `322` alertas cosméticas y `3` avisos de cabecera; **`0 / 28` detecciones relacionales (`100%` FN)** y `100%` *Quality Gates* aprobados. | **$H_1$ Confirmada** |
| **Nivel 2 vs. Nivel 3 — LLMs y Agente MCP** ($RQ_2$) | Zero-Shot (`EXP-01,04,07`) vs. CoT Estático (`EXP-02,05,08`) vs. Agente MCP + Skill + Dry-Run `BEGIN...ROLLBACK` (`EXP-03,06,09`), *Greedy Decoding* (`T=0, seed=42`) | Zero-Shot tuvo `43.75%` alucinación FK y `0%` compilación; CoT estático logró `100%` $F_1$ teórico pero `0%` compilación (`23503` por huérfanos); **Agente MCP alcanzó `100%` $F_1$, `0%` alucinación y `100%` compilación en `1.67` iteraciones**. | **$H_2$ Confirmada** |
| **Impacto Backend — AST & ISO/IEC 25010** ($RQ_3$) | `measure_quality.py` + `radon` sobre 7 rutas equivalentes FastAPI (`10` tests `pytest` compartidos) | **`-100%` de $SLOC_{def}$ (`24 -> 0`)**, **`-100%` de $Q_{prev}$ (`6 -> 0`, incluyendo bucle $O(N)$)**, **`-31.03%` $CC$ global en routers** (`-42.86%` en afectadas; picos de **`-57.1%`**) y **`7/7` en Rango A**. | **$H_3$ Parcialmente Confirmada** |

---

## 2. Arquitectura Modular del Repositorio (`main`)

La rama principal (`main`) integra de forma ordenada todas las capas del proyecto (incluido el módulo de Estado del Arte & SLR, que reside directamente en `main` sin rama exclusiva):

```text
ProyectoCalidadDeSoftware/
├── 01_estado_del_arte_slr/       # Revisión Sistemática (SLR), ecuación booleana, 17 citas y referencias.bib
├── 02_benchmark_sql_backend/     # Corpus PG 16 (Pagila 15->16, Northwind 14->15, Sintético 5->7), 28 defectos y Backend Dual FastAPI
├── 03_linters_ast_baseline/      # Auditoría Nivel 1: SQLFluff 4.5.0, SonarQube 26.10, controles positivos y matriz de 28 filas
├── 04_agente_mcp_normalizacion/  # Auditoría Nivel 2 vs 3: MCP server-postgres, SKILL.md, Dry-Run validator y EXP-01..EXP-09
├── 05_metricas_calidad_backend/  # Análisis estático AST Python/Radon (CC, SLOC_def, Q_prev, Δ%) e ISO/IEC 25010
├── 06_documentacion_paper/       # Borrador consolidado del Paper IEEE/ACM, Definición del Problema y Resultados Integrales
├── .sqlfluff                     # Configuración global SQLFluff (--dialect postgres, templater raw)
├── docker-compose.yml            # PostgreSQL 16 con carga automática de las 6 bases de datos del benchmark
└── sonar-project.properties      # Configuración SonarScanner hacia los 3 esquemas defectuosos
```

| Carpeta | Contenido y Propósito | Documentación Específica |
| :--- | :--- | :--- |
| [`01_estado_del_arte_slr/`](01_estado_del_arte_slr/README.md) | Protocolo SLR, matriz de literatura hasta 2026 (DNBench/MARS, NormaScore, SQLFlex, SQLMentor), brechas y `.bib`. | [README Módulo 01](01_estado_del_arte_slr/README.md) |
| [`02_benchmark_sql_backend/`](02_benchmark_sql_backend/README.md) | DDLs defectuosos y *Ground Truth*, semillas con anomalías deliberadas, `defects_manifest.json`, backends FastAPI duales y 10 tests `pytest`. | [README Módulo 02](02_benchmark_sql_backend/README.md) |
| [`03_linters_ast_baseline/`](03_linters_ast_baseline/README.md) | Evidencia empírica del Nivel 1, huellas SHA-256, resultados crudos JSON/logs y matriz de detección de 28 filas. | [README Módulo 03](03_linters_ast_baseline/README.md) |
| [`04_agente_mcp_normalizacion/`](04_agente_mcp_normalizacion/README.md) | Configuración de inferencia determinista, `SKILL.md` (5 etapas), introspección MCP, arnés *Dry-Run* y 9 scripts DDL (`EXP-01`..`09`). | [README Módulo 04](04_agente_mcp_normalizacion/README.md) |
| [`05_metricas_calidad_backend/`](05_metricas_calidad_backend/README.md) | Instrumento AST `measure_quality.py`, calibración sintética, formalización ISO/IEC 25010 y matriz verificada de los 7 endpoints. | [README Módulo 05](05_metricas_calidad_backend/README.md) |
| [`06_documentacion_paper/`](06_documentacion_paper/README.md) | Planteamiento formal, análisis integral tripartito, borrador completo IEEE/ACM IMRyD y entregable parcial hasta metodología. | [README Módulo 06](06_documentacion_paper/README.md) |

---

## 3. Arquitectura Estandarizada de Ramas y Respaldos Reversibles

Para profesionalizar el flujo de trabajo colaborativo en Git, cada componente técnico cuenta con una rama funcional estandarizada y su `README.md` dedicado, mientras **`main`** centraliza la integración final y la parte de SLR / Estado del Arte:

| Rama en GitHub | Rol Funcional / Módulo | Origen Conservado | Enlace de Contenido en `main` |
| :--- | :--- | :--- | :--- |
| **`main`** | Integración completa del paper + Estado del Arte (SLR) | Evolución consolidada de `main` | [`01_` a `06_`](06_documentacion_paper/README.md) |
| **`benchmark-sql-backend`** | Dataset PostgreSQL 16 (3 casos, 28 defectos), FastAPI dual y `pytest` | Histórico original de `main` | [`02_benchmark_sql_backend/`](02_benchmark_sql_backend/README.md) |
| **`linters-ast-baseline`** | Línea base AST tradicional (SQLFluff 4.5.0 + SonarQube 26.10) | Estandarización de `miembro3/trabajo` | [`03_linters_ast_baseline/`](03_linters_ast_baseline/README.md) |
| **`agente-mcp-normalizacion`** | Agente autónomo MCP + `SKILL.md` + *Dry-Run* (`EXP-01`..`09`) | Estandarización de `rama-de-sofia` | [`04_agente_mcp_normalizacion/`](04_agente_mcp_normalizacion/README.md) |
| **`metricas-calidad-backend`** | Instrumento AST Python/Radon, ISO/IEC 25010 y resultados $\Delta\%$ | Nueva rama del bloque de métricas | [`05_metricas_calidad_backend/`](05_metricas_calidad_backend/README.md) |

### Etiquetas Inmutables de Respaldo (*Rollback* Garantizado)
Antes de estandarizar las ramas y reorganizar `main`, se publicaron tres etiquetas inmutables sobre los *commits* originales exactos:
* `backup/pre-reorg-main` — estado original intacto previo a los *merges*.
* `backup/pre-reorg-miembro3-trabajo` — estado original de `miembro3/trabajo`.
* `backup/pre-reorg-rama-de-sofia` — estado original de `rama-de-sofia`.

Para inspeccionar o revertir hacia cualquiera de los estados previos a la reorganización:
```bash
git fetch --tags
git checkout backup/pre-reorg-main
```

---

## 4. Guía Rápida de Reproducción

### A. Levantar PostgreSQL 16 y verificar el Benchmark (Módulo 02)
```bash
docker compose up -d
cd 02_benchmark_sql_backend
python -m pip install -r backend_defensive/requirements.txt
BACKEND_DIR=backend_defensive pytest tests -v
BACKEND_DIR=backend_normalized pytest tests -v
```

### B. Verificar Línea Base de Linters AST (Módulo 03)
```powershell
# Verificar integridad SHA-256 desde el directorio del benchmark
cd 02_benchmark_sql_backend
Get-Content ..\03_linters_ast_baseline\inputs.sha256.txt | ForEach-Object {
  $p, $h = $_ -split '\s+'
  "$( (Get-FileHash $p -Algorithm SHA256).Hash -eq $h ) $p"
}
cd ..

# Ejecutar SQLFluff desde la raíz (usa .sqlfluff global)
python -m pip install -r 03_linters_ast_baseline/requirements.txt
sqlfluff lint 02_benchmark_sql_backend/case1_pagila/schema_defective.sql --format json
```

### C. Ejecutar Validación *Dry-Run* del Agente MCP (Módulo 04)
```bash
python 04_agente_mcp_normalizacion/tools/dry_run_validator.py \
  --db pagila_defective \
  --file 04_agente_mcp_normalizacion/resultados_experimentos/case1_pagila/exp03_ddl_agent_optimized.sql

python 04_agente_mcp_normalizacion/tools/run_benchmark_suite.py
```

### D. Reproducir Métricas AST de Calidad Backend (Módulo 05)
```bash
python 05_metricas_calidad_backend/measure_quality.py \
  02_benchmark_sql_backend/backend_defensive/app/routers \
  --compare 02_benchmark_sql_backend/backend_normalized/app/routers
```
