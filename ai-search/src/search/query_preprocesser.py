"""
Query preprocessing utilities.
"""

import re


class QueryPreprocessor:

    @staticmethod
    def preprocess(query: str) -> str:
        """
        Clean user query before encoding.
        """

        query = query.lower().strip()

        query = re.sub(r"[^\w\s]", " ", query)

        query = re.sub(r"\s+", " ", query)

        return query