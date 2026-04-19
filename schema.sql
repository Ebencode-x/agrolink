-- AgroLink Tanzania PostgreSQL Schema
-- Author: Ebenezer Richard Masanja

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    full_name     VARCHAR(120) NOT NULL,
    phone         VARCHAR(20) NOT NULL UNIQUE,
    email         VARCHAR(120) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    region        VARCHAR(80),
    role          VARCHAR(20) NOT NULL DEFAULT 'farmer'
                  CHECK (role IN ('farmer','agent','admin')),
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS crops (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name_sw     VARCHAR(100) NOT NULL,
    name_en     VARCHAR(100) NOT NULL,
    category    VARCHAR(50) NOT NULL
                CHECK (category IN ('grain','vegetable','fruit','cash','legume','other')),
    season      VARCHAR(50),
    hectares    NUMERIC(10,2),
    region      VARCHAR(80),
    description TEXT,
    image_url   VARCHAR(300),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_prices (
    id          SERIAL PRIMARY KEY,
    crop_id     INTEGER NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
    region      VARCHAR(80) NOT NULL,
    market      VARCHAR(120),
    price_tzs   NUMERIC(12,2) NOT NULL,
    unit        VARCHAR(20) NOT NULL DEFAULT 'kg',
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source      VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS market_listings (
    id           SERIAL PRIMARY KEY,
    seller_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title        VARCHAR(200) NOT NULL,
    crop_name    VARCHAR(100) NOT NULL,
    quantity_kg  NUMERIC(12,2) NOT NULL,
    price_tzs    NUMERIC(12,2) NOT NULL,
    region       VARCHAR(80) NOT NULL,
    contact      VARCHAR(50) NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    image_url    VARCHAR(300),
    posted_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at   TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS weather_logs (
    id          SERIAL PRIMARY KEY,
    city        VARCHAR(100) NOT NULL,
    temperature NUMERIC(5,2),
    humidity    NUMERIC(5,2),
    description VARCHAR(200),
    wind_speed  NUMERIC(6,2),
    icon        VARCHAR(20),
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_crops_updated
    BEFORE UPDATE ON crops
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();
