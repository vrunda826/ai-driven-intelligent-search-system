from abc import ABC, abstractmethod

import numpy as np
import torch


class BaseEmbedder(ABC):

    @abstractmethod
    def generate(
        self,
        batch: torch.Tensor,
    ) -> np.ndarray:
        pass