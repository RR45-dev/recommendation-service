"""
Synthetic user-item interaction data. Real deployments would pull this from
clickstream/purchase history; generating it here keeps the whole project
runnable with no external dataset download, while still giving the model
real latent structure to learn (users and items are assigned to one of a
handful of "taste clusters").
"""
import numpy as np


def generate_interactions(num_users=500, num_items=150, num_interactions=8000, seed=42):
    rng = np.random.default_rng(seed)
    num_clusters = 5
    user_cluster = rng.integers(0, num_clusters, size=num_users)
    item_cluster = rng.integers(0, num_clusters, size=num_items)

    users, items, labels = [], [], []

    for _ in range(num_interactions):
        u = rng.integers(0, num_users)
        if rng.random() < 0.8:
            candidates = np.where(item_cluster == user_cluster[u])[0]
            if len(candidates) == 0:
                candidates = np.arange(num_items)
        else:
            candidates = np.arange(num_items)
        i = rng.choice(candidates)
        users.append(u)
        items.append(i)
        labels.append(1 if item_cluster[i] == user_cluster[u] else 0)

    # Explicit random negative/positive samples so the label distribution
    # isn't dominated by the clustered sampling above.
    for _ in range(num_interactions // 2):
        u = rng.integers(0, num_users)
        i = rng.integers(0, num_items)
        users.append(u)
        items.append(i)
        labels.append(1 if item_cluster[i] == user_cluster[u] else 0)

    return (
        np.array(users, dtype=np.int32),
        np.array(items, dtype=np.int32),
        np.array(labels, dtype=np.float32),
        num_users,
        num_items,
    )
