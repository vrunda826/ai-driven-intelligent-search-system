class Diversifier:

    @staticmethod
    def diversify(results):

        final = []

        seen = set()

        for result in results:

            key = (

                result.track_id,

                result.description,

            )

            if key in seen:
                continue

            seen.add(key)

            final.append(result)

        return final