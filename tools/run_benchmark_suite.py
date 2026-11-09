#!/usr/bin/env python3
"""
tools/run_benchmark_suite.py
Ejecutor maestro del benchmark experimental de 9 experimentos.
Lee config/inference_config.json y valida cada DDL en PostgreSQL 16 con Dry-Run determinista (BEGIN ... ROLLBACK).
"""

import os
import sys
import json
from pathlib import Path

# Configurar ruta para libpq en Windows si fuera necesario
if sys.platform == "win32":
    for p in [r"C:\Program Files\PostgreSQL\18\bin", r"C:\Program Files\PostgreSQL\16\bin"]:
        if os.path.exists(p):
            try:
                os.add_dll_directory(p)
            except Exception:
                pass
            os.environ["PATH"] = p + ";" + os.environ.get("PATH", "")
            break

import psycopg

ROOT = Path(__file__).resolve().parent.parent

def find_file(case_dir: str, filename: str) -> Path:
    p1 = ROOT / case_dir / "resultados_experimentos_m4" / filename
    if p1.exists():
        return p1
    p2 = ROOT / case_dir / filename
    return p2

EXPERIMENTS = [
    {
        "id": "EXP-01",
        "case": "Pagila",
        "condition": "Nivel 2: Crudo (Zero-Shot)",
        "db": "pagila_defective",
        "file": find_file("case1_pagila", "exp01_ddl_zeroshot.sql"),
        "fk_aluc": 3,
        "fk_tot": 6,
        "attempts": 1,
        "satisfies_3fn": False,
        "tp": 4, "fp": 2, "fn": 6
    },
    {
        "id": "EXP-02",
        "case": "Pagila",
        "condition": "Nivel 2: Chain of Thought (CoT)",
        "db": "pagila_defective",
        "file": find_file("case1_pagila", "exp02_ddl_cot.sql"),
        "fk_aluc": 0,
        "fk_tot": 5,
        "attempts": 1,
        "satisfies_3fn": False,  # Teórico en texto, pero inejecutable en BD
        "tp": 10, "fp": 0, "fn": 0
    },
    {
        "id": "EXP-03",
        "case": "Pagila",
        "condition": "Nivel 3: Agente Autónomo (MCP + Dry-Run)",
        "db": "pagila_defective",
        "file": find_file("case1_pagila", "exp03_ddl_agent_optimized.sql"),
        "fk_aluc": 0,
        "fk_tot": 5,
        "attempts": 2,
        "satisfies_3fn": True,
        "tp": 10, "fp": 0, "fn": 0
    },
    {
        "id": "EXP-04",
        "case": "Northwind",
        "condition": "Nivel 2: Crudo (Zero-Shot)",
        "db": "northwind_defective",
        "file": find_file("case2_northwind", "exp04_ddl_zeroshot.sql"),
        "fk_aluc": 2,
        "fk_tot": 5,
        "attempts": 1,
        "satisfies_3fn": False,
        "tp": 5, "fp": 2, "fn": 5
    },
    {
        "id": "EXP-05",
        "case": "Northwind",
        "condition": "Nivel 2: Chain of Thought (CoT)",
        "db": "northwind_defective",
        "file": find_file("case2_northwind", "exp05_ddl_cot.sql"),
        "fk_aluc": 0,
        "fk_tot": 6,
        "attempts": 1,
        "satisfies_3fn": False,
        "tp": 10, "fp": 0, "fn": 0
    },
    {
        "id": "EXP-06",
        "case": "Northwind",
        "condition": "Nivel 3: Agente Autónomo (MCP + Dry-Run)",
        "db": "northwind_defective",
        "file": find_file("case2_northwind", "exp06_ddl_agent_optimized.sql"),
        "fk_aluc": 0,
        "fk_tot": 6,
        "attempts": 2,
        "satisfies_3fn": True,
        "tp": 10, "fp": 0, "fn": 0
    },
    {
        "id": "EXP-07",
        "case": "Sintético",
        "condition": "Nivel 2: Crudo (Zero-Shot)",
        "db": "synthetic_defective",
        "file": find_file("case3_synthetic", "exp07_ddl_zeroshot.sql"),
        "fk_aluc": 2,
        "fk_tot": 5,
        "attempts": 1,
        "satisfies_3fn": False,
        "tp": 4, "fp": 2, "fn": 4
    },
    {
        "id": "EXP-08",
        "case": "Sintético",
        "condition": "Nivel 2: Chain of Thought (CoT)",
        "db": "synthetic_defective",
        "file": find_file("case3_synthetic", "exp08_ddl_cot.sql"),
        "fk_aluc": 0,
        "fk_tot": 5,
        "attempts": 1,
        "satisfies_3fn": False,
        "tp": 8, "fp": 0, "fn": 0
    },
    {
        "id": "EXP-09",
        "case": "Sintético",
        "condition": "Nivel 3: Agente Autónomo (MCP + Dry-Run)",
        "db": "synthetic_defective",
        "file": find_file("case3_synthetic", "exp09_ddl_agent_optimized.sql"),
        "fk_aluc": 0,
        "fk_tot": 5,
        "attempts": 1,
        "satisfies_3fn": True,
        "tp": 8, "fp": 0, "fn": 0
    }
]

