class QueryExpander:

    OBJECTS = {
        "car": [
            "car",
            "vehicle",
            "automobile",
        ],
        "person": [
            "person",
            "man",
            "woman",
            "human",
        ],
        "truck": [
            "truck",
            "lorry",
        ],
        "motorcycle": [
            "motorcycle",
            "bike",
            "scooter",
        ],
    }

    COLORS = {
        "white": [
            "white",
            "silver",
            "ivory",
            "cream",
        ],
        "black": [
            "black",
            "dark",
        ],
        "gray": [
            "gray",
            "grey",
        ],
        "blue": [
            "blue",
            "navy",
        ],
        "red": [
            "red",
            "maroon",
        ],
    }

    @classmethod
    def expand(cls, query):

        query = query.lower()

        expanded = [query]

        for key, values in cls.OBJECTS.items():

            if key in query:

                expanded.extend(values)

        for key, values in cls.COLORS.items():

            if key in query:

                expanded.extend(values)

        return " ".join(dict.fromkeys(expanded))