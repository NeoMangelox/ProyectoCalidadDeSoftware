#!/usr/bin/env python3
"""Genera seed_defective.sql y seed_ground_truth.sql para los 3 casos.

Una sola fuente de datos "limpia" por caso; la version defectuosa se deriva
de ella (desnormalizando) y le agrega anomalias de datos deliberadas
(huerfanos, valores obsoletos, CSV mal formateados) que SOLO existen en la
version defectuosa. Uso:  python tools/generate_seeds.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def emit(tables):
    """tables: lista de (nombre, columnas, filas, columna_identity|None)"""
    out = ["BEGIN;"]
    idents = []
    for name, cols, rows, ident in tables:
        if not rows:
            continue
        ov = " OVERRIDING SYSTEM VALUE" if ident else ""
        out.append(f"INSERT INTO {name} ({', '.join(cols)}){ov} VALUES")
        out.append(",\n".join("  (" + ", ".join(q(x) for x in r) + ")" for r in rows) + ";")
        if ident:
            idents.append((name, ident))
    for name, col in idents:
        out.append(
            f"SELECT setval(pg_get_serial_sequence('{name}', '{col}'), "
            f"(SELECT COALESCE(MAX({col}), 1) FROM {name}));"
        )
    out.append("COMMIT;")
    return "\n".join(out) + "\n"


def write(case, kind, tables, header):
    p = ROOT / case / f"seed_{kind}.sql"
    p.write_text(f"-- {header}\n-- Generado por tools/generate_seeds.py (no editar a mano)\n" + emit(tables))
    print("escrito", p.relative_to(ROOT))


# ----------------------------------------------------------------- CASO 3
def case3():
    cp = [("15001", "Lima"), ("15036", "Lima"), ("04001", "Arequipa"), ("08002", "Cusco")]
    ciudad = dict(cp)
    cli = [  # id, nombre, email, telefonos[], direccion, cp
        (1, "Ana Torres", "ana@ex.pe", ["+51 987654321", "+51 912345678"], "Av. Arequipa 123", "15001"),
        (2, "Luis Quispe", "luis@ex.pe", ["+51 955111222"], "Jr. Union 45", "04001"),
        (3, "Marta Rojas", "marta@ex.pe", ["+51 944000111", "+51 944000222", "+51 1 4445566"], "Calle Sol 9", "08002"),
        (4, "Carlos Vega", "carlos@ex.pe", [], "Av. Brasil 800", "15036"),
        (5, "Rosa Diaz", "rosa@ex.pe", ["+51 933222111"], "Av. Grau 77", "04001"),
    ]
    prod = [
        (1, "Teclado Mecanico", "Perifericos", 120.00, 50),
        (2, "Mouse Optico", "Perifericos", 35.50, 120),
        (3, 'Monitor 24"', "Pantallas", 650.00, 15),
        (4, "Cable HDMI", "Accesorios", 12.90, 300),
        (5, 'Laptop 14"', "Computo", 2800.00, 8),
    ]
    ped = [
        (1, 1, "2026-09-01 10:00:00-05", "PAGADO"), (2, 2, "2026-09-03 15:30:00-05", "ENVIADO"),
        (3, 3, "2026-09-10 09:15:00-05", "PENDIENTE"), (4, 1, "2026-10-02 18:00:00-05", "PAGADO"),
        (5, 5, "2026-10-15 11:45:00-05", "CANCELADO"),
    ]
    det = [(1, 1, 1, 120.00), (1, 2, 2, 35.50), (2, 3, 1, 650.00), (3, 4, 5, 12.90),
           (3, 2, 1, 35.50), (4, 5, 1, 2800.00), (5, 1, 1, 120.00)]
    env = [(1, 1, "Av. Arequipa 123", "ENTREGADO", "2026-09-02 09:00:00-05"),
           (2, 2, "Jr. Union 45", "ENTREGADO", "2026-09-05 09:00:00-05"),
           (3, 4, "Av. Arequipa 123", "EN_RUTA", "2026-10-04 09:00:00-05")]
    P = {p[0]: p for p in prod}

    # ---- ground truth
    gt = [
        ("codigos_postales", ["codigo_postal", "ciudad"], cp, None),
        ("clientes", ["cliente_id", "nombre", "email", "direccion", "codigo_postal"],
         [(c[0], c[1], c[2], c[4], c[5]) for c in cli], "cliente_id"),
        ("clientes_telefonos", ["cliente_id", "telefono"], [(c[0], t) for c in cli for t in c[3]], None),
        ("productos", ["producto_id", "nombre", "categoria", "precio_catalogo", "stock"], prod, "producto_id"),
        ("pedidos", ["pedido_id", "cliente_id", "fecha", "estado"], ped, "pedido_id"),
        ("detalle_pedido", ["pedido_id", "producto_id", "cantidad", "precio_unitario"], det, None),
        ("envios", ["envio_id", "pedido_id", "direccion_envio", "estado", "fecha_envio"], env, "envio_id"),
    ]
    # ---- defectuoso (con anomalias de datos)
    telcsv = {1: "+51 987654321, +51 912345678", 2: "+51 955111222",
              3: "+51 944000111, +51 944000222;+51 1 4445566",  # separador mixto (mal formateado)
              4: None, 5: "+51 933222111"}
    ciu = {c[0]: ciudad[c[5]] for c in cli}
    ciu[5] = "AREQUIPA"  # inconsistente con la ciudad de 04001 -> anomalia de actualizacion
    dd = [
        ("clientes", ["cliente_id", "nombre", "email", "telefonos", "direccion", "codigo_postal", "ciudad"],
         [(c[0], c[1], c[2], telcsv[c[0]], c[4], c[5], ciu[c[0]]) for c in cli], "cliente_id"),
        ("productos", ["producto_id", "nombre", "categoria", "precio_catalogo", "stock"], prod, "producto_id"),
        ("pedidos", ["pedido_id", "cliente_id", "fecha", "estado"],
         ped + [(6, 77, "2026-10-20 08:00:00-05", "PENDIENTE")], "pedido_id"),  # huerfano: cliente 77
        ("detalle_pedido",
         ["pedido_id", "producto_id", "cantidad", "precio_unitario", "nombre_producto", "categoria_producto"],
         [(p, pr, c, pu, ("Mouse Optico USB" if (p, pr) == (1, 2) else P[pr][1]), P[pr][2]) for p, pr, c, pu in det]
         + [(6, 999, 1, 10.00, "Producto fantasma", None)], None),  # huerfano: producto 999
        ("envios", ["envio_id", "pedido_id", "direccion_envio", "estado", "fecha_envio"],
         env + [(4, 999, "Calle Falsa 123", "PREPARANDO", None)], "envio_id"),  # huerfano: pedido 999
    ]
    write("case3_synthetic", "ground_truth", gt, "Caso 3 - datos semilla (esquema normalizado)")
    write("case3_synthetic", "defective", dd, "Caso 3 - datos semilla (esquema defectuoso, con anomalias)")


# ----------------------------------------------------------------- CASO 2
def case2():
    region = [(1, "Eastern"), (2, "Western")]
    terr = [("01581", "Westboro", 1), ("98004", "Bellevue", 2)]
    emp = [(1, "Davolio", "Nancy", "Sales Representative", None), (2, "Fuller", "Andrew", "Vice President, Sales", 1)]
    et = [(1, "01581"), (2, "98004")]
    cat = [(1, "Beverages", "Soft drinks, coffees, teas"), (2, "Condiments", "Sweet and savory sauces"),
           (3, "Seafood", "Seaweed and fish")]
    sup = [(1, "Exotic Liquids", "Charlotte Cooper", "London", "UK", "(171) 555-2222"),
           (2, "New Orleans Cajun Delights", "Shelley Burke", "New Orleans", "USA", "(100) 555-4822"),
           (3, "Pavlova, Ltd.", "Ian Devling", "Melbourne", "Australia", "(03) 444-2343")]
    shp = [(1, "Speedy Express", "(503) 555-9831"), (2, "United Package", "(503) 555-3199"),
           (3, "Federal Shipping", "(503) 555-9931")]
    SH = {s[0]: s[1] for s in shp}
    demo = [("STD", "Standard"), ("PRM", "Premium")]
    states = [(1, "Alabama", "AL", "south"), (2, "Alaska", "AK", "west")]
    cust = [  # id, company, contact, address, city, postal, country, phones[]
        ("ALFKI", "Alfreds Futterkiste", "Maria Anders", "Obere Str. 57", "Berlin", "12209", "Germany",
         ["030-0074321", "030-0076545"]),
        ("ANATR", "Ana Trujillo Emparedados", "Ana Trujillo", "Avda. de la Constitucion 2222", "Mexico D.F.",
         "05021", "Mexico", ["(5) 555-4729"]),
        ("BONAP", "Bon app'", "Laurence Lebihan", "12, rue des Bouchers", "Marseille", "13008", "France",
         ["91.24.45.40", "91.24.45.41", "91.24.45.42"]),
        ("CACTU", "Cactus Comidas para llevar", "Patricio Simpson", "Cerrito 333", "Buenos Aires", "1010",
         "Argentina", []),
        ("DRACD", "Drachenblut Delikatessen", "Sven Ottlieb", "Walserweg 21", "Aachen", "52066", "Germany",
         ["0241-039123"]),
    ]
    ccd = [("ALFKI", "PRM"), ("BONAP", "STD")]
    prod = [(1, "Chai", 1, 1, "10 boxes x 20 bags", 18.0, 39, 0, 10, 0),
            (2, "Chang", 1, 1, "24 - 12 oz bottles", 19.0, 17, 40, 25, 0),
            (3, "Aniseed Syrup", 1, 2, "12 - 550 ml bottles", 10.0, 13, 70, 25, 0),
            (4, "Chef Anton's Cajun Seasoning", 2, 2, "48 - 6 oz jars", 22.0, 53, 0, 0, 0),
            (5, "Chef Anton's Gumbo Mix", 2, 2, "36 boxes", 21.35, 0, 0, 0, 1),
            (6, "Ikura", 3, 3, "12 - 200 ml jars", 31.0, 31, 0, 0, 0),
            (7, "Konbu", 3, 3, "2 kg box", 6.0, 24, 0, 5, 0),
            (8, "Carnarvon Tigers", 3, 3, "16 kg pkg.", 62.5, 42, 0, 0, 0)]
    P = {p[0]: p for p in prod}
    ordr = [  # id, cust, emp, order_date, required, shipped, ship_via, freight, ship_name, ship_city, ship_country
        (1, "ALFKI", 1, "2026-09-01", "2026-09-15", "2026-09-03", 1, 32.38, "Alfreds Futterkiste", "Berlin", "Germany"),
        (2, "ANATR", 2, "2026-09-05", "2026-09-19", "2026-09-08", 2, 11.61, "Ana Trujillo Emparedados", "Mexico D.F.", "Mexico"),
        (3, "BONAP", 1, "2026-09-12", "2026-09-26", "2026-09-14", 3, 65.83, "Bon app'", "Marseille", "France"),
        (4, "ALFKI", 2, "2026-10-02", "2026-10-16", None, 1, 41.34, "Alfreds Futterkiste", "Berlin", "Germany"),
    ]
    od = [(1, 1, 18.0, 10, 0.0), (1, 2, 19.0, 5, 0.05), (2, 3, 10.0, 20, 0.0),
          (3, 6, 31.0, 2, 0.0), (3, 8, 62.5, 1, 0.1), (4, 4, 22.0, 3, 0.0)]

    common = [
        ("region", ["region_id", "region_description"], region, None),
        ("territories", ["territory_id", "territory_description", "region_id"], terr, None),
        ("employees", ["employee_id", "last_name", "first_name", "title", "reports_to"], emp, None),
        ("employee_territories", ["employee_id", "territory_id"], et, None),
        ("categories", ["category_id", "category_name", "description"], cat, None),
        ("suppliers", ["supplier_id", "company_name", "contact_name", "city", "country", "phone"], sup, None),
        ("shippers", ["shipper_id", "company_name", "phone"], shp, None),
        ("customer_demographics", ["customer_type_id", "customer_desc"], demo, None),
        ("us_states", ["state_id", "state_name", "state_abbr", "state_region"], states, None),
    ]
    pcols = ["product_id", "product_name", "supplier_id", "category_id", "quantity_per_unit",
             "unit_price", "units_in_stock", "units_on_order", "reorder_level", "discontinued"]
    ocols = ["order_id", "customer_id", "employee_id", "order_date", "required_date", "shipped_date",
             "ship_via", "freight", "ship_name", "ship_city", "ship_country"]
    ccols = ["customer_id", "company_name", "contact_name", "address", "city", "postal_code", "country"]
    base_c = lambda c: c[:7]
    gt = common + [
        ("customers", ccols, [base_c(c) for c in cust], None),
        ("customer_phones", ["customer_id", "phone"], [(c[0], t) for c in cust for t in c[7]], None),
        ("customer_customer_demo", ["customer_id", "customer_type_id"], ccd, None),
        ("products", pcols, prod, None),
        ("orders", ocols, ordr, "order_id"),
        ("order_details", ["order_id", "product_id", "unit_price", "quantity", "discount"], od, None),
    ]
    phonecsv = {"ALFKI": "030-0074321, 030-0076545", "ANATR": "(5) 555-4729",
                "BONAP": "91.24.45.40,91.24.45.41 / 91.24.45.42",  # mal formateado
                "CACTU": None, "DRACD": "0241-039123"}
    shipname = {o[0]: SH[o[6]] for o in ordr}
    shipname[3] = "Federal Shipping Co."  # obsoleto: el shipper se llama 'Federal Shipping'
    dd = common + [
        ("customers", ccols[:7] + ["phones"], [base_c(c) + (phonecsv[c[0]],) for c in cust], None),
        ("customer_customer_demo", ["customer_id", "customer_type_id"], ccd, None),
        ("products", pcols, prod, None),
        ("orders", ocols + ["shipper_name"],
         [o + (shipname[o[0]],) for o in ordr]
         + [(5, "ZZZZZ", 1, "2026-10-20", "2026-11-03", None, 99, 5.0, "Cliente fantasma", "Nowhere", "None", None)],
         "order_id"),
        ("order_details",
         ["order_id", "product_id", "unit_price", "quantity", "discount", "product_name", "quantity_per_unit"],
         [d + (("Chang Beer" if (d[0], d[1]) == (1, 2) else P[d[1]][1]), P[d[1]][4]) for d in od]
         + [(5, 999, 1.0, 1, 0.0, "Producto fantasma", None)], None),
    ]
    write("case2_northwind", "ground_truth", gt, "Caso 2 - datos semilla (esquema normalizado)")
    write("case2_northwind", "defective", dd, "Caso 2 - datos semilla (esquema defectuoso, con anomalias)")


# ----------------------------------------------------------------- CASO 1
def case1():
    country = [(1, "Peru"), (2, "Spain")]
    city = [(1, "Lima", 1), (2, "Cusco", 1), (3, "Madrid", 2)]
    lang = [(1, "English"), (2, "Spanish")]
    actor = [(1, "Penelope", "Guiness"), (2, "Nick", "Wahlberg"), (3, "Ed", "Chase"), (4, "Jennifer", "Davis")]
    cat = [(1, "Action"), (2, "Comedy"), (3, "Drama")]
    CAT = dict(cat)
    ACT = {a[0]: f"{a[1]} {a[2]}" for a in actor}
    addr = [(1, "47 MySakila Drive", "Lima", 1, "15001", "555-0001"), (2, "28 MySQL Boulevard", "Cusco", 2, "08002", "555-0002"),
            (3, "23 Workhaven Lane", "Lima", 1, "15036", "555-0003"), (4, "1411 Lillydale Drive", "Madrid", 3, "28001", "555-0004"),
            (5, "1913 Hanoi Way", "Lima", 1, "15001", "555-0005"), (6, "1121 Loja Avenue", "Cusco", 2, "08002", "555-0006"),
            (7, "692 Joliet Street", "Madrid", 3, "28002", "555-0007")]
    CITY = {c[0]: c[1] for c in city}
    staff = [(1, "Mike", "Hillyer", 3, "mike@sakila.example", 1, "mike"), (2, "Jon", "Stephens", 4, "jon@sakila.example", 2, "jon")]
    store = [(1, 1, 1), (2, 2, 2)]
    cust = [(1, 1, "Mary", "Smith", "mary@x.example", 5), (2, 1, "Patricia", "Johnson", "pat@x.example", 6),
            (3, 2, "Linda", "Williams", "linda@x.example", 7)]
    film = [  # id, title, year, lang, rate, len, repl, rating, features[]
        (1, "Academy Dinosaur", 2006, 1, 0.99, 86, 20.99, "PG", ["Deleted Scenes", "Behind the Scenes"]),
        (2, "Ace Goldfinger", 2006, 1, 4.99, 48, 12.99, "G", ["Trailers", "Deleted Scenes"]),
        (3, "Adaptation Holes", 2006, 1, 2.99, 50, 18.99, "NC-17", ["Trailers", "Deleted Scenes"]),
        (4, "Affair Prejudice", 2006, 1, 2.99, 117, 26.99, "G", ["Commentaries", "Behind the Scenes"]),
        (5, "African Egg", 2006, 2, 2.99, 130, 22.99, "G", ["Deleted Scenes"]),
        (6, "Agent Truman", 2006, 2, 2.99, 169, 17.99, "PG", []),
    ]
    FT = {f[0]: f[1] for f in film}
    fa = [(1, 1), (2, 1), (1, 2), (3, 3), (4, 4), (2, 5), (4, 6)]
    fc = [(1, 3), (2, 1), (3, 2), (4, 3), (5, 2), (6, 1)]
    inv = [(1, 1, 1), (2, 1, 2), (3, 2, 1), (4, 3, 1), (5, 4, 2), (6, 5, 1), (7, 6, 2), (8, 2, 2)]
    ren = [(1, "2026-05-24 22:53:30+00", 1, 1, "2026-05-26 22:04:30+00", 1),
           (2, "2026-05-24 23:03:39+00", 3, 2, None, 1),
           (3, "2026-05-25 00:00:40+00", 4, 3, "2026-06-02 01:20:40+00", 2),
           (4, "2026-05-25 00:02:21+00", 5, 1, None, 2),
           (5, "2026-06-03 10:00:00+00", 1, 2, "2026-06-10 10:00:00+00", 1)]
    pay = [(1, 1, 1, 1, 2.99, "2026-05-25 10:00:00+00"), (2, 2, 1, 2, 4.99, "2026-05-25 11:00:00+00"),
           (3, 3, 2, 3, 0.99, "2026-05-26 09:00:00+00"), (4, 1, 2, 4, 5.99, "2026-05-26 12:00:00+00"),
           (5, 2, 1, 5, 2.99, "2026-06-03 10:30:00+00")]

    fcols = ["film_id", "title", "release_year", "language_id", "rental_rate", "length", "replacement_cost", "rating"]
    film_base = [f[:8] for f in film]
    head = [("country", ["country_id", "country"], country, "country_id"),
            ("city", ["city_id", "city", "country_id"], city, "city_id"),
            ("language", ["language_id", "name"], lang, "language_id"),
            ("actor", ["actor_id", "first_name", "last_name"], actor, "actor_id"),
            ("category", ["category_id", "name"], cat, "category_id")]
    acols = ["address_id", "address", "district", "city_id", "postal_code", "phone"]
    tail_people = [
        ("staff", ["staff_id", "first_name", "last_name", "address_id", "email", "store_id", "username"], staff, "staff_id"),
        ("store", ["store_id", "manager_staff_id", "address_id"], store, "store_id"),
        ("customer", ["customer_id", "store_id", "first_name", "last_name", "email", "address_id"], cust, "customer_id"),
    ]
    gt = head + [("address", acols, addr, "address_id")] + tail_people + [
        ("film", fcols, film_base, "film_id"),
        ("film_special_feature", ["film_id", "feature"], [(f[0], x) for f in film for x in f[8]], None),
        ("film_actor", ["actor_id", "film_id"], fa, None),
        ("film_category", ["film_id", "category_id"], fc, None),
        ("inventory", ["inventory_id", "film_id", "store_id"], inv, "inventory_id"),
        ("rental", ["rental_id", "rental_date", "inventory_id", "customer_id", "return_date", "staff_id"], ren, "rental_id"),
        ("payment", ["payment_id", "customer_id", "staff_id", "rental_id", "amount", "payment_date"], pay, "payment_id"),
    ]
    featcsv = {1: "Deleted Scenes,Behind the Scenes", 2: "Trailers,Deleted Scenes",
               3: "Trailers, Deleted Scenes", 4: "Commentaries,Behind the Scenes",  # 3: espacio tras la coma
               5: "Deleted Scenes", 6: None}
    cname = {a[0]: CITY[a[3]] for a in addr}
    cname[6] = "cusco "  # inconsistente (minuscula + espacio)
    ititle = {i[0]: FT[i[1]] for i in inv}
    ititle[8] = "Ace Goldfinger (old)"  # obsoleto tras renombrar la pelicula
    dd = head + [("address", acols[:4] + ["city_name"] + acols[4:], [a[:4] + (cname[a[0]],) + a[4:] for a in addr], "address_id")] + tail_people + [
        ("film", fcols + ["special_features"], [f[:8] + (featcsv[f[0]],) for f in film], "film_id"),
        ("film_actor", ["actor_id", "film_id", "actor_full_name"],
         [(a, f, ("Nicholas Wahlberg" if (a, f) == (2, 5) else ACT[a])) for a, f in fa], None),
        ("film_category", ["film_id", "category_id", "category_name"], [(f, c, CAT[c]) for f, c in fc], None),
        ("inventory", ["inventory_id", "film_id", "store_id", "film_title"],
         [i + (ititle[i[0]],) for i in inv] + [(9, 999, 1, None)], "inventory_id"),  # huerfano: film 999
        ("rental", ["rental_id", "rental_date", "inventory_id", "customer_id", "return_date", "staff_id"],
         ren + [(6, "2026-06-20 10:00:00+00", 999, 77, None, 1)], "rental_id"),  # huerfano: inventario 999, cliente 77
        ("payment", ["payment_id", "customer_id", "staff_id", "rental_id", "amount", "payment_date"],
         pay + [(6, 1, 1, 999, 3.99, "2026-06-20 11:00:00+00")], "payment_id"),  # huerfano: renta 999
    ]
    write("case1_pagila", "ground_truth", gt, "Caso 1 - datos semilla (esquema normalizado)")
    write("case1_pagila", "defective", dd, "Caso 1 - datos semilla (esquema defectuoso, con anomalias)")


if __name__ == "__main__":
    case1(); case2(); case3()
