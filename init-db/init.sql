-- Tables are also created idempotently by training/train.py; this file just
-- lets the Postgres container initialize an empty schema on first boot.
CREATE TABLE IF NOT EXISTS recommendations (
    user_id INT, item_id INT, score REAL, rank INT,
    PRIMARY KEY (user_id, rank)
);
CREATE TABLE IF NOT EXISTS item_similarity (
    item_id INT, similar_item_id INT, similarity REAL, rank INT,
    PRIMARY KEY (item_id, rank)
);
CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY, metric_name TEXT, metric_value REAL,
    computed_at TIMESTAMP DEFAULT now()
);
