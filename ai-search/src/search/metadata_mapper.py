"""
Maps FAISS search results back to metadata.
"""

from __future__ import annotations

import pandas as pd

from search.schemas import SearchResult


class MetadataMapper:
    """
    Converts FAISS indices into SearchResult objects.
    """

    def __init__(
        self,
        metadata: pd.DataFrame,
    ) -> None:

        self.metadata = metadata.reset_index(
    drop=True
)

    def map_results(
        self,
        indices,
        scores,
    ) -> list[SearchResult]:

        results = []

        for idx, score in zip(indices, scores):

            if idx < 0:
                continue
            if idx >= len(self.metadata):
                continue
            row = self.metadata.iloc[idx]

            results.append(

                SearchResult(

                    track_id=row["track_id"],
                    camera_id=row["camera_id"],
                    class_name=row["class_name"],
                    first_seen_time=row["first_seen_time"],
                    last_seen_time=row["last_seen_time"],
                    description=row["description"],
                    similarity_score=float(score),
                    clip_score=float(score),
                    final_score=float(score),

                )

            )

        return results