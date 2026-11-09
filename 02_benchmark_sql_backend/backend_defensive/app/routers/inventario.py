"""PUT/GET/DELETE /inventario/{id} - Pagila (esquema DEFECTUOSO)."""
from fastapi import APIRouter, HTTPException, Request, Response

from ..models import InventarioIn

router = APIRouter()


@router.put("/inventario/{inventory_id}")
async def poner_inventario(inventory_id: int, body: InventarioIn, request: Request, response: Response):
    async with request.app.state.pg.acquire() as con:
        async with con.transaction():
            # >>> DEFENSIVE-BEGIN D4-01+D3-01 (inventory.film_id sin FK; film_title desnormalizado)
            film_title = await con.fetchval("SELECT title FROM film WHERE film_id=$1", body.film_id)
            if film_title is None:
                raise HTTPException(422, f"pelicula {body.film_id} no existe")
            # <<< DEFENSIVE-END
            # >>> DEFENSIVE-BEGIN D4-02 (inventory.store_id sin FK)
            if await con.fetchval("SELECT COUNT(*) FROM store WHERE store_id=$1", body.store_id) == 0:
                raise HTTPException(422, f"tienda {body.store_id} no existe")
            # <<< DEFENSIVE-END
            inserted = await con.fetchval(
                "INSERT INTO inventory (inventory_id, film_id, store_id, film_title) OVERRIDING SYSTEM VALUE"
                " VALUES ($1,$2,$3,$4) ON CONFLICT (inventory_id) DO UPDATE SET film_id=EXCLUDED.film_id,"
                " store_id=EXCLUDED.store_id, film_title=EXCLUDED.film_title, last_update=now()"
                " RETURNING (xmax = 0)", inventory_id, body.film_id, body.store_id, film_title)
    response.status_code = 201 if inserted else 200
    return {"inventory_id": inventory_id, "film_id": body.film_id, "store_id": body.store_id, "film_title": film_title}


@router.get("/inventario/{inventory_id}")
async def obtener_inventario(inventory_id: int, request: Request):
    async with request.app.state.pg.acquire() as con:
        row = await con.fetchrow(
            "SELECT inventory_id, film_id, store_id, film_title FROM inventory WHERE inventory_id=$1", inventory_id)
    if row is None:
        raise HTTPException(404, "item de inventario no encontrado")
    return dict(row)


@router.delete("/inventario/{inventory_id}", status_code=204)
async def borrar_inventario(inventory_id: int, request: Request):
    async with request.app.state.pg.acquire() as con:
        async with con.transaction():
            # >>> DEFENSIVE-BEGIN D4-03 (rental.inventory_id sin FK: evitar rentas huerfanas)
            if await con.fetchval("SELECT COUNT(*) FROM rental WHERE inventory_id=$1", inventory_id) > 0:
                raise HTTPException(409, "el item tiene rentas asociadas")
            # <<< DEFENSIVE-END
            res = await con.execute("DELETE FROM inventory WHERE inventory_id=$1", inventory_id)
    if res == "DELETE 0":
        raise HTTPException(404, "item de inventario no encontrado")
