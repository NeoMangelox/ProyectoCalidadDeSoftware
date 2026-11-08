# Miembro 3: análisis estático de los tres DDL

Ejecución local del 8 de noviembre de 2026 en la rama `miembro3/trabajo`. Se analizaron únicamente `case1_pagila/schema_defective.sql`, `case2_northwind/schema_defective.sql` y `case3_synthetic/schema_defective.sql`. Las huellas de esos archivos se conservan en [`inputs.sha256.txt`](inputs.sha256.txt). Los DDL y los manifiestos no se modificaron.

## Configuración

| Herramienta | Versión y configuración | Archivo |
| --- | --- | --- |
| Python y SQLFluff | Python 3.12.10; SQLFluff 4.5.0; dialecto `postgres`, templater `raw`, longitud máxima 100; 79 reglas disponibles sin exclusiones | [`requirements.txt`](requirements.txt), [`.sqlfluff`](../.sqlfluff) |
| SonarQube y plugin SQL | Community Build 26.10.0.133078; `sonar-sql-plugin` 1.4.0; perfil `SQL rules` con 20 reglas activas; dialecto `pssqlv2` | [`sonar-project.properties`](../sonar-project.properties) |
| SonarScanner CLI | 8.1.0.6389, ejecutado desde la imagen indicada en [`environment.txt`](sonarqube/results/2026-11-08/environment.txt) | [`scanner.log`](sonarqube/results/2026-11-08/scanner.log) |

No se requiere licencia de pago. El JAR del plugin y el token de análisis se mantienen fuera de Git.

## Resultados observados

| Caso | SQLFluff: diagnósticos de estilo | SQLFluff: errores PRS/LXR/TMP | SonarQube: incidencias |
| --- | ---: | ---: | ---: |
| Pagila | 189 | 0 | 1 × `SQLCC:C030` |
| Northwind | 96 | 0 | 1 × `SQLCC:C030` |
| Synthetic | 37 | 0 | 1 × `SQLCC:C030` |

SQLFluff devolvió código 1 en los tres casos por infracciones de estilo. Los códigos observados fueron CP03, CP05, LT01, LT02 y RF04 en Pagila; LT01 y RF04 en Northwind; LT01 y LT02 en Synthetic. La [sentencia de control de estilo](sqlfluff/control_style.sql), separada del benchmark, produjo una infracción LT01.

SonarScanner indexó los tres DDL como lenguaje `sql` y ejecutó `SQLSensor` con código de salida 0. La tarea del servidor terminó en `SUCCESS`. Las tres incidencias `C030` indican ausencia de un comentario de cabecera multilínea; los DDL empiezan con comentarios `--`. El sensor externo `SqlCheckSensor` se omitió porque no estaba instalado su ejecutable opcional `/usr/bin/sqlcheck`. El panel registró 357 líneas de código, 3 *code smells*, 0 bugs y 0 vulnerabilidades.

Estos diagnósticos **no equivalen a defectos relacionales detectados**. La comparación individual con los 28 defectos de los manifiestos, la matriz TP/FN y las tasas de detección siguen pendientes de la Fase 8. No se afirma una tasa de falsos negativos antes de esa correspondencia.

## Evidencias conservadas

- [`sqlfluff/results/2026-11-08`](sqlfluff/results/2026-11-08): tres respuestas JSON originales y el control de estilo. Las salidas de error estándar estuvieron vacías; los códigos de salida de los cuatro análisis fueron 1 por infracciones.
- [`sonarqube/results/2026-11-08`](sonarqube/results/2026-11-08): `issues.json`, `files.json`, `measures.json`, `task.json`, versión del plugin, perfil y reglas activas, registros de escáner y servidor, versiones e imágenes con digestos.
- [`sonarqube-dashboard.jpeg`](sonarqube/results/2026-11-08/sonarqube-dashboard.jpeg): captura del panel con la sesión iniciada; muestra el proyecto y sus tres incidencias abiertas.

## Repetición

Desde la raíz del repositorio, para SQLFluff:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r m3\requirements.txt
.\.venv\Scripts\sqlfluff.exe lint case1_pagila\schema_defective.sql --format json
.\.venv\Scripts\sqlfluff.exe lint case2_northwind\schema_defective.sql --format json
.\.venv\Scripts\sqlfluff.exe lint case3_synthetic\schema_defective.sql --format json
```

Para SonarQube, iniciar Community Build con el JAR de `sonar-sql-plugin` 1.4.0 en su carpeta de plugins y disponer de un token de análisis local en `SONAR_TOKEN`. Con el servidor disponible en `http://127.0.0.1:9000`, ejecutar desde la raíz:

```powershell
$repo = (Get-Location).Path
docker run --rm -e SONAR_TOKEN -e SONAR_HOST_URL=http://host.docker.internal:9000 `
  -v "${repo}:/usr/src:ro" `
  sonarsource/sonar-scanner-cli:12.3.0.4285_8.1.0 `
  '-Dsonar.working.directory=/tmp/sonar-work'
```

Esperar el estado `SUCCESS` de la tarea del servidor antes de consultar las incidencias. El proyecto local es `calidadsw-m3-sql-baseline`.
