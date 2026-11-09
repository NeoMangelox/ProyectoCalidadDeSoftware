# 06 — Documentación Científica Consolidada y Borrador del Paper

> **Propósito:** Reunir los documentos rectores de formulación del problema, discusión empírica consolidada (*Control AST* + *Agente MCP* + *Métricas Backend*) y el manuscrito científico en estructura IMRyD listo para maquetación IEEE / ACM.

---

## Inventario de Documentos

| Documento | Alcance y Contenido | Trazabilidad con Módulos |
| :--- | :--- | :--- |
| [`Borrador_Paper_Cientifico.md`](Borrador_Paper_Cientifico.md) | Manuscrito completo IMRyD (*Abstract/Resumen*, *Introduction*, *Related Work*, *Experimental Methodology*, *Results & Discussion*, *Threats to Validity*, *Conclusion* y **17 referencias verificadas**). | Integra Módulos [`01`](../01_estado_del_arte_slr/README.md)–[`05`](../05_metricas_calidad_backend/README.md) |
| [`Entregable_Parcial_Metodologia.md`](Entregable_Parcial_Metodologia.md) | Versión ejecutiva acotada hasta **Sección III (Metodología)** con tablas esenciales e historial bibliográfico completo (`[1]`–`[20]`). | Basado en Módulos [`01`](../01_estado_del_arte_slr/README.md) y [`02`](../02_benchmark_sql_backend/README.md)–[`05`](../05_metricas_calidad_backend/README.md) |
| [`Definicion_Problema_y_Objetivos.md`](Definicion_Problema_y_Objetivos.md) | Planteamiento formal, preguntas $RQ_1$–$RQ_3$, hipótesis $H_1$–$H_3$, objetivos ($OG$, $OE_1$–$OE_5$) y *Quality Gates* de coordinación. | Marco rector de todo el proyecto |
| [`Analisis_Integral_Resultados.md`](Analisis_Integral_Resultados.md) | Triangulación cuantitativa de Nivel 1 ([`03_`](../03_linters_ast_baseline/README.md)), Nivel 2–3 ([`04_`](../04_agente_mcp_normalizacion/README.md)) e impacto backend ([`05_`](../05_metricas_calidad_backend/README.md)), incluyendo amenazas a la validez. | Evidencia empírica verificada |

---

## Flujo de Trazabilidad (*Quality Gates* del Proyecto)

1. **Gate 1 (SLR & Gap):** 17 referencias canónicas en [`../01_estado_del_arte_slr/`](../01_estado_del_arte_slr/README.md) sustentan el vacío **DDL-to-DDL $\leftrightarrow$ Calidad Backend**.
2. **Gate 2 (Corpus PG 16):** 3 esquemas + 28 defectos + dual FastAPI (`10/10` tests `pytest`) en [`../02_benchmark_sql_backend/`](../02_benchmark_sql_backend/README.md).
3. **Gate 3 (Línea Base AST):** `0 / 28 TP` (`100% FN`) con SHA-256 y controles positivos en [`../03_linters_ast_baseline/`](../03_linters_ast_baseline/README.md).
4. **Gate 4 (Agente MCP + Dry-Run):** `100%` $F_1$ y compilación con `0%` alucinación en [`../04_agente_mcp_normalizacion/`](../04_agente_mcp_normalizacion/README.md).
5. **Gate 5 (Métricas ISO/IEC 25010):** `24 -> 0` $SLOC_{def}$, `6 -> 0` $Q_{prev}$ y hasta `-57.1%` $CC$ en [`../05_metricas_calidad_backend/`](../05_metricas_calidad_backend/README.md).
