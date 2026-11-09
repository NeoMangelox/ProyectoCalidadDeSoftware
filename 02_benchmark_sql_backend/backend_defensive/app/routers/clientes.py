"""POST /clientes y GET /clientes/{id} - Northwind (esquema DEFECTUOSO).
Marcadores DEFENSIVE-BEGIN/END delimitan las lineas forzadas por el esquema (para SLOC_def)."""
import re
import asyncpg
from fastapi import APIRouter, HTTPException, Request

from ..models import ClienteIn

router = APIRouter()


@router.post("/clientes", status_code=201)
async def crear_cliente(body: ClienteIn, request: Request):
    # >>> DEFENSIVE-BEGIN D1-01 (1FN: customers.phones es un VARCHAR CSV)
    telefonos = []
    for t in body.phones:
        if t not in telefonos:
            telefonos.append(t)
    phones_csv = ",".join(telefonos) if telefonos else None
    if phones_csv is not None and len(phones_csv) > 255:
        raise HTTPException(422, "la lista de telefonos excede 255 caracteres")
    # <<< DEFENSIVE-END
    async with request.app.state.nw.acquire() as con:
        try:
            await con.execute(
                "INSERT INTO customers (customer_id, company_name, contact_name, address, city,"
                " postal_code, country, phones) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)",
                body.customer_id, body.company_name, body.contact_name, body.address,
                body.city, body.postal_code, body.country, phones_csv)
        except asyncpg.UniqueViolationError:
            raise HTTPException(409, "customer_id ya existe")
    return {"customer_id": body.customer_id, "phones": telefonos}


@router.get("/clientes/{customer_id}")
async def obtener_cliente(customer_id: str, request: Request):
    async with request.app.state.nw.acquire() as con:
        row = await con.fetchrow("SELECT * FROM customers WHERE customer_id=$1", customer_id)
    if row is None:
        raise HTTPException(404, "cliente no encontrado")
    # >>> DEFENSIVE-BEGIN D1-01 (parseo manual del CSV; separadores mixtos en los datos)
    phones = [p.strip() for p in re.split(r"[,;/]", row["phones"] or "") if p.strip()]
    # <<< DEFENSIVE-END
    return {"customer_id": row["customer_id"], "company_name": row["company_name"], "phones": phones}
