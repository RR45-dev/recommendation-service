import os

import numpy as np
import psycopg
from sklearn.model_selection import train_test_split

from generate_synthetic_data import generate_interactions
from model import build_model
from similarity import cosine_similarity_matrix

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://recadmin:recadmin@localhost:5432/recsys")
TOP_N_RECOMMENDATIONS = 10
TOP_N_SIMILAR_ITEMS = 5


def ensure_schema(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            user_id INT, item_id INT, score REAL, rank INT,
            PRIMARY KEY (user_id, rank)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS item_similarity (
            item_id INT, similar_item_id INT, similarity REAL, rank INT,
            PRIMARY KEY (item_id, rank)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS model_metrics (
            id SERIAL PRIMARY KEY, metric_name TEXT, metric_value REAL,
            computed_at TIMESTAMP DEFAULT now()
        )
    """)


def main():
    users, items, labels, num_users, num_items = generate_interactions()
    u_train, u_test, i_train, i_test, y_train, y_test = train_test_split(
        users, items, labels, test_size=0.2, random_state=42
    )

    model = build_model(num_users, num_items)
    model.fit(
        [u_train, i_train], y_train,
        validation_data=([u_test, i_test], y_test),
        epochs=5, batch_size=64, verbose=2,
    )
    loss, accuracy = model.evaluate([u_test, i_test], y_test, verbose=0)
    print(f"Held-out test accuracy: {accuracy:.3f}, loss: {loss:.3f}")

    item_embeddings = model.get_layer("item_embedding").get_weights()[0]
    similarity_matrix = cosine_similarity_matrix(item_embeddings)

    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        ensure_schema(conn)
        conn.execute("DELETE FROM recommendations")
        conn.execute("DELETE FROM item_similarity")
        conn.execute("DELETE FROM model_metrics")

        all_items = np.arange(num_items, dtype=np.int32)
        for user_id in range(num_users):
            user_batch = np.full_like(all_items, user_id)
            scores = model.predict([user_batch, all_items], verbose=0).flatten()
            top_idx = np.argsort(-scores)[:TOP_N_RECOMMENDATIONS]
            for rank, item_id in enumerate(top_idx):
                conn.execute(
                    "INSERT INTO recommendations (user_id, item_id, score, rank) VALUES (%s,%s,%s,%s)",
                    (user_id, int(item_id), float(scores[item_id]), rank),
                )

        for item_id in range(num_items):
            sims = similarity_matrix[item_id]
            ranked = np.argsort(-sims)
            top_idx = [int(i) for i in ranked if i != item_id][:TOP_N_SIMILAR_ITEMS]
            for rank, similar_item_id in enumerate(top_idx):
                conn.execute(
                    "INSERT INTO item_similarity (item_id, similar_item_id, similarity, rank) VALUES (%s,%s,%s,%s)",
                    (item_id, similar_item_id, float(sims[similar_item_id]), rank),
                )

        conn.execute("INSERT INTO model_metrics (metric_name, metric_value) VALUES (%s,%s)", ("test_accuracy", float(accuracy)))
        conn.execute("INSERT INTO model_metrics (metric_name, metric_value) VALUES (%s,%s)", ("test_loss", float(loss)))
        conn.execute("INSERT INTO model_metrics (metric_name, metric_value) VALUES (%s,%s)", ("num_users", float(num_users)))
        conn.execute("INSERT INTO model_metrics (metric_name, metric_value) VALUES (%s,%s)", ("num_items", float(num_items)))

    print("Training complete: recommendations, item similarities, and metrics written to Postgres.")


if __name__ == "__main__":
    main()
