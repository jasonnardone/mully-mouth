"""Main CLI entry point for Mully Mouth Golf Caddy."""
import argparse
import sys
from pathlib import Path

from src.cli.monitor import Monitor
from src.lib.config import load_config
from src.lib.exceptions import ServiceError


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(
            description="Mully Mouth Golf Caddy - AI-powered golf shot narration for GS Pro"
        )
        parser.add_argument(
            "-p",
            "--personality",
            type=str,
            help="Personality for commentary (e.g., neutral, sarcastic, encouraging)",
        )
        parser.add_argument(
            "--list-personalities",
            action="store_true",
            help="List available personalities and exit",
        )
        parser.add_argument(
            "--config",
            type=str,
            help="Path to config file (default: config/config.yaml)",
        )

        args = parser.parse_args()

        # Print banner
        print_banner()

        # Load configuration
        print("Loading configuration...")
        config = load_config(config_path=args.config)

        # Override personality if provided
        if args.personality:
            config.personality = args.personality

        # List personalities if requested
        if args.list_personalities:
            from src.services.commentary_generator import CommentaryGeneratorService

            # Create temporary service to list personalities
            temp_service = CommentaryGeneratorService(
                api_key="dummy",  # Not used for listing
                personality_name="neutral",
            )
            personalities = temp_service.list_available_personalities()

            print("\nAvailable personalities:")
            for p in personalities:
                print(f"  - {p}")

            return 0

        # Validate required API keys
        if not config.anthropic.api_key:
            print("\nError: ANTHROPIC_API_KEY not configured.")
            print("Please set the environment variable or add it to config/config.yaml")
            return 1

        if not config.elevenlabs.api_key:
            print("\nError: ELEVENLABS_API_KEY not configured.")
            print("Please set the environment variable or add it to config/config.yaml")
            return 1

        # Create and start monitor
        monitor = Monitor(config)
        monitor.start()

        return 0

    except ServiceError as e:
        print(f"\nService error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\nShutdown requested.")
        return 0
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def print_banner() -> None:
    """Print application banner."""
    banner = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║           MULLY MOUTH GOLF CADDY v3.0.0              ║
║                                                       ║
║         AI-Powered Golf Shot Narration for           ║
║                    GS Pro                             ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    """
    print(banner)


if __name__ == "__main__":
    sys.exit(main())
