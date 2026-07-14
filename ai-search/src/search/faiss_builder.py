"""
Builds a FAISS index from image embeddings.
"""

from __future__ import annotations

import faiss
import numpy as np

from core.exceptions import IndexBuildError


class FAISSBuilder:
    """
    Builds a FAISS index from normalized embeddings.
    """

    def __init__(
        self,
        dimension: int,
    ) -> None:

        self.dimension = dimension

    def build(
        self,
        embeddings: np.ndarray,
    ) -> faiss.Index:

        self._validate(embeddings)

        index = faiss.IndexFlatIP(
            self.dimension,
        )

        index.add(embeddings)

        return index

    def _validate(
        self,
        embeddings: np.ndarray,
    ) -> None:

        if embeddings.size == 0:
            raise IndexBuildError(
                "Embedding array is empty."
            )

        if embeddings.dtype != np.float32:
            raise IndexBuildError(
                "Embeddings must be float32."
            )

        if embeddings.ndim != 2:
            raise IndexBuildError(
                "Embeddings must be 2-dimensional."
            )

        if embeddings.shape[1] != self.dimension:
            raise IndexBuildError(
                f"Expected embedding dimension "
                f"{self.dimension}, "
                f"received {embeddings.shape[1]}."
            )

        if np.isnan(embeddings).any():
            raise IndexBuildError(
                "Embeddings contain NaN values."
            )

        if np.isinf(embeddings).any():
            raise IndexBuildError(
                "Embeddings contain Inf values."
            )