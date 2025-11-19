"""Motion detection service for shot event identification."""
import time
from typing import Callable, Optional

import cv2
import numpy as np


class MotionDetectorService:
    """
    Motion detection service using OpenCV frame differencing.

    Detects when the golf ball has stopped moving (shot complete).
    """

    def __init__(self, threshold: float = 0.02, ball_stop_duration: float = 1.0):
        """
        Initialize motion detector.

        Args:
            threshold: Pixel change ratio (0.0-1.0) to consider motion
            ball_stop_duration: Seconds of stillness before shot complete
        """
        self.threshold = threshold
        self.ball_stop_duration = ball_stop_duration
        self.previous_frame: Optional[np.ndarray] = None
        self.last_motion_time: Optional[float] = None
        self.motion_detected = False
        self.shot_callback: Optional[Callable[[np.ndarray], None]] = None
        self.last_shot_frame: Optional[np.ndarray] = None

    def analyze_frame(self, frame: np.ndarray) -> bool:
        """
        Analyze frame for motion.

        Args:
            frame: Current frame (RGB)

        Returns:
            True if motion detected, False otherwise
        """
        if self.previous_frame is None:
            self.previous_frame = frame.copy()
            return False

        # Convert to grayscale
        gray1 = cv2.cvtColor(self.previous_frame, cv2.COLOR_RGB2GRAY)
        gray2 = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Compute absolute difference
        diff = cv2.absdiff(gray1, gray2)

        # Apply Gaussian blur to reduce noise
        blur = cv2.GaussianBlur(diff, (5, 5), 0)

        # Threshold
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)

        # Count motion pixels
        motion_pixels = cv2.countNonZero(thresh)
        total_pixels = frame.shape[0] * frame.shape[1]
        motion_ratio = motion_pixels / total_pixels

        # Update previous frame
        self.previous_frame = frame.copy()

        # Detect motion
        if motion_ratio > self.threshold:
            self.motion_detected = True
            self.last_motion_time = time.time()
            return True
        else:
            return False

    def is_ball_stopped(self) -> bool:
        """
        Check if ball has stopped moving (shot complete).

        Returns:
            True if no motion for configured duration (1 second default)
        """
        if not self.motion_detected or self.last_motion_time is None:
            return False

        time_since_motion = time.time() - self.last_motion_time

        # Ball stopped if no motion for ball_stop_duration
        if time_since_motion >= self.ball_stop_duration:
            return True

        return False

    def reset(self) -> None:
        """Reset motion detector state (e.g., between rounds)."""
        self.previous_frame = None
        self.last_motion_time = None
        self.motion_detected = False
        self.last_shot_frame = None

    def set_threshold(self, threshold: float) -> None:
        """
        Adjust motion sensitivity.

        Args:
            threshold: Pixel change ratio (0.0-1.0, default 0.02)
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")
        self.threshold = threshold

    def on_shot_detected(self, callback: Callable[[np.ndarray], None]) -> None:
        """
        Register callback for shot completion events.

        Args:
            callback: Function to call with final frame when shot complete
        """
        self.shot_callback = callback

    def check_and_fire_shot_event(self, current_frame: np.ndarray) -> bool:
        """
        Check if shot is complete and fire callback if registered.

        Args:
            current_frame: Current frame

        Returns:
            True if shot was detected and callback fired
        """
        if self.is_ball_stopped():
            if self.shot_callback:
                self.shot_callback(current_frame)

            # Reset for next shot
            self.motion_detected = False
            self.last_motion_time = None
            self.last_shot_frame = current_frame.copy()

            return True

        return False
