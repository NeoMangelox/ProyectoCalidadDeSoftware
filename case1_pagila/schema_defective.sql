-- =====================================================================
-- CASO 1 - Pagila (Sakila PostgreSQL) | schema_defective.sql
-- Base: pagila-schema.sql (devrimgunduz/pagila), nucleo de 15 tablas.
-- Simplificaciones de portabilidad (PG 16/17, sin extensiones): se omiten
-- uuid/uuidv7, tsvector, film_embedding (pgvector), vistas, funciones y
-- particionado de payment. Los IDs (D<tipo>-<n>) coinciden con defects_manifest.json
-- 15 tablas | 10 instancias de defecto
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
    city_id      INTEGER NOT NULL REFERENCES city (city_id),
    city_name    TEXT,                    -- [D3-02] 3FN: address_id -> city_id -> city.city
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
    last_update          TIMESTAMPTZ NOT NULL DEFAULT now(),
    special_features     TEXT             -- [D1-01] 1FN: lista CSV ("Trailers,Deleted Scenes")
);

CREATE TABLE film_actor (
    actor_id         INTEGER NOT NULL REFERENCES actor (actor_id),
    film_id          INTEGER NOT NULL REFERENCES film (film_id),
    actor_full_name  TEXT,                -- [D2-01] 2FN: depende solo de actor_id
    last_update      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (actor_id, film_id)
);

CREATE TABLE film_category (
    film_id        INTEGER NOT NULL REFERENCES film (film_id),
    category_id    INTEGER NOT NULL REFERENCES category (category_id),
    category_name  TEXT,                  -- [D2-02] 2FN: depende solo de category_id
    last_update    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (film_id, category_id)
);

CREATE TABLE inventory (
    inventory_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    film_id       INTEGER NOT NULL,       -- [D4-01] sin FOREIGN KEY -> film
    store_id      INTEGER NOT NULL,       -- [D4-02] sin FOREIGN KEY -> store
    film_title    TEXT,                   -- [D3-01] 3FN: inventory_id -> film_id -> film.title
    last_update   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE rental (
    rental_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rental_date   TIMESTAMPTZ NOT NULL,
    inventory_id  INTEGER NOT NULL,       -- [D4-03] sin FOREIGN KEY -> inventory
    customer_id   INTEGER NOT NULL,       -- [D4-04] sin FOREIGN KEY -> customer
    return_date   TIMESTAMPTZ,
    staff_id      INTEGER NOT NULL REFERENCES staff (staff_id),
    last_update   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE payment (
    payment_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id   INTEGER NOT NULL REFERENCES customer (customer_id),
    staff_id      INTEGER NOT NULL REFERENCES staff (staff_id),
    rental_id     INTEGER NOT NULL,       -- [D4-05] sin FOREIGN KEY -> rental
    amount        NUMERIC(5,2) NOT NULL,
    payment_date  TIMESTAMPTZ NOT NULL
);
