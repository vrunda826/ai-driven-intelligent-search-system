"""
Ranks semantic search results.
"""

from __future__ import annotations

from search.schemas import SearchResult


class ResultRanker:

    @staticmethod
    def rank(
        results: list[SearchResult],
    ) -> list[SearchResult]:

        return sorted(

            results,

            key=lambda result:
            result.similarity_score,

            reverse=True,

        )