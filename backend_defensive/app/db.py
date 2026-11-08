"""Pools asyncpg. Una BD por caso: Northwind (clientes/pedidos) y Pagila (inventario)."""
import os
import asyncpg

NORTHWIND_DSN = os.getenv("NORTHWIND_DSN", "postgresql://postgres:postgres@127.0.0.1:5432/northwind_defective")
PAGILA_DSN = os.getenv("PAGILA_DSN", "postgresql://postgres:postgres@127.0.0.1:5432/pagila_defective")


async def open_pools(app):
    app.state.nw = await asyncpg.create_pool(NORTHWIND_DSN, min_size=1, max_size=5)
    app.state.pg = await asyncpg.create_pool(PAGILA_DSN, min_size=1, max_size=5)


async def close_pools(app):
    await app.state.nw.close()
    await app.state.pg.close()
