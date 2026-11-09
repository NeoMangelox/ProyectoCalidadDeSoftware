# Resultados Empíricos de Calidad Backend ($\Delta CC$, $\Delta SLOC_{def}$, $\Delta Q_{prev}$)

> **Instrumento:** [`measure_quality.py`](../measure_quality.py) sobre `backend_defensive/app/routers` vs. `backend_normalized/app/routers` (equivalencia certificada mediante 10 pruebas de contrato en `pytest`).  
> **Artefactos JSON/MD:** [`metricas_m2_audit.json`](../results/metricas_m2_audit.json) · [`tabla_m2_audit.md`](../results/tabla_m2_audit.md)

---

## 1. Matriz de Resultados por Endpoint (7 Rutas Evaluadas)

| Caso | Endpoint / Función | Defectos Compensados | $CC_{\text{def}}$ (Rango) | $CC_{\text{norm}}$ (Rango) | $\Delta CC$ (%) | $SLOC_{def}$ (Def $\to$ Norm) | $\Delta SLOC_{def}$ (%) | $Q_{prev}$ | Impacto ISO/IEC 25010 |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Northwind** | `POST /clientes` (`crear_cliente`) | 1FN (`customers.phones` CSV) | **7** (B) | **3** (A) | **-57.1%** | $7 \to 0$ | **-100.0%** | $0 \to 0$ | **Analizabilidad (+)** (Rango B $\to$ A) |
| **Northwind** | `GET /clientes/{id}` (`obtener_cliente`) | 1FN (`re.split` mixto) | **4** (A) | **2** (A) | **-50.0%** | $1 \to 0$ | **-100.0%** | $0 \to 0$ | **Modificabilidad (+)** (Cero parsing) |
| **Pagila** | `PUT /inventario/{id}` (`poner_inventario`) | Keyless (`D4-01/02`) + 3FN (`D3-01`) | **4** (A) | **3** (A) | **-25.0%** | $5 \to 0$ | **-100.0%** | $2 \to 0$ (**-100%**) | **Fiabilidad (ACID)** / Integridad |
| **Pagila** | `GET /inventario/{id}` (`obtener_inventario`) | Ninguno (lectura directa) | **2** (A) | **2** (A) | $0.0\%$ | $0 \to 0$ | — | $0 \to 0$ | Estabilidad mantenida |
| **Pagila** | `DELETE /inventario/{id}` (`borrar_inventario`) | Keyless (`D4-03` en `rental`) | **3** (A) | **3** (A) | $0.0\%$ | $2 \to 0$ | **-100.0%** | $1 \to 0$ (**-100%**) | **Tolerancia a fallos** (Fin TOCTOU) |
| **Northwind** | `POST /pedidos` (`crear_pedido`) | Keyless (`D4-01..04`) + 2FN/3FN | **6** (B) | **4** (A) | **-33.3%** | $9 \to 0$ | **-100.0%** | $3^* \to 0$ (**-100%**) | **Analizabilidad (+)** / Elimina bucle $O(N)$ |
| **Northwind** | `GET /pedidos/{id}` (`obtener_pedido`) | Ninguno (lectura con `JOIN`) | **3** (A) | **3** (A) | $0.0\%$ | $0 \to 0$ | — | $0 \to 0$ | Integridad referencial en lectura |

*\*En `crear_pedido`, la consulta sobre `products` se ejecuta dentro del bucle por ítem (`for it in body.items:`), generando $2 + N$ consultas previas por petición ($O(N)$) en tiempo de ejecución.*

---

## 2. Consolidado Global y Hallazgo de Auditoría AST

| Indicador Global | Backend Defensivo | Backend Normalizado | Reducción ($\Delta$) |
| :--- | :---: | :---: | :---: |
| **$\sum CC$ en los 7 endpoints (`app/routers/`)** | **29** ($\bar{x}=4.14$) | **20** ($\bar{x}=2.86$) | **-31.03%** |
| **$\sum CC$ en los 4 endpoints afectados** | **21** ($\bar{x}=5.25$) | **12** ($\bar{x}=3.00$) | **-42.86%** |
| **$CC$ global del paquete `app/` (vía `radon`)** | **45** ($SLOC=170$) | **35** ($SLOC=162$) | **-22.2%** |
| **$\sum SLOC_{def}$ en routers** | **24 líneas** ($26.1\%$ de 92) | **0 líneas** | **-100.0%** |
| **$\sum Q_{prev}$ previas a mutación** | **6 estáticas ($+O(N)$ bucle)** | **0 consultas** | **-100.0%** |
| **Distribución Radon** | 2 en Rango B, 5 en Rango A | **7/7 (100%) en Rango A ($CC \le 4$)** | **Cero Rango B** |

> **Corrección de Auditoría (`31` $\to$ `24` líneas):** El conteo preliminar por línea en `tools/measure_defensive.py` sobrecontó `7` líneas de importaciones porque la línea 2 del *docstring* de `clientes.py` mencionaba simultáneamente `"DEFENSIVE-BEGIN"` y `"DEFENSIVE-END"`. El análisis AST por rango de función de `measure_quality.py` fijó el valor exacto en **24 líneas ejecutables**.

---

## 3. Dictamen sobre la Hipótesis $H_3$

**$H_3$: PARCIALMENTE CONFIRMADA.** Se cumplió al **100%** la erradicación de deuda defensiva ($SLOC_{def} \to 0$, $Q_{prev} \to 0$) y las rutas de clientes superaron la meta del $50\%$ en $CC$ (`-57.1%` y `-50.0%`), pero las rutas transaccionales mixtas conservaron bifurcaciones HTTP legítimas (`404`/`409`/`422`), situando la reducción agregada de los endpoints afectados en **`-42.86%`** (`-31.03%` global en routers).
