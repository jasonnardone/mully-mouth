"""System tray application for Mully Mouth Golf Caddy."""
import ctypes
import os
import platform
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional

import pystray
from PIL import Image, ImageDraw, ImageFont
from pystray import MenuItem as Item

from src.cli.monitor import Monitor
from src.lib.config import Config, load_config
from src.lib.exceptions import ServiceError
from src.lib.single_instance import SingleInstance, SingleInstanceError


class TrayApplication:
    """
    System tray application for Mully Mouth Golf Caddy.

    Provides a user-friendly Windows system tray interface for controlling
    the golf commentary system without command line interaction.
    """

    def __init__(self, config: Config):
        """
        Initialize tray application.

        Args:
            config: Application configuration
        """
        self.config = config
        self.monitor: Optional[Monitor] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.icon: Optional[pystray.Icon] = None # type: ignore
        self.should_exit = False
        self.single_instance: Optional[SingleInstance] = None

    def run(self) -> None:
        """Run the system tray application."""
        # Create tray icon
        self.icon = pystray.Icon(
            "mully_mouth",
            icon=self._create_icon(active=False),
            title="Mully Mouth Golf Caddy",
            menu=self._create_menu(),
        )

        # Start in stopped mode - user must manually start monitoring
        # This prevents accidental monitoring when app launches

        # Run the icon (blocks until exit)
        self.icon.run()

    def start_monitoring(self) -> None:
        """Start monitoring in background thread."""
        if self.monitor and self.monitor.is_running:
            return

        try:
            # Create new monitor instance
            self.monitor = Monitor(self.config)

            # Start in background thread
            self.monitor_thread = threading.Thread(
                target=self._run_monitor,
                daemon=True
            )
            self.monitor_thread.start()

            # Update icon to active state
            if self.icon:
                self.icon.icon = self._create_icon(active=True)
                self.icon.menu = self._create_menu()

        except Exception as e:
            self._show_error(f"Failed to start monitoring: {e}")

    def stop_monitoring(self) -> None:
        """Stop monitoring and cleanup."""
        if not self.monitor or not self.monitor.is_running:
            return

        try:
            # Update icon immediately to show we're stopping
            if self.icon:
                self.icon.icon = self._create_icon(active=False)
                self.icon.menu = self._create_menu()

            # Stop the monitor
            self.monitor.stop(print_summary=False)

            # Wait for thread to finish (with longer timeout for in-progress shots)
            if self.monitor_thread and self.monitor_thread.is_alive():
                # Give it 10 seconds to finish any in-progress shot processing
                self.monitor_thread.join(timeout=10.0)

                # If still running, force flag to false
                if self.monitor_thread.is_alive():
                    self.monitor.is_running = False
                    # Wait a bit more
                    self.monitor_thread.join(timeout=2.0)

        except Exception as e:
            self._show_error(f"Error stopping monitor: {e}")
            # Ensure icon is stopped even on error
            if self.icon:
                self.icon.icon = self._create_icon(active=False)
                self.icon.menu = self._create_menu()

    def toggle_monitoring(self, icon=None, item=None) -> None:
        """Toggle monitoring on/off."""
        if self.monitor and self.monitor.is_running:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def change_personality(self, personality_name: str) -> None:
        """
        Change commentary personality.

        Args:
            personality_name: Name of personality to switch to
        """
        was_running = self.monitor and self.monitor.is_running

        try:
            # Stop monitoring if running
            if was_running:
                self.stop_monitoring()

            # Update config
            self.config.personality = personality_name

            # Save config
            self._save_config()

            # Restart if was running
            if was_running:
                self.start_monitoring()

            # Update menu
            if self.icon:
                self.icon.menu = self._create_menu()

            print(f"Personality changed to: {personality_name}")

        except Exception as e:
            self._show_error(f"Failed to change personality: {e}")
            # Ensure icon is updated even on error
            if self.icon:
                self.icon.icon = self._create_icon(active=False)
                self.icon.menu = self._create_menu()

    def set_commentary_frequency(self, frequency: float) -> None:
        """
        Set commentary frequency.

        Args:
            frequency: Frequency value (0.0-1.0)
        """
        was_running = self.monitor and self.monitor.is_running

        # Update config first
        self.config.commentary_frequency = frequency

        # If monitor is running, update its config too
        if self.monitor:
            self.monitor.config.commentary_frequency = frequency

        # Save config to file
        self._save_config()

        # Show confirmation
        print(f"Commentary frequency set to {frequency*100:.0f}%")

        # Update menu to show new checkmark
        if self.icon:
            self.icon.menu = self._create_menu()

    def set_name_frequency(self, frequency: float) -> None:
        """
        Set name frequency.

        Args:
            frequency: Frequency value (0.0-1.0)
        """
        was_running = self.monitor and self.monitor.is_running

        # Update config first
        self.config.name_frequency = frequency

        # If monitor is running, update its config too
        if self.monitor:
            self.monitor.config.name_frequency = frequency

        # Save config to file
        self._save_config()

        # Show confirmation
        print(f"Name frequency set to {frequency*100:.0f}%")

        # Update menu to show new checkmark
        if self.icon:
            self.icon.menu = self._create_menu()

    def set_monitor(self, monitor_index: int) -> None:
        """
        Set which monitor to capture.

        Args:
            monitor_index: Monitor index (0 = primary, 1 = second, etc.)
        """
        was_running = self.monitor and self.monitor.is_running

        # Stop monitoring if running
        if was_running:
            self.stop_monitoring()

        # Update config
        self.config.monitoring.monitor_index = monitor_index

        # Save config to file
        self._save_config()

        # Show confirmation
        print(f"Monitor set to Monitor {monitor_index + 1}")

        # Restart if was running
        if was_running:
            self.start_monitoring()

        # Update menu to show new checkmark
        if self.icon:
            self.icon.menu = self._create_menu()

    def show_stats(self, icon=None, item=None) -> None:
        """Show session statistics in message box."""
        if not self.monitor:
            self._show_message_async("No active session", "Stats")
            return

        status = self.monitor.get_status()

        if not status["session_active"]:
            self._show_message_async("No active session", "Stats")
            return

        message = (
            f"Session Statistics\n\n"
            f"Total Shots: {status['total_shots']}\n"
            f"Total Cost: ${status['total_cost']:.4f}\n"
            f"Cache Hit Rate: {status['cache_hit_rate']*100:.1f}%\n"
            f"Accuracy: {status['accuracy_rate']*100:.1f}%\n"
            f"API Calls: {status['total_api_calls']}\n\n"
            f"Personality: {status['personality']}\n"
            f"Commentary Frequency: {status['commentary_frequency']*100:.0f}%\n"
            f"Name Frequency: {status['name_frequency']*100:.0f}%"
        )

        self._show_message_async(message, "Mully Mouth Stats")

    def open_config(self, icon=None, item=None) -> None:
        """Open config file in default editor."""
        config_path = Path("config/config.yaml")

        if not config_path.exists():
            self._show_error("Config file not found")
            return

        try:
            if platform.system() == 'Windows':
                os.startfile(str(config_path))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(config_path)])
            else:  # Linux
                subprocess.run(['xdg-open', str(config_path)])
        except Exception as e:
            self._show_error(f"Failed to open config: {e}")

    def exit_app(self, icon=None, item=None) -> None:
        """Exit the application."""
        # Stop monitoring
        if self.monitor and self.monitor.is_running:
            self.monitor.stop(print_summary=True)

            # Wait for thread to finish
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5.0)

        # Release single instance lock
        if self.single_instance:
            self.single_instance.release()

        # Stop the icon
        if self.icon:
            self.icon.stop()

        self.should_exit = True

    def _run_monitor(self) -> None:
        """Run monitor in background thread."""
        try:
            self.monitor.start_non_blocking()
        except ServiceError as e:
            # Monitor stopped due to error
            if self.icon:
                self.icon.icon = self._create_icon(active=False)
                self.icon.menu = self._create_menu()
        except Exception as e:
            # Unexpected error
            if self.icon:
                self.icon.icon = self._create_icon(active=False)
                self.icon.menu = self._create_menu()

    def _create_menu(self) -> pystray.Menu:
        """
        Create dynamic menu based on current state.

        Returns:
            pystray.Menu instance
        """
        is_running = self.monitor and self.monitor.is_running

        return pystray.Menu(
            # Start/Stop
            Item(
                'Stop Monitoring' if is_running else 'Start Monitoring',
                self.toggle_monitoring
            ),
            pystray.Menu.SEPARATOR,

            # Change Personality
            Item(
                'Change Personality',
                pystray.Menu(
                    *[
                        Item(
                            p.title(),
                            lambda _, p=p: self.change_personality(p),
                            checked=lambda item, p=p: str(self.config.personality).lower() == p.lower()
                        )
                        for p in self._get_personalities()
                    ]
                )
            ),

            # Select Monitor
            Item(
                'Select Monitor',
                pystray.Menu(
                    *[
                        Item(
                            f"Monitor {m['index'] + 1} ({m['width']}x{m['height']})",
                            lambda _, idx=m['index']: self.set_monitor(idx),
                            checked=lambda item, idx=m['index']: self.config.monitoring.monitor_index == idx
                        )
                        for m in self._get_available_monitors()
                    ]
                )
            ),

            # Adjust Settings
            Item(
                'Adjust Settings',
                pystray.Menu(
                    # Commentary Frequency
                    Item(
                        'Commentary Frequency',
                        pystray.Menu(
                            Item(
                                '50%',
                                lambda _: self.set_commentary_frequency(0.5),
                                checked=lambda item: abs(self.config.commentary_frequency - 0.5) < 0.01
                            ),
                            Item(
                                '40%',
                                lambda _: self.set_commentary_frequency(0.4),
                                checked=lambda item: abs(self.config.commentary_frequency - 0.4) < 0.01
                            ),
                            Item(
                                '30%',
                                lambda _: self.set_commentary_frequency(0.3),
                                checked=lambda item: abs(self.config.commentary_frequency - 0.3) < 0.01
                            ),
                            Item(
                                '20%',
                                lambda _: self.set_commentary_frequency(0.2),
                                checked=lambda item: abs(self.config.commentary_frequency - 0.2) < 0.01
                            ),
                            Item(
                                '10%',
                                lambda _: self.set_commentary_frequency(0.1),
                                checked=lambda item: abs(self.config.commentary_frequency - 0.1) < 0.01
                            ),
                            Item(
                                '0%',
                                lambda _: self.set_commentary_frequency(0.0),
                                checked=lambda item: abs(self.config.commentary_frequency - 0.0) < 0.01
                            ),
                        )
                    ),
                    # Name Frequency
                    Item(
                        'Name Frequency',
                        pystray.Menu(
                            Item(
                                '100%',
                                lambda _: self.set_name_frequency(1.0),
                                checked=lambda item: abs(self.config.name_frequency - 1.0) < 0.01
                            ),
                            Item(
                                '90%',
                                lambda _: self.set_name_frequency(0.9),
                                checked=lambda item: abs(self.config.name_frequency - 0.9) < 0.01
                            ),
                            Item(
                                '80%',
                                lambda _: self.set_name_frequency(0.8),
                                checked=lambda item: abs(self.config.name_frequency - 0.8) < 0.01
                            ),
                            Item(
                                '70%',
                                lambda _: self.set_name_frequency(0.7),
                                checked=lambda item: abs(self.config.name_frequency - 0.7) < 0.01
                            ),
                            Item(
                                '60%',
                                lambda _: self.set_name_frequency(0.6),
                                checked=lambda item: abs(self.config.name_frequency - 0.6) < 0.01
                            ),
                            Item(
                                '50%',
                                lambda _: self.set_name_frequency(0.5),
                                checked=lambda item: abs(self.config.name_frequency - 0.5) < 0.01
                            ),
                            Item(
                                '40%',
                                lambda _: self.set_name_frequency(0.4),
                                checked=lambda item: abs(self.config.name_frequency - 0.4) < 0.01
                            ),
                            Item(
                                '30%',
                                lambda _: self.set_name_frequency(0.3),
                                checked=lambda item: abs(self.config.name_frequency - 0.3) < 0.01
                            ),
                            Item(
                                '20%',
                                lambda _: self.set_name_frequency(0.2),
                                checked=lambda item: abs(self.config.name_frequency - 0.2) < 0.01
                            ),
                            Item(
                                '10%',
                                lambda _: self.set_name_frequency(0.1),
                                checked=lambda item: abs(self.config.name_frequency - 0.1) < 0.01
                            ),
                            Item(
                                '0%',
                                lambda _: self.set_name_frequency(0.0),
                                checked=lambda item: abs(self.config.name_frequency - 0.0) < 0.01
                            ),
                        )
                    ),
                )
            ),

            pystray.Menu.SEPARATOR,

            # Session Stats
            Item('Session Stats', self.show_stats),

            # Open Config
            Item('Open Config File', self.open_config),

            pystray.Menu.SEPARATOR,

            # Exit
            Item('Exit', self.exit_app)
        )

    def _create_icon(self, active: bool = False) -> Image.Image:
        """
        Create system tray icon.

        Args:
            active: Whether monitoring is active

        Returns:
            PIL Image for icon
        """
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Choose color based on state
        color = (34, 139, 34) if active else (128, 128, 128)  # Green or Gray

        # Draw circle
        draw.ellipse([4, 4, size-4, size-4], fill=color, outline='white', width=3)

        # Draw "M" letter
        try:
            # Try to load a system font
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            # Fallback to default font
            font = ImageFont.load_default()

        # Draw text
        text = "M"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size - text_width) // 2
        text_y = (size - text_height) // 2 - 2

        draw.text((text_x, text_y), text, fill='white', font=font)

        return image

    def _get_personalities(self) -> list[str]:
        """
        Get list of available personalities.

        Returns:
            List of personality names
        """
        personalities_dir = Path("data/personalities")
        if not personalities_dir.exists():
            return ["neutral"]

        personalities = []
        for yaml_file in personalities_dir.glob("*.yaml"):
            personalities.append(yaml_file.stem)

        return sorted(personalities) if personalities else ["neutral"]

    def _get_available_monitors(self) -> list[dict]:
        """
        Get list of available monitors.

        Returns:
            List of monitor info dicts
        """
        from src.services.screen_capture import ScreenCaptureService
        temp_capture = ScreenCaptureService()
        return temp_capture.get_available_monitors()

    def _save_config(self) -> None:
        """Save current config to file."""
        import yaml

        config_file = Path("config/config.yaml")

        try:
            # Load current config file
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)

            # Update with current values (ensure strings, not objects)
            config_data['personality'] = str(self.config.personality)
            config_data['commentary_frequency'] = float(self.config.commentary_frequency)
            config_data['name_frequency'] = float(self.config.name_frequency)

            # Update monitoring config
            if 'monitoring' not in config_data:
                config_data['monitoring'] = {}
            config_data['monitoring']['monitor_index'] = int(self.config.monitoring.monitor_index)

            # Save back using safe_dump to prevent object serialization
            with open(config_file, 'w') as f:
                yaml.safe_dump(config_data, f, default_flow_style=False, sort_keys=False)

        except Exception as e:
            self._show_error(f"Failed to save config: {e}")

    def _show_message(self, message: str, title: str = "Mully Mouth") -> None:
        """
        Show Windows message box (synchronous - blocks until closed).

        Args:
            message: Message text
            title: Window title
        """
        try:
            # MB_OK | MB_ICONINFORMATION = 0x00000000 | 0x00000040
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x00000040)
        except Exception:
            # Fallback to console if message box fails
            print(f"{title}: {message}")

    def _show_message_async(self, message: str, title: str = "Mully Mouth") -> None:
        """
        Show Windows message box in background thread (non-blocking).

        Args:
            message: Message text
            title: Window title
        """
        def show():
            try:
                # MB_OK | MB_ICONINFORMATION
                ctypes.windll.user32.MessageBoxW(0, message, title, 0x00000040)
            except Exception:
                print(f"{title}: {message}")

        thread = threading.Thread(target=show, daemon=True)
        thread.start()

    def _show_error(self, message: str) -> None:
        """
        Show error message box.

        Args:
            message: Error message
        """
        try:
            # MB_OK | MB_ICONERROR = 0x00000000 | 0x00000010
            ctypes.windll.user32.MessageBoxW(0, message, "Error", 0x00000010)
        except Exception:
            # Fallback to console if message box fails
            print(f"Error: {message}")


