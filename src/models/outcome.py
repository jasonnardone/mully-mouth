"""Shot outcome enumeration."""
from enum import Enum


class Outcome(str, Enum):
    """Possible shot outcomes detected by the system."""

    FAIRWAY = "fairway"
    GREEN = "green"
    WATER = "water"
    BUNKER = "bunker"
    ROUGH = "rough"
    TREES = "trees"
    OUT_OF_BOUNDS = "out_of_bounds"
    TEE_SHOT = "tee_shot"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return self.value
