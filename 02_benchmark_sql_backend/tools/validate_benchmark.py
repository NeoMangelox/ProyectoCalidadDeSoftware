#!/usr/bin/env python3
"""Verifica contra PostgreSQL REAL que cada defecto del manifiesto existe en
schema_defective.sql y esta corregido en schema_ground_truth.sql.

Requiere una instancia accesible (variables PG* o --dsn-base). Crea y destruye
bases temporales bench_<caso>_{defective,ground_truth}.
Uso: python tools/validate_benchmark.py [--dsn-base postgresql://postgres@localhost:5432]
"""
import argparse, asyncio, json, sys
from pathlib import Path
import asyncpg

ROOT = Path(__file__).resolve().parent.parent
CASES = ["case1_pagila", "case2_northwind", "case3_synthetic"]

FKS = """SELECT tc.table_name, kcu.column_name, ccu.table_name AS ref_table, ccu.column_name AS ref_col
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu USING (constraint_name, table_schema)
JOIN information_schema.constraint_column_usage ccu USING (constraint_name, table_schema)
WHERE tc.constraint_type='FOREIGN KEY' AND tc.table_schema='public'"""
COLS = "SELECT table_name, column_name FROM information_schema.columns WHERE table_schema='public'"


async def load(base, name, files):
    admin = await asyncpg.connect(base + "/postgres")
    await admin.execute(f'DROP DATABASE IF EXISTS "{name}"')
    await admin.execute(f'CREATE DATABASE "{name}"')
    await admin.close()
    con = await asyncpg.connect(f"{base}/{name}")
    for f in files:
        await con.execute(Path(f).read_text())
    return con


async def catalog(con):
    cols = {(r["table_name"], r["column_name"]) for r in await con.fetch(COLS)}
    fks = {(r["table_name"], r["column_name"], r["ref_table"], r["ref_col"]) for r in await con.fetch(FKS)}
    tables = {r["table_name"] for r in await con.fetch(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public'")}
    return tables, cols, fks


async def main(base):
    ok_all = True
    for case in CASES:
        d = ROOT / case
        man = json.loads((d / "defects_manifest.json").read_text())
        cat = {}
        for kind in ("defective", "ground_truth"):
            con = await load(base, f"bench_{case}_{kind}", [d / f"schema_{kind}.sql", d / f"seed_{kind}.sql"])
            cat[kind] = await catalog(con)
            await con.close()
        print(f"\n== {case}: tablas defective={len(cat['defective'][0])}, ground_truth={len(cat['ground_truth'][0])}")
        for x in man["defects"]:
            t, cols = x["table"], x["columns"]
            if x["type"] == "falta_integridad_referencial":
                ref_t, ref_c = x["missing_fk_references"].rstrip(")").split("(")
                key = (t, cols[0], ref_t, ref_c)
                ok = key not in cat["defective"][2] and key in cat["ground_truth"][2]
            else:
                ok = all((t, c) in cat["defective"][1] for c in cols) and \
                     all((t, c) not in cat["ground_truth"][1] for c in cols)
            ok_all &= ok
            print(f"  [{'OK' if ok else 'FALLA'}] {x['id']} {x['type']:<30} {t}.{','.join(cols)}")
    print("\nRESULTADO:", "TODOS LOS DEFECTOS VERIFICADOS" if ok_all else "HAY INCONSISTENCIAS")
    return 0 if ok_all else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsn-base", default="postgresql://postgres@localhost:5432")
    sys.exit(asyncio.run(main(ap.parse_args().dsn_base)))
