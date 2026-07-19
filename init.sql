CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(10) NOT NULL CHECK(type IN ('expense', 'income'))
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(12,2) NOT NULL,
    category_id INTEGER NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    description TEXT,

    CONSTRAINT fk_category
    FOREIGN KEY (category_id)
    REFERENCES categories(id)
    ON DELETE CASCADE
)