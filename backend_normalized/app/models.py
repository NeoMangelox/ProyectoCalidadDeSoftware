"""Modelos de entrada. Validacion de FORMATO (identica en ambos backends; no cuenta como SLOC_def)."""
import re
from pydantic import BaseModel, Field, field_validator

PHONE_RE = re.compile(r"^[0-9+()\-. ]{5,24}$")


class ClienteIn(BaseModel):
    customer_id: str = Field(min_length=1, max_length=5)
    company_name: str = Field(min_length=1, max_length=40)
    contact_name: str | None = Field(None, max_length=30)
    address: str | None = Field(None, max_length=60)
    city: str | None = Field(None, max_length=15)
    postal_code: str | None = Field(None, max_length=10)
    country: str | None = Field(None, max_length=15)
    phones: list[str] = Field(default_factory=list)

    @field_validator("phones")
    @classmethod
    def _formato_telefonos(cls, v):
        for p in v:
            if not PHONE_RE.match(p.strip()):
                raise ValueError(f"telefono con formato invalido: {p!r}")
        return [p.strip() for p in v]


class ItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    unit_price: float = Field(ge=0)
    discount: float = Field(0, ge=0, le=1)


class PedidoIn(BaseModel):
    customer_id: str = Field(min_length=1, max_length=5)
    employee_id: int | None = None
    ship_via: int
    freight: float | None = Field(None, ge=0)
    ship_name: str | None = Field(None, max_length=40)
    ship_city: str | None = Field(None, max_length=15)
    ship_country: str | None = Field(None, max_length=15)
    items: list[ItemIn] = Field(min_length=1)


class InventarioIn(BaseModel):
    film_id: int
    store_id: int
