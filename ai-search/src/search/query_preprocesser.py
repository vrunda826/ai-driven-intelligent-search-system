import re

from search.schemas import FilterConfig


class QueryPreprocessor:

    COLOR_SYNONYMS = {
        "white": ["white", "ivory", "cream"],
        "black": ["black", "dark"],
        "gray": ["gray", "grey", "silver"],
        "blue": ["blue", "navy"],
        "red": ["red", "maroon"],
        "green": ["green"],
        "yellow": ["yellow"],
        "orange": ["orange"],
        "brown": ["brown"],
        "beige": ["beige", "tan"],
        "purple": ["purple"],
        "pink": ["pink"],
        "gold": ["gold"],
    }
    QUERY_EXPANSIONS = {

            "dark": [
                "black",
                "navy",
                "dark",
            ],

            "light": [
                "white",
                "gray",
                "silver",
                "beige",
            ],

            "vehicle": [
                "car",
                "automobile",
            ],

            "person": [
                "man",
                "woman",
                "human",
            ],

            "motorbike": [
                "motorcycle",
                "bike",
            ],
        }
    OBJECT_SYNONYMS = {
        "car": [
            "car",
            "cars",
            "vehicle",
            "vehicles",
            "automobile",
        ],
        "motorcycle": [
            "motorcycle",
            "bike",
            "bikes",
            "scooter",
        ],
        "truck": [
            "truck",
            "lorry",
        ],
        "bus": [
            "bus",
        ],
        "person": [
            "person",
            "people",
            "man",
            "woman",
            "boy",
            "girl",
            "human",
            "lady",
            "gentleman",
        ],
    }

    VEHICLE_TYPES = {
        "sedan",
        "suv",
        "hatchback",
        "pickup",
        "truck",
        "bus",
        "motorcycle",
    }

    LOCATION_WORDS = {
        "gate",
        "parking",
        "road",
        "street",
        "entrance",
        "entry",
        "exit",
        "crossing",
        "corridor",
        "lobby",
        "hall",
    }

    ACTION_WORDS = {
        "walking",
        "running",
        "standing",
        "parking",
        "crossing",
        "entering",
        "leaving",
        "waiting",
        "driving",
        "coming",
        "going",
    }

    @classmethod
    def preprocess(cls, query):

        query = query.lower().strip()

        expanded = query

        if "dark vehicle" in expanded:
            expanded += " black car"

        if "light vehicle" in expanded:
            expanded += " white car"

        if "light colored" in expanded:
            expanded += " white"

        if "dark colored" in expanded:
            expanded += " black"

        if "automobile" in expanded:
            expanded += " car"

        if "bike" in expanded:
            expanded += " motorcycle"

        filters = FilterConfig()

        words = set(re.findall(r"\w+", expanded))

        cleaned = expanded

        for canonical, synonyms in cls.COLOR_SYNONYMS.items():

            for word in synonyms:

                if word in words:

                    filters.color = canonical

                    cleaned = re.sub(
                        rf"\b{re.escape(word)}\b",
                        canonical,
                        cleaned,
                    )

                    break

        for canonical, synonyms in cls.OBJECT_SYNONYMS.items():

            for word in synonyms:

                if word in words:

                    filters.class_name = canonical

                    cleaned = re.sub(
                        rf"\b{re.escape(word)}\b",
                        canonical,
                        cleaned,
                    )

                    break

        for vehicle in cls.VEHICLE_TYPES:

            if vehicle in words:

                filters.vehicle_type = vehicle

                break

        if "shirt" in words:

            for color in cls.COLOR_SYNONYMS:

                if color in words:

                    filters.shirt_color = color

                    break

        if (
            "pant" in words
            or "pants" in words
            or "trouser" in words
            or "trousers" in words
        ):

            for color in cls.COLOR_SYNONYMS:

                if color in words:

                    filters.pant_color = color

                    break

        if "cap" in words or "hat" in words:
            filters.cap = True

        if (
            "bag" in words
            or "backpack" in words
            or "handbag" in words
            or "luggage" in words
        ):
            filters.bag = True

        for location in cls.LOCATION_WORDS:

            if location in words:

                filters.location = location

                break

        for action in cls.ACTION_WORDS:

            if action in words:

                filters.action = action

                break

        cleaned = " ".join(cleaned.split())
        expanded = cleaned

        for key, values in cls.QUERY_EXPANSIONS.items():

            if key in cleaned:

                expanded += " " + " ".join(values)

        expanded = " ".join(expanded.split())

        return expanded, filters
        return cleaned, filters