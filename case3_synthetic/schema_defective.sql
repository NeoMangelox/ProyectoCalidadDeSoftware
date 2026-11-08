-- =====================================================================
-- CASO 3 - Sintetico de Control PG | schema_defective.sql
-- Dialecto: PostgreSQL 16/17 | 5 tablas | 8 instancias de defecto aisladas
-- Cada defecto lleva un ID (D<tipo>-<n>) que coincide con defects_manifest.json
-- =====================================================================

CREATE TABLE clientes (
    cliente_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    email          VARCHAR(150) NOT NULL UNIQUE,
    telefonos      VARCHAR(255),               -- [D1-01] 1FN: lista CSV de telefonos
    direccion      VARCHAR(200),
    codigo_postal  VARCHAR(10),
    ciudad         VARCHAR(80),                -- [D3-01] 3FN: codigo_postal -> ciudad
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE productos (
    producto_id      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    categoria        VARCHAR(50),
    precio_catalogo  NUMERIC(10,2) NOT NULL CHECK (precio_catalogo >= 0),
    stock            INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

CREATE TABLE pedidos (
    pedido_id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id  INTEGER NOT NULL,              -- [D4-01] sin FOREIGN KEY -> clientes
    fecha       TIMESTAMPTZ NOT NULL DEFAULT now(),
    estado      VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE'
                CHECK (estado IN ('PENDIENTE','PAGADO','ENVIADO','CANCELADO'))
);

CREATE TABLE detalle_pedido (
    pedido_id           INTEGER NOT NULL,      -- [D4-02] sin FOREIGN KEY -> pedidos
    producto_id         INTEGER NOT NULL,      -- [D4-03] sin FOREIGN KEY -> productos
    cantidad            INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario     NUMERIC(10,2) NOT NULL,   -- legitimo: precio historico de la venta
    nombre_producto     VARCHAR(100) NOT NULL,    -- [D2-01] 2FN: depende solo de producto_id
    categoria_producto  VARCHAR(50),              -- [D2-02] 2FN: depende solo de producto_id
    PRIMARY KEY (pedido_id, producto_id)
);

CREATE TABLE envios (
    envio_id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pedido_id        INTEGER NOT NULL,         -- [D4-04] sin FOREIGN KEY -> pedidos
    direccion_envio  VARCHAR(200) NOT NULL,
    estado           VARCHAR(20) NOT NULL DEFAULT 'PREPARANDO'
                     CHECK (estado IN ('PREPARANDO','EN_RUTA','ENTREGADO')),
    fecha_envio      TIMESTAMPTZ
);
