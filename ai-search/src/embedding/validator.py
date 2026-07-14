"""
Embedding validation.
"""

import numpy as np

from core.exceptions import (
    InvalidEmbeddingError,
)


class EmbeddingValidator:
    """
    Validate generated embeddings.
    """

    @staticmethod
    def validate(
        embeddings: np.ndarray,
    ) -> None:

        if embeddings.ndim != 2:
            raise InvalidEmbeddingError(
                "Embeddings must be 2-dimensional."
            )

        if np.isnan(embeddings).any():
            raise InvalidEmbeddingError(
                "NaN values found."
            )

        if np.isinf(embeddings).any():
            raise InvalidEmbeddingError(
                "Infinite values found."
            )

        norms = np.linalg.norm(
            embeddings,
            axis=1,
        )

        if not np.allclose(
            norms,
            1.0,
            atol=1e-3,
        ):
            raise InvalidEmbeddingError(
                "Embeddings are not normalized."
            )

    @staticmethod
    def summary(
        embeddings: np.ndarray,
    ) -> dict:

        norms = np.linalg.norm(
            embeddings,
            axis=1,
        )

        unique = np.unique(
            embeddings,
            axis=0,
        ).shape[0]

        return {

            "Shape": embeddings.shape,

            "DType": str(
                embeddings.dtype,
            ),

            "Average Norm": float(
                norms.mean(),
            ),

            "Minimum Norm": float(
                norms.min(),
            ),

            "Maximum Norm": float(
                norms.max(),
            ),

            "NaN Count": int(
                np.isnan(
                    embeddings
                ).sum()
            ),

            "Inf Count": int(
                np.isinf(
                    embeddings
                ).sum()
            ),

            "Duplicate Embeddings":
                embeddings.shape[0] - unique,
        }