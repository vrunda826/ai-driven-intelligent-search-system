"""
Loads and validates metadata.csv.
"""

from pathlib import Path

import pandas as pd

from core.exceptions import MetadataError


class MetadataLoader:
    """
    Load metadata from CSV.
    """
    REQUIRED_COLUMNS = {
        "track_id",
        "camera_id",
        "class_name",
        "first_seen_time",
        "last_seen_time",
        "num_observations",
        "max_confidence",
        "description",
    }

    def __init__(self, csv_path: str):

        self.csv_path = Path(csv_path)

    def load(self) -> pd.DataFrame:

        if not self.csv_path.exists():
            raise MetadataError(
                f"Metadata not found: {self.csv_path}"
            )

        metadata = pd.read_csv(self.csv_path)

        missing = self.REQUIRED_COLUMNS - set(metadata.columns)

        if missing:
            raise MetadataError(
                f"Missing required columns: {missing}"
            )

        metadata = metadata.sort_values(
            by="track_id"
        ).reset_index(drop=True)

        return metadata