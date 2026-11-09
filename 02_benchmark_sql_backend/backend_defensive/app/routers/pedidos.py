"""POST /pedidos y GET /pedidos/{id} - Northwind (esquema DEFECTUOSO)."""
import asyncpg
from fastapi import APIRouter, HTTPException, Request

from ..models import PedidoIn

router = APIRouter()


@router.post("/pedidos", status_code=201)
async def crear_pedido(body: PedidoIn, request: Request):
    async with request.app.state.nw.acquire() as con:
        async with con.transaction():
            # >>> DEFENSIVE-BEGIN D4-01 (orders.customer_id sin FK)
            if await con.fetchval("SELECT COUNT(*) FROM customers WHERE customer_id=$1", body.customer_id) == 0:
                raise HTTPException(422, f"cliente {body.customer_id!r} no existe")
            # <<< DEFENSIVE-END
            # >>> DEFENSIVE-BEGIN D4-02+D3-01 (ship_via sin FK; shipper_name desnormalizado)
            shipper_name = await con.fetchval("SELECT company_name FROM shippers WHERE shipper_id=$1", body.ship_via)
            if shipper_name is None:
                raise HTTPException(422, f"transportista {body.ship_via} no existe")
            # <<< DEFENSIVE-END
            order_id = await con.fetchval(
                "INSERT INTO orders (customer_id, employee_id, order_date, ship_via, shipper_name, freight,"
                " ship_name, ship_city, ship_country) VALUES ($1,$2,CURRENT_DATE,$3,$4,$5,$6,$7,$8)"
                " RETURNING order_id",
                body.customer_id, body.employee_id, body.ship_via, shipper_name, body.freight,
                body.ship_name, body.ship_city, body.ship_country)
            for it in body.items:
                # >>> DEFENSIVE-BEGIN D4-04+D2-01+D2-02 (product_id sin FK; nombre/presentacion copiados)
                prod = await con.fetchrow(
                    "SELECT product_name, quantity_per_unit FROM products WHERE product_id=$1", it.product_id)
                if prod is None:
                    raise HTTPException(422, f"producto {it.product_id} no existe")
                # <<< DEFENSIVE-END
                try:
                    await con.execute(
                        "INSERT INTO order_details (order_id, product_id, unit_price, quantity, discount,"
                        " product_name, quantity_per_unit) VALUES ($1,$2,$3,$4,$5,$6,$7)",
                        order_id, it.product_id, it.unit_price, it.quantity, it.discount,
                        prod["product_name"], prod["quantity_per_unit"])
                except asyncpg.UniqueViolationError:
                    raise HTTPException(422, f"producto {it.product_id} repetido en el pedido")
    return {"order_id": order_id, "customer_id": body.customer_id, "items": len(body.items)}


@router.get("/pedidos/{order_id}")
async def obtener_pedido(order_id: int, request: Request):
    async with request.app.state.nw.acquire() as con:
        o = await con.fetchrow("SELECT order_id, customer_id, ship_via, shipper_name FROM orders WHERE order_id=$1", order_id)
        if o is None:
            raise HTTPException(404, "pedido no encontrado")
        items = await con.fetch(
            "SELECT product_id, product_name, quantity, unit_price, discount FROM order_details"
            " WHERE order_id=$1 ORDER BY product_id", order_id)
    return {**dict(o), "items": [dict(i) for i in items]}
