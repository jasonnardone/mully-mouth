"""
Utility script to help capture idle/non-gameplay screens for training.

This makes it easy to add screenshots to the idle training directory
when you encounter setup screens, round complete screens, etc.
"""
import datetime
from pathlib import Path

import mss
from PIL import Image


def capture_idle_screen(description: str = "idle"):
    """
    Capture current screen and save to idle training directory.

    Args:
        description: Description of the screen type (e.g., "round_complete", "setup")
    """
    # Create screenshots directory
    idle_dir = Path("data/training/images/idle")
    idle_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{description}_{timestamp}.png"
    filepath = idle_dir / filename

    # Capture screenshot
    with mss.mss() as sct:
        # Capture primary monitor (monitor 1)
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)

        # Convert to PIL Image and save
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save(filepath)

    print(f"Screenshot saved: {filepath}")
    print(f"Total idle screens: {len(list(idle_dir.glob('*.png')))}")


if __name__ == "__main__":
    import sys

    # Get description from command line argument or use default
    description = sys.argv[1] if len(sys.argv) > 1 else "idle"

    print(f"Capturing idle screen: {description}")
    print("Press Enter to capture...")
    input()

    capture_idle_screen(description)

    print("\nDone! You can capture more screens by running this script again.")
    print("\nUsage examples:")
    print("  python capture_idle_screen.py round_complete")
    print("  python capture_idle_screen.py player_setup")
    print("  python capture_idle_screen.py main_menu")
