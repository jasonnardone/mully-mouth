"""Session entity."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from src.models.shot_event import ShotEvent


@dataclass
class Session:
    """Represents a single round of golf with aggregate statistics."""

    id: str
    start_time: datetime
    personality_name: str
    shot_events: List[ShotEvent] = field(default_factory=list)
    end_time: Optional[datetime] = None

    @property
    def total_api_calls(self) -> int:
        """Number of AI API calls made (non-cached shots)."""
        return sum(1 for shot in self.shot_events if not shot.was_cached)

    @property
    def total_cost(self) -> float:
        """Total AI API cost in USD."""
        return sum(shot.api_cost for shot in self.shot_events)

    @property
    def cache_hit_rate(self) -> float:
        """Percentage of shots served from cache."""
        if not self.shot_events:
            return 0.0
        cached = sum(1 for shot in self.shot_events if shot.was_cached)
        return cached / len(self.shot_events)

    @property
    def accuracy_rate(self) -> float:
        """
        Accuracy rate based on corrections.

        Returns:
            1.0 if no corrections (100% accurate), otherwise (total - corrections) / total
        """
        if not self.shot_events:
            return 1.0
        corrected_shots = [s for s in self.shot_events if s.correction]
        if not corrected_shots:
            return 1.0  # No corrections = 100% accurate
        return 1.0 - (len(corrected_shots) / len(self.shot_events))

    def to_dict(self) -> dict:
        """
        Serialize to JSON.

        Returns:
            Dictionary representation with computed statistics
        """
        return {
            "id": self.id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "personality_name": self.personality_name,
            "total_shots": len(self.shot_events),
            "total_api_calls": self.total_api_calls,
            "total_cost": self.total_cost,
            "cache_hit_rate": self.cache_hit_rate,
            "accuracy_rate": self.accuracy_rate,
        }

    @classmethod
    def from_dict(cls, data: dict, shot_events: Optional[List[ShotEvent]] = None) -> "Session":
        """
        Deserialize from dictionary.

        Args:
            data: Dictionary representation
            shot_events: Optional list of shot events (loaded separately)

        Returns:
            Session instance
        """
        return cls(
            id=data["id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=(
                datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
            ),
            personality_name=data["personality_name"],
            shot_events=shot_events if shot_events is not None else [],
        )
