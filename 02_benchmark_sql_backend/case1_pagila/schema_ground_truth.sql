-- =====================================================================
-- CASO 1 - Pagila (Sakila PostgreSQL) | schema_ground_truth.sql
-- Referencia normalizada (3FN/BCNF), todas las FK con accion explicita e
-- indices sobre FK. 16 tablas (15 + film_special_feature).
-- =====================================================================

CREATE TYPE mpaa_rating AS ENUM ('G', 'PG', 'PG-13', 'R', 'NC-17');

CREATE TABLE country (
    country_id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country      TEXT NOT NULL,
    last_update  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE city (
    city_id      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city         TEXT NOT NULL,
    country_id   INTEGER NOT NULL REFERENCES country (country_id),
    last_update  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE language (
    language_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name         TEXT NOT NULL,
    last_update  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE actor (
    actor_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    last_update  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE category (
    category_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name         TEXT NOT NULL,
    last_update  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE address (
    address_id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    address      TEXT NOT NULL,
    address2     TEXT,
    district     TEXT NOT NULL,
    city_id      INTEGER NOT NULL REFERENCES city (city_id),   -- (D3-02 corregido: sin city_name)
    postal_code  TEXT,
    phone        TEXT NOT NULL,
    last_update  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE staff (
    staff_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    address_id   INTEGER NOT NULL REFERENCES address (address_id),
    email        TEXT,
    store_id     INTEGER NOT NULL,
    active       BOOLEAN NOT NULL DEFAULT true,
    username     TEXT NOT NULL,
    password     TEXT,
    last_update  TIMESTAMPTZ NOT NULL DEFAULT now(),
    picture      BYTEA
);

CREATE TABLE store (
    store_id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    manager_staff_id  INTEGER NOT NULL UNIQUE,
    address_id        INTEGER NOT NULL REFERENCES address (address_id),
    last_update       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Dependencia circular nativa de Sakila/Pagila (store <-> staff): FK diferidas
ALTER TABLE staff ADD CONSTRAINT staff_store_id_fkey
    FOREIGN KEY (store_id) REFERENCES store (store_id)
    DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE store ADD CONSTRAINT store_manager_staff_id_fkey
    FOREIGN KEY (manager_staff_id) REFERENCES staff (staff_id)
    DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE customer (
    customer_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    store_id     INTEGER NOT NULL REFERENCES store (store_id),
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    email        TEXT,
    address_id   INTEGER NOT NULL REFERENCES address (address_id),
    activebool   BOOLEAN NOT NULL DEFAULT true,
    create_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    last_update  TIMESTAMPTZ DEFAULT now(),
    active       INTEGER
);

CREATE TABLE film (
    film_id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title                TEXT NOT NULL,
    description          TEXT,
    release_year         INTEGER CHECK (release_year BETWEEN 1901 AND 2155),
    language_id          INTEGER NOT NULL REFERENCES language (language_id),
    original_language_id INTEGER REFERENCES language (language_id),
    rental_duration      SMALLINT NOT NULL DEFAULT 3,
    rental_rate          NUMERIC(4,2) NOT NULL DEFAULT 4.99,
    length               SMALLINT,
    replacement_cost     NUMERIC(5,2) NOT NULL DEFAULT 19.99,
    rating               mpaa_rating DEFAULT 'G',
    last_update          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE film_special_feature (                    -- corrige D1-01
    film_id  INTEGER NOT NULL REFERENCES film (film_id) ON DELETE CASCADE,
    feature  TEXT NOT NULL,
    PRIMARY KEY (film_id, feature)
);

CREATE TABLE film_actor (                              -- D2-01 corregido
    actor_id     INTEGER NOT NULL REFERENCES actor (actor_id) ON DELETE CASCADE,
    film_id      INTEGER NOT NULL REFERENCES film (film_id) ON DELETE CASCADE,
    last_update  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (actor_id, film_id)
);

CREATE TABLE film_category (                           -- D2-02 corregido
    film_id      INTEGER NOT NULL REFERENCES film (film_id) ON DELETE CASCADE,
    category_id  INTEGER NOT NULL REFERENCES category (category_id) ON DELETE CASCADE,
    last_update  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (film_id, category_id)
);

CREATE TABLE inventory (                               -- D3-01 corregido
    inventory_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    film_id       INTEGER NOT NULL REFERENCES film (film_id) ON DELETE RESTRICT,    -- D4-01
    store_id      INTEGER NOT NULL REFERENCES store (store_id) ON DELETE RESTRICT,  -- D4-02
    last_update   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE rental (
    rental_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rental_date   TIMESTAMPTZ NOT NULL,
    inventory_id  INTEGER NOT NULL REFERENCES inventory (inventory_id) ON DELETE RESTRICT,  -- D4-03
    customer_id   INTEGER NOT NULL REFERENCES customer (customer_id) ON DELETE RESTRICT,    -- D4-04
    return_date   TIMESTAMPTZ,
    staff_id      INTEGER NOT NULL REFERENCES staff (staff_id),
    last_update   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE payment (
    payment_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id   INTEGER NOT NULL REFERENCES customer (customer_id),
    staff_id      INTEGER NOT NULL REFERENCES staff (staff_id),
    rental_id     INTEGER NOT NULL REFERENCES rental (rental_id) ON DELETE RESTRICT,  -- D4-05
    amount        NUMERIC(5,2) NOT NULL,
    payment_date  TIMESTAMPTZ NOT NULL
);

-- Indices sobre FK (PostgreSQL no los crea automaticamente)
CREATE INDEX idx_city_country        ON city (country_id);
CREATE INDEX idx_address_city        ON address (city_id);
CREATE INDEX idx_customer_store      ON customer (store_id);
CREATE INDEX idx_customer_address    ON customer (address_id);
CREATE INDEX idx_film_language       ON film (language_id);
CREATE INDEX idx_film_actor_film     ON film_actor (film_id);
CREATE INDEX idx_film_category_cat   ON film_category (category_id);
CREATE INDEX idx_inventory_film      ON inventory (film_id);
CREATE INDEX idx_inventory_store     ON inventory (store_id);
CREATE INDEX idx_rental_inventory    ON rental (inventory_id);
CREATE INDEX idx_rental_customer     ON rental (customer_id);
CREATE INDEX idx_rental_staff        ON rental (staff_id);
CREATE INDEX idx_payment_customer    ON payment (customer_id);
CREATE INDEX idx_payment_rental      ON payment (rental_id);
CREATE INDEX idx_payment_staff       ON payment (staff_id);
CREATE INDEX idx_staff_store         ON staff (store_id);
