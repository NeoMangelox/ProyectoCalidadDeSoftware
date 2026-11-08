"""POST /clientes y GET /clientes/{id} - Northwind (esquema NORMALIZADO / ground truth)."""
import asyncpg
from fastapi import APIRouter, HTTPException, Request

from ..models import ClienteIn

router = APIRouter()


@router.post("/clientes", status_code=201)
async def crear_cliente(body: ClienteIn, request: Request):
    async with request.app.state.nw.acquire() as con:
        try:
            async with con.transaction():
                await con.execute(
                    "INSERT INTO customers (customer_id, company_name, contact_name, address, city,"
                    " postal_code, country) VALUES ($1,$2,$3,$4,$5,$6,$7)",
                    body.customer_id, body.company_name, body.contact_name, body.address,
                    body.city, body.postal_code, body.country)
                await con.executemany(
                    "INSERT INTO customer_phones (customer_id, phone) VALUES ($1,$2) ON CONFLICT DO NOTHING",
                    [(body.customer_id, p) for p in body.phones])
        except asyncpg.UniqueViolationError:
            raise HTTPException(409, "customer_id ya existe")
    return {"customer_id": body.customer_id, "phones": sorted(set(body.phones), key=body.phones.index)}


@router.get("/clientes/{customer_id}")
async def obtener_cliente(customer_id: str, request: Request):
    async with request.app.state.nw.acquire() as con:
        row = await con.fetchrow(
            "SELECT c.customer_id, c.company_name, COALESCE(array_agg(p.phone ORDER BY p.phone)"
            " FILTER (WHERE p.phone IS NOT NULL), '{}') AS phones FROM customers c"
            " LEFT JOIN customer_phones p USING (customer_id) WHERE c.customer_id=$1 GROUP BY c.customer_id",
            customer_id)
    if row is None:
        raise HTTPException(404, "cliente no encontrado")
    return dict(row)
