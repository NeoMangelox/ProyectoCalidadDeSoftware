-- =====================================================================
-- EXP-06: Northwind - Nivel 3 (Agente Autonomo MCP + Dry-Run)
-- Generado siguiendo el protocolo de 4 fases con saneamiento determinista
-- =====================================================================

-- 1. Descomposicion 1FN: tabla customer_phones y migracion de telefonos
CREATE TABLE IF NOT EXISTS customer_phones (
    customer_id  VARCHAR(5) NOT NULL REFERENCES customers (customer_id) ON DELETE CASCADE,
    phone        VARCHAR(30) NOT NULL,
    CONSTRAINT pk_customer_phones PRIMARY KEY (customer_id, phone)
);

INSERT INTO customer_phones (customer_id, phone)
SELECT customer_id, trim(unnest(string_to_array(phones, ',')))
FROM customers
WHERE phones IS NOT NULL AND phones <> ''
ON CONFLICT DO NOTHING;

ALTER TABLE customers DROP COLUMN IF EXISTS phones;

-- 2. Eliminacion de atributos dependientes parciales (2FN)
ALTER TABLE order_details DROP COLUMN IF EXISTS product_name;
ALTER TABLE order_details DROP COLUMN IF EXISTS quantity_per_unit;

-- 3. Eliminacion de dependencia transitiva (3FN)
ALTER TABLE orders DROP COLUMN IF EXISTS shipper_name;

-- 4. Saneamiento de registros huerfanos detectados en Fase 1
DELETE FROM order_details WHERE product_id NOT IN (SELECT product_id FROM products);
DELETE FROM orders WHERE customer_id NOT IN (SELECT customer_id FROM customers)
                      OR (ship_via IS NOT NULL AND ship_via NOT IN (SELECT shipper_id FROM shippers));

-- 5. Creacion de restricciones FOREIGN KEY formales
ALTER TABLE orders 
    ADD CONSTRAINT fk_orders_customers FOREIGN KEY (customer_id) 
    REFERENCES customers (customer_id) ON DELETE RESTRICT;

ALTER TABLE orders 
    ADD CONSTRAINT fk_orders_shippers FOREIGN KEY (ship_via) 
    REFERENCES shippers (shipper_id) ON DELETE RESTRICT;

ALTER TABLE order_details 
    ADD CONSTRAINT fk_order_details_orders FOREIGN KEY (order_id) 
    REFERENCES orders (order_id) ON DELETE CASCADE;

ALTER TABLE order_details 
    ADD CONSTRAINT fk_order_details_products FOREIGN KEY (product_id) 
    REFERENCES products (product_id) ON DELETE RESTRICT;

ALTER TABLE products 
    ADD CONSTRAINT fk_products_categories FOREIGN KEY (category_id) 
    REFERENCES categories (category_id) ON DELETE RESTRICT;

ALTER TABLE products 
    ADD CONSTRAINT fk_products_suppliers FOREIGN KEY (supplier_id) 
    REFERENCES suppliers (supplier_id) ON DELETE RESTRICT;

-- Indices para acelerar JOINs y mantener integridad referencial
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_ship_via ON orders (ship_via);
CREATE INDEX IF NOT EXISTS idx_order_details_product_id ON order_details (product_id);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products (category_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier_id ON products (supplier_id);

