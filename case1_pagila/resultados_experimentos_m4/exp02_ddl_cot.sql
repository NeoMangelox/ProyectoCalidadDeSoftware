-- =====================================================================
-- EXP-02: Pagila - Nivel 2 (Chain of Thought / CoT sin conexion MCP)
-- Generado mediante razonamiento estructurado en 5 fases de SKILL.md
-- =====================================================================

-- Fase 1: Creacion de tabla 1FN para atributos multivaluados
CREATE TABLE film_special_feature (
    film_id   INTEGER NOT NULL REFERENCES film (film_id) ON DELETE CASCADE,
    feature   TEXT NOT NULL,
    PRIMARY KEY (film_id, feature)
);

ALTER TABLE film DROP COLUMN special_features;

-- Fase 2: Eliminacion de dependencias parciales (2FN)
ALTER TABLE film_actor DROP COLUMN actor_full_name;
ALTER TABLE film_category DROP COLUMN category_name;

-- Fase 3: Eliminacion de dependencias transitivas (3FN)
ALTER TABLE inventory DROP COLUMN film_title;
ALTER TABLE address DROP COLUMN city_name;

-- Fase 4: Declaracion de claves foraneas ausentes (sin saneamiento de huerfanos)
ALTER TABLE inventory ADD CONSTRAINT fk_inventory_film
    FOREIGN KEY (film_id) REFERENCES film (film_id) ON DELETE RESTRICT;

ALTER TABLE inventory ADD CONSTRAINT fk_inventory_store
    FOREIGN KEY (store_id) REFERENCES store (store_id) ON DELETE RESTRICT;

ALTER TABLE rental ADD CONSTRAINT fk_rental_inventory
    FOREIGN KEY (inventory_id) REFERENCES inventory (inventory_id) ON DELETE RESTRICT;

ALTER TABLE rental ADD CONSTRAINT fk_rental_customer
    FOREIGN KEY (customer_id) REFERENCES customer (customer_id) ON DELETE RESTRICT;

ALTER TABLE payment ADD CONSTRAINT fk_payment_rental
    FOREIGN KEY (rental_id) REFERENCES rental (rental_id) ON DELETE RESTRICT;

