"""Pre-flight screen classifier using color histogram comparison against training images.

Runs entirely in OpenCV — zero API calls. Determines whether the current screen
looks like an active golf course before the motion detector arms, so menus,
desktop, and non-GSPro content are suppressed without burning API budget.
"""
from pathlib import Path
from typing import Optional

import cv2
import numpy as np


# Outcome folders that represent active gameplay
_GAMEPLAY_FOLDERS = {"fairway", "green", "bunker", "rough", "trees", "out_of_bounds", "water"}
_IDLE_FOLDERS = {"idle"}

# Histogram parameters
_H_BINS = 30
_S_BINS = 32
_HIST_SIZE = [_H_BINS, _S_BINS]
_H_RANGES = [0, 180]
_S_RANGES = [0, 256]
_RANGES = _H_RANGES + _S_RANGES
_CHANNELS = [0, 1]  # H and S from HSV — ignore V (lighting-insensitive)

# How much more similar to gameplay than idle before we call it gameplay.
# Calibrated against training data: all gameplay images have a gap >= 0.20,
# the hardest idle image has a gap of 0.09, so 0.15 splits them cleanly.
_GAMEPLAY_BIAS = 0.15


class ScreenClassifier:
    """
    Lightweight pre-flight classifier that keeps the monitor idle until
    a genuine golf-course screen is detected.

    Uses HSV hue/saturation histograms built from the training images
    in data/training/images/. Falls back to "assume gameplay" if no
    training data is found, so it never silently breaks a fresh install.
    """

    def __init__(self, training_dir: str = "data/training/images"):
        self._training_dir = Path(training_dir)
        self._gameplay_hist: Optional[np.ndarray] = None
        self._idle_hist: Optional[np.ndarray] = None
        self._has_training_data = False
        self._load_training_histograms()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_gameplay_screen(self, frame: np.ndarray) -> bool:
        """
        Return True if the frame resembles an active golf course.

        When no training data is loaded this always returns True (fail-open)
        so the rest of the pipeline is unaffected on a fresh install.

        Args:
            frame: RGB numpy array (any resolution)
        """
        if not self._has_training_data:
            return True

        hist = self._compute_hist(frame)

        gameplay_score = cv2.compareHist(hist, self._gameplay_hist, cv2.HISTCMP_CORREL)
        idle_score = cv2.compareHist(hist, self._idle_hist, cv2.HISTCMP_CORREL)

        return gameplay_score > idle_score + _GAMEPLAY_BIAS

    @property
    def has_training_data(self) -> bool:
        return self._has_training_data

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_training_histograms(self) -> None:
        """Build averaged histograms for gameplay and idle categories."""
        gameplay_hists = []
        idle_hists = []

        if not self._training_dir.exists():
            return

        for folder in self._training_dir.iterdir():
            if not folder.is_dir():
                continue

            name = folder.name.lower()
            if name not in _GAMEPLAY_FOLDERS and name not in _IDLE_FOLDERS:
                continue

            bucket = gameplay_hists if name in _GAMEPLAY_FOLDERS else idle_hists

            for img_path in folder.iterdir():
                if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                    continue
                hist = self._load_and_hash(img_path)
                if hist is not None:
                    bucket.append(hist)

        if not gameplay_hists or not idle_hists:
            return

        self._gameplay_hist = self._average_hists(gameplay_hists)
        self._idle_hist = self._average_hists(idle_hists)
        self._has_training_data = True

    def _load_and_hash(self, path: Path) -> Optional[np.ndarray]:
        """Load an image file and return its HS histogram, or None on error."""
        try:
            img_bgr = cv2.imread(str(path))
            if img_bgr is None:
                return None
            return self._compute_hist_bgr(img_bgr)
        except Exception:
            return None

    def _compute_hist(self, frame_rgb: np.ndarray) -> np.ndarray:
        """Compute HS histogram from an RGB frame."""
        # Downsample to 128x72 — more than enough for color distribution
        small = cv2.resize(frame_rgb, (128, 72), interpolation=cv2.INTER_AREA)
        bgr = cv2.cvtColor(small, cv2.COLOR_RGB2BGR)
        return self._compute_hist_bgr(bgr)

    def _compute_hist_bgr(self, img_bgr: np.ndarray) -> np.ndarray:
        """Compute normalized HS histogram from a BGR image."""
        small = cv2.resize(img_bgr, (128, 72), interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], _CHANNELS, None, _HIST_SIZE, _RANGES)
        cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        return hist

    @staticmethod
    def _average_hists(hists: list) -> np.ndarray:
        """Return the element-wise average of a list of histograms."""
        stacked = np.stack(hists, axis=0)
        avg = np.mean(stacked, axis=0)
        cv2.normalize(avg, avg, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        return avg
