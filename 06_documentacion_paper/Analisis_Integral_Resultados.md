# 📊 Análisis Integral de Resultados y Discusión Empírica

> **Integración Tripartita (M3 + M4 + M5 sobre Corpus M2)**  
> **Compilador / Árbitro Técnico:** Miembro 5 (Coordinador General)  
> **Destino en el Paper:** Sección IV (*Results and Discussion*) y Sección V (*Threats to Validity*)

---

## 1. Nivel 1: Evaluación de Linters Estáticos AST — Grupo de Control ($RQ_1$)

Los tres archivos `schema_defective.sql` (28 defectos totales certificados por SHA-256 en [`inputs.sha256.txt`](../03_linters_ast_baseline/inputs.sha256.txt)) fueron sometidos a **SQLFluff 4.5.0** (`--dialect postgres`, 79 reglas activas) y **SonarQube Community Build 26.10** (`sonar-sql-plugin 1.4.0`, dialecto `pssqlv2`).

### 1.1. Matriz Empírica de Detección en Herramientas AST

| Caso de Estudio | Defectos Inyectados | SQLFluff (Alertas de Estilo) | SQLFluff (Errores AST / PRS) | SQLFluff ($TP / FN$ Relacionales) | SonarQube (Incidencias) | SonarQube ($TP / FN$ Relacionales) | Estado Quality Gate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pagila** (`case1_pagila`) | 10 | 189 (`CP03, CP05, LT01, LT02, RF04`) | 0 | **0 / 10** ($100\%$ FN) | 1 (`SQLCC:C030`) | **0 / 10** ($100\%$ FN) | **PASSED** |
| **Northwind-PG** (`case2_northwind`) | 10 | 96 (`LT01, RF04`) | 0 | **0 / 10** ($100\%$ FN) | 1 (`SQLCC:C030`) | **0 / 10** ($100\%$ FN) | **PASSED** |
| **Sintético** (`case3_synthetic`) | 8 | 37 (`LT01, LT02`) | 0 | **0 / 8** ($100\%$ FN) | 1 (`SQLCC:C030`) | **0 / 8** ($100\%$ FN) | **PASSED** |
| **Total Consolidado** | **28** | **322 avisos cosméticos** | **0** | **0 / 28 ($100\%$ FN)** | **3 cabeceras** | **0 / 28 ($100\%$ FN)** | **100% Aprobados** |

### 1.2. Validación mediante Controles Positivos e Implicación Teórica
* **Controles Positivos:** Para descartar fallos de configuración, se analizaron externamente [`control_style.sql`](../03_linters_ast_baseline/sqlfluff/control_style.sql) (disparó `LT01` en SQLFluff) y [`header_control.sql`](../03_linters_ast_baseline/sonarqube/header_control.sql) (disparó `SQLCC:C030` en SonarQube).
* **Análisis de Causa Raíz:** Aunque SQLFluff reportó reglas de espaciado (`LT01`) o capitalización (`CP05`) en líneas donde coincidían comentarios de defectos, el análisis línea por línea en [`matriz_deteccion.csv`](../03_linters_ast_baseline/matriz_deteccion.csv) confirma que **ninguna regla diagnosticó violaciones de 1FN, 2FN, 3FN o ausencia de FKs**. La precisión relacional es indefinida ($TP=0, FP=0$) y la tasa de falsos negativos alcanza el **$100\%$**, confirmando plenamente la hipótesis **$H_1$**: un Árbol de Sintaxis Abstracta verifica gramática BNF de PostgreSQL, no dependencias funcionales ni integridad referencial omitida.

---

## 2. Nivel 2 vs Nivel 3: Prompts Crudos vs Agente Autónomo MCP ($RQ_2$)

A partir de los 9 scripts DDL validados transaccionalmente en Docker PostgreSQL 16 mediante [`dry_run_validator.py`](../04_agente_mcp_normalizacion/tools/dry_run_validator.py) y documentados en [`resultados_experimentos_ia.md`](../04_agente_mcp_normalizacion/docs/resultados_experimentos_ia.md):

### 2.1. Resultados por Experimento (EXP-01 al EXP-09)

