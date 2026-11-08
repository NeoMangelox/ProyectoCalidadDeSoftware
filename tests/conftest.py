"""Pruebas de CONTRATO: el mismo test corre contra backend_defensive y backend_normalized.
   BACKEND_DIR=backend_defensive pytest tests   |   BACKEND_DIR=backend_normalized pytest tests
Requiere PostgreSQL accesible (ADMIN_BASE, por defecto postgresql://postgres:postgres@127.0.0.1:5432)."""
import asyncio, os, sys
from pathlib import Path
import asyncpg, pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
BACKEND = os.environ.get("BACKEND_DIR", "backend_defensive")
KIND = "defective" if BACKEND == "backend_defensive" else "ground_truth"
BASE = os.environ.get("ADMIN_BASE", "postgresql://postgres:postgres@127.0.0.1:5432")


async def _reset(db, case):
    admin = await asyncpg.connect(f"{BASE}/postgres")
    await admin.execute(f"DROP DATABASE IF EXISTS {db} WITH (FORCE)")
    await admin.execute(f"CREATE DATABASE {db}")
    await admin.close()
    con = await asyncpg.connect(f"{BASE}/{db}")
    for f in (f"schema_{KIND}.sql", f"seed_{KIND}.sql"):
        await con.execute((ROOT / case / f).read_text())
    await con.close()


@pytest.fixture()
def client():
    os.environ["NORTHWIND_DSN"] = f"{BASE}/northwind_{KIND}"
    os.environ["PAGILA_DSN"] = f"{BASE}/pagila_{KIND}"
    asyncio.run(_reset(f"northwind_{KIND}", "case2_northwind"))
    asyncio.run(_reset(f"pagila_{KIND}", "case1_pagila"))
    sys.path.insert(0, str(ROOT / BACKEND))
    for m in [m for m in sys.modules if m == "app" or m.startswith("app.")]:
        del sys.modules[m]
    from app.main import app
    with TestClient(app) as c:
        yield c
    sys.path.remove(str(ROOT / BACKEND))
