from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(slots=True)
class ModelBundle:
    """
    Stores all OpenCLIP components.
    """

    model: Any
    preprocess: Any
    tokenizer: Any


@dataclass(slots=True)
class CropSample:
    """
    Represents one cropped object and its metadata.
    """

    image_path: Path
    metadata: pd.Series