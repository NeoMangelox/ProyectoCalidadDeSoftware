-- =====================================================================
-- EXP-09: Sintetico - Nivel 3 (Agente Autonomo MCP + Dry-Run)
-- Generado siguiendo el protocolo de 4 fases con saneamiento determinista
-- =====================================================================

-- 1. Normalizacion 3FN: Creacion y poblado de codigos_postales
CREATE TABLE IF NOT EXISTS codigos_postales (
    codigo_postal  VARCHAR(10) CONSTRAINT pk_codigos_postales PRIMARY KEY,
    ciudad         VARCHAR(80) NOT NULL
);

INSERT INTO codigos_postales (codigo_postal, ciudad)
SELECT DISTINCT codigo_postal, initcap(trim(ciudad))
FROM clientes
WHERE codigo_postal IS NOT NULL AND ciudad IS NOT NULL
ON CONFLICT (codigo_postal) DO NOTHING;

ALTER TABLE clientes DROP COLUMN IF EXISTS ciudad;

ALTER TABLE clientes 
    ADD CONSTRAINT fk_clientes_codigos_postales FOREIGN KEY (codigo_postal) 
    REFERENCES codigos_postales (codigo_postal) 
    ON UPDATE CASCADE ON DELETE RESTRICT;

-- 2. Descomposicion 1FN: Creacion y migracion atomica de clientes_telefonos
CREATE TABLE IF NOT EXISTS clientes_telefonos (
    cliente_id  INTEGER NOT NULL REFERENCES clientes (cliente_id) ON DELETE CASCADE,
    telefono    VARCHAR(30) NOT NULL,
    CONSTRAINT pk_clientes_telefonos PRIMARY KEY (cliente_id, telefono)
);

INSERT INTO clientes_telefonos (cliente_id, telefono)
SELECT cliente_id, trim(unnest(regexp_split_to_array(telefonos, '[,;]')))
FROM clientes
WHERE telefonos IS NOT NULL AND telefonos <> ''
ON CONFLICT DO NOTHING;

ALTER TABLE clientes DROP COLUMN IF EXISTS telefonos;

-- 3. Eliminacion de dependencias parciales (2FN)
ALTER TABLE detalle_pedido DROP COLUMN IF EXISTS nombre_producto;
ALTER TABLE detalle_pedido DROP COLUMN IF EXISTS categoria_producto;

-- 4. Saneamiento previo de integridad referencial (huerfanos detectados en Fase 1)
DELETE FROM envios WHERE pedido_id NOT IN (SELECT pedido_id FROM pedidos);
DELETE FROM detalle_pedido WHERE producto_id NOT IN (SELECT producto_id FROM productos)
                              OR pedido_id NOT IN (SELECT pedido_id FROM pedidos);
DELETE FROM pedidos WHERE cliente_id NOT IN (SELECT cliente_id FROM clientes);

-- 5. Creacion de restricciones FOREIGN KEY formales
ALTER TABLE pedidos 
    ADD CONSTRAINT fk_pedidos_clientes FOREIGN KEY (cliente_id) 
    REFERENCES clientes (cliente_id) ON DELETE RESTRICT;

ALTER TABLE detalle_pedido 
    ADD CONSTRAINT fk_detalle_pedidos FOREIGN KEY (pedido_id) 
    REFERENCES pedidos (pedido_id) ON DELETE CASCADE;

ALTER TABLE detalle_pedido 
    ADD CONSTRAINT fk_detalle_productos FOREIGN KEY (producto_id) 
    REFERENCES productos (producto_id) ON DELETE RESTRICT;

ALTER TABLE envios 
    ADD CONSTRAINT fk_envios_pedidos FOREIGN KEY (pedido_id) 
    REFERENCES pedidos (pedido_id) ON DELETE CASCADE;

-- Indices sobre claves foraneas
CREATE INDEX IF NOT EXISTS idx_clientes_codigo_postal ON clientes (codigo_postal);
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente_id ON pedidos (cliente_id);
CREATE INDEX IF NOT EXISTS idx_detalle_pedido_producto_id ON detalle_pedido (producto_id);
CREATE INDEX IF NOT EXISTS idx_envios_pedido_id ON envios (pedido_id);

