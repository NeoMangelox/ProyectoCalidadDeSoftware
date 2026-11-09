-- =====================================================================
-- CASO 3 - Sintetico de Control PG | schema_ground_truth.sql
-- Referencia normalizada (3FN/BCNF) con todas las FK e indices de FK.
-- Tablas: 7 (5 originales + clientes_telefonos + codigos_postales)
-- =====================================================================

CREATE TABLE codigos_postales (                       -- corrige D3-01
    codigo_postal  VARCHAR(10) PRIMARY KEY,
    ciudad         VARCHAR(80) NOT NULL
);

CREATE TABLE clientes (
    cliente_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    email          VARCHAR(150) NOT NULL UNIQUE,
    direccion      VARCHAR(200),
    codigo_postal  VARCHAR(10) REFERENCES codigos_postales (codigo_postal)
                   ON UPDATE CASCADE ON DELETE RESTRICT,
    creado_en      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE clientes_telefonos (                     -- corrige D1-01
    cliente_id  INTEGER NOT NULL REFERENCES clientes (cliente_id) ON DELETE CASCADE,
    telefono    VARCHAR(30) NOT NULL,
    PRIMARY KEY (cliente_id, telefono)
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
    cliente_id  INTEGER NOT NULL REFERENCES clientes (cliente_id) ON DELETE RESTRICT,  -- D4-01
    fecha       TIMESTAMPTZ NOT NULL DEFAULT now(),
    estado      VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE'
                CHECK (estado IN ('PENDIENTE','PAGADO','ENVIADO','CANCELADO'))
);

CREATE TABLE detalle_pedido (                         -- D2-01/D2-02 eliminados
    pedido_id        INTEGER NOT NULL REFERENCES pedidos (pedido_id) ON DELETE CASCADE,       -- D4-02
    producto_id      INTEGER NOT NULL REFERENCES productos (producto_id) ON DELETE RESTRICT,  -- D4-03
    cantidad         INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario  NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (pedido_id, producto_id)
);

CREATE TABLE envios (
    envio_id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pedido_id        INTEGER NOT NULL REFERENCES pedidos (pedido_id) ON DELETE CASCADE,  -- D4-04
    direccion_envio  VARCHAR(200) NOT NULL,
    estado           VARCHAR(20) NOT NULL DEFAULT 'PREPARANDO'
                     CHECK (estado IN ('PREPARANDO','EN_RUTA','ENTREGADO')),
    fecha_envio      TIMESTAMPTZ
);

-- Indices sobre FK (PostgreSQL no los crea automaticamente)
CREATE INDEX idx_clientes_codigo_postal ON clientes (codigo_postal);
CREATE INDEX idx_pedidos_cliente        ON pedidos (cliente_id);
CREATE INDEX idx_detalle_producto       ON detalle_pedido (producto_id);
CREATE INDEX idx_envios_pedido          ON envios (pedido_id);
