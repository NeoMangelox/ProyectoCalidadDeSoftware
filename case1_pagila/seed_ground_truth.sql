-- Caso 1 - datos semilla (esquema normalizado)
-- Generado por tools/generate_seeds.py (no editar a mano)
BEGIN;
INSERT INTO country (country_id, country) OVERRIDING SYSTEM VALUE VALUES
  (1, 'Peru'),
  (2, 'Spain');
INSERT INTO city (city_id, city, country_id) OVERRIDING SYSTEM VALUE VALUES
  (1, 'Lima', 1),
  (2, 'Cusco', 1),
  (3, 'Madrid', 2);
INSERT INTO language (language_id, name) OVERRIDING SYSTEM VALUE VALUES
  (1, 'English'),
  (2, 'Spanish');
INSERT INTO actor (actor_id, first_name, last_name) OVERRIDING SYSTEM VALUE VALUES
  (1, 'Penelope', 'Guiness'),
  (2, 'Nick', 'Wahlberg'),
  (3, 'Ed', 'Chase'),
  (4, 'Jennifer', 'Davis');
INSERT INTO category (category_id, name) OVERRIDING SYSTEM VALUE VALUES
  (1, 'Action'),
  (2, 'Comedy'),
  (3, 'Drama');
INSERT INTO address (address_id, address, district, city_id, postal_code, phone) OVERRIDING SYSTEM VALUE VALUES
  (1, '47 MySakila Drive', 'Lima', 1, '15001', '555-0001'),
  (2, '28 MySQL Boulevard', 'Cusco', 2, '08002', '555-0002'),
  (3, '23 Workhaven Lane', 'Lima', 1, '15036', '555-0003'),
  (4, '1411 Lillydale Drive', 'Madrid', 3, '28001', '555-0004'),
  (5, '1913 Hanoi Way', 'Lima', 1, '15001', '555-0005'),
  (6, '1121 Loja Avenue', 'Cusco', 2, '08002', '555-0006'),
  (7, '692 Joliet Street', 'Madrid', 3, '28002', '555-0007');
INSERT INTO staff (staff_id, first_name, last_name, address_id, email, store_id, username) OVERRIDING SYSTEM VALUE VALUES
  (1, 'Mike', 'Hillyer', 3, 'mike@sakila.example', 1, 'mike'),
  (2, 'Jon', 'Stephens', 4, 'jon@sakila.example', 2, 'jon');
INSERT INTO store (store_id, manager_staff_id, address_id) OVERRIDING SYSTEM VALUE VALUES
  (1, 1, 1),
  (2, 2, 2);
INSERT INTO customer (customer_id, store_id, first_name, last_name, email, address_id) OVERRIDING SYSTEM VALUE VALUES
  (1, 1, 'Mary', 'Smith', 'mary@x.example', 5),
  (2, 1, 'Patricia', 'Johnson', 'pat@x.example', 6),
  (3, 2, 'Linda', 'Williams', 'linda@x.example', 7);
INSERT INTO film (film_id, title, release_year, language_id, rental_rate, length, replacement_cost, rating) OVERRIDING SYSTEM VALUE VALUES
  (1, 'Academy Dinosaur', 2006, 1, 0.99, 86, 20.99, 'PG'),
  (2, 'Ace Goldfinger', 2006, 1, 4.99, 48, 12.99, 'G'),
  (3, 'Adaptation Holes', 2006, 1, 2.99, 50, 18.99, 'NC-17'),
  (4, 'Affair Prejudice', 2006, 1, 2.99, 117, 26.99, 'G'),
  (5, 'African Egg', 2006, 2, 2.99, 130, 22.99, 'G'),
  (6, 'Agent Truman', 2006, 2, 2.99, 169, 17.99, 'PG');
INSERT INTO film_special_feature (film_id, feature) VALUES
  (1, 'Deleted Scenes'),
  (1, 'Behind the Scenes'),
  (2, 'Trailers'),
  (2, 'Deleted Scenes'),
  (3, 'Trailers'),
  (3, 'Deleted Scenes'),
  (4, 'Commentaries'),
  (4, 'Behind the Scenes'),
  (5, 'Deleted Scenes');