def main():
    """Main entry point for system tray application."""
    single_instance = None

    try:
        # Check for single instance FIRST before loading anything else
        try:
            single_instance = SingleInstance("mully_mouth")
        except SingleInstanceError as e:
            # Another instance is already running
            error_msg = str(e)
            try:
                import ctypes
                # MB_OK | MB_ICONWARNING
                ctypes.windll.user32.MessageBoxW(0, error_msg, "Mully Mouth Already Running", 0x00000030)
            except:
                print(error_msg)
            sys.exit(0)

        # Load configuration
        config = load_config()

        # Create and run tray application
        app = TrayApplication(config)
        app.single_instance = single_instance  # Store reference for cleanup
        app.run()

    except SingleInstanceError as e:
        # Already handled above, but just in case
        error_msg = str(e)
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, error_msg, "Mully Mouth Already Running", 0x00000030)
        except:
            print(error_msg)
        sys.exit(0)

    except Exception as e:
        # Show error in message box for GUI users
        error_msg = str(e)

        # Check if it's an API key error
        if "api_key" in error_msg.lower():
            error_msg = (
                "API keys not configured!\n\n"
                "Please set environment variables:\n"
                "- ANTHROPIC_API_KEY\n"
                "- ELEVENLABS_API_KEY\n\n"
                "Or edit config/config.yaml\n\n"
                f"Error: {e}"
            )

        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, error_msg, "Mully Mouth Error", 0x10)
        except:
            print(f"Fatal error: {error_msg}")

        sys.exit(1)

    finally:
        # Always release single instance lock on exit
        if single_instance:
            single_instance.release()


if __name__ == "__main__":
    main()
