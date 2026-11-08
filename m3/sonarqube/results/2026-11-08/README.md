# SonarQube: ejecución formal del Miembro 3

Fecha local: 8 de noviembre de 2026. Proyecto: `calidadsw-m3-sql-baseline`. Configuración: [`sonar-project.properties`](../../../../sonar-project.properties). El análisis se ejecutó con SonarQube Community Build 26.10.0.133078, `sonar-sql-plugin` 1.4.0 y SonarScanner CLI 8.1.0.6389. Las imágenes y sus digestos están en `environment.txt`.

SonarScanner leyó `sonar-project.properties`, indexó **tres archivos**, identificó el lenguaje `sql`, aplicó el perfil predeterminado `SQL rules` de 20 reglas activas y ejecutó `SQLSensor`. El código de salida fue 0. La tarea del servidor `0ec071a3-961a-4423-b15b-4a14a1e2cefa` terminó en `SUCCESS`; el identificador de análisis es `74c7d110-74e6-4bc0-a300-e66712868820`.

| Archivo analizado | Hallazgos observados |
| --- | --- |
| `case1_pagila/schema_defective.sql` | 1 × `SQLCC:C030` |
| `case2_northwind/schema_defective.sql` | 1 × `SQLCC:C030` |
| `case3_synthetic/schema_defective.sql` | 1 × `SQLCC:C030` |

`C030` informa que no encontró un comentario de cabecera multilínea. Los tres DDL comienzan con comentarios `--`. SonarQube registró 3 *code smells*, 0 bugs y 0 vulnerabilidades en los tres archivos (357 líneas de código según la métrica del servidor). No se registró un hallazgo que identifique explícitamente 1FN, 2FN, 3FN o una clave foránea ausente. **Estos datos todavía no constituyen una matriz de detección ni prueban una tasa de falsos negativos del 100 %.** Esa correspondencia con los 28 defectos de los manifiestos pertenece a la Fase 8.

El sensor SQL externo `SqlCheckSensor` se omitió porque su ejecutable opcional `/usr/bin/sqlcheck` no está instalado en la imagen. Los hallazgos aquí proceden de `SQLSensor` del plugin. Una prueba exploratoria anterior mostró que `C002` no se disparó ante un `SELECT *` de control; sus archivos de prueba no forman parte de este entregable. Esta limitación se debe considerar antes de interpretar ausencias de hallazgos.

## Archivos conservados

- `scanner.log` y `scanner-exit.txt`: salida y estado de SonarScanner.
- `task.json` y `server-ce-task.log`: procesamiento en el servidor.
- `issues.json`, `files.json`, `measures.json`, `analyses.json`: resultados exportados desde la API de SonarQube.
- `plugin-sql.json`, `profile-sql.json`, `rules-sql.json`, `system-status.json`: versión y configuración del análisis.
- `environment.txt` e `inputs.sha256.txt`: imágenes, versiones, commit y huellas de los tres DDL originales.
- `sonarqube-dashboard.jpeg`: captura auténtica del panel del proyecto, tomada con la sesión iniciada; muestra 357 líneas de código y 3 incidencias abiertas.

Los tokens y la contraseña de administración se guardan fuera del repositorio. Los DDL y manifiestos no se modificaron.

La captura complementa las respuestas de la API y los registros, que conservan el detalle verificable de esta ejecución. El panel muestra el estado general del proyecto; los archivos JSON contienen la correspondencia de cada incidencia con su DDL.

## Repetición

Desde la raíz del clon, con SonarQube disponible en `http://127.0.0.1:9000` y un token de análisis local definido en `SONAR_TOKEN`:

```powershell
$repo = (Get-Location).Path
docker run --rm -e SONAR_TOKEN -e SONAR_HOST_URL=http://host.docker.internal:9000 `
  -v "${repo}:/usr/src:ro" `
  sonarsource/sonar-scanner-cli:12.3.0.4285_8.1.0 `
  '-Dsonar.working.directory=/tmp/sonar-work'
```

Esperar después el estado `SUCCESS` de la tarea indicada por el escáner antes de consultar las incidencias. El panel local está en `http://127.0.0.1:9000/dashboard?id=calidadsw-m3-sql-baseline`.
