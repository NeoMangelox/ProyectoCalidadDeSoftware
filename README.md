# Línea Base Industrial con Analizadores Estáticos AST (`linters-ast-baseline`)

> **Alcance de la Rama:** Auditoría estática de control (Nivel 1) sobre los esquemas defectuosos de PostgreSQL 16 utilizando **SQLFluff 4.5.0** y **SonarQube Community Build 26.10 (`sonar-sql-plugin` 1.4.0)** para contrastar la pregunta $RQ_1$ y la hipótesis $H_1$.

---

## 1. Propósito Metodológico

Esta rama implementa el **Grupo de Control Industrial** del experimento. Antes de evaluar arquitecturas basadas en LLMs, demuestra empíricamente que las herramientas tradicionales orientadas a Árboles de Sintaxis Abstracta (AST) en *pipelines* CI/CD operan bajo una **ceguera semántica** frente a defectos relacionales:
- Verifican conformidad léxica, sintaxis gramatical (BNF de PostgreSQL) y formato estilístico.
- No detectan atributos multivaluados (1FN), dependencias parciales (2FN), dependencias transitivas (3FN) ni omisión de claves foráneas (*keyless entry*).

---

## 2. Configuración Estandarizada y Certificación de Entradas

- **Inmutabilidad de Esquemas (`m3/inputs.sha256.txt`):** Sellado SHA-256 de `case1_pagila/schema_defective.sql`, `case2_northwind/schema_defective.sql` y `case3_synthetic/schema_defective.sql`.
- **SQLFluff (`4.5.0`):** Configurado en `.sqlfluff` con `dialect = postgres`, `templater = raw`, `max_line_length = 100` y las **79 reglas activas sin exclusiones** (`m3/requirements.txt`).
- **SonarQube (`26.10.0.133078` + `sonar-sql-plugin 1.4.0`):** Configurado en `sonar-project.properties` (`sonar.sql.dialect = pssqlv2`, perfil `SQL rules` con `20` reglas activas, SonarScanner CLI `8.1.0.6389`).

---

## 3. Evidencia Empírica y Controles Positivos

| Caso Evaluado | Defectos Reales | SQLFluff (Estilo) | SQLFluff Relacional ($TP / FN$) | SonarQube (Incidencias) | SonarQube Relacional ($TP / FN$) | Quality Gate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`case1_pagila`** | 10 | 189 (`CP03, CP05, LT01, LT02, RF04`) | **0 / 10** ($100\%$ FN) | 1 (`SQLCC:C030`) | **0 / 10** ($100\%$ FN) | **PASSED** |
| **`case2_northwind`** | 10 | 96 (`LT01, RF04`) | **0 / 10** ($100\%$ FN) | 1 (`SQLCC:C030`) | **0 / 10** ($100\%$ FN) | **PASSED** |
| **`case3_synthetic`** | 8 | 37 (`LT01, LT02`) | **0 / 8** ($100\%$ FN) | 1 (`SQLCC:C030`) | **0 / 8** ($100\%$ FN) | **PASSED** |
| **Total Nivel 1** | **28** | **322 avisos de formato** | **0 / 28 ($100\%$ FN)** | **3 cabeceras** | **0 / 28 ($100\%$ FN)** | **100% Aprobados** |

* **Controles Positivos Independientes:** [`m3/sqlfluff/control_style.sql`](m3/sqlfluff/control_style.sql) disparó `LT01` en SQLFluff, y [`m3/sonarqube/header_control.sql`](m3/sonarqube/header_control.sql) disparó `SQLCC:C030` en un proyecto aislado (`calidadsw-m3-header`), descartando fallos de configuración.
* **Criterio Estricto de Puntuación (`m3/matriz_deteccion.csv`):** Coincidir físicamente en una línea con una alerta cosmética (`LT01`/`CP05`) **no** califica como detección semántica ($TP=0, FN=28$, precisión relacional indefinida).

---

## 4. Reproducción Rápida

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r m3\requirements.txt
.\.venv\Scripts\sqlfluff.exe lint case1_pagila\schema_defective.sql --format json
.\.venv\Scripts\sqlfluff.exe lint case2_northwind\schema_defective.sql --format json
.\.venv\Scripts\sqlfluff.exe lint case3_synthetic\schema_defective.sql --format json
```

Para las instrucciones completas de SonarQube en Docker y trazabilidad línea a línea, consultar [`m3/README.md`](m3/README.md) y [`m3/Analisis de Resultados.md`](<m3/Analisis de Resultados.md>).

---

## 5. Estructura Específica Añadida en la Rama

```text
├── README.md                            # Documentación específica de esta rama
├── .sqlfluff                            # Configuración dialect=postgres (79 reglas activas)
├── sonar-project.properties             # Configuración SonarScanner (pssqlv2)
└── m3/
    ├── README.md                        # Guía detallada de reproducción Nivel 1
    ├── Analisis de Resultados.md        # Discusión formal y límites de interpretación
    ├── inputs.sha256.txt                # Huellas SHA-256 de esquemas evaluados
    ├── matriz_deteccion.csv             # Matriz de 28 filas mapeando TP/FN línea por línea
    ├── requirements.txt                 # sqlfluff==4.5.0
    ├── sqlfluff/                        # control_style.sql + resultados JSON
    └── sonarqube/                       # header_control.sql, control_issues.json + evidencias
```
