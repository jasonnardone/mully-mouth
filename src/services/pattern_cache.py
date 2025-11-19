"""Pattern cache service for screenshot matching and outcome prediction."""
import json
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

import imagehash
import numpy as np
from PIL import Image

from src.lib.exceptions import CacheError
from src.models.outcome import Outcome


@dataclass
class CachedPattern:
    """Represents a cached screenshot pattern with outcome."""

    hash: str
    outcome: Outcome
    confidence: float
    hit_count: int = 0
    last_used: Optional[str] = None


class PatternCacheService:
    """
    Pattern cache service using perceptual hashing.

    Matches similar screenshots to cached outcomes, reducing AI API calls.
    Uses imagehash library with Hamming distance threshold.
    """

    def __init__(self, cache_file: str = "data/cache/pattern_cache.json", hamming_threshold: int = 10):
        """
        Initialize pattern cache.

        Args:
            cache_file: Path to JSON cache file
            hamming_threshold: Maximum Hamming distance for match (default: 10)
        """
        self.cache_file = Path(cache_file)
        self.hamming_threshold = hamming_threshold
        self.patterns: Dict[str, CachedPattern] = {}
        self._lock = threading.Lock()

        # Ensure cache directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing cache
        self.load()

    def find_match(self, screenshot: np.ndarray) -> Optional[tuple[Outcome, float]]:
        """
        Find matching pattern in cache.

        Args:
            screenshot: Screenshot to match (RGB numpy array)

        Returns:
            Tuple of (outcome, confidence) if match found, None otherwise
        """
        with self._lock:
            # Compute perceptual hash
            img_hash = self._compute_hash(screenshot)

            # Search for match with Hamming distance < threshold
            best_match: Optional[CachedPattern] = None
            best_distance = self.hamming_threshold

            for cached_pattern in self.patterns.values():
                distance = img_hash - imagehash.hex_to_hash(cached_pattern.hash)

                if distance < best_distance:
                    best_distance = distance
                    best_match = cached_pattern

            if best_match:
                # Update hit count
                best_match.hit_count += 1
                from datetime import datetime

                best_match.last_used = datetime.now().isoformat()

                return (best_match.outcome, best_match.confidence)

            return None

    def add_pattern(
        self, screenshot: np.ndarray, outcome: Outcome, confidence: float
    ) -> None:
        """
        Add new pattern to cache.

        Args:
            screenshot: Screenshot to cache
            outcome: Detected outcome
            confidence: Confidence score (0.0-1.0)
        """
        with self._lock:
            img_hash = self._compute_hash(screenshot)
            hash_str = str(img_hash)

            # Add or update pattern
            if hash_str in self.patterns:
                # Update existing pattern
                pattern = self.patterns[hash_str]
                pattern.outcome = outcome
                pattern.confidence = confidence
            else:
                # Add new pattern
                from datetime import datetime

                self.patterns[hash_str] = CachedPattern(
                    hash=hash_str,
                    outcome=outcome,
                    confidence=confidence,
                    hit_count=0,
                    last_used=datetime.now().isoformat(),
                )

    def persist(self) -> None:
        """Save cache to disk (JSON format)."""
        with self._lock:
            try:
                # Convert patterns to JSON-serializable format
                cache_data = {
                    "patterns": [
                        {
                            "hash": pattern.hash,
                            "outcome": str(pattern.outcome),
                            "confidence": pattern.confidence,
                            "hit_count": pattern.hit_count,
                            "last_used": pattern.last_used,
                        }
                        for pattern in self.patterns.values()
                    ]
                }

                with open(self.cache_file, "w") as f:
                    json.dump(cache_data, f, indent=2)

            except Exception as e:
                raise CacheError(f"Failed to persist pattern cache: {e}")

    def load(self) -> None:
        """Load cache from disk."""
        with self._lock:
            if not self.cache_file.exists():
                # No cache file yet
                return

            try:
                with open(self.cache_file, "r") as f:
                    cache_data = json.load(f)

                # Load patterns
                self.patterns = {}
                for pattern_data in cache_data.get("patterns", []):
                    pattern = CachedPattern(
                        hash=pattern_data["hash"],
                        outcome=Outcome(pattern_data["outcome"]),
                        confidence=pattern_data["confidence"],
                        hit_count=pattern_data.get("hit_count", 0),
                        last_used=pattern_data.get("last_used"),
                    )
                    self.patterns[pattern.hash] = pattern

            except Exception as e:
                raise CacheError(f"Failed to load pattern cache: {e}")

    def get_stats(self) -> Dict[str, int | float]:
        """
        Get cache statistics.

        Returns:
            Dictionary with total_patterns, total_hits, hit_rate
        """
        with self._lock:
            total_patterns = len(self.patterns)
            total_hits = sum(p.hit_count for p in self.patterns.values())

            # Calculate hit rate (hits / (patterns + hits))
            # This approximates cache_hits / total_lookups
            total_lookups = total_patterns + total_hits
            hit_rate = total_hits / total_lookups if total_lookups > 0 else 0.0

            return {
                "total_patterns": total_patterns,
                "total_hits": total_hits,
                "hit_rate": hit_rate,
            }

    def update_confidence(self, screenshot: np.ndarray, new_confidence: float) -> None:
        """
        Update confidence for existing pattern.

        Args:
            screenshot: Screenshot to find
            new_confidence: New confidence value
        """
        with self._lock:
            img_hash = self._compute_hash(screenshot)
            hash_str = str(img_hash)

            if hash_str in self.patterns:
                self.patterns[hash_str].confidence = new_confidence

    def clear(self) -> None:
        """Clear all cached patterns (useful for testing or reset)."""
        with self._lock:
            self.patterns = {}

            # Delete cache file
            if self.cache_file.exists():
                self.cache_file.unlink()

    def _compute_hash(self, screenshot: np.ndarray) -> imagehash.ImageHash:
        """
        Compute perceptual hash for screenshot.

        Args:
            screenshot: RGB numpy array

        Returns:
            ImageHash object
        """
        # Convert numpy array to PIL Image
        img = Image.fromarray(screenshot.astype("uint8"), "RGB")

        # Compute perceptual hash (default: phash with 8x8 DCT)
        return imagehash.phash(img)
