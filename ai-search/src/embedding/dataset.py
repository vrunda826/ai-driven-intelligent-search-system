"""
Dataset returning all crops for one tracked object.
"""

from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset


class CropDataset(Dataset):

    def __init__(
        self,
        image_dir: str,
        metadata,
        preprocess,
    ):
        self.image_dir = Path(image_dir)
        self.metadata = metadata
        self.preprocess = preprocess

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):

        row = self.metadata.iloc[idx]

        track_id = row["track_id"]

        image_paths = sorted(list(self.image_dir.glob(f"{track_id}_*.*")))

        images = []

        for path in image_paths:
            with Image.open(path) as img:
                img = img.convert("RGB")
                img = self.preprocess(img)
                images.append(img)

        return {
            "track_id": track_id,
            "images": images,
            "metadata": row.to_dict(),
        }