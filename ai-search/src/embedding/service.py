"""
Embedding generation service.
"""

from time import perf_counter

import numpy as np
from torch.utils.data import DataLoader
from tqdm import tqdm
import torch
from embedding.dataset import CropDataset
from embedding.embedder import ImageEmbedder
from embedding.metadata_loader import MetadataLoader
from embedding.saver import EmbeddingSaver
from embedding.validator import EmbeddingValidator

def collate_tracks(batch):
    return batch
class EmbeddingService:
    """
    Orchestrates the complete embedding generation pipeline.
    """

    def __init__(
        self,
        config,
        bundle,
        device,
        logger,
    ):

        self.config = config
        self.bundle = bundle
        self.device = device
        self.logger = logger

    def run(self):

        total_start = perf_counter()

        metadata = self._load_metadata()

        dataloader = self._build_dataloader(metadata)

        embeddings = self._generate_embeddings(dataloader)

        self._validate_embeddings(embeddings)

        self._save_outputs(
            embeddings,
            metadata,
        )

        self.logger.info(
            f"Pipeline Completed in {perf_counter()-total_start:.2f} sec"
        )

    def _load_metadata(self):

        start = perf_counter()

        loader = MetadataLoader(
            self.config.get(
                "paths",
                "metadata_csv",
            )
        )

        metadata = loader.load()

        self.logger.info(
            f"Loaded {len(metadata)} metadata records."
        )

        self.logger.info(
            f"Metadata Loading Time : {perf_counter()-start:.2f}s"
        )

        return metadata

    def _build_dataloader(
        self,
        metadata,
    ):

        dataset = CropDataset(

            image_dir=self.config.get(
                "paths",
                "crop_dir",
            ),

            metadata=metadata,

            preprocess=self.bundle.preprocess,
        )

        dataloader = DataLoader(
            dataset,
            batch_size=1,
            shuffle=False,
            num_workers=self.config.get(
                "embedding",
                "num_workers",
            ),
            pin_memory=self.device.type == "cuda",
            collate_fn=collate_tracks,
        )
        self.logger.info(
            f"Dataset Size : {len(dataset)}"
        )

        return dataloader

    def _generate_embeddings(
    self,
    dataloader):
        

        start = perf_counter()

        embedder = ImageEmbedder(
                model=self.bundle.model,
                device=self.device,
            )
        all_embeddings = []

        for batch in tqdm(
                dataloader,
                desc="Generating Embeddings",
            ):

                # batch_size = 1 because each track has a variable
                # number of crop images
                sample = batch[0]

                images = sample["images"]

                if len(images) == 0:
                    self.logger.warning(
                        f"No crops found for track {sample['track_id']}"
                    )
                    continue

                image_batch = torch.stack(images)

                crop_embeddings = embedder.generate(
                    image_batch,
                    normalize=False,
                )

                track_embedding = crop_embeddings.mean(axis=0)
                track_embedding /= np.linalg.norm(track_embedding)

                all_embeddings.append(track_embedding)

        embeddings = np.stack(
                all_embeddings,
                axis=0,
            ).astype(np.float32)

        self.logger.info(
                f"Generated {embeddings.shape[0]} track embeddings."
            )

        self.logger.info(
                f"Embedding Generation Time : {perf_counter()-start:.2f}s"
            )

        return embeddings

    def _validate_embeddings(
        self,
        embeddings,
    ):

        EmbeddingValidator.validate(
            embeddings
        )

        stats = EmbeddingValidator.summary(
            embeddings
        )

        self.logger.info(
            "========== Embedding Validation =========="
        )

        for key, value in stats.items():

            self.logger.info(
                f"{key:<25}: {value}"
            )

        self.logger.info(
            "=========================================="
        )

    def _save_outputs(
        self,
        embeddings,
        metadata,
    ):

        start = perf_counter()

        saver = EmbeddingSaver(

            embedding_path=self.config.get(
                "paths",
                "embedding_file",
            ),

            metadata_path=self.config.get(
                "paths",
                "embedding_metadata",
            ),
        )

        saver.save_embeddings(
            embeddings
        )

        saver.save_metadata(
            metadata
        )

        self.logger.info(
            f"Saving Time : {perf_counter()-start:.2f}s"
        )