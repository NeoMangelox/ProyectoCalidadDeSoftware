-- Caso 2 - datos semilla (esquema normalizado)
-- Generado por tools/generate_seeds.py (no editar a mano)
BEGIN;
INSERT INTO region (region_id, region_description) VALUES
  (1, 'Eastern'),
  (2, 'Western');
INSERT INTO territories (territory_id, territory_description, region_id) VALUES
  ('01581', 'Westboro', 1),
  ('98004', 'Bellevue', 2);
INSERT INTO employees (employee_id, last_name, first_name, title, reports_to) VALUES
  (1, 'Davolio', 'Nancy', 'Sales Representative', NULL),
  (2, 'Fuller', 'Andrew', 'Vice President, Sales', 1);
INSERT INTO employee_territories (employee_id, territory_id) VALUES
  (1, '01581'),
  (2, '98004');
INSERT INTO categories (category_id, category_name, description) VALUES
  (1, 'Beverages', 'Soft drinks, coffees, teas'),
  (2, 'Condiments', 'Sweet and savory sauces'),
  (3, 'Seafood', 'Seaweed and fish');
INSERT INTO suppliers (supplier_id, company_name, contact_name, city, country, phone) VALUES
  (1, 'Exotic Liquids', 'Charlotte Cooper', 'London', 'UK', '(171) 555-2222'),
  (2, 'New Orleans Cajun Delights', 'Shelley Burke', 'New Orleans', 'USA', '(100) 555-4822'),
  (3, 'Pavlova, Ltd.', 'Ian Devling', 'Melbourne', 'Australia', '(03) 444-2343');
INSERT INTO shippers (shipper_id, company_name, phone) VALUES
  (1, 'Speedy Express', '(503) 555-9831'),
  (2, 'United Package', '(503) 555-3199'),
  (3, 'Federal Shipping', '(503) 555-9931');
INSERT INTO customer_demographics (customer_type_id, customer_desc) VALUES
  ('STD', 'Standard'),
  ('PRM', 'Premium');
INSERT INTO us_states (state_id, state_name, state_abbr, state_region) VALUES
  (1, 'Alabama', 'AL', 'south'),
  (2, 'Alaska', 'AK', 'west');
INSERT INTO customers (customer_id, company_name, contact_name, address, city, postal_code, country) VALUES
  ('ALFKI', 'Alfreds Futterkiste', 'Maria Anders', 'Obere Str. 57', 'Berlin', '12209', 'Germany'),
  ('ANATR', 'Ana Trujillo Emparedados', 'Ana Trujillo', 'Avda. de la Constitucion 2222', 'Mexico D.F.', '05021', 'Mexico'),
  ('BONAP', 'Bon app''', 'Laurence Lebihan', '12, rue des Bouchers', 'Marseille', '13008', 'France'),
  ('CACTU', 'Cactus Comidas para llevar', 'Patricio Simpson', 'Cerrito 333', 'Buenos Aires', '1010', 'Argentina'),
  ('DRACD', 'Drachenblut Delikatessen', 'Sven Ottlieb', 'Walserweg 21', 'Aachen', '52066', 'Germany');
INSERT INTO customer_phones (customer_id, phone) VALUES
  ('ALFKI', '030-0074321'),
  ('ALFKI', '030-0076545'),
  ('ANATR', '(5) 555-4729'),
  ('BONAP', '91.24.45.40'),
  ('BONAP', '91.24.45.41'),
  ('BONAP', '91.24.45.42'),
  ('DRACD', '0241-039123');
INSERT INTO customer_customer_demo (customer_id, customer_type_id) VALUES
  ('ALFKI', 'PRM'),
  ('BONAP', 'STD');
INSERT INTO products (product_id, product_name, supplier_id, category_id, quantity_per_unit, unit_price, units_in_stock, units_on_order, reorder_level, discontinued) VALUES
  (1, 'Chai', 1, 1, '10 boxes x 20 bags', 18.0, 39, 0, 10, 0),
  (2, 'Chang', 1, 1, '24 - 12 oz bottles', 19.0, 17, 40, 25, 0),
  (3, 'Aniseed Syrup', 1, 2, '12 - 550 ml bottles', 10.0, 13, 70, 25, 0),
  (4, 'Chef Anton''s Cajun Seasoning', 2, 2, '48 - 6 oz jars', 22.0, 53, 0, 0, 0),
  (5, 'Chef Anton''s Gumbo Mix', 2, 2, '36 boxes', 21.35, 0, 0, 0, 1),
  (6, 'Ikura', 3, 3, '12 - 200 ml jars', 31.0, 31, 0, 0, 0),
  (7, 'Konbu', 3, 3, '2 kg box', 6.0, 24, 0, 5, 0),
  (8, 'Carnarvon Tigers', 3, 3, '16 kg pkg.', 62.5, 42, 0, 0, 0);
INSERT INTO orders (order_id, customer_id, employee_id, order_date, required_date, shipped_date, ship_via, freight, ship_name, ship_city, ship_country) OVERRIDING SYSTEM VALUE VALUES
  (1, 'ALFKI', 1, '2026-09-01', '2026-09-15', '2026-09-03', 1, 32.38, 'Alfreds Futterkiste', 'Berlin', 'Germany'),
  (2, 'ANATR', 2, '2026-09-05', '2026-09-19', '2026-09-08', 2, 11.61, 'Ana Trujillo Emparedados', 'Mexico D.F.', 'Mexico'),
  (3, 'BONAP', 1, '2026-09-12', '2026-09-26', '2026-09-14', 3, 65.83, 'Bon app''', 'Marseille', 'France'),
  (4, 'ALFKI', 2, '2026-10-02', '2026-10-16', NULL, 1, 41.34, 'Alfreds Futterkiste', 'Berlin', 'Germany');
INSERT INTO order_details (order_id, product_id, unit_price, quantity, discount) VALUES
  (1, 1, 18.0, 10, 0.0),
  (1, 2, 19.0, 5, 0.05),
  (2, 3, 10.0, 20, 0.0),
  (3, 6, 31.0, 2, 0.0),
  (3, 8, 62.5, 1, 0.1),
  (4, 4, 22.0, 3, 0.0);
SELECT setval(pg_get_serial_sequence('orders', 'order_id'), (SELECT COALESCE(MAX(order_id), 1) FROM orders));
COMMIT;
