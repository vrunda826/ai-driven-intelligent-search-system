"""
Structured metadata filters.
"""

from datetime import datetime

from search.schemas import (
    FilterConfig,
    SearchResult,
)


class ResultFilter:

    @staticmethod
    def apply(

        results,

        filters,

    ):

        filtered = results

        if filters.camera_id:

            filtered = [

                r

                for r in filtered

                if r.camera_id == filters.camera_id

            ]

        if filters.class_name:

            filtered = [

                r

                for r in filtered

                if r.class_name == filters.class_name

            ]

        try:

            if filters.start_time:

                start = datetime.fromisoformat(
                    filters.start_time
                )

                filtered = [

                    r

                    for r in filtered

                    if datetime.fromisoformat(
                        r.first_seen_time
                    )
                    >= start

                ]

            if filters.end_time:

                end = datetime.fromisoformat(
                    filters.end_time
                )

                filtered = [

                    r

                    for r in filtered

                    if datetime.fromisoformat(
                        r.last_seen_time
                    )
                    <= end

                ]

        except ValueError:

            raise ValueError(
                "Invalid ISO datetime."
            )

        return filtered