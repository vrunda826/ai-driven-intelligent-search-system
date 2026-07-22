"""
Structured metadata filters.
"""

from datetime import datetime


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

                if getattr(r, "camera_id", "").lower()
                == filters.camera_id.lower()

            ]

        if filters.class_name:

            filtered = [

                r

                for r in filtered

                if getattr(r, "class_name", "").lower()
                == filters.class_name.lower()

            ]

        if filters.color:

            filtered = [

                r

                for r in filtered

                if (

                    getattr(r, "color", "").lower()
                    == filters.color.lower()

                )

                or (

                    filters.color.lower()
                    in getattr(r, "description", "").lower()

                )

            ]

        if filters.vehicle_type:

            filtered = [

                r

                for r in filtered

                if (

                    getattr(r, "vehicle_type", "").lower()
                    == filters.vehicle_type.lower()

                )

                or (

                    filters.vehicle_type.lower()
                    in getattr(r, "description", "").lower()

                )

            ]

        if filters.shirt_color:

            filtered = [

                r

                for r in filtered

                if (

                    getattr(r, "shirt_color", "").lower()
                    == filters.shirt_color.lower()

                )

                or (

                    f"{filters.shirt_color.lower()} shirt"
                    in getattr(r, "description", "").lower()

                )

            ]

        if filters.pant_color:

            filtered = [

                r

                for r in filtered

                if (

                    getattr(r, "pant_color", "").lower()
                    == filters.pant_color.lower()

                )

                or (

                    f"{filters.pant_color.lower()} pants"
                    in getattr(r, "description", "").lower()

                )

            ]

        if filters.cap:

            filtered = [

                r

                for r in filtered

                if (

                    getattr(r, "cap", False)

                )

                or (

                    "cap"
                    in getattr(r, "description", "").lower()

                )

            ]

        if filters.bag:

            filtered = [

                r

                for r in filtered

                if (

                    getattr(r, "bag", False)

                )

                or (

                    "bag"
                    in getattr(r, "description", "").lower()

                )

            ]

        if filters.location:

            filtered = [

                r

                for r in filtered

                if (

                    getattr(r, "location", "").lower()
                    == filters.location.lower()

                )

                or (

                    filters.location.lower()
                    in getattr(r, "description", "").lower()

                )

            ]

        if getattr(filters, "action", None):

            filtered = [

                r

                for r in filtered

                if (

                    getattr(r, "action", "").lower()
                    == filters.action.lower()

                )

                or (

                    filters.action.lower()
                    in getattr(r, "description", "").lower()

                )

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