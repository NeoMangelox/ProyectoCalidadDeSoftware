CLIENTE = {"customer_id": "TSTCL", "company_name": "Test SAC", "city": "Lima",
           "phones": ["+51 987654321", "+51 912345678", "+51 987654321"]}


def test_crear_y_leer_cliente(client):
    r = client.post("/clientes", json=CLIENTE)
    assert r.status_code == 201
    got = client.get("/clientes/TSTCL").json()
    assert sorted(got["phones"]) == ["+51 912345678", "+51 987654321"]  # sin duplicados


def test_cliente_duplicado_409(client):
    client.post("/clientes", json=CLIENTE)
    assert client.post("/clientes", json=CLIENTE).status_code == 409


def test_telefono_invalido_422(client):
    r = client.post("/clientes", json={**CLIENTE, "customer_id": "TSTC2", "phones": ["abc"]})
    assert r.status_code == 422


def test_pedido_feliz(client):
    body = {"customer_id": "ALFKI", "ship_via": 1, "freight": 10,
            "items": [{"product_id": 1, "quantity": 2, "unit_price": 18.0},
                      {"product_id": 6, "quantity": 1, "unit_price": 31.0, "discount": 0.1}]}
    r = client.post("/pedidos", json=body)
    assert r.status_code == 201
    got = client.get(f"/pedidos/{r.json()['order_id']}").json()
    assert got["shipper_name"] == "Speedy Express"
    assert [i["product_name"] for i in got["items"]] == ["Chai", "Ikura"]


def test_pedido_cliente_inexistente_422(client):
    body = {"customer_id": "NOPE1", "ship_via": 1, "items": [{"product_id": 1, "quantity": 1, "unit_price": 1}]}
    assert client.post("/pedidos", json=body).status_code == 422


def test_pedido_transportista_inexistente_422(client):
    body = {"customer_id": "ALFKI", "ship_via": 99, "items": [{"product_id": 1, "quantity": 1, "unit_price": 1}]}
    assert client.post("/pedidos", json=body).status_code == 422


def test_pedido_producto_inexistente_422_y_atomico(client):
    body = {"customer_id": "ALFKI", "ship_via": 1,
            "items": [{"product_id": 1, "quantity": 1, "unit_price": 1},
                      {"product_id": 999, "quantity": 1, "unit_price": 1}]}
    assert client.post("/pedidos", json=body).status_code == 422
    ok = {"customer_id": "ALFKI", "ship_via": 1, "items": [{"product_id": 1, "quantity": 1, "unit_price": 1}]}
    assert client.post("/pedidos", json=ok).status_code == 201  # el fallido hizo rollback completo


def test_inventario_crear_actualizar(client):
    r = client.put("/inventario/100", json={"film_id": 1, "store_id": 1})
    assert r.status_code == 201 and r.json()["film_title"] == "Academy Dinosaur"
    r = client.put("/inventario/100", json={"film_id": 2, "store_id": 2})
    assert r.status_code == 200
    assert client.get("/inventario/100").json()["film_title"] == "Ace Goldfinger"


def test_inventario_fk_inexistente_422(client):
    assert client.put("/inventario/101", json={"film_id": 4242, "store_id": 1}).status_code == 422
    assert client.put("/inventario/101", json={"film_id": 1, "store_id": 4242}).status_code == 422


def test_inventario_borrar(client):
    assert client.delete("/inventario/3").status_code == 409      # tiene rentas
    client.put("/inventario/102", json={"film_id": 1, "store_id": 1})
    assert client.delete("/inventario/102").status_code == 204    # libre
    assert client.delete("/inventario/102").status_code == 404
