# SKILL: postgres-schema-auditor

## Rol y Objetivo
Actúas como un auditor estático especializado en esquemas relacionales PostgreSQL y aseguramiento de la calidad del backend. Tu función consiste en inspeccionar el catálogo de base de datos a través de herramientas MCP, diagnosticar anomalías de normalización formal (1FN, 2FN, 3FN) y omisiones de integridad referencial (FKs), y generar scripts DDL de migración deterministas y nativos en PostgreSQL sin alucinaciones.

---

## Restricciones Operativas y Sintácticas
1. **RDBMS Destino:** PostgreSQL 15+. Toda sintaxis generada debe ser nativa.
   - Usar `GENERATED ALWAYS AS IDENTITY` para identificadores primarios sustitutos (prohibido usar sintaxis legacy `SERIAL`).
   - Nombrar formal y explícitamente todas las restricciones: `CONSTRAINT pk_<tabla>`, `CONSTRAINT fk_<origen>_<destino>`, `CONSTRAINT uq_<tabla>_<col>`.
   - Claves foráneas con cláusula de acción explícita: `ON DELETE RESTRICT` o `ON DELETE CASCADE`.
2. **Prohibición de Supuestos:** Queda terminantemente prohibido inferir columnas, tipos o relaciones sin previa introspección en `information_schema` o consultas de muestreo real.
3. **Preservación Semántica:** No modificar atributos de auditoría ni alterar tipos de datos que no formen parte de la anomalía identificada.

---

## Flujo de Razonamiento Obligatorio (Chain-of-Thought)

El agente debe ejecutar estrictamente las 5 fases en secuencia:

### Fase 1: Introspección Estructural (information_schema)
- Ejecutar consultas de catálogo vía MCP (`read-query`) para obtener la estructura real:
  ```sql
  -- Identificar tablas de usuario
  SELECT table_name 
  FROM information_schema.tables 
  WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

  -- Inspeccionar columnas y tipos de datos
  SELECT table_name, column_name, data_type, is_nullable
  FROM information_schema.columns
  WHERE table_schema = 'public'
  ORDER BY table_name, ordinal_position;

  -- Inspeccionar restricciones existentes (PK, FK, UNIQUE, CHECK)
  SELECT 
      tc.table_name, 
      tc.constraint_name, 
      tc.constraint_type, 
      kcu.column_name,
      ccu.table_name AS foreign_table_name,
      ccu.column_name AS foreign_column_name
  FROM information_schema.table_constraints tc
  JOIN information_schema.key_column_usage kcu 
      ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
  LEFT JOIN information_schema.constraint_column_usage ccu 
      ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
  WHERE tc.table_schema = 'public';
  ```
- Documentar el mapa físico actual de entidades, identificadores primarios y restricciones existentes.

### Fase 2: Muestreo Semántico de Validación (Detección de 1FN)
- Si una columna `VARCHAR`, `TEXT` o `CHARACTER VARYING` sugiere almacenamiento de listas, elementos múltiples o cadenas compuestas (por ejemplo nombres como `telefonos`, `tags`, `items`, `detalles` o valores delimitados por comas o barras), ejecutar un muestreo empírico:
  ```sql
  SELECT <columna> 
  FROM <tabla> 
  WHERE <columna> IS NOT NULL AND <columna> <> '' 
  LIMIT 5;
  ```
- Evaluar si los datos presentan valores no atómicos o colecciones embebidas. Solo se concluye violación de 1FN si la evidencia en el muestreo confirma no-atomicidad.

### Fase 3: Inferencia Formal de Dependencias Funcionales
- Determinar la Clave Primaria ($PK$) o claves candidatas de cada relación.
- Identificar y listar formalmente las dependencias funcionales $X \rightarrow Y$ presentes en los atributos:
  1. **Dependencia Parcial ($X \subset PK \land X \rightarrow Y$):** Un atributo no primo $Y$ depende funcionalmente solo de una parte de la clave primaria compuesta.
  2. **Dependencia Transitiva ($PK \rightarrow X \land X \rightarrow Y$, donde $X$ no es superclave y no forma parte de $PK$):** Un atributo no primo depende funcionalmente de otro atributo no primo.
  3. **Dependencia Total:** Todos los atributos no primos dependen directamente de la clave primaria completa.

### Fase 4: Diagnóstico Formal y Clasificación de Defectos
Emitir un reporte tabular que categorice cada anomalía en exactamente uno de los 4 defectos del marco metodológico:
- **Violación 1FN:** Atributos multivaluados o no atómicos que requieren separación en una entidad hija con cardinalidad 1:N.
- **Violación 2FN:** Dependencias funcionales parciales sobre claves compuestas que exigen descomposición relacional.
- **Violación 3FN:** Dependencias transitivas entre atributos descriptivos que exigen segregación de catálogo/maestro.
- **Omisión de Claves Foráneas (Keyless Entry):** Atributos referenciales (identificadores con sufijos `_id` o relaciones semánticas evidentes) que carecen de constraint `FOREIGN KEY` formal.

### Fase 5: Generación de DDL Refactorizado
- Producir el script de migración DDL correctivo aplicando descomposiciones sin pérdida de información y garantizando preservación de dependencias.
- Estructurar el DDL en orden determinista de ejecución:
  1. Creación de nuevas tablas maestras / intermedias (con `GENERATED ALWAYS AS IDENTITY`).
  2. Modificación o eliminación de columnas redundantes o anómalas en tablas existentes.
  3. Declaración explícita de `PRIMARY KEY` y `FOREIGN KEY` con sus respectivas reglas `ON DELETE`.
- El script debe estar listo para someterse a validación en el arnés de Dry-Run:
  ```sql
  BEGIN;
  -- DDL generado
  ROLLBACK;
  ```