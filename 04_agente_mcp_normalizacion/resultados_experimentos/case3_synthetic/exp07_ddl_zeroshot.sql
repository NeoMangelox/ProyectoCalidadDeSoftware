-- =====================================================================
-- EXP-07: Sintetico - Nivel 2 (Crudo / Zero-Shot)
-- Generado por LLM Zero-Shot sin introspeccion de catalogo ni CoT
-- =====================================================================

-- Alucinacion 1: Tabla inventada 'ciudades' para normalizar ciudad
CREATE TABLE ciudades (
    ciudad_id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL
);

ALTER TABLE clientes 
    ADD CONSTRAINT fk_clientes_ciudades FOREIGN KEY (ciudad) 
    REFERENCES ciudades (nombre);

-- Alucinacion 2: Columna 'id' inexistente en pedidos (la PK es pedido_id)
ALTER TABLE envios 
    ADD CONSTRAINT fk_envios_pedidos FOREIGN KEY (pedido_id) 
    REFERENCES pedidos (id);

-- Restricciones estandar propuestas
ALTER TABLE pedidos 
    ADD CONSTRAINT fk_pedidos_clientes FOREIGN KEY (cliente_id) 
    REFERENCES clientes (cliente_id);

ALTER TABLE detalle_pedido 
    ADD CONSTRAINT fk_detalle_pedidos FOREIGN KEY (pedido_id) 
    REFERENCES pedidos (pedido_id);

ALTER TABLE detalle_pedido 
    ADD CONSTRAINT fk_detalle_productos FOREIGN KEY (producto_id) 
    REFERENCES productos (producto_id);

-- Desnormalizaciones eliminadas
ALTER TABLE detalle_pedido DROP COLUMN nombre_producto;
ALTER TABLE detalle_pedido DROP COLUMN categoria_producto;

