# 03 — Línea Base de Linters AST Tradicionales (Control Nivel 1)

> **Rama Estandarizada Asociada:** `linters-ast-baseline` (estandarización de `miembro3/trabajo`, respaldada bajo `backup/pre-reorg-miembro3-trabajo`).  
> **Propósito:** Medir empíricamente si los analizadores estáticos industriales basados en Árboles de Sintaxis Abstracta (**SQLFluff** y **SonarQube**) detectan los **28 defectos relacionales** inyectados en el benchmark PostgreSQL (`RQ1` / `H1`).

---

## 1. Configuración y Evidencia Conservada

* **SQLFluff `4.5.0`** (Python `3.12.10`): Ejecutado con configuración global [`../.sqlfluff`](../.sqlfluff) (`dialect = postgres`, `templater = raw`, `max_line_length = 100`, 79 reglas sin exclusiones).
* **SonarQube Community Build `26.10.0.133078`** + `sonar-sql-plugin 1.4.0`: Ejecutado vía [`../sonar-project.properties`](../sonar-project.properties) con dialecto `pssqlv2` y perfil `SQL rules` (20 reglas activas).
* **Controles Positivos Independientes:** [`sqlfluff/control_style.sql`](sqlfluff/control_style.sql) (disparó `LT01`) y [`sonarqube/header_control.sql`](sonarqube/header_control.sql) (disparó `SQLCC:C030`), descartando fallos de instalación o configuración.

---

## 2. Resultados Empíricos Consolidados (`0 / 28 TP`, `100% FN`)

| Caso | Defectos del Manifiesto | SQLFluff: Avisos Estilo | SQLFluff: Errores `PRS`/`LXR`/`TMP` | SQLFluff ($TP / FN$) | SonarQube: Incidencias | SonarQube ($TP / FN$) | Quality Gate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pagila** (`case1_pagila`) | 10 | 189 (`CP03, CP05, LT01, LT02, RF04`) | 0 | **`0 / 10` (`100%` FN)** | 1 (`SQLCC:C030`) | **`0 / 10` (`100%` FN)** | PASSED |
| **Northwind** (`case2_northwind`) | 10 | 96 (`LT01, RF04`) | 0 | **`0 / 10` (`100%` FN)** | 1 (`SQLCC:C030`) | **`0 / 10` (`100%` FN)** | PASSED |
| **Sintético** (`case3_synthetic`) | 8 | 37 (`LT01, LT02`) | 0 | **`0 / 8` (`100%` FN)** | 1 (`SQLCC:C030`) | **`0 / 8` (`100%` FN)** | PASSED |
| **Total** | **28** | **322 cosméticos** | **0** | **`0 / 28` (`100%` FN)** | **3 cabeceras** | **`0 / 28` (`100%` FN)** | **100% PASSED** |

*Nota crítica:* La coincidencia espacial de avisos de formato (`LT01`, `CP05`) en líneas con comentarios de defectos **no** constituye detección relacional; ningún diagnóstico identificó anomalías 1FN–3FN ni claves foráneas ausentes (detalles fila a fila en [`matriz_deteccion.csv`](matriz_deteccion.csv)).

---

## 3. Archivos y Repetición

* [`Guia_Ejecucion_Linters.md`](Guia_Ejecucion_Linters.md): Bitácora técnica de ejecución, versiones y comandos de repetición.
* [`Analisis_de_Resultados.md`](Analisis_de_Resultados.md): Análisis completo de falsos negativos, causa raíz AST vs. semántica y límites de validez.
* [`inputs.sha256.txt`](inputs.sha256.txt): Huellas SHA-256 verificables sobre `02_benchmark_sql_backend/case*/schema_defective.sql`.
* [`sqlfluff/`](sqlfluff/results/2026-11-08/) y [`sonarqube/`](sonarqube/results/2026-11-08/): Salidas JSON originales, logs de escáner y captura del dashboard.

### Verificar Huellas y Re-ejecutar SQLFluff
```powershell
# 1. Validar integridad criptográfica de los DDL analizados
cd 02_benchmark_sql_backend
Get-Content ..\03_linters_ast_baseline\inputs.sha256.txt | ForEach-Object {
  $p, $h = $_ -split '\s+'
  "$( (Get-FileHash $p -Algorithm SHA256).Hash -eq $h ) $p"
}
cd ..

# 2. Ejecutar SQLFluff usando .sqlfluff de la raíz
python -m pip install -r 03_linters_ast_baseline/requirements.txt
sqlfluff lint 02_benchmark_sql_backend/case1_pagila/schema_defective.sql --format json
```
