#!/usr/bin/env python3
"""Genera defects_manifest.json por caso (verdad de terreno para Precision/Recall/F1)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = {"1FN": "violacion_1FN", "2FN": "violacion_2FN", "3FN": "violacion_3FN", "FK": "falta_integridad_referencial"}


def d(id_, kind, table, cols, desc, fix, fd=None, ref=None, endpoint=None):
    x = {"id": id_, "type": T[kind], "table": table, "columns": cols, "description": desc,
         "expected_fix": fix, "exercised_by": endpoint}
    if fd: x["functional_dependency"] = fd
    if ref: x["missing_fk_references"] = ref
    return x


CASES = {
    "case1_pagila": {
        "case": "Caso 1 - Pagila (Sakila PostgreSQL), nucleo de 15 tablas",
        "defects": [
            d("D1-01", "1FN", "film", ["special_features"], "Lista CSV de extras ('Trailers,Deleted Scenes') en un TEXT.",
              "Tabla film_special_feature(film_id, feature) con PK compuesta."),
            d("D2-01", "2FN", "film_actor", ["actor_full_name"], "Nombre del actor repetido en la tabla puente.",
              "Eliminar la columna; el nombre vive en actor.", fd="actor_id -> actor_full_name (PK: actor_id, film_id)"),
            d("D2-02", "2FN", "film_category", ["category_name"], "Nombre de categoria repetido en la tabla puente.",
              "Eliminar la columna; el nombre vive en category.", fd="category_id -> category_name (PK: film_id, category_id)"),
            d("D3-01", "3FN", "inventory", ["film_title"], "Titulo de la pelicula copiado en inventory.",
              "Eliminar la columna; obtenerlo via JOIN film.", fd="inventory_id -> film_id -> film_title", endpoint="PUT /inventario"),
            d("D3-02", "3FN", "address", ["city_name"], "Nombre de ciudad copiado en address.",
              "Eliminar la columna; obtenerlo via JOIN city.", fd="address_id -> city_id -> city_name"),
            d("D4-01", "FK", "inventory", ["film_id"], "Sin FK a film.", "FOREIGN KEY ... REFERENCES film ON DELETE RESTRICT",
              ref="film(film_id)", endpoint="PUT /inventario"),
            d("D4-02", "FK", "inventory", ["store_id"], "Sin FK a store.", "FOREIGN KEY ... REFERENCES store ON DELETE RESTRICT",
              ref="store(store_id)", endpoint="PUT /inventario"),
            d("D4-03", "FK", "rental", ["inventory_id"], "Sin FK a inventory.", "FOREIGN KEY ... REFERENCES inventory ON DELETE RESTRICT",
              ref="inventory(inventory_id)", endpoint="PUT /inventario"),
            d("D4-04", "FK", "rental", ["customer_id"], "Sin FK a customer.", "FOREIGN KEY ... REFERENCES customer ON DELETE RESTRICT",
              ref="customer(customer_id)"),
            d("D4-05", "FK", "payment", ["rental_id"], "Sin FK a rental.", "FOREIGN KEY ... REFERENCES rental ON DELETE RESTRICT",
              ref="rental(rental_id)"),
        ],
        "known_native_smells": [
            "customer.activebool y customer.active son redundantes (nativo de Sakila).",
            "address.phone / customer.email: atributos de contacto sin tabla propia (nativo, no inyectado).",
        ],
    },
    "case2_northwind": {
        "case": "Caso 2 - Northwind-PostgreSQL, 14 tablas",
        "defects": [
            d("D1-01", "1FN", "customers", ["phones"], "Telefonos separados por coma en una columna (reemplaza a phone).",
              "Tabla customer_phones(customer_id, phone).", endpoint="POST /clientes"),
            d("D2-01", "2FN", "order_details", ["product_name"], "Nombre del producto copiado en la linea de pedido.",
              "Eliminar la columna; JOIN products.", fd="product_id -> product_name (PK: order_id, product_id)", endpoint="POST /pedidos"),
            d("D2-02", "2FN", "order_details", ["quantity_per_unit"], "Presentacion del producto copiada en la linea de pedido.",
              "Eliminar la columna; JOIN products.", fd="product_id -> quantity_per_unit (PK: order_id, product_id)", endpoint="POST /pedidos"),
            d("D3-01", "3FN", "orders", ["shipper_name"], "Nombre del transportista copiado en orders.",
              "Eliminar la columna; JOIN shippers.", fd="order_id -> ship_via -> shipper_name", endpoint="POST /pedidos"),
            d("D4-01", "FK", "orders", ["customer_id"], "Sin FK a customers.", "FOREIGN KEY ... REFERENCES customers ON DELETE RESTRICT",
              ref="customers(customer_id)", endpoint="POST /pedidos"),
            d("D4-02", "FK", "orders", ["ship_via"], "Sin FK a shippers.", "FOREIGN KEY ... REFERENCES shippers ON DELETE RESTRICT",
              ref="shippers(shipper_id)", endpoint="POST /pedidos"),
            d("D4-03", "FK", "order_details", ["order_id"], "Sin FK a orders.", "FOREIGN KEY ... REFERENCES orders ON DELETE CASCADE",
              ref="orders(order_id)", endpoint="POST /pedidos"),
            d("D4-04", "FK", "order_details", ["product_id"], "Sin FK a products.", "FOREIGN KEY ... REFERENCES products ON DELETE RESTRICT",
              ref="products(product_id)", endpoint="POST /pedidos"),
            d("D4-05", "FK", "products", ["category_id"], "Sin FK a categories.", "FOREIGN KEY ... REFERENCES categories ON DELETE RESTRICT",
              ref="categories(category_id)"),
            d("D4-06", "FK", "products", ["supplier_id"], "Sin FK a suppliers.", "FOREIGN KEY ... REFERENCES suppliers ON DELETE RESTRICT",
              ref="suppliers(supplier_id)"),
        ],
        "known_native_smells": [
            "customers/suppliers/employees: postal_code -> city, region, country (3FN latente del Northwind original).",
            "orders.ship_* repite datos de direccion; es una instantanea al momento del envio (defendible, no se puntua).",
            "unit_price/freight como REAL (tipo inadecuado para dinero; no es un defecto relacional).",
            "us_states: tabla aislada sin relaciones (nativo).",
        ],
    },
    "case3_synthetic": {
        "case": "Caso 3 - Sintetico de Control PG, 5 tablas (mutaciones aisladas, estilo DNBench)",
        "defects": [
            d("D1-01", "1FN", "clientes", ["telefonos"], "Lista CSV de telefonos.", "Tabla clientes_telefonos(cliente_id, telefono)."),
            d("D2-01", "2FN", "detalle_pedido", ["nombre_producto"], "Nombre del producto en tabla con PK compuesta.",
              "Eliminar la columna; JOIN productos.", fd="producto_id -> nombre_producto (PK: pedido_id, producto_id)"),
            d("D2-02", "2FN", "detalle_pedido", ["categoria_producto"], "Categoria del producto en tabla con PK compuesta.",
              "Eliminar la columna; JOIN productos.", fd="producto_id -> categoria_producto (PK: pedido_id, producto_id)"),
            d("D3-01", "3FN", "clientes", ["ciudad"], "La ciudad depende del codigo postal, no del cliente.",
              "Tabla codigos_postales(codigo_postal, ciudad) + FK.", fd="cliente_id -> codigo_postal -> ciudad"),
            d("D4-01", "FK", "pedidos", ["cliente_id"], "Sin FK a clientes.", "FOREIGN KEY ... REFERENCES clientes ON DELETE RESTRICT", ref="clientes(cliente_id)"),
            d("D4-02", "FK", "detalle_pedido", ["pedido_id"], "Sin FK a pedidos.", "FOREIGN KEY ... REFERENCES pedidos ON DELETE CASCADE", ref="pedidos(pedido_id)"),
            d("D4-03", "FK", "detalle_pedido", ["producto_id"], "Sin FK a productos.", "FOREIGN KEY ... REFERENCES productos ON DELETE RESTRICT", ref="productos(producto_id)"),
            d("D4-04", "FK", "envios", ["pedido_id"], "Sin FK a pedidos.", "FOREIGN KEY ... REFERENCES pedidos ON DELETE CASCADE", ref="pedidos(pedido_id)"),
        ],
        "known_native_smells": [],
    },
}

for case, m in CASES.items():
    m["dbms"] = "PostgreSQL 16/17"
    m["defect_count"] = len(m["defects"])
    m["defect_count_by_type"] = {t: sum(1 for x in m["defects"] if x["type"] == t) for t in T.values()}
    (ROOT / case / "defects_manifest.json").write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    print(case, m["defect_count"], m["defect_count_by_type"])
