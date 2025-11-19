"""User correction entity for learning system."""
from dataclasses import dataclass
from datetime import datetime

from src.models.outcome import Outcome


@dataclass
class UserCorrection:
    """Represents a user correction for a misidentified shot."""

    original_outcome: Outcome
    corrected_outcome: Outcome
    timestamp: datetime
    user_notes: str = ""

    def to_dict(self) -> dict:
        """
        Serialize to JSON.

        Returns:
            Dictionary representation
        """
        return {
            "original_outcome": str(self.original_outcome),
            "corrected_outcome": str(self.corrected_outcome),
            "timestamp": self.timestamp.isoformat(),
            "user_notes": self.user_notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserCorrection":
        """
        Deserialize from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            UserCorrection instance
        """
        return cls(
            original_outcome=Outcome(data["original_outcome"]),
            corrected_outcome=Outcome(data["corrected_outcome"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            user_notes=data.get("user_notes", ""),
        )
