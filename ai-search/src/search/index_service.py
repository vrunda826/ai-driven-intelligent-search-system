"""
Builds and persists the FAISS index.
"""

from __future__ import annotations

from pathlib import Path
from time import perf_counter

import numpy as np

from core.logger import get_logger
from search.faiss_builder import FAISSBuilder
from search.faiss_manager import FAISSManager


class IndexService:
    """
    Orchestrates FAISS index creation.
    """

    def __init__(self, config) -> None:

        self.config = config

        self.logger = get_logger(
            "index_service",
            config.get("paths", "log_dir"),
        )

        self.builder = FAISSBuilder(
            dimension=config.get(
                "faiss",
                "dimension",
            )
        )

        self.manager = FAISSManager(config)

    def run(self) -> None:

        start = perf_counter()

        embeddings = self._load_embeddings()

        index = self.builder.build(
            embeddings
        )

        self.manager.set_index(index)

        self.manager.save(
            self.config.get(
                "paths",
                "faiss_index",
            )
        )

        elapsed = perf_counter() - start

        self.logger.info(
            f"Index built successfully."
        )

        self.logger.info(
            f"Vectors : {self.manager.ntotal}"
        )

        self.logger.info(
            f"Dimension : {self.manager.dimension}"
        )

        self.logger.info(
            f"Completed in {elapsed:.2f}s"
        )

    def _load_embeddings(
        self,
    ) -> np.ndarray:

        path = Path(
            self.config.get(
                "paths",
                "embedding_dir",
            )
        ) / "embeddings.npy"

        self.logger.info(
            "Loading embeddings..."
        )

        embeddings = np.load(path)

        self.logger.info(
            f"Loaded {embeddings.shape[0]} embeddings."
        )

        return embeddings.astype(
            np.float32
        )