"""Shot Event entity."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import numpy as np

from src.models.outcome import Outcome


@dataclass
class ShotEvent:
    """Represents a detected golf shot with analysis results."""

    id: str
    timestamp: datetime
    screenshot: np.ndarray
    screenshot_hash: str
    detected_outcome: Outcome
    confidence: float
    commentary_text: str
    was_cached: bool
    api_cost: float
    correction: Optional["UserCorrection"] = None

    def to_dict(self) -> dict:
        """
        Serialize to JSON (excluding screenshot which is too large).

        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "screenshot_hash": self.screenshot_hash,
            "detected_outcome": str(self.detected_outcome),
            "confidence": self.confidence,
            "commentary_text": self.commentary_text,
            "was_cached": self.was_cached,
            "api_cost": self.api_cost,
            "correction": self.correction.to_dict() if self.correction else None,
        }

    @classmethod
    def from_dict(cls, data: dict, screenshot: Optional[np.ndarray] = None) -> "ShotEvent":
        """
        Deserialize from dictionary.

        Args:
            data: Dictionary representation
            screenshot: Optional screenshot array (not stored in dict)

        Returns:
            ShotEvent instance
        """
        from src.models.correction import UserCorrection  # Avoid circular import

        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            screenshot=screenshot if screenshot is not None else np.array([]),
            screenshot_hash=data["screenshot_hash"],
            detected_outcome=Outcome(data["detected_outcome"]),
            confidence=data["confidence"],
            commentary_text=data["commentary_text"],
            was_cached=data["was_cached"],
            api_cost=data["api_cost"],
            correction=(
                UserCorrection.from_dict(data["correction"])
                if data.get("correction")
                else None
            ),
        )


# Type stub to avoid circular import issues
UserCorrection = "UserCorrection"
