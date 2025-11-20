"""Screen capture service for GS Pro window detection and monitoring."""
import threading
import time
from typing import Optional

import mss
import numpy as np
import pygetwindow as gw

from src.lib.exceptions import CaptureError, WindowNotFoundError


class ScreenCaptureService:
    """
    Screen capture and window detection service.

    Uses MSS for fast screen capture and pygetwindow for window detection.
    """

    def __init__(self):
        """Initialize screen capture service."""
        self.sct = None  # Will be created in the thread that uses it
        self.window_id: Optional[str] = None
        self.window_rect: Optional[dict] = None
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.latest_frame: Optional[np.ndarray] = None
        self.fps = 2
        self._lock = threading.Lock()

    def find_gs_pro_window(self) -> Optional[str]:
        """
        Use primary monitor for capture (fullscreen mode).

        Returns:
            Monitor description
        """
        try:
            # Create MSS instance if not already created
            if self.sct is None:
                self.sct = mss.mss()

            # Use primary monitor (monitor 1)
            monitor = self.sct.monitors[1]  # 0 is all monitors, 1 is primary
            self.window_rect = {
                "left": monitor["left"],
                "top": monitor["top"],
                "width": monitor["width"],
                "height": monitor["height"],
            }
            self.window_id = "Primary Monitor"
            return f"Primary Monitor ({monitor['width']}x{monitor['height']})"
        except Exception as e:
            raise WindowNotFoundError(f"Failed to access primary monitor: {e}")

    def capture_window(self, window_id: Optional[str] = None) -> np.ndarray:
        """
        Capture screenshot of specified window.

        Args:
            window_id: Window title (uses stored window if None)

        Returns:
            Screenshot as NumPy array (RGB format)

        Raises:
            WindowNotFoundError: If window no longer exists
            CaptureError: If screenshot fails
        """
        if window_id:
            self.window_id = window_id
            # Update window rect
            windows = gw.getWindowsWithTitle(window_id)
            if not windows:
                raise WindowNotFoundError(f"Window not found: {window_id}")
            window = windows[0]
            self.window_rect = {
                "left": window.left,
                "top": window.top,
                "width": window.width,
                "height": window.height,
            }

        if not self.window_rect:
            raise WindowNotFoundError("No window selected. Call find_gs_pro_window() first.")

        try:
            # Capture using MSS
            screenshot = self.sct.grab(self.window_rect)
            # Convert to RGB numpy array
            img = np.array(screenshot)
            # MSS returns BGRA, convert to RGB
            img_rgb = img[:, :, :3][:, :, ::-1]  # Drop alpha and BGR->RGB
            return img_rgb
        except Exception as e:
            raise CaptureError(f"Failed to capture screenshot: {e}")

    def start_monitoring(self, window_id: Optional[str] = None, fps: int = 2) -> None:
        """
        Begin continuous screen capture at specified FPS.

        Args:
            window_id: Window to monitor (uses stored window if None)
            fps: Frames per second (default: 2)

        Raises:
            WindowNotFoundError: If window doesn't exist
        """
        if window_id:
            self.window_id = window_id

        if not self.window_id:
            raise WindowNotFoundError(
                "No window selected. Call find_gs_pro_window() first or provide window_id."
            )

        self.fps = fps
        self.monitoring = True

        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop continuous capture and release resources."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        self.latest_frame = None

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """
        Get most recent captured frame.

        Returns:
            Latest screenshot or None if no frames captured
        """
        with self._lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def _monitor_loop(self) -> None:
        """
        Background thread loop for continuous capture.

        Captures frames at specified FPS and stores in latest_frame.
        """
        # Create MSS instance in this thread
        thread_sct = mss.mss()
        interval = 1.0 / self.fps

        try:
            while self.monitoring:
                try:
                    # Capture using thread-local MSS instance
                    if not self.window_rect:
                        print("No window rect set")
                        time.sleep(interval)
                        continue

                    screenshot = thread_sct.grab(self.window_rect)
                    # Convert to RGB numpy array
                    img = np.array(screenshot)
                    # MSS returns BGRA, convert to RGB
                    img_rgb = img[:, :, :3][:, :, ::-1]  # Drop alpha and BGR->RGB

                    with self._lock:
                        self.latest_frame = img_rgb
                except Exception as e:
                    # Log error but continue monitoring
                    print(f"Capture error in monitoring loop: {e}")

                time.sleep(interval)
        finally:
            # Clean up thread-local MSS instance
            thread_sct.close()

    def __del__(self):
        """Cleanup on deletion."""
        self.stop_monitoring()
        if hasattr(self, "sct"):
            self.sct.close()
