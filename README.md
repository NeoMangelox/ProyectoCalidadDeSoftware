# Métricas Estructurales de Calidad Backend e ISO/IEC 25010 (`metricas-calidad-backend`)

> **Alcance de la Rama:** Formalización matemática e instrumentación estática determinista sobre AST de Python 3.12 (`metrics_quality/measure_quality.py`) para cuantificar el impacto de la normalización PostgreSQL en la Complejidad Ciclomática ($CC$), Código Defensivo ($SLOC_{def}$) y Consultas Previas ($Q_{prev}$), respondiendo $RQ_3$ y contrastando $H_3$.

---

## 1. Propósito Metodológico

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
```
