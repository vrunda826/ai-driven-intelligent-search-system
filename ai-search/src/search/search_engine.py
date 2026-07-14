"""
Semantic Search Engine.
"""

from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import pandas as pd
from search.query_preprocesser import QueryPreprocessor
from core.logger import get_logger

from search.schemas import (
    SearchRequest,
    SearchResult,
)
from search.constants import SIMILARITY_THRESHOLD
from search.query_embedder import QueryEmbedder
from search.metadata_mapper import MetadataMapper
from search.filters import ResultFilter
from search.result_ranker import ResultRanker
from search.faiss_manager import FAISSManager


class SearchEngine:

    def __init__(
        self,
        config,
        bundle,
        device,
    ):

        self.config = config
        self.threshold=SIMILARITY_THRESHOLD
        self.logger = get_logger(
            "search",
            config.get(
                "paths",
                "log_dir",
            ),
        )

        self.query_embedder = QueryEmbedder(
            bundle,
            device,
        )

        self.faiss = FAISSManager(
            config,
        )

        self.faiss.load(
            config.get(
                "paths",
                "faiss_index",
            )
        )

        self._verify_index()

        metadata = pd.read_csv(
            config.get(
                "paths",
                "embedding_metadata",
            )
        )
        if self.metadata is None or len(self.metadata) == 0:
            raise RuntimeError("Metadata not loaded.")
        self.mapper = MetadataMapper(
            metadata,
        )

    def search(
        self,
        request: SearchRequest,
    ) -> list[SearchResult]:

        start = perf_counter()

        request.top_k = min(
            request.top_k,
            self.faiss.ntotal,
        )
        if request.top_k <= 0:
            raise ValueError("top_k must be greater than 0.")
        candidate_pool = max(

            self.config.get(
                "search",
                "candidate_pool",
            ),

            request.top_k,

        )
        self.logger.info(
            f"Top-K : {request.top_k}"
        )

        self.logger.info(
            f"Candidate Pool : {candidate_pool}"
        )
        query = QueryPreprocessor.preprocess(request.query)
        query_embedding = (
            self.query_embedder.encode(
                query
            )
        )
        if self.faiss is None:
            raise RuntimeError("FAISS index has not been loaded.")
        scores, indices = self.faiss.search(
            query_embedding,
            candidate_pool,
        )

        results = self.mapper.map_results(
            indices,
            scores,
        )

        threshold = self.threshold

        results = [

            result

            for result in results

            if result.similarity_score >= threshold

        ]

        results = ResultFilter.apply(
            results,
            request.filters,
        )
        if len(results) == 0:
            return []
        results = ResultRanker.rank(
            results,
        )

        elapsed = perf_counter() - start

        self.logger.info(
            f"Query: {request.query}"
        )

        self.logger.info(
            f"Returned {len(results)} results."
        )

        self.logger.info(
            f"Search Time : {elapsed:.3f}s"
        )

        return results[: request.top_k]

    def _verify_index(
        self,
    ):

        info_path = Path(

            self.config.get(
                "paths",
                "index_dir",
            )

        ) / "index_info.json"

        with open(
            info_path,
            encoding="utf-8",
        ) as file:

            info = json.load(file)

        expected = self.config.get(
            "faiss",
            "dimension",
        )

        if info["dimension"] != expected:

            raise ValueError(
                "Embedding dimension mismatch."
            )

        if info["metric"] != "Inner Product":

            raise ValueError(
                "Unsupported FAISS metric."
            )
    def health(self):

        return {

            "vectors": self.faiss.ntotal,

            "dimension": self.faiss.dimension,

            "threshold": self.config.getfloat(
                "search",
                "threshold",
            ),

        }