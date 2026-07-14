"""
Generates normalized OpenCLIP text embeddings.
"""

from __future__ import annotations
from search.constants import MAX_QUERY_LENGTH
import numpy as np
import torch
import re

class QueryEmbedder:
    """
    Encodes natural language queries into OpenCLIP embeddings.
    """

    def __init__(
        self,
        bundle,
        device,
    ) -> None:

        self.model = bundle.model
        self.tokenizer = bundle.tokenizer
        self.device = device
        self.MAX_QUERY_LENGTH=MAX_QUERY_LENGTH

    @torch.inference_mode()
    def encode(
        self,
        query: str,
    ) -> np.ndarray:
        """
        Converts a text query into a normalized embedding.
        """

        query = re.sub(
            r"\s+",
            " ",
            query.strip(),
        )

        if not query:
            raise ValueError(
                "Query cannot be empty."
            )

        if len(query) > self.MAX_QUERY_LENGTH:
            raise ValueError(
                f"Query exceeds {self.MAX_QUERY_LENGTH} characters."
            )

        tokens = self.tokenizer([query]).to(
            self.device
        )

        embedding = self.model.encode_text(
            tokens
        )

        embedding /= embedding.norm(
            dim=-1,
            keepdim=True,
        )

        return (
            embedding.squeeze(0)
            .cpu()
            .numpy()
            .astype(np.float32)
        )