-- =====================================================================
-- EXP-08: Sintetico - Nivel 2 (Chain of Thought / CoT sin conexion MCP)
-- Generado mediante razonamiento estructurado en 5 fases de SKILL.md
-- =====================================================================

-- Fase 1: Creacion de tabla 1FN clientes_telefonos
CREATE TABLE clientes_telefonos (
    cliente_id  INTEGER NOT NULL REFERENCES clientes (cliente_id) ON DELETE CASCADE,
    telefono    VARCHAR(30) NOT NULL,
    PRIMARY KEY (cliente_id, telefono)
);

ALTER TABLE clientes DROP COLUMN telefonos;

-- Fase 2: Creacion de tabla 3FN codigos_postales
CREATE TABLE codigos_postales (
    codigo_postal  VARCHAR(10) PRIMARY KEY,
    ciudad         VARCHAR(80) NOT NULL
);

ALTER TABLE clientes 
    ADD CONSTRAINT fk_clientes_codigos_postales FOREIGN KEY (codigo_postal) 
    REFERENCES codigos_postales (codigo_postal) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE clientes DROP COLUMN ciudad;

-- Fase 3: Eliminacion de dependencias parciales (2FN)
ALTER TABLE detalle_pedido DROP COLUMN nombre_producto;
ALTER TABLE detalle_pedido DROP COLUMN categoria_producto;

-- Fase 4: Declaracion de claves foraneas (sin saneamiento de huerfanos)
ALTER TABLE pedidos ADD CONSTRAINT fk_pedidos_clientes
    FOREIGN KEY (cliente_id) REFERENCES clientes (cliente_id) ON DELETE RESTRICT;

ALTER TABLE detalle_pedido ADD CONSTRAINT fk_detalle_pedidos
    FOREIGN KEY (pedido_id) REFERENCES pedidos (pedido_id) ON DELETE CASCADE;

ALTER TABLE detalle_pedido ADD CONSTRAINT fk_detalle_productos
    FOREIGN KEY (producto_id) REFERENCES productos (producto_id) ON DELETE RESTRICT;

ALTER TABLE envios ADD CONSTRAINT fk_envios_pedidos
    FOREIGN KEY (pedido_id) REFERENCES pedidos (pedido_id) ON DELETE CASCADE;

