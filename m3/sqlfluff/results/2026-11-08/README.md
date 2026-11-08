# Ejecución SQLFluff — 8 de noviembre de 2026

Versión: SQLFluff 4.5.0 con [`.sqlfluff`](../../../../.sqlfluff): dialecto `postgres`, templater `raw`, longitud máxima 100 y reglas predeterminadas. Se ejecutó `sqlfluff lint <archivo> --format json` desde la raíz del repositorio, sin `fix` ni modificaciones de los DDL.

| Archivo original | Diagnósticos | Códigos observados | PRS / LXR / TMP |
| --- | ---: | --- | ---: |
| `case1_pagila/schema_defective.sql` | 189 | CP03: 1; CP05: 89; LT01: 92; LT02: 4; RF04: 3 | 0 / 0 / 0 |
| `case2_northwind/schema_defective.sql` | 96 | LT01: 95; RF04: 1 | 0 / 0 / 0 |
| `case3_synthetic/schema_defective.sql` | 37 | LT01: 35; LT02: 2 | 0 / 0 / 0 |

Cada salida original está en `pagila.json`, `northwind.json` y `synthetic.json`, con su archivo `.exit.txt` y `.stderr.txt`. Los tres códigos de salida fueron 1 porque hubo infracciones; las tres salidas de error estándar quedaron vacías. El control [`control_style.sql`](../../control_style.sql), separado del benchmark, generó una sola infracción `LT01` por dos espacios antes de `AS`; sus archivos se llaman `control_style.*`.

Estos números cuentan diagnósticos de SQLFluff, **no** defectos relacionales detectados. La relación entre cada diagnóstico y los 28 defectos documentados en los manifiestos pertenece a la Fase 8. No se infiere una tasa de falsos negativos a partir de esta ejecución.