| ID Exp | Caso | Condición Metodológica | $TP$ | $FP$ | $FN$ | Precision | Recall | $F_1$ | FKs Alucinadas | Compila DDL | Código PG | Intentos |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **EXP-01** | Pagila | Nivel 2: Crudo (Zero-Shot) | 4 | 2 | 6 | 66.67% | 40.00% | 50.00% | 3 / 6 (50.0%) | **No** | `42830` | 1 |
| **EXP-02** | Pagila | Nivel 2: CoT Estático | 10 | 0 | 0 | 100.0% | 100.0% | 100.0% | 0 / 5 (0.0%) | **No** | `23503` | 1 |
| **EXP-03** | Pagila | Nivel 3: Agente MCP + Dry-Run | 10 | 0 | 0 | 100.0% | 100.0% | 100.0% | **0 / 5 (0.0%)** | **Sí** | *Ninguno* | 2 |
| **EXP-04** | Northwind | Nivel 2: Crudo (Zero-Shot) | 5 | 2 | 5 | 71.43% | 50.00% | 58.82% | 2 / 5 (40.0%) | **No** | `42703` | 1 |
| **EXP-05** | Northwind | Nivel 2: CoT Estático | 10 | 0 | 0 | 100.0% | 100.0% | 100.0% | 0 / 6 (0.0%) | **No** | `23503` | 1 |
| **EXP-06** | Northwind | Nivel 3: Agente MCP + Dry-Run | 10 | 0 | 0 | 100.0% | 100.0% | 100.0% | **0 / 6 (0.0%)** | **Sí** | *Ninguno* | 2 |
| **EXP-07** | Sintético | Nivel 2: Crudo (Zero-Shot) | 4 | 2 | 4 | 66.67% | 50.00% | 57.14% | 2 / 5 (40.0%) | **No** | `42830` | 1 |
| **EXP-08** | Sintético | Nivel 2: CoT Estático | 8 | 0 | 0 | 100.0% | 100.0% | 100.0% | 0 / 5 (0.0%) | **No** | `23503` | 1 |
| **EXP-09** | Sintético | Nivel 3: Agente MCP + Dry-Run | 8 | 0 | 0 | 100.0% | 100.0% | 100.0% | **0 / 5 (0.0%)** | **Sí** | *Ninguno* | 1 |

### 2.2. Consolidado Comparativo Nivel 2 vs Nivel 3

| Condición Metodológica | $\Sigma TP$ | $\Sigma FP$ | $\Sigma FN$ | Precision Global | Recall Global | $F_1$-Score Global | Tasa Compilación DDL | Tasa Alucinación FK | Iteraciones Promedio |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Nivel 2A: LLM Crudo (Zero-Shot)** | 13 | 6 | 15 | 68.42% | 46.43% | 55.32% | **0.0% (0/3)** | **43.75% (7/16)** | 1.00 |
| **Nivel 2B: LLM CoT sin MCP** | 28 | 0 | 0 | 100.0% | 100.0% | 100.0% | **0.0% (0/3)** | **0.00% (0/16)** | 1.00 |
| **Nivel 3: Agente MCP + Dry-Run** | **28** | **0** | **0** | **100.0%** | **100.0%** | **100.0%** | **100.0% (3/3)** | **0.00% (0/16)** | **1.67** |

### 2.3. Discusión de Hallazgos Clave
1. **Patología de Alucinación en Zero-Shot:** Los modelos sin introspección inventaron entidades (`ratings` en Pagila, `countries` en Northwind, `ciudades` en Sintético) y claves primarias inexistentes (`customers(id)`, `pedidos(id)`), disparando los códigos PostgreSQL `42830` (*invalid_foreign_key*) y `42703` (*undefined_column*), con una tasa de alucinación del **$43.75\%$** que valida $H_2$.
2. **La Paradoja del Chain-of-Thought sin Herramientas:** El CoT estático logró $100\%$ de diagnóstico conceptual en papel ($F_1 = 100\%$), pero fracasó en el **$100\%$ de ejecuciones en PostgreSQL (`23503: foreign_key_violation`)**. Al no poder consultar las filas reales mediante MCP, no detectó la presencia de tuplas huérfanas (`inventory.film_id = 999`, `orders.customer_id = 'ZZZZZ'`, `envios.pedido_id = 999`) ni pobló previamente tablas catálogo (`codigos_postales`), haciendo inaplicable el DDL en producción.
3. **Resolución mediante Bucle Cerrado en Nivel 3:** El Agente equipado con MCP y la Skill `postgres-schema-auditor` comprobó empíricamente las violaciones 1FN mediante `SELECT ... LIMIT 5` (Fase 2), capturó las excepciones `23503` durante la primera iteración del Dry-Run (`BEGIN...ROLLBACK`), inyectó saneamiento transaccional previo y alcanzó **$100.0\%$ de DDL ejecutable con $0.0\%$ de alucinaciones** en un promedio de **1.67 iteraciones**.

---

## 3. Impacto Cuantitativo en el Backend e ISO/IEC 25010 ($RQ_3$ — M5)

Ejecutando el analizador estático [`measure_quality.py`](../05_metricas_calidad_backend/measure_quality.py) sobre los 7 endpoints equivalentes de [`backend_defensive/app/routers/`](../02_benchmark_sql_backend/backend_defensive/app/routers) y [`backend_normalized/app/routers/`](../02_benchmark_sql_backend/backend_normalized/app/routers) (certificados mediante 10 pruebas funcionales de contrato en `pytest`):

### 3.1. Matriz Empírica de Calidad Backend por Endpoint

| Endpoint / Función (`app/routers/`) | Defectos Compensados | $CC_{\text{def}}$ (Rango) | $CC_{\text{norm}}$ (Rango) | $\Delta CC$ (%) | $SLOC_{def}$ (Inicial $\to$ Final) | $\Delta SLOC_{def}$ (%) | $Q_{prev}$ (Def $\to$ Norm) | Subcaracterísticas ISO/IEC 25010 Mejoradas |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `crear_cliente` (`POST /clientes`) | 1FN (`customers.phones` CSV) | **7** (B) | **3** (A) | **$-57.1\%$** | $7 \to 0$ | **$-100.0\%$** | $0 \to 0$ | **Analizabilidad (+)** / Transición Rango B $\to$ A |
| `obtener_cliente` (`GET /clientes/{id}`) | 1FN (`split` con separadores mixtos) | **4** (A) | **2** (A) | **$-50.0\%$** | $1 \to 0$ | **$-100.0\%$** | $0 \to 0$ | **Modificabilidad (+)** / Cero parsing manual |
| `poner_inventario` (`PUT /inventario/{id}`) | Keyless (`D4-01/02`) + 3FN (`D3-01`) | **4** (A) | **3** (A) | **$-25.0\%$** | $5 \to 0$ | **$-100.0\%$** | $2 \to 0$ (**$-100\%$**) | **Fiabilidad (ACID)** / **Integridad (+)** |
| `borrar_inventario` (`DELETE /inventario/{id}`) | Keyless (`D4-03` `rental.inventory_id`) | **3** (A) | **3** (A) | $0.0\%$ | $2 \to 0$ | **$-100.0\%$** | $1 \to 0$ (**$-100\%$**) | **Tolerancia a fallos** / Mitigación TOCTOU |
| `crear_pedido` (`POST /pedidos`) | Keyless (`D4-01..04`) + 2FN/3FN | **6** (B) | **4** (A) | **$-33.3\%$** | $9 \to 0$ | **$-100.0\%$** | $3^*$ $\to 0$ (**$-100\%$**) | **Analizabilidad (+)** / Elimina consulta $O(N)$ en bucle |
| `obtener_inventario` (`GET /inventario/{id}`) | Ninguno (solo lectura directa) | **2** (A) | **2** (A) | $0.0\%$ | $0 \to 0$ | $0.0\%$ | $0 \to 0$ | Estabilidad mantenida |
| `obtener_pedido` (`GET /pedidos/{id}`) | Ninguno (lectura con JOINs en norm) | **3** (A) | **3** (A) | $0.0\%$ | $0 \to 0$ | $0.0\%$ | $0 \to 0$ | Integridad referencial en lectura |
| **Total Endpoints (`app/routers/`)** | **12 defectos ejercitados** | **29** | **20** | **$-31.03\%$** | **$24 \to 0$** | **$-100.0\%$** | **$6^* \to 0$** | **100% Endpoints en Rango A ($CC \le 4$)** |
| **Subconjunto Afectado en $CC$ (4 endpoints)** | **Endpoints con $\Delta CC > 0$** | **21** ($\bar{x}=5.25$) | **12** ($\bar{x}=3.00$) | **$-42.86\%$** | **$22 \to 0$** | **$-100.0\%$** | **$5^* \to 0$** | **Reducción sustancial de picos de riesgo** |

*\*Nota sobre $Q_{prev}$ en `crear_pedido`: En código existen 3 consultas de verificación (`customers`, `shippers` y `products`), pero la consulta sobre `products` se ejecuta dentro del bucle `for it in body.items:`, generando una sobrecarga de $2 + N$ consultas adicionales en tiempo de ejecución ($O(N)$ round-trips por pedido) que desaparece por completo en `backend_normalized`.*

### 3.2. Consolidado Global del Paquete Backend (`app/` completo)
- **Reducción en Código de Endpoints (`app/routers/`):** Las **24 líneas lógicas de código defensivo** ($SLOC_{def}$) representaban el **$26.1\%$** de las 92 líneas totales de los controladores web en `backend_defensive` y fueron erradicadas al **$100.0\%$** ($24 \to 0$).
- **Reducción Global de Complejidad (`app/` incluyendo DTOs y pooling):** De acuerdo con `radon`, el total de $CC$ en todo el microservicio cayó de **45 a 35 ($\Delta CC = -22.2\%$)**. *(Nota de auditoría del Coordinador: El script preliminar `measure_defensive.py` reportó originalmente 31 líneas de $SLOC_{def}$ porque el comentario de cabecera de `clientes.py` contenía simultáneamente las cadenas `"DEFENSIVE-BEGIN"` y `"DEFENSIVE-END"`, activando un falso positivo sobre 7 líneas de `import`; el conteo exacto AST verificado por `measure_quality.py` es estrictamente de 24 líneas ejecutables).*
- **Erradicación de Condiciones de Carrera (TOCTOU):** El código defensivo realiza una comprobación en dos fases (*check-then-insert* o *check-then-delete* en `poner_inventario`, `borrar_inventario`, `crear_pedido`), dejando una ventana de concurrencia vulnerable ante peticiones simultáneas. Delegar la verificación en restricciones declarativas (`FOREIGN KEY`, `UNIQUE`) de PostgreSQL resuelve la atomicidad en el motor ACID sin sobrecarga lógica ni *locks* en la aplicación.

---

## 4. Verificación Global de Hipótesis y Amenazas a la Validez

| Hipótesis | Predicción Original | Resultado Empírico Medido | Dictamen |
| :---: | :--- | :--- | :---: |
| **$H_1$** | Linters AST arrojan $100\%$ de falsos negativos ante defectos relacionales. | SQLFluff y SonarQube obtuvieron $0/28$ detecciones relacionales ($FN = 100\%$). | **CONFIRMADA** |
| **$H_2$** | Agente MCP + Dry-Run logra $>90\%$ precisión, $0\%$ alucinaciones y $0\%$ DDL inválido vs ~40% fallo crudo. | Zero-Shot tuvo $43.75\%$ aluc. FK y $0\%$ DDL compilable; Agente MCP alcanzó $100\%$ $F_1$, $0\%$ aluc. y $100\%$ DDL compilable. | **CONFIRMADA** |
| **$H_3$** | Optimización relacional logra $\Delta CC \ge 50\%$ y elimina $100\%$ de $SLOC_{def}$ y $Q_{prev}$. | $SLOC_{def} \to 0$ ($-100\%$), $Q_{prev} \to 0$ ($-100\%$), $\Delta CC$ de **$-50.0\%$ a $-57.1\%$** en endpoints de clientes (`crear_cliente`, `obtener_cliente`) y **$-42.86\%$ promedio** en endpoints afectados en $CC$ ($-31.03\%$ en todos los routers). | **PARCIALMENTE CONFIRMADA*** |

*\*Interpretación científica transparente de $H_3$:* Mientras la eliminación del $100\%$ del código defensivo y de consultas previas se cumplió cabalmente y los endpoints críticos superaron el $50\%$ de reducción en $CC$, los endpoints mixtos (`crear_pedido`, `poner_inventario`) retuvieron bifurcaciones legítimas de manejo de respuesta HTTP (`404`/`409`/`422`), situando la reducción agregada de los endpoints afectados en $-42.86\%$. Reportar este matiz fortalece la validez interna y la honestidad experimental del artículo.

### Amenazas a la Validez Controladas y Limitaciones Abiertas
1. **Validez de Constructo:** Se mitigó la ambigüedad de conteo por comentarios/espacios mediante análisis AST directo y la detección del error de parseo de marcadores en el script preliminar (`31` vs `24` líneas reales).
2. **Validez Externa y Muestreo:** Aunque el benchmark cubre 28 defectos en 3 esquemas representativos, `backend_defensive` ejercita explícitamente 12 de los 20 defectos de Pagila/Northwind (los 8 restantes son estructurales de esquema sin impacto directo en las rutas diseñadas).
3. **Estrategia de Saneamiento en Producción:** El Agente optó por la purga transaccional (`DELETE`) de huérfanos para habilitar `FOREIGN KEY`; en producción real, la Skill debe parametrizarse hacia tablas de cuarentena para evitar pérdida de datos históricos.
4. **Pendientes de Verificación Final en IA:** Queda pendiente confirmar el identificador exacto del modelo LLM empleado en el endpoint de inferencia (documentado en `inference_config.json` como `gemini-3.8-flash`) y añadir mediciones de latencia y consumo de tokens por corrida.