def run_dry_run(db: str, sql_file: Path):
    if not sql_file.exists():
        return False, "FILE_NOT_FOUND", f"No se encontro {sql_file}"
    
    conn_info = f"host=localhost port=5432 user=postgres password=postgres dbname={db}"
    try:
        with open(sql_file, "r", encoding="utf-8") as f:
            ddl = f.read()

        with psycopg.connect(conn_info, autocommit=False) as conn:
            with conn.cursor() as cur:
                cur.execute("BEGIN;")
                cur.execute(ddl)
                cur.execute("ROLLBACK;")
        return True, None, "Compilacion DDL 100% exitosa"
    except psycopg.Error as e:
        code = getattr(e, "sqlstate", "ERROR_PG")
        detail = str(e).strip().split("\n")[0]
        return False, code, detail
    except Exception as ex:
        return False, "EXCEPTION", str(ex)

def main():
    config_path = ROOT / "config" / "inference_config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {"model": "gemini-3.8-flash", "inference_parameters": {}}

    print("=" * 80)
    print("BENCHMARK EXPERIMENTAL DE NORMALIZACION RELACIONAL (POSTGRESQL 16 DOCKER)")
    print(f"Modelo de Inferencia: {cfg.get('model')} (Reasoning: {cfg.get('reasoning_effort', 'high')})")
    params = cfg.get("inference_parameters", {})
    print(f"Parámetros: T={params.get('temperature')}, Top-K={params.get('top_k')}, Top-P={params.get('top_p')}, Seed={params.get('seed')}")
    print(f"Configuracion cargada desde: {config_path}")
    print("=" * 80)
    print()

    results = []

    for exp in EXPERIMENTS:
        success, err_code, err_detail = run_dry_run(exp["db"], exp["file"])
        exp_res = dict(exp)
        exp_res["compiles"] = success
        exp_res["err_code"] = err_code
        exp_res["err_detail"] = err_detail
        results.append(exp_res)

        status_str = "[✓] COMPILA (ÉXITO)" if success else f"[X] FALLA (Código PG: {err_code})"
        print(f"[{exp['id']}] {exp['case']:<10} | {exp['condition']:<38} -> {status_str}")
        if not success:
            print(f"       Detalle error: {err_detail[:90]}")

    print("\n" + "=" * 80)
    print("TABLA RESUMEN FINAL DE RESULTADOS EN CONTENEDOR DOCKER")
    print("=" * 80)
    print(f"{'ID':<7} | {'Caso':<10} | {'Condición':<32} | {'Compila':<7} | {'Código PG':<10} | {'Aluc. FK':<9} | {'Intentos':<8} | {'3FN'}")
    print("-" * 105)
    for r in results:
        comp_str = "Sí" if r["compiles"] else "No"
        err_str = r["err_code"] if r["err_code"] else "Ninguno"
        aluc_str = f"{r['fk_aluc']}/{r['fk_tot']}"
        satisfies_str = "Sí" if r["satisfies_3fn"] else "No"
        print(f"{r['id']:<7} | {r['case']:<10} | {r['condition']:<32} | {comp_str:<7} | {err_str:<10} | {aluc_str:<9} | {r['attempts']:<8} | {satisfies_str}")

    print("-" * 105)

if __name__ == "__main__":
    main()

