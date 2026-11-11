# Architecture

The `training` job (Python, one-shot) reads historical data, trains a model,
and writes recommendations to Postgres. `similarity-cpp` is a native module
used for fast nearest-neighbor lookups. `serving-api` (Node) serves
recommendations from Postgres with a Redis cache in front, consumed by the
React `dashboard`.
