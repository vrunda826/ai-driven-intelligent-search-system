"""
OpenCLIP embedding generation.
"""

from typing import Dict

import numpy as np
import torch

from embedding.base_embedder import BaseEmbedder


class ImageEmbedder(BaseEmbedder):
    """
    Generates OpenCLIP embeddings.
    """

    def __init__(
        self,
        model,
        device: torch.device,
        normalize: bool = True,
    ):

        self.model = model

        self.device = device

        self.normalize = normalize

    @torch.inference_mode()
    def generate(
        self,
        batch: torch.Tensor,
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Generate embeddings for one image batch.
        """

        batch = batch.to(
            self.device,
            non_blocking=True,
        )

        embeddings = self.model.encode_image(batch)

        if self.normalize:

            embeddings = embeddings / embeddings.norm(
                dim=-1,
                keepdim=True,
            )

        return embeddings.cpu().numpy()