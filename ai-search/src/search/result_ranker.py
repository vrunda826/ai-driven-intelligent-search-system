"""
Hybrid Result Ranking.
"""

from search.query_preprocesser import QueryPreprocessor


class ResultRanker:

    CLIP_WEIGHT = 0.60

    CLASS_WEIGHT = 0.15
    COLOR_WEIGHT = 0.10
    VEHICLE_TYPE_WEIGHT = 0.08

    SHIRT_WEIGHT = 0.03
    PANT_WEIGHT = 0.03
    CAP_WEIGHT = 0.02
    BAG_WEIGHT = 0.02

    LOCATION_WEIGHT = 0.05
    ACTION_WEIGHT = 0.05

    EXACT_QUERY_WEIGHT = 0.15

    @staticmethod
    def rank(results, query=None):

        if not query:

            for r in results:
                r.final_score = r.similarity_score

            return sorted(
                results,
                key=lambda x: x.final_score,
                reverse=True,
            )

        cleaned_query, parsed = QueryPreprocessor.preprocess(query)

        cleaned_query = cleaned_query.lower()

        for r in results:

            score = r.similarity_score * ResultRanker.CLIP_WEIGHT

            description = getattr(
                r,
                "description",
                "",
            ).lower()

            class_name = getattr(
                r,
                "class_name",
                "",
            ).lower()

            vehicle_type = getattr(
                r,
                "vehicle_type",
                "",
            ).lower()

            location = getattr(
                r,
                "location",
                "",
            ).lower()

            action = getattr(
                r,
                "action",
                "",
            ).lower()

            if (
                parsed.class_name
                and parsed.class_name == class_name
            ):
                score += ResultRanker.CLASS_WEIGHT

            if (
                parsed.color
                and parsed.color in description
            ):
                score += ResultRanker.COLOR_WEIGHT

            if (
                parsed.vehicle_type
                and (
                    parsed.vehicle_type == vehicle_type
                    or parsed.vehicle_type in description
                )
            ):
                score += ResultRanker.VEHICLE_TYPE_WEIGHT

            if (
                parsed.shirt_color
                and f"{parsed.shirt_color} shirt" in description
            ):
                score += ResultRanker.SHIRT_WEIGHT

            if (
                parsed.pant_color
                and parsed.pant_color in description
                and (
                    "pant" in description
                    or "trouser" in description
                )
            ):
                score += ResultRanker.PANT_WEIGHT

            if parsed.cap and "cap" in description:
                score += ResultRanker.CAP_WEIGHT

            if parsed.bag and "bag" in description:
                score += ResultRanker.BAG_WEIGHT

            if (
                parsed.location
                and (
                    parsed.location == location
                    or parsed.location in description
                )
            ):
                score += ResultRanker.LOCATION_WEIGHT

            if (
                parsed.action
                and (
                    parsed.action == action
                    or parsed.action in description
                )
            ):
                score += ResultRanker.ACTION_WEIGHT

            if cleaned_query and cleaned_query in description:
                score += ResultRanker.EXACT_QUERY_WEIGHT

            r.final_score = round(score, 4)

        return sorted(
            results,
            key=lambda x: x.final_score,
            reverse=True,
        )