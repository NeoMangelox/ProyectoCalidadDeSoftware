# Fase 8: correspondencia de hallazgos con defectos relacionales

Fecha de evaluación: 8 de noviembre de 2026. Se usaron las salidas originales de [SQLFluff](sqlfluff/results/2026-11-08) y [SonarQube](sonarqube/results/2026-11-08), sin modificar ni volver a analizar los DDL. La [matriz de 28 filas](matriz_deteccion.csv) permite revisar cada decisión por caso, ID, tipo, tabla, columna y línea del DDL.

## Criterio de clasificación

La unidad de evaluación es **cada defecto inyectado** de los tres `defects_manifest.json` (10 Pagila, 10 Northwind y 8 Synthetic). Se contó un verdadero positivo (TP) solo cuando un diagnóstico de la herramienta describió el defecto relacional concreto de esa fila: lista multivaluada (1FN), dependencia parcial (2FN), dependencia transitiva (3FN) o ausencia de la FK indicada. Si no hubo tal diagnóstico, se clasificó como falso negativo (FN) respecto del manifiesto.

Se comprobó que los 28 IDs aparecen en los comentarios de los DDL, en la tabla y columna indicadas por su manifiesto. La matriz registra los códigos de SQLFluff que empiezan en la misma línea; **coincidir en la línea no basta para contar una detección**. Las reglas `LT01` (espaciado) y `CP05` (mayúsculas/minúsculas de tipos) aparecen en las 28 líneas marcadas: `LT01` en todas y `CP05` además en las 10 de Pagila. Ninguna describe la anomalía relacional de la fila. Los otros diagnósticos de SQLFluff fueron `CP03`, `LT02` y `RF04`, también ajenos a las cuatro clases evaluadas.

La respuesta `issues.json` de SonarQube contiene solo tres incidencias `SQLCC:C030`, una por archivo: falta de comentario de cabecera multilínea. Son incidencias de archivo, sin correspondencia con ninguno de los 28 defectos. El [perfil de reglas exportado](sonarqube/results/2026-11-08/rules-sql.json) incluye `C011` para **nombres de claves foráneas ya definidas**; no es una regla que identifique FKs ausentes. El registro del escáner confirma que el sensor SQL se ejecutó y que el sensor externo opcional `SqlCheckSensor` se omitió por falta del ejecutable `/usr/bin/sqlcheck`.

## Resultados

| Caso | Defectos del manifiesto | SQLFluff TP | SQLFluff FN | SonarQube TP | SonarQube FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pagila | 10 | 0 | 10 | 0 | 10 |
| Northwind | 10 | 0 | 10 | 0 | 10 |
| Synthetic | 8 | 0 | 8 | 0 | 8 |
| **Total** | **28** | **0** | **28** | **0** | **28** |

| Tipo de defecto | Total | TP por herramienta | FN por herramienta |
| --- | ---: | ---: | ---: |
| 1FN: columna multivaluada | 3 | 0 | 3 |
| 2FN: dependencia parcial | 6 | 0 | 6 |
| 3FN: dependencia transitiva | 4 | 0 | 4 |
| Integridad referencial: FK ausente | 15 | 0 | 15 |

Para **cada herramienta en esta ejecución**, la detección observada de defectos relacionales fue `TP / (TP + FN) = 0 / 28 = 0 %` y la tasa de falsos negativos respecto de los 28 defectos documentados fue `FN / (TP + FN) = 28 / 28 = 100 %`. La precisión relacional queda indefinida porque no hubo predicciones positivas de estas clases; la especificidad no se calcula porque no hay un conjunto etiquetado de casos negativos para contar verdaderos negativos. Los **322 diagnósticos de SQLFluff** y las **3 incidencias de SonarQube** son hallazgos de estilo o cabecera fuera de la taxonomía evaluada; no se presentan como TP ni como FP relacionales.

## Causa y límites de la conclusión

SQLFluff 4.5.0 procesó los tres DDL con dialecto PostgreSQL y no emitió diagnósticos `PRS`, `LXR` ni `TMP`. Sus reglas disparadas evaluaron formato, uso de mayúsculas y nombres de identificadores. El parseo correcto y los diagnósticos de estilo no verifican dependencias funcionales ni si una columna de texto contiene listas CSV en los datos. La ausencia de una FK es observable en el DDL, pero ninguna regla disparada de SQLFluff la señaló en esta ejecución.

SonarQube Community Build 26.10.0.133078 con `sonar-sql-plugin` 1.4.0 sí analizó los tres archivos como SQL y reportó `C030`. La única incidencia por archivo trata del formato de cabecera; el estado *Passed* del quality gate no implica conformidad con 1FN, 2FN, 3FN ni integridad referencial. El ejecutable opcional de `SqlCheckSensor` no estuvo disponible, por lo que estos resultados corresponden al `SQLSensor` que sí se ejecutó.

La verdad de referencia son los manifiestos del benchmark. En particular, confirmar una lista CSV y las dependencias funcionales requiere el contexto del dominio o los datos; el DDL por sí solo no prueba todos esos hechos. El **100 % de FN es una observación limitada a estos 28 defectos, estos tres archivos, estas versiones, este perfil y el criterio explícito de correspondencia**. No demuestra que toda versión o configuración de las herramientas falle siempre, ni que no puedan detectar otros problemas SQL. Tampoco significa que los DDL hayan sido certificados como «código limpio»: ambas herramientas emitieron otros diagnósticos.

Antes de integrar, el equipo debe armonizar la sección del Miembro 3 en el README compartido: allí se anticipan códigos `LT05` y la expresión «código limpio», mientras que las salidas conservadas muestran `CP03`, `CP05`, `LT01`, `LT02`, `RF04` y tres incidencias `C030`.