INSERT INTO film_actor (actor_id, film_id) VALUES
  (1, 1),
  (2, 1),
  (1, 2),
  (3, 3),
  (4, 4),
  (2, 5),
  (4, 6);
INSERT INTO film_category (film_id, category_id) VALUES
  (1, 3),
  (2, 1),
  (3, 2),
  (4, 3),
  (5, 2),
  (6, 1);
INSERT INTO inventory (inventory_id, film_id, store_id) OVERRIDING SYSTEM VALUE VALUES
  (1, 1, 1),
  (2, 1, 2),
  (3, 2, 1),
  (4, 3, 1),
  (5, 4, 2),
  (6, 5, 1),
  (7, 6, 2),
  (8, 2, 2);
INSERT INTO rental (rental_id, rental_date, inventory_id, customer_id, return_date, staff_id) OVERRIDING SYSTEM VALUE VALUES
  (1, '2026-05-24 22:53:30+00', 1, 1, '2026-05-26 22:04:30+00', 1),
  (2, '2026-05-24 23:03:39+00', 3, 2, NULL, 1),
  (3, '2026-05-25 00:00:40+00', 4, 3, '2026-06-02 01:20:40+00', 2),
  (4, '2026-05-25 00:02:21+00', 5, 1, NULL, 2),
  (5, '2026-06-03 10:00:00+00', 1, 2, '2026-06-10 10:00:00+00', 1);
INSERT INTO payment (payment_id, customer_id, staff_id, rental_id, amount, payment_date) OVERRIDING SYSTEM VALUE VALUES
  (1, 1, 1, 1, 2.99, '2026-05-25 10:00:00+00'),
  (2, 2, 1, 2, 4.99, '2026-05-25 11:00:00+00'),
  (3, 3, 2, 3, 0.99, '2026-05-26 09:00:00+00'),
  (4, 1, 2, 4, 5.99, '2026-05-26 12:00:00+00'),
  (5, 2, 1, 5, 2.99, '2026-06-03 10:30:00+00');
SELECT setval(pg_get_serial_sequence('country', 'country_id'), (SELECT COALESCE(MAX(country_id), 1) FROM country));
SELECT setval(pg_get_serial_sequence('city', 'city_id'), (SELECT COALESCE(MAX(city_id), 1) FROM city));
SELECT setval(pg_get_serial_sequence('language', 'language_id'), (SELECT COALESCE(MAX(language_id), 1) FROM language));
SELECT setval(pg_get_serial_sequence('actor', 'actor_id'), (SELECT COALESCE(MAX(actor_id), 1) FROM actor));
SELECT setval(pg_get_serial_sequence('category', 'category_id'), (SELECT COALESCE(MAX(category_id), 1) FROM category));
SELECT setval(pg_get_serial_sequence('address', 'address_id'), (SELECT COALESCE(MAX(address_id), 1) FROM address));
SELECT setval(pg_get_serial_sequence('staff', 'staff_id'), (SELECT COALESCE(MAX(staff_id), 1) FROM staff));
SELECT setval(pg_get_serial_sequence('store', 'store_id'), (SELECT COALESCE(MAX(store_id), 1) FROM store));
SELECT setval(pg_get_serial_sequence('customer', 'customer_id'), (SELECT COALESCE(MAX(customer_id), 1) FROM customer));
SELECT setval(pg_get_serial_sequence('film', 'film_id'), (SELECT COALESCE(MAX(film_id), 1) FROM film));
SELECT setval(pg_get_serial_sequence('inventory', 'inventory_id'), (SELECT COALESCE(MAX(inventory_id), 1) FROM inventory));
SELECT setval(pg_get_serial_sequence('rental', 'rental_id'), (SELECT COALESCE(MAX(rental_id), 1) FROM rental));
SELECT setval(pg_get_serial_sequence('payment', 'payment_id'), (SELECT COALESCE(MAX(payment_id), 1) FROM payment));
COMMIT;
