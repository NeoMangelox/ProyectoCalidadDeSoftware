# 05 — Métricas Estructurales de Calidad Backend e ISO/IEC 25010

> **Rama Estandarizada Asociada:** `metricas-calidad-backend`.  
> **Propósito:** Formalizar e instrumentar deterministamente la medición del impacto de la normalización relacional sobre el código *backend* ($RQ_3$ / $H_3$), evaluando Complejidad Ciclomática de McCabe ($CC$), líneas lógicas defensivas ($SLOC_{def}$) y consultas existenciales previas ($Q_{prev}$).

---

## 1. Marco Formal e Instrumentación AST

* [`docs/Marco_Metrico_y_Formalizacion.md`](docs/Marco_Metrico_y_Formalizacion.md): Definición matemática de $CC = E - N + 2P = 1 + \sum \pi_i$, $SLOC_{def}$, $Q_{prev}$, deltas $\Delta\%$, mapeo ontológico con **ISO/IEC 25010** (*Mantenibilidad* y *Fiabilidad* frente a TOCTOU) y control de amenazas a la validez.
* [`measure_quality.py`](measure_quality.py): Analizador estático determinista construido sobre el módulo `ast` de Python `3.12`. Evalúa exclusivamente rangos exactos `[start_line, end_line]` de nodos `FunctionDef` / `AsyncFunctionDef`, clasificando $CC$ en la escala estándar de `radon`.
* [`test_sample_backend.py`](test_sample_backend.py): Módulo sintético de calibración síncrono/asíncrono.
* [`results/`](results/): Salidas JSON y tablas Markdown exportadas automáticamente ([`metricas_m2_audit.json`](results/metricas_m2_audit.json), [`tabla_m2_audit.md`](results/tabla_m2_audit.md)).

---

## 2. Resultados Verificados en el Benchmark Dual (`7` Endpoints)

| Indicador Global (`backend_defensive` $\to$ `backend_normalized`) | Inicial | Final | Diferencial ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **$\sum CC$ en los 7 *endpoints* (`app/routers/`)** | **29** ($\bar{x}=4.14$) | **20** ($\bar{x}=2.86$) | **-31.03%** |
| **$\sum CC$ en los 4 *endpoints* con variación** (`crear_cliente` **-57.1%**, `obtener_cliente` **-50.0%**) | **21** ($\bar{x}=5.25$) | **12** ($\bar{x}=3.00$) | **-42.86%** |
| **$CC$ global en todo el paquete `app/` (`radon`)** | **45** (`SLOC=170`) | **35** (`SLOC=162`) | **-22.2%** |
| **$\sum SLOC_{def}$ en routers** *(corregido `31` $\to$ `24` por auditoría AST)* | **24 líneas** (`26.1%`) | **0 líneas** | **-100.0%** |
| **$\sum Q_{prev}$ previas a mutación** *(suprime bucle $O(N)$ en `crear_pedido`)* | **6 ($+O(N)$)** | **0 consultas** | **-100.0%** |
| **Distribución de Riesgo Radon** | 2 en Rango B, 5 en Rango A | **7/7 (100%) en Rango A ($CC \le 4$)** | **Cero picos Rango B** |

**Dictamen sobre $H_3$:** **Parcialmente Confirmada.** Se erradicaron al `100%` $SLOC_{def}$ y $Q_{prev}$, superando el umbral de `50%` en rutas de clientes (`-57.1%` / `-50.0%`), mientras las rutas transaccionales mixtas conservaron bifurcaciones HTTP legítimas (`404`/`409`/`422`). Ver desglose completo en [`docs/Resultados_Calidad_Backend.md`](docs/Resultados_Calidad_Backend.md).

---

## 3. Reproducción

```bash
# 1. Calibración sobre el módulo sintético de prueba
python 05_metricas_calidad_backend/measure_quality.py 05_metricas_calidad_backend/test_sample_backend.py

# 2. Auditoría comparativa sobre los routers equivalentes del Módulo 02
python 05_metricas_calidad_backend/measure_quality.py \
  02_benchmark_sql_backend/backend_defensive/app/routers \
  --compare 02_benchmark_sql_backend/backend_normalized/app/routers \
  --json 05_metricas_calidad_backend/results/metricas_m2_audit.json \
  --md 05_metricas_calidad_backend/results/tabla_m2_audit.md

# 3. Verificación opcional con radon y black
python -m pip install -r 05_metricas_calidad_backend/requirements.txt
```
