# RecoEngine — AI Product Recommendation Service

## Business problem

An e-commerce or content site showing every visitor the same generic "bestsellers" list leaves engagement on the table — personalized "customers also liked" recommendations reliably lift click-through over generic lists. RecoEngine trains a small collaborative-filtering model offline and serves personalized recommendations (plus item-to-item similarity for cold-start/related-items use cases) from a low-latency API.

## Architecture

```
training (Python/TensorFlow + C++ similarity module) --writes--> PostgreSQL
                                                                      |
                                                                      v
                                          serving-api (Node.js) --cache--> Redis
                                                      |
                                                      v
                                        dashboard (React/TypeScript, admin)
```

1. **training** (**Python**, **TensorFlow**) generates synthetic user-item interaction data with real latent structure, trains a neural collaborative-filtering model (user/item embeddings + dot product), and evaluates held-out accuracy.
2. It then computes the full item-item cosine-similarity matrix using a **C++** extension (`similarity-cpp/`, built with **pybind11**) — the kind of hot loop that's worth dropping into C++ once the catalog is large — falling back to a pure-NumPy implementation automatically if the extension isn't built yet.
3. Per-user top-10 recommendations, per-item top-5 similar items, and model quality metrics are written to **PostgreSQL**.
4. **serving-api** (**Node.js**/Express) serves that data over REST, caching hot lookups in **Redis** so repeat requests don't hit Postgres.
5. **dashboard** (**React** + **TypeScript**) is an admin view: current model quality metrics, a per-user recommendation lookup, and a per-item similarity lookup.

## Tech stack coverage

Python, C++ (via pybind11), TypeScript, TensorFlow, PostgreSQL, Redis, Node.js, REST APIs, React.

## Running it locally

```bash
docker compose up --build
```

The `training` service runs once, trains the model (a few minutes on CPU), writes results to Postgres, and exits — then `serving-api` and `dashboard` serve what it produced.

- Dashboard: http://localhost:3003
- Serving API: http://localhost:5000/api/recommendations/1

To retrain after changing the model or data generation:

```bash
docker compose run --rm training
```

## Building the C++ extension standalone (outside Docker)

```bash
cd similarity-cpp
pip install pybind11
python setup.py build_ext --inplace
cp simfast*.so ../training/
```

## Taking it further (what to mention in an interview)

- Replace the synthetic data generator with a real interaction log export (purchases, clicks, add-to-cart) and add implicit-feedback weighting.
- Add a proper offline evaluation metric (precision@k / recall@k against a held-out set) instead of raw binary-classification accuracy.
- Serve the model directly for cold-start users (e.g. content-based fallback using item metadata) instead of only the precomputed table.
- Add a scheduled retraining job (cron/Airflow) instead of the current one-shot `docker compose run training`.
