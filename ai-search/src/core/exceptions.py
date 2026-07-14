"""
Custom exceptions used across the Smart CCTV Search project.
"""


class EmbeddingError(Exception):
    """Base exception for embedding-related errors."""


class InvalidEmbeddingError(EmbeddingError):
    """Raised when generated embeddings fail validation."""


class ImageLoadingError(Exception):
    """Raised when an image cannot be loaded."""


class MetadataError(Exception):
    """Raised when metadata is invalid or missing."""

class IndexBuildError(Exception):
    """Raised when the FAISS index cannot be built."""


class IndexLoadError(Exception):
    """Raised when a FAISS index cannot be loaded."""