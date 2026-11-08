# Benchmark Experimental SQL-Backend (PostgreSQL 16/17)

## 1. Visión General del Benchmark

Este repositorio contiene el **banco de pruebas experimental unificado** para evaluar la auditoría y corrección de esquemas relacionales defectuosos en **PostgreSQL**, así como su impacto directo en la deuda técnica y complejidad ciclomática del código backend.

El benchmark implementa de forma estricta las invariantes metodológicas del proyecto:
1. **Motor RDBMS Único:** 100% PostgreSQL nativo (con tipos estándar `TIMESTAMPTZ`, `BIGINT GENERATED ALWAYS AS IDENTITY` y llaves foráneas declarativas).
2. **3 Casos de Estudio Canónicos y Controlados:**
   - **Caso 1 (`case1_pagila`):** Núcleo OLTP transaccional de alquileres e inventario (15 tablas defectuosas $\rightarrow$ 16 tablas normalizadas, 10 defectos).
   - **Caso 2 (`case2_northwind`):** Sistema clásico de órdenes, clientes y proveedores adaptado a PostgreSQL (14 tablas defectuosas $\rightarrow$ 15 tablas normalizadas, 10 defectos).
   - **Caso 3 (`case3_synthetic`):** Micro-benchmark sintético de control inspirado en *DNBench (2026)* (5 tablas defectuosas $\rightarrow$ 7 tablas normalizadas, 8 defectos).
3. **Taxonomía de 4 Smells Relacionales (28 Defectos Totales):**
   - **Violación 1FN (Jaywalking / CSV):** Listas multivaluadas en columnas de texto plano.
   - **Violación 2FN (Dependencias Parciales):** Atributos no clave dependientes de un subconjunto de una PK compuesta.
   - **Violación 3FN (Dependencias Transitivas):** Atributos dependientes de columnas no clave (e.g. `codigo_postal -> ciudad`).
   - **Ausencia de Claves Foráneas (Keyless Entry):** Relaciones lógicas sin restricción `FOREIGN KEY`, provocando riesgo de registros huérfanos.
4. **Backend Dual en FastAPI:** Una versión con código defensivo (`backend_defensive/`) y una versión limpia delegada en la base de datos (`backend_normalized/`), ambas compartiendo exactamente el mismo contrato de API.

---

## 2. Puesta en Marcha Rápida (Infraestructura PostgreSQL)

El proyecto incluye un entorno Docker listo para levantar las **6 bases de datos precargadas** (3 casos $\times$ {`_defective`, `_ground_truth`}) con sus esquemas DDL y datos semilla (*seeds*):

```bash
# 1. Levantar contenedor de PostgreSQL 16
docker compose up -d

# Credenciales por defecto:
# Host: 127.0.0.1 | Puerto: 5432 | Usuario: postgres | Contraseña: postgres
```

Las 6 bases de datos quedan creadas automáticamente:
- `pagila_defective` & `pagila_ground_truth`
- `northwind_defective` & `northwind_ground_truth`
- `synthetic_defective` & `synthetic_ground_truth`

*(Opcional: Si cuentas con una instancia local propia de PostgreSQL, ejecuta:)*
```bash
PGHOST=127.0.0.1 PGUSER=postgres PGPASSWORD=postgres bash scripts/setup_databases.sh
```

---

## 3. Guía Operativa para el Miembro 3 (Auditor de Calidad & Linters)

### 3.1. Objetivo Metodológico
El Miembro 3 instrumenta el **Nivel 1 del Experimento (Grupo de Control)**: evaluar cómo responden SQLFluff y SonarQube frente a los tres esquemas relacionales defectuosos, usando los manifiestos como verdad de referencia.

> **Hipótesis evaluada ($H_1$):** en estos tres DDL, las herramientas no identificarán los defectos inyectados de 1FN, 2FN, 3FN y ausencia de claves foráneas. La conclusión se limita a las versiones, reglas y archivos efectivamente analizados.

### 3.2. Archivos de Trabajo para M3
- **Esquemas a Auditar:**
  - `case1_pagila/schema_defective.sql`
  - `case2_northwind/schema_defective.sql`
  - `case3_synthetic/schema_defective.sql`
- **Verdad de Terreno (Ground Truth para contrastar):**
  - `case1_pagila/defects_manifest.json` (10 defectos esperados)
  - `case2_northwind/defects_manifest.json` (10 defectos esperados)
  - `case3_synthetic/defects_manifest.json` (8 defectos esperados)

### 3.3. Instrucciones de Ejecución con SQLFluff

Se usaron Python 3.12.10 y SQLFluff 4.5.0, fijado en [`m3/requirements.txt`](m3/requirements.txt). La configuración [`.sqlfluff`](.sqlfluff) define el dialecto PostgreSQL. Desde la raíz del repositorio:

```bash
python -m pip install -r m3/requirements.txt
sqlfluff lint case1_pagila/schema_defective.sql --format json
sqlfluff lint case2_northwind/schema_defective.sql --format json
sqlfluff lint case3_synthetic/schema_defective.sql --format json
```

Los [tres resultados JSON](m3/sqlfluff/results/2026-11-08) originales se conservan en `m3/sqlfluff/results/2026-11-08/`. El código de salida fue 1 en los tres casos por infracciones de estilo; no se ejecutó `fix`.

### 3.4. Cómo Interpretar y Reportar los Hallazgos

SQLFluff produjo 189 diagnósticos en Pagila, 96 en Northwind y 37 en Synthetic, con códigos `CP03`, `CP05`, `LT01`, `LT02` y `RF04`. No emitió diagnósticos de parseo `PRS`, `LXR` ni `TMP`. Los avisos tratan de estilo, capitalización o nombres de identificadores, incluso cuando aparecen en la misma línea que un defecto marcado.

SonarQube **Community Build 26.10.0.133078**, gratuito, con `sonar-sql-plugin` 1.4.0 y SonarScanner CLI 8.1.0.6389 analizó los tres DDL como SQL. Registró tres incidencias `SQLCC:C030`, una por archivo, sobre comentarios de cabecera. La configuración está en [`sonar-project.properties`](sonar-project.properties) y las [evidencias del servidor](m3/sonarqube/results/2026-11-08) contienen incidencias, reglas activas, registros y captura. El sensor externo opcional `SqlCheckSensor` no se ejecutó porque faltaba `/usr/bin/sqlcheck`.

Un [control SQL separado](m3/sonarqube/header_control.sql) también activó `C030`; la [respuesta de la API](m3/sonarqube/control_issues.json) respalda esa comprobación. El control prueba el funcionamiento de esa regla concreta, sin sustituir una validación exhaustiva del plugin.

La [matriz individual](m3/matriz_deteccion.csv) y el [análisis de Fase 8](<m3/Analisis de Resultados.md>) comparan cada salida con los 28 defectos de los manifiestos. **En esta ejecución**, cada herramienta obtuvo 0 TP y 28 FN para las cuatro clases relacionales, con detección observada del 0 % y tasa de FN del 100 %. Las incidencias de estilo y cabecera no se cuentan como detecciones relacionales. Estos valores no prueban el comportamiento de otras versiones, perfiles o esquemas, ni significan que los DDL carezcan de otros problemas.

---

## 4. Guía Operativa para el Miembro 4 (Ingeniero de Prompts & Agentic AI)

### 4.1. Objetivo Metodológico
El Miembro 4 debe ejecutar y contrastar el **Nivel 2 (LLM Crudo / Zero-Shot)** contra el **Nivel 3 (Agente Autónomo con PostgreSQL MCP Server + Dry-Run determinista)**.

> **Hipótesis a Demostrar ($H_2$ y $H_3$):**  
> *Los prompts Zero-Shot / CoT en chatbots crudos sufren de alucinaciones de claves foráneas y generan DDL inválido (~40% de fallos sintácticos). En contraste, un Agente dotado de MCP Server y validación Dry-Run (`BEGIN...ROLLBACK`) alcanza un 0% de alucinaciones y 100% de DDL ejecutable.*

### 4.2. Insumos para M4
1. **Bases de Datos Defectuosas en Vivo:**
   - Cadena de conexión (DSN) para el MCP Server:
     - `postgresql://postgres:postgres@localhost:5432/synthetic_defective`
     - `postgresql://postgres:postgres@localhost:5432/northwind_defective`
     - `postgresql://postgres:postgres@localhost:5432/pagila_defective`
2. **Datos Semilla con Anomalías Deliberadas:**
   - Los datos en `seed_defective.sql` contienen anomalías reales (listas CSV, registros huérfanos, inconsistencias de duplicación) diseñadas para que las consultas de muestreo (`SELECT ... LIMIT 5`) del agente revelen los defectos.
3. **Estándar de Oro (Ground Truth Oculto para Benchmark):**
   - `case*/schema_ground_truth.sql` (DDL corregido canónico).
   - `case*/defects_manifest.json` (lista formal de IDs de defectos: `D1-01`, `D2-01`, etc.).
   - `known_native_smells` en los manifiestos: lista de dependencias menores nativas de Sakila/Northwind para **no penalizar al LLM como falso positivo** si las detecta.

### 4.3. Protocolo de Ejecución del Agente en 4 Fases (Skill / CoT)

El Miembro 4 debe configurar su agente (e.g. en Antigravity o LangChain) para seguir rigurosamente este flujo:

```mermaid
flowchart LR
    Fase1["Fase 1:<br/>Introspección Dinámica<br/>(information_schema & LIMIT 5)"] --> Fase2["Fase 2:<br/>Auditoría Relacional<br/>(Taxonomía 1FN-3FN + FK)"]
    Fase2 --> Fase3["Fase 3:<br/>Generación de DDL<br/>(schema_optimized.sql)"]
    Fase3 --> Fase4["Fase 4:<br/>Validación Dry-Run<br/>(BEGIN ... ROLLBACK)"]
```

1. **Fase 1 (Introspección):**
   - El agente ejecuta herramientas del MCP Server:
     ```sql
     -- Inspección de catálogo
     SELECT table_name, column_name, data_type 
     FROM information_schema.columns 
     WHERE table_schema = 'public';

     -- Muestreo de datos reales para detectar CSV o inconsistencias
     SELECT * FROM clientes LIMIT 5;
     ```
2. **Fase 2 (Auditoría Relacional):**
   - El agente clasifica los hallazgos en la taxonomía acordada (1FN, 2FN, 3FN, Keyless Entry).
3. **Fase 3 (Generación de DDL Optimizado):**
   - El agente produce el script DDL de refactorización (`schema_optimized.sql`) con creación de tablas intermedias, eliminación de columnas desnormalizadas y agregación formal de restricciones `FOREIGN KEY` con sus respectivas acciones referenciales (`ON DELETE RESTRICT` o `CASCADE`).
4. **Fase 4 (Validación Dry-Run Determinista):**
   - El agente **debe probar su propio DDL** dentro de una transacción atómica protegida contra la base de datos de pruebas:
     ```sql
     BEGIN;
     -- Ejecutar DDL generado por el agente
     ROLLBACK;
     ```
   - Si PostgreSQL arroja un error (e.g., violación de clave foránea preexistente, tabla inexistente, error de sintaxis), el agente captura el mensaje de error de PostgreSQL y corrige el DDL iterativamente antes de emitir la versión final.

### 4.4. Métricas a Calcular para la Sección IV-B del Paper
Para contrastar el Nivel 2 (LLM crudo) vs el Nivel 3 (Agente MCP):
- **Precision:** $\frac{TP}{TP + FP}$
- **Recall:** $\frac{TP}{TP + FN}$
- **F1-Score:** $2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$
- **Tasa de Compilación Exitosa del DDL (%):** Porcentaje de scripts que ejecutan sin error en PostgreSQL.
- **Tasa de Alucinación de FKs (%):** Claves foráneas inventadas hacia columnas que no existen en el catálogo.

---

## 5. Guía Operativa para el Miembro 5 (Métricas de Calidad Backend & Coordinador)

### 5.1. Pruebas de Contrato
Ambos backends (`backend_defensive` y `backend_normalized`) comparten el mismo contrato de endpoints (`/clientes`, `/inventario`, `/pedidos`). Para verificar que ambos responden idénticamente a la suite de pruebas:

```bash
# Instalar dependencias
pip install -r backend_defensive/requirements.txt pytest httpx radon

# Ejecutar pruebas contra backend defensivo
BACKEND_DIR=backend_defensive pytest

# Ejecutar pruebas contra backend normalizado
BACKEND_DIR=backend_normalized pytest
```

### 5.2. Medición Automatizada de Complejidad Ciclomática y SLOC
Para auditar la reducción de complejidad entre el código defensivo y el código limpio normalizado:

```bash
# Herramienta rápida del benchmark:
python tools/measure_defensive.py

# O el script formal de instrumentación del Miembro 5:
python ../../Proyecto/03-Metodologia/scripts/measure_quality.py \
  --compare \
  backend_defensive/routers/ \
  backend_normalized/routers/
```

Métricas obtenidas:
- **Reducción de Complejidad Ciclomática ($\Delta CC$):** Disminución superior al $40\%$ en endpoints críticos (`crear_cliente`, `crear_pedido`).
- **Líneas de Código Defensivo ($SLOC_{def}$):** ~90 líneas eliminadas (parsing manual, validaciones en memoria).
- **Consultas Previas Eliminadas ($Q_{prev}$):** Eliminación del 100% de `SELECT COUNT(*)` de verificación previa.
- **Mitigación de TOCTOU:** Eliminación de la ventana de condición de carrera (*Time-of-Check to Time-of-Use*) delegando la atomicidad en los constraints `UNIQUE` y `FOREIGN KEY` de PostgreSQL.

---

## 6. Estructura del Repositorio

```text
ENTREGABLES/ProyectoCalidadDeSoftware/
├── README.md                      # [ESTE ARCHIVO] Guía unificada para M2, M3, M4 y M5
├── Ficha_Tecnica_Benchmark.md     # Especificación exhaustiva de los 28 defectos y tablas
├── docker-compose.yml             # Despliegue inmediato de PostgreSQL 16 con las 6 BDs
├── docker/
│   └── init.sh                    # Script de inicialización automática del contenedor
├── scripts/
│   └── setup_databases.sh         # Carga idempotente de esquemas y semillas
├── case1_pagila/                  # Caso 1: Pagila OLTP (15 -> 16 tablas)
│   ├── schema_defective.sql       # DDL con 10 defectos relacionales inyectados
│   ├── schema_ground_truth.sql    # DDL canónico normalizado
│   ├── seed_defective.sql         # Datos semilla con anomalías deliberadas
│   ├── seed_ground_truth.sql      # Datos semilla canónicos
│   └── defects_manifest.json      # Manifiesto JSON para cálculo de Precision/Recall
├── case2_northwind/               # Caso 2: Northwind (14 -> 15 tablas)
│   ├── schema_defective.sql       # DDL con 10 defectos relacionales inyectados
│   ├── schema_ground_truth.sql    # DDL canónico normalizado
│   ├── seed_defective.sql         # Datos semilla con anomalías deliberadas
│   ├── seed_ground_truth.sql      # Datos semilla canónicos
│   └── defects_manifest.json      # Manifiesto JSON para cálculo de Precision/Recall
├── case3_synthetic/               # Caso 3: Micro-benchmark Sintético DNBench (5 -> 7 tablas)
│   ├── schema_defective.sql       # DDL con 8 defectos relacionales inyectados
│   ├── schema_ground_truth.sql    # DDL canónico normalizado
│   ├── seed_defective.sql         # Datos semilla con anomalías deliberadas
│   ├── seed_ground_truth.sql      # Datos semilla canónicos
│   └── defects_manifest.json      # Manifiesto JSON para cálculo de Precision/Recall
├── backend_defensive/             # FastAPI asíncrono con validación manual defensiva
│   ├── app/                       # Código fuente (routers, modelos, db)
│   └── requirements.txt
├── backend_normalized/            # FastAPI asíncrono limpio apoyado en BD normalizada
│   ├── app/                       # Código fuente idéntico en contrato API
│   └── requirements.txt
├── tests/
│   └── test_contract.py           # 10 pruebas funcionales de contrato agnósticas
└── tools/
    ├── generate_seeds.py          # Generador determinista de seeds (no tocar los .sql a mano)
    ├── validate_benchmark.py      # Verificador de presencia/ausencia de defectos en BD
    └── measure_defensive.py       # Script rápido de medición de CC con Radon
```

---

## 7. Preguntas Frecuentes y Resolución de Problemas (FAQ)

1. **¿Por qué Northwind tiene 14 tablas en lugar de las 13 mencionadas inicialmente?**  
   El dialecto original de `northwind_psql` incluye la tabla auxiliar `us_states`. Se conservaron las 14 tablas originales en el esquema defectuoso para mantener la fidelidad del benchmark canónico.

2. **¿Por qué Pagila no incluye particiones de `payment` ni `pgvector`?**  
   Se aisló el núcleo OLTP para que el DDL compile de forma limpia e idéntica en cualquier distribución de PostgreSQL 15, 16 o 17 estándar, sin requerir extensiones externas compiladas en C.

3. **¿Cómo resetear las bases de datos a su estado limpio inicial?**  
   ```bash
   docker compose down -v
   docker compose up -d
   ```

4. **Si necesito regenerar o cambiar el volumen de datos de prueba:**  
   Modifica los parámetros en `tools/generate_seeds.py` y vuelve a ejecutarlo. Nunca edites a mano los archivos `seed_*.sql` para evitar romper las restricciones de llaves foráneas.
