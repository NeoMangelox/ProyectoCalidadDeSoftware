# 01 — Estado del Arte y Revisión Sistemática de Literatura (SLR)

> **Ubicación:** Integrado directamente en `main` (sin rama aislada, por diseño organizacional del equipo).  
> **Propósito:** Fundamentar teóricamente las preguntas de investigación ($RQ_1$–$RQ_3$) mediante una Revisión Sistemática de Literatura (SLR) hasta 2026 e identificar los vacíos científicos (*Research Gaps*) cubiertos por este estudio.

---

## Contenido de la Carpeta

| Archivo | Descripción |
| :--- | :--- |
| [`Revision_Sistematica_Literatura.md`](Revision_Sistematica_Literatura.md) | Protocolo SLR completo: ecuación booleana, matriz comparativa de **16 fuentes + ISO/IEC 25010 = 17 referencias**, 3 brechas formales y redacción académica *Related Work*. |
| [`Estado_del_Arte_Original.md`](Estado_del_Arte_Original.md) | Aporte base inicial del Miembro 1 con tabla comparativa, *Trabajos Relacionados* y *Brechas de Investigación* (DDL-to-DDL y métricas backend). |
| [`Repositorio_Bibliografico.md`](Repositorio_Bibliografico.md) | Catálogo maestro con las 17 claves BibTeX verificadas y su trazabilidad hacia los documentos de metodología, métricas y paper. |
| [`referencias.bib`](referencias.bib) | Archivo BibTeX listo para compilación LaTeX (IEEE / ACM), incluyendo DOI, arXiv ePrint y conferencias core (`ICSE`, `SIGMOD/PACMMOD`, `NeurIPS`, `EMNLP`, `MDPI BDCC`). |

---

## Ejes Científicos y Brechas Cubiertas

1. **Brecha 1 (*Text-to-SQL* vs. *DDL-to-DDL*):** La literatura de LLMs privilegió la generación de consultas (`Spider`, `BIRD`) sobre esquemas sanos; incluso trabajos recientes de remediación (`de Medeiros et al., 2026`, `DNBench & MARS, 2026`, `NormaScore, 2026`, `Miffie, 2025`) concluyen al validar el esquema.
2. **Brecha 2 (Ceguera AST vs. Alucinación sin *Grounding*):** Parsers gramaticales como SQLFluff o `sqlglot` (`SQLMentor, 2025`, `SQLFlex, 2026`) no detectan anomalías semánticas DDL, mientras los LLMs pasivos sufren alucinaciones de catálogo y fallos por datos sucios o huérfanos.
3. **Brecha 3 (Desconexión Esquema $\leftrightarrow$ Backend):** Aunque Karwin (2010) y Sharma et al. (2018) advierten la propagación de deuda hacia el software cliente, ningún estudio previo había medido end-to-end la reducción cuantitativa en $CC$ de McCabe, $SLOC_{def}$ y $Q_{prev}$ alineada con **ISO/IEC 25010**.
