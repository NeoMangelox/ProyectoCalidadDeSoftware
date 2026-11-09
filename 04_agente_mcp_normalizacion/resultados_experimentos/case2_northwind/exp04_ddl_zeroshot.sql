-- =====================================================================
-- EXP-04: Northwind - Nivel 2 (Crudo / Zero-Shot)
-- Generado por LLM Zero-Shot sin introspeccion de catalogo ni CoT
-- =====================================================================

-- Alucinacion 1: Columna 'id' inexistente en tabla customers (la PK es customer_id VARCHAR(5))
ALTER TABLE orders 
    ADD CONSTRAINT fk_orders_customers FOREIGN KEY (customer_id) 
    REFERENCES customers (id);

-- Alucinacion 2: Tabla inventada 'countries' para normalizar country
CREATE TABLE countries (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(50) NOT NULL
);

ALTER TABLE suppliers 
    ADD CONSTRAINT fk_suppliers_country FOREIGN KEY (country) 
    REFERENCES countries (country_name);

-- Claves foraneas estandar propuestas
ALTER TABLE orders 
    ADD CONSTRAINT fk_orders_shippers FOREIGN KEY (ship_via) 
    REFERENCES shippers (shipper_id);

ALTER TABLE order_details 
    ADD CONSTRAINT fk_order_details_orders FOREIGN KEY (order_id) 
    REFERENCES orders (order_id);

ALTER TABLE order_details 
    ADD CONSTRAINT fk_order_details_products FOREIGN KEY (product_id) 
    REFERENCES products (product_id);

-- Desnormalizaciones eliminadas
ALTER TABLE order_details DROP COLUMN product_name;
ALTER TABLE order_details DROP COLUMN quantity_per_unit;
ALTER TABLE orders DROP COLUMN shipper_name;

