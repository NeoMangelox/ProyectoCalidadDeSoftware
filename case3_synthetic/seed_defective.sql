-- Caso 3 - datos semilla (esquema defectuoso, con anomalias)
-- Generado por tools/generate_seeds.py (no editar a mano)
BEGIN;
INSERT INTO clientes (cliente_id, nombre, email, telefonos, direccion, codigo_postal, ciudad) OVERRIDING SYSTEM VALUE VALUES
  (1, 'Ana Torres', 'ana@ex.pe', '+51 987654321, +51 912345678', 'Av. Arequipa 123', '15001', 'Lima'),
  (2, 'Luis Quispe', 'luis@ex.pe', '+51 955111222', 'Jr. Union 45', '04001', 'Arequipa'),
  (3, 'Marta Rojas', 'marta@ex.pe', '+51 944000111, +51 944000222;+51 1 4445566', 'Calle Sol 9', '08002', 'Cusco'),
  (4, 'Carlos Vega', 'carlos@ex.pe', NULL, 'Av. Brasil 800', '15036', 'Lima'),
  (5, 'Rosa Diaz', 'rosa@ex.pe', '+51 933222111', 'Av. Grau 77', '04001', 'AREQUIPA');
INSERT INTO productos (producto_id, nombre, categoria, precio_catalogo, stock) OVERRIDING SYSTEM VALUE VALUES
  (1, 'Teclado Mecanico', 'Perifericos', 120.0, 50),
  (2, 'Mouse Optico', 'Perifericos', 35.5, 120),
  (3, 'Monitor 24"', 'Pantallas', 650.0, 15),
  (4, 'Cable HDMI', 'Accesorios', 12.9, 300),
  (5, 'Laptop 14"', 'Computo', 2800.0, 8);
INSERT INTO pedidos (pedido_id, cliente_id, fecha, estado) OVERRIDING SYSTEM VALUE VALUES
  (1, 1, '2026-09-01 10:00:00-05', 'PAGADO'),
  (2, 2, '2026-09-03 15:30:00-05', 'ENVIADO'),
  (3, 3, '2026-09-10 09:15:00-05', 'PENDIENTE'),
  (4, 1, '2026-10-02 18:00:00-05', 'PAGADO'),
  (5, 5, '2026-10-15 11:45:00-05', 'CANCELADO'),
  (6, 77, '2026-10-20 08:00:00-05', 'PENDIENTE');
INSERT INTO detalle_pedido (pedido_id, producto_id, cantidad, precio_unitario, nombre_producto, categoria_producto) VALUES
  (1, 1, 1, 120.0, 'Teclado Mecanico', 'Perifericos'),
  (1, 2, 2, 35.5, 'Mouse Optico USB', 'Perifericos'),
  (2, 3, 1, 650.0, 'Monitor 24"', 'Pantallas'),
  (3, 4, 5, 12.9, 'Cable HDMI', 'Accesorios'),
  (3, 2, 1, 35.5, 'Mouse Optico', 'Perifericos'),
  (4, 5, 1, 2800.0, 'Laptop 14"', 'Computo'),
  (5, 1, 1, 120.0, 'Teclado Mecanico', 'Perifericos'),
  (6, 999, 1, 10.0, 'Producto fantasma', NULL);
INSERT INTO envios (envio_id, pedido_id, direccion_envio, estado, fecha_envio) OVERRIDING SYSTEM VALUE VALUES
  (1, 1, 'Av. Arequipa 123', 'ENTREGADO', '2026-09-02 09:00:00-05'),
  (2, 2, 'Jr. Union 45', 'ENTREGADO', '2026-09-05 09:00:00-05'),
  (3, 4, 'Av. Arequipa 123', 'EN_RUTA', '2026-10-04 09:00:00-05'),
  (4, 999, 'Calle Falsa 123', 'PREPARANDO', NULL);
SELECT setval(pg_get_serial_sequence('clientes', 'cliente_id'), (SELECT COALESCE(MAX(cliente_id), 1) FROM clientes));
SELECT setval(pg_get_serial_sequence('productos', 'producto_id'), (SELECT COALESCE(MAX(producto_id), 1) FROM productos));
SELECT setval(pg_get_serial_sequence('pedidos', 'pedido_id'), (SELECT COALESCE(MAX(pedido_id), 1) FROM pedidos));
SELECT setval(pg_get_serial_sequence('envios', 'envio_id'), (SELECT COALESCE(MAX(envio_id), 1) FROM envios));
COMMIT;
