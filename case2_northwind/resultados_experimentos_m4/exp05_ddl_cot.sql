-- =====================================================================
-- EXP-05: Northwind - Nivel 2 (Chain of Thought / CoT sin conexion MCP)
-- Generado mediante razonamiento estructurado en 5 fases de SKILL.md
-- =====================================================================

-- Fase 1: Creacion de tabla 1FN customer_phones
CREATE TABLE customer_phones (
    customer_id  VARCHAR(5) NOT NULL REFERENCES customers (customer_id) ON DELETE CASCADE,
    phone        VARCHAR(30) NOT NULL,
    PRIMARY KEY (customer_id, phone)
);

ALTER TABLE customers DROP COLUMN phones;

-- Fase 2: Eliminacion de dependencias parciales (2FN)
ALTER TABLE order_details DROP COLUMN product_name;
ALTER TABLE order_details DROP COLUMN quantity_per_unit;

-- Fase 3: Eliminacion de dependencia transitiva (3FN)
ALTER TABLE orders DROP COLUMN shipper_name;

-- Fase 4: Declaracion de claves foraneas (sin saneamiento de huerfanos)
ALTER TABLE orders ADD CONSTRAINT fk_orders_customers
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE RESTRICT;

ALTER TABLE orders ADD CONSTRAINT fk_orders_shippers
    FOREIGN KEY (ship_via) REFERENCES shippers (shipper_id) ON DELETE RESTRICT;

ALTER TABLE order_details ADD CONSTRAINT fk_order_details_orders
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE;

ALTER TABLE order_details ADD CONSTRAINT fk_order_details_products
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE RESTRICT;

ALTER TABLE products ADD CONSTRAINT fk_products_categories
    FOREIGN KEY (category_id) REFERENCES categories (category_id) ON DELETE RESTRICT;

ALTER TABLE products ADD CONSTRAINT fk_products_suppliers
    FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id) ON DELETE RESTRICT;

