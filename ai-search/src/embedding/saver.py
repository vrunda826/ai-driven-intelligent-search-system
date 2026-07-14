"""
Save embeddings and metadata.
"""

from pathlib import Path

import numpy as np
import pandas as pd


class EmbeddingSaver:
    """
    Saves generated embeddings and corresponding metadata.
    """

    def __init__(
        self,
        embedding_path: str,
        metadata_path: str,
    ):

        self.embedding_path = Path(embedding_path)
        self.metadata_path = Path(metadata_path)

        self.embedding_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.metadata_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save_embeddings(
        self,
        embeddings: np.ndarray,
    ) -> None:

        np.save(
            self.embedding_path,
            embeddings,
        )

    def save_metadata(
        self,
        metadata: pd.DataFrame,
    ) -> None:

        metadata.to_csv(
            self.metadata_path,
            index=False,
        )