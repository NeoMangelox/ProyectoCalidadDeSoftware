-- =====================================================================
-- EXP-01: Pagila - Nivel 2 (Crudo / Zero-Shot)
-- Generado por LLM Zero-Shot sin introspeccion de catalogo ni CoT
-- =====================================================================

-- Alucinacion 1: Tabla de lookup inventada 'ratings' para el tipo enum mpaa_rating
CREATE TABLE ratings (
    rating_id SERIAL PRIMARY KEY,
    rating_name VARCHAR(10) NOT NULL
);

ALTER TABLE film ADD CONSTRAINT fk_film_rating FOREIGN KEY (rating) REFERENCES ratings(rating_name);

-- Alucinacion 2: Clave foranea hacia tabla inexistente en plural 'films'
ALTER TABLE inventory ADD CONSTRAINT fk_inventory_films FOREIGN KEY (film_id) REFERENCES films(film_id);

-- Alucinacion 3: Clave foranea hacia tabla inexistente 'addresses'
ALTER TABLE store ADD CONSTRAINT fk_store_addresses FOREIGN KEY (address_id) REFERENCES addresses(address_id);

-- Claves foraneas estandar identificadas
ALTER TABLE inventory ADD CONSTRAINT fk_inventory_store FOREIGN KEY (store_id) REFERENCES store(store_id);
ALTER TABLE rental ADD CONSTRAINT fk_rental_inventory FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id);
ALTER TABLE payment ADD CONSTRAINT fk_payment_rental FOREIGN KEY (rental_id) REFERENCES rental(rental_id);

-- Desnormalizaciones eliminadas
ALTER TABLE film_actor DROP COLUMN actor_full_name;
ALTER TABLE film_category DROP COLUMN category_name;
ALTER TABLE inventory DROP COLUMN film_title;

