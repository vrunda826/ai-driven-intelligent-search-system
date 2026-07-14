"""
Runtime manager for FAISS indices.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import faiss
import numpy as np

from core.exceptions import IndexLoadError
from core.logger import get_logger
from search.base_index import BaseIndex


class FAISSManager(BaseIndex):
    """
    Handles loading, saving and searching a FAISS index.
    """

    def __init__(
        self,
        config,
    ) -> None:

        self.config = config

        self.logger = get_logger(
            "faiss",
            config.get(
                "paths",
                "log_dir",
            ),
        )

        self.index = None

    def build(
        self,
        embeddings: np.ndarray,
    ) -> None:
        """
        Required by BaseIndex.

        Actual construction is handled by FAISSBuilder.
        """
        raise NotImplementedError(
            "Use FAISSBuilder.build()."
        )

    def save(
        self,
        path: str,
    ) -> None:

        if self.index is None:
            raise IndexLoadError(
                "No FAISS index available."
            )

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            self.index,
            str(path),
        )

        info = {

            "index_type": type(
                self.index
            ).__name__,

            "dimension": self.dimension,

            "vectors": self.ntotal,

            "metric": "Inner Product",

            "normalized": True,

            "created_at": datetime.utcnow().isoformat(),

            "version": "1.0",
        }

        info_path = path.with_name(
            "index_info.json"
        )

        with open(
            info_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                info,
                file,
                indent=4,
            )

        self.logger.info(
            f"FAISS index saved to {path}"
        )

    def load(
        self,
        path: str,
    ) -> None:

        path = Path(path)

        if not path.exists():

            raise IndexLoadError(
                f"{path} does not exist."
            )

        self.index = faiss.read_index(
            str(path),
        )

        self.logger.info(
            f"Loaded {self.ntotal} vectors."
        )

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int,
    ) -> tuple[np.ndarray, np.ndarray]:

        if self.index is None:

            raise IndexLoadError(
                "Index not loaded."
            )

        if query_embedding.ndim == 1:
            query_embedding = np.expand_dims(
                query_embedding,
                axis=0,
            )

        scores, indices = self.index.search(
            query_embedding.astype(
                np.float32
            ),
            top_k,
        )

        return scores[0], indices[0]

    @property
    def ntotal(
        self,
    ) -> int:

        return self.index.ntotal

    @property
    def dimension(
        self,
    ) -> int:

        return self.index.d

    def set_index(
        self,
        index: faiss.Index,
    ) -> None:
        """
        Injects an already-built index.
        """

        self.index = index
    def statistics(self):

        return {

        "vectors": self.ntotal,

        "dimension": self.dimension,

        "index_type": type(
            self.index
        ).__name__,

    }