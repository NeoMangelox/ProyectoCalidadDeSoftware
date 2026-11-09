# Marco Métrico Formal de Calidad Backend y Alineación ISO/IEC 25010

> **Propósito:** Formalizar matemática y operativamente la medición cuantitativa del impacto que produce la normalización de esquemas PostgreSQL sobre la calidad estructural del código *backend* ($RQ_3$ / $H_3$).  
> **Norma de Referencia:** ISO/IEC 25010:2011 (*Systems and software Quality Requirements and Evaluation — SQuaRE*).

---

## 1. Fundamentación Teórica: Traslación de Deuda Técnica

Cuando el esquema relacional adolece de violaciones de formas normales (1FN, 2FN, 3FN) o omite restricciones `FOREIGN KEY` (*keyless entry*), la regla de consistencia migra forzosamente a los controladores web mediante programación defensiva:
1. Deserialización manual en memoria (`split()`, `re.split`) para listas multivaluadas (1FN).
2. Consultas existenciales previas (`SELECT COUNT(*)`, `SELECT EXISTS`) antes de insertar o borrar (ausencia de FKs).
3. Sincronización manual de atributos redundantes (2FN/3FN).

---

## 2. Formalización Matemática de Métricas

### 2.1 Complejidad Ciclomática de McCabe ($CC$)
Mide el número de caminos linealmente independientes a través del Grafo de Flujo de Control ($CFG$) de cada endpoint (`P = 1`):

$$CC = V(G) = E - N + 2P = 1 + \sum_{i=1}^{k} \pi_i$$

El visitante determinista `McCabeASTVisitor` en [`measure_quality.py`](../measure_quality.py) contabiliza en el AST estándar de Python 3.12 los nodos `If`, `IfExp`, `For`, `AsyncFor`, `While`, `ExceptHandler`, `Assert`, `comprehension`, `BoolOp` y `Match`, clasificando cada función en la escala estándar de Radon:
* **Rango A ($1 \le CC \le 5$):** Bajo riesgo / alta analizabilidad.
* **Rango B ($6 \le CC \le 10$):** Riesgo bajo-medio.
* **Rango C–F ($CC > 10$):** Riesgo moderado a crítico.

### 2.2 Líneas Lógicas de Código Defensivo ($SLOC_{def}$) y Consultas Previas ($Q_{prev}$)
* **$SLOC_{def}$:** Sentencias ejecutables añadidas exclusivamente para compensar carencias relacionales del esquema (delimitadas entre `# >>> DEFENSIVE-BEGIN` y `# <<< DEFENSIVE-END` dentro de cada función), excluyendo comentarios, líneas en blanco, importaciones y validaciones de formato HTTP en DTOs Pydantic.
* **$Q_{prev}$:** Llamadas de verificación existencial previas a operaciones `INSERT`/`UPDATE`/`DELETE`.

### 2.3 Diferenciales Relativos de Calidad ($\Delta$)
Para toda métrica $M \in \{CC, SLOC_{def}, Q_{prev}\}$ entre el servicio defensivo y el normalizado:

$$\Delta M(\%) = \left( \frac{M_{\text{defectuoso}} - M_{\text{normalizado}}}{M_{\text{defectuoso}}} \right) \times 100\%$$

---

## 3. Mapeo Ontológico con ISO/IEC 25010

* **Mantenibilidad:**
  * *Analizabilidad:* Reducir $CC$ hacia Rango A ($CC \le 4$) minimiza las rutas lógicas que deben inspeccionarse y probarse.
  * *Modificabilidad y Modularidad:* Erradicar $SLOC_{def}$ desacopla la lógica de negocio de la integridad referencial delegada al RDBMS.
* **Fiabilidad:**
  * *Tolerancia a fallos e Integridad de datos:* Eliminar el patrón *check-then-mutate* ($Q_{prev}$) cierra ventanas de condición de carrera (TOCTOU) garantizando atomicidad ACID directamente en PostgreSQL.

---

## 4. Control de Amenazas a la Validez

1. **Validez de Constructo:** Conteo directo sobre rangos AST de funciones (`FunctionDef`/`AsyncFunctionDef`) tras formateo determinista con `black --line-length 88`, calibrado en [`test_sample_backend.py`](../test_sample_backend.py).
2. **Validez Interna:** Equivalencia funcional certificada mediante las **10 pruebas agnósticas de contrato en `pytest`** sobre ambos servicios.
3. **Validez Externa:** Cobertura transparente de **12 de los 20 defectos** de Pagila y Northwind ejercitados por rutas REST reales (los 8 restantes son estructurales sin impacto REST en la API).
