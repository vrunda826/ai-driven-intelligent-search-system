from dataclasses import dataclass

@dataclass
class QueryIntent:

    object=None

    color=None

    vehicle_type=None

    shirt_color=None

    pant_color=None

    cap=False

    bag=False

    action=None

    location=None

    remaining_text=""