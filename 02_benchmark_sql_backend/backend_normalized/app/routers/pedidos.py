"""POST /pedidos y GET /pedidos/{id} - Northwind (esquema NORMALIZADO / ground truth)."""
import asyncpg
from fastapi import APIRouter, HTTPException, Request

from ..models import PedidoIn

router = APIRouter()


@router.post("/pedidos", status_code=201)
async def crear_pedido(body: PedidoIn, request: Request):
    async with request.app.state.nw.acquire() as con:
        try:
            async with con.transaction():
                order_id = await con.fetchval(
                    "INSERT INTO orders (customer_id, employee_id, order_date, ship_via, freight,"
                    " ship_name, ship_city, ship_country) VALUES ($1,$2,CURRENT_DATE,$3,$4,$5,$6,$7)"
                    " RETURNING order_id",
                    body.customer_id, body.employee_id, body.ship_via, body.freight,
                    body.ship_name, body.ship_city, body.ship_country)
                await con.executemany(
                    "INSERT INTO order_details (order_id, product_id, unit_price, quantity, discount)"
                    " VALUES ($1,$2,$3,$4,$5)",
                    [(order_id, i.product_id, i.unit_price, i.quantity, i.discount) for i in body.items])
        except asyncpg.ForeignKeyViolationError as e:
            raise HTTPException(422, f"referencia inexistente ({e.constraint_name})")
        except asyncpg.UniqueViolationError:
            raise HTTPException(422, "producto repetido en el pedido")
    return {"order_id": order_id, "customer_id": body.customer_id, "items": len(body.items)}


@router.get("/pedidos/{order_id}")
async def obtener_pedido(order_id: int, request: Request):
    async with request.app.state.nw.acquire() as con:
        o = await con.fetchrow(
            "SELECT o.order_id, o.customer_id, o.ship_via, s.company_name AS shipper_name FROM orders o"
            " LEFT JOIN shippers s ON s.shipper_id = o.ship_via WHERE o.order_id=$1", order_id)
        if o is None:
            raise HTTPException(404, "pedido no encontrado")
        items = await con.fetch(
            "SELECT d.product_id, p.product_name, d.quantity, d.unit_price, d.discount FROM order_details d"
            " JOIN products p USING (product_id) WHERE d.order_id=$1 ORDER BY d.product_id", order_id)
    return {**dict(o), "items": [dict(i) for i in items]}
