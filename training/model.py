"""
Simple neural collaborative-filtering model: separate embedding tables for
users and items, combined with a dot product and a sigmoid output predicting
"will this user engage with this item". Small and fast enough to train in a
minute or two on CPU, which is the point for a portfolio-scale project —
swap in a deeper tower model or a sequence model for production scale.
"""
import tensorflow as tf


def build_model(num_users: int, num_items: int, embedding_dim: int = 32) -> tf.keras.Model:
    user_input = tf.keras.Input(shape=(1,), name="user_id")
    item_input = tf.keras.Input(shape=(1,), name="item_id")

    user_embedding = tf.keras.layers.Embedding(num_users, embedding_dim, name="user_embedding")(user_input)
    item_embedding = tf.keras.layers.Embedding(num_items, embedding_dim, name="item_embedding")(item_input)

    user_vec = tf.keras.layers.Flatten()(user_embedding)
    item_vec = tf.keras.layers.Flatten()(item_embedding)

    dot = tf.keras.layers.Dot(axes=1)([user_vec, item_vec])
    output = tf.keras.layers.Activation("sigmoid", name="engagement_probability")(dot)

    model = tf.keras.Model(inputs=[user_input, item_input], outputs=output)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model
