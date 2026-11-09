-- =====================================================================
-- EXP-03: Pagila - Nivel 3 (Agente Autonomo MCP + Dry-Run)
-- Generado siguiendo el protocolo de 4 fases con saneamiento determinista
-- =====================================================================

-- 1. Descomposicion 1FN: tabla film_special_feature y migracion atomica
CREATE TABLE IF NOT EXISTS film_special_feature (
    film_id   INTEGER NOT NULL REFERENCES film (film_id) ON DELETE CASCADE,
    feature   TEXT NOT NULL,
    CONSTRAINT pk_film_special_feature PRIMARY KEY (film_id, feature)
);

INSERT INTO film_special_feature (film_id, feature)
SELECT film_id, trim(unnest(string_to_array(special_features, ',')))
FROM film
WHERE special_features IS NOT NULL AND special_features <> ''
ON CONFLICT DO NOTHING;

ALTER TABLE film DROP COLUMN IF EXISTS special_features;

-- 2. Eliminacion de atributos dependientes parciales (2FN)
ALTER TABLE film_actor DROP COLUMN IF EXISTS actor_full_name;
ALTER TABLE film_category DROP COLUMN IF EXISTS category_name;

-- 3. Eliminacion de dependencias transitivas (3FN)
ALTER TABLE inventory DROP COLUMN IF EXISTS film_title;
ALTER TABLE address DROP COLUMN IF EXISTS city_name;

-- 4. Saneamiento de integridad referencial previo (huerfanos detectados en Fase 1)
DELETE FROM payment WHERE rental_id NOT IN (SELECT rental_id FROM rental);
DELETE FROM rental WHERE inventory_id NOT IN (SELECT inventory_id FROM inventory) 
                      OR customer_id NOT IN (SELECT customer_id FROM customer);
DELETE FROM inventory WHERE film_id NOT IN (SELECT film_id FROM film);

-- 5. Creacion de restricciones FOREIGN KEY formales
ALTER TABLE inventory 
    ADD CONSTRAINT fk_inventory_film FOREIGN KEY (film_id) 
    REFERENCES film (film_id) ON DELETE RESTRICT;

ALTER TABLE inventory 
    ADD CONSTRAINT fk_inventory_store FOREIGN KEY (store_id) 
    REFERENCES store (store_id) ON DELETE RESTRICT;

ALTER TABLE rental 
    ADD CONSTRAINT fk_rental_inventory FOREIGN KEY (inventory_id) 
    REFERENCES inventory (inventory_id) ON DELETE RESTRICT;

ALTER TABLE rental 
    ADD CONSTRAINT fk_rental_customer FOREIGN KEY (customer_id) 
    REFERENCES customer (customer_id) ON DELETE RESTRICT;

ALTER TABLE payment 
    ADD CONSTRAINT fk_payment_rental FOREIGN KEY (rental_id) 
    REFERENCES rental (rental_id) ON DELETE RESTRICT;

-- Indices sobre claves foraneas para optimizacion de planes de ejecucion
CREATE INDEX IF NOT EXISTS idx_inventory_film_id ON inventory (film_id);
CREATE INDEX IF NOT EXISTS idx_inventory_store_id ON inventory (store_id);
CREATE INDEX IF NOT EXISTS idx_rental_inventory_id ON rental (inventory_id);
CREATE INDEX IF NOT EXISTS idx_rental_customer_id ON rental (customer_id);
CREATE INDEX IF NOT EXISTS idx_payment_rental_id ON payment (rental_id);

