"""
Abstract interface for vector indices.
"""

from abc import ABC, abstractmethod

import numpy as np


class BaseIndex(ABC):
    """
    Base interface for all vector index implementations.
    """

    @abstractmethod
    def build(
        self,
        embeddings: np.ndarray,
    ) -> None:
        """
        Build the index from embeddings.
        """
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        path: str,
    ) -> None:
        """
        Persist the index to disk.
        """
        raise NotImplementedError

    @abstractmethod
    def load(
        self,
        path: str,
    ) -> None:
        """
        Load an index from disk.
        """
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Search for the nearest neighbours.

        Returns
        -------
        scores : np.ndarray
        indices : np.ndarray
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def ntotal(self) -> int:
        """
        Number of indexed vectors.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Embedding dimension.
        """
        raise NotImplementedError