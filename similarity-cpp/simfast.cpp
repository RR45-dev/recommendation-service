#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <vector>
#include <stdexcept>

namespace py = pybind11;

/*
 * Computes the full pairwise cosine-similarity matrix for a set of item
 * embedding vectors. Written in C++ (called from Python via pybind11)
 * because computing this in pure Python/NumPy loops becomes the bottleneck
 * in the offline recommendation job once the catalog grows past a few
 * thousand items — this is O(n^2 * dim) either way, but the constant factor
 * of a tight C++ loop matters a lot at that scale.
 */
py::array_t<double> cosine_similarity_matrix(py::array_t<double> embeddings) {
    auto buf = embeddings.request();
    if (buf.ndim != 2) {
        throw std::runtime_error("expected a 2D array of shape (num_items, embedding_dim)");
    }

    size_t n = buf.shape[0];
    size_t dim = buf.shape[1];
    const double *data = static_cast<double *>(buf.ptr);

    std::vector<double> norms(n);
    for (size_t i = 0; i < n; ++i) {
        double sumsq = 0.0;
        for (size_t d = 0; d < dim; ++d) {
            double v = data[i * dim + d];
            sumsq += v * v;
        }
        norms[i] = std::sqrt(sumsq) + 1e-9;
    }

    py::array_t<double> result({n, n});
    auto res_buf = result.request();
    double *res_data = static_cast<double *>(res_buf.ptr);

    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            double dot = 0.0;
            for (size_t d = 0; d < dim; ++d) {
                dot += data[i * dim + d] * data[j * dim + d];
            }
            res_data[i * n + j] = dot / (norms[i] * norms[j]);
        }
    }
    return result;
}

PYBIND11_MODULE(simfast, m) {
    m.doc() = "Fast cosine similarity for item embeddings";
    m.def("cosine_similarity_matrix", &cosine_similarity_matrix,
          "Compute the pairwise cosine similarity matrix for a (num_items, dim) embedding array");
}
