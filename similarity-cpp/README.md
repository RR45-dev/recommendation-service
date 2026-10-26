# simfast — C++ cosine similarity module

Build it:

```bash
pip install pybind11
python setup.py build_ext --inplace
```

This produces a `simfast*.so` (or `.pyd` on Windows) importable from Python:

```python
import simfast
import numpy as np
sims = simfast.cosine_similarity_matrix(embeddings.astype(np.float64))
```

The training pipeline (`training/similarity.py`) imports this module and
falls back to a pure-NumPy implementation automatically if it hasn't been
built yet, so `docker compose up` works either way — the Docker image for
`training/` builds this extension as part of its image build.
