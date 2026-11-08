# Entorno SQLFluff del Miembro 3

Verificación local: 8 de noviembre de 2026, rama `miembro3/trabajo`.

| Componente | Valor comprobado |
| --- | --- |
| Python | 3.12.10 |
| SQLFluff | 4.5.0 |
| Dialecto efectivo | `postgres` |
| Procesador de plantillas efectivo | `raw` |
| Longitud máxima de línea | 100 |
| Reglas disponibles | 79; `rules = all` (valor predeterminado), sin exclusiones configuradas |

La configuración está en [`.sqlfluff`](../.sqlfluff) y la versión requerida en [`m3/requirements.txt`](requirements.txt). El entorno virtual `.venv` se mantiene local y está excluido de Git.

Para reproducir desde la raíz del repositorio en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r m3\requirements.txt
.\.venv\Scripts\sqlfluff.exe --version
.\.venv\Scripts\sqlfluff.exe rules
```

La configuración se comprobó leyendo sus valores efectivos con `FluffConfig.from_root()`. Una sentencia de control con `BIGINT GENERATED ALWAYS AS IDENTITY` y `TIMESTAMPTZ` se analizó con `sqlfluff parse` desde la raíz del repositorio sin indicar el dialecto por línea de comandos; terminó con código 0. Esta verificación no constituye aún la evaluación de los tres esquemas defectuosos de la Fase 5.
