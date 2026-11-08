from contextlib import asynccontextmanager
from fastapi import FastAPI

from .db import close_pools, open_pools
from .routers import clientes, inventario, pedidos


@asynccontextmanager
async def lifespan(app: FastAPI):
    await open_pools(app)
    yield
    await close_pools(app)


app = FastAPI(title="Mini-backend SQL-Backend benchmark", lifespan=lifespan)
app.include_router(clientes.router)
app.include_router(pedidos.router)
app.include_router(inventario.router)
