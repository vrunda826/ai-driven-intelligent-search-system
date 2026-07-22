"""
Dataclasses used by the semantic search module.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class FilterConfig:
    """
    Structured filters applied after semantic search.
    """


    camera_id: Optional[str] = None
    class_name: Optional[str] = None

    start_time: Optional[str] = None
    end_time: Optional[str] = None

    color: Optional[str] = None

    vehicle_type: Optional[str] = None

    shirt_color: Optional[str] = None
    pant_color: Optional[str] = None

    cap: Optional[bool] = None
    bag: Optional[bool] = None
    location: Optional[str] = None
    action: Optional[str] = None

@dataclass(slots=True)
class SearchRequest:
    """
    Represents a user search request.
    """

    query: str
    top_k: int
    filters: FilterConfig


@dataclass(slots=True)
class SearchResult:
    """
    Represents one semantic search result.
    """

    track_id: str
    camera_id: str
    class_name: str
    first_seen_time: str
    last_seen_time: str
    description: str
    similarity_score: float
    clip_score: float = 0.0
    final_score: float = 0.0

    @property
    def duration(self) -> tuple[str, str]:
        """
        Returns the object's visible time range.
        """
        return (
            self.first_seen_time,
            self.last_seen_time,
        )