"""PUT/GET/DELETE /inventario/{id} - Pagila (esquema NORMALIZADO / ground truth)."""
import asyncpg
from fastapi import APIRouter, HTTPException, Request, Response

from ..models import InventarioIn

router = APIRouter()


@router.put("/inventario/{inventory_id}")
async def poner_inventario(inventory_id: int, body: InventarioIn, request: Request, response: Response):
    async with request.app.state.pg.acquire() as con:
        try:
            inserted = await con.fetchval(
                "INSERT INTO inventory (inventory_id, film_id, store_id) OVERRIDING SYSTEM VALUE"
                " VALUES ($1,$2,$3) ON CONFLICT (inventory_id) DO UPDATE SET film_id=EXCLUDED.film_id,"
                " store_id=EXCLUDED.store_id, last_update=now() RETURNING (xmax = 0)",
                inventory_id, body.film_id, body.store_id)
        except asyncpg.ForeignKeyViolationError as e:
            raise HTTPException(422, f"referencia inexistente ({e.constraint_name})")
        title = await con.fetchval("SELECT title FROM film WHERE film_id=$1", body.film_id)
    response.status_code = 201 if inserted else 200
    return {"inventory_id": inventory_id, "film_id": body.film_id, "store_id": body.store_id, "film_title": title}


@router.get("/inventario/{inventory_id}")
async def obtener_inventario(inventory_id: int, request: Request):
    async with request.app.state.pg.acquire() as con:
        row = await con.fetchrow(
            "SELECT i.inventory_id, i.film_id, i.store_id, f.title AS film_title FROM inventory i"
            " JOIN film f USING (film_id) WHERE i.inventory_id=$1", inventory_id)
    if row is None:
        raise HTTPException(404, "item de inventario no encontrado")
    return dict(row)


@router.delete("/inventario/{inventory_id}", status_code=204)
async def borrar_inventario(inventory_id: int, request: Request):
    async with request.app.state.pg.acquire() as con:
        try:
            res = await con.execute("DELETE FROM inventory WHERE inventory_id=$1", inventory_id)
        except asyncpg.ForeignKeyViolationError:
            raise HTTPException(409, "el item tiene rentas asociadas")
    if res == "DELETE 0":
        raise HTTPException(404, "item de inventario no encontrado")
