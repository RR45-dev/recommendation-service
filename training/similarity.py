import numpy as np

try:
    import simfast  # compiled C++ extension (see similarity-cpp/)

    def cosine_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
        return simfast.cosine_similarity_matrix(embeddings.astype(np.float64))

except ImportError:
    def cosine_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
        # Pure-NumPy fallback so the pipeline still runs before the C++
        # extension has been built — see similarity-cpp/README.md.
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-9
        normalized = embeddings / norms
        return normalized @ normalized.T
