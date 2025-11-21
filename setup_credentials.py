#!/usr/bin/env python
"""
Simple credential setup tool for Mully Mouth Golf Caddy.

Stores API keys securely in Windows Credential Manager.
"""
import sys
import getpass
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.lib.credentials import CredentialsManager


def main():
    """Main credential setup function."""
    print("=" * 60)
    print("Mully Mouth Golf Caddy - Secure Credential Setup")
    print("=" * 60)
    print()
    print("This tool will securely store your API keys in Windows")
    print("Credential Manager. Your keys will be encrypted and never")
    print("stored in plain text files or committed to Git.")
    print()

    creds = CredentialsManager()

    # Check if credentials already exist
    if creds.has_credentials():
        print("Existing credentials found!")
        print()
        response = input("Do you want to update your credentials? (y/n): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return

    print()
    print("Please enter your API keys:")
    print()

    # Get Anthropic API key
    print("1. Anthropic (Claude) API Key")
    print("   Get yours at: https://console.anthropic.com/")
    anthropic_key = getpass.getpass("   Enter key (hidden): ").strip()

    if not anthropic_key:
        print("\nError: Anthropic API key is required")
        sys.exit(1)

    # Get ElevenLabs API key
    print()
    print("2. ElevenLabs API Key")
    print("   Get yours at: https://elevenlabs.io/")
    elevenlabs_key = getpass.getpass("   Enter key (hidden): ").strip()

    if not elevenlabs_key:
        print("\nError: ElevenLabs API key is required")
        sys.exit(1)

    # Store credentials
    print()
    print("Storing credentials securely...")

    success_anthropic = creds.store_anthropic_key(anthropic_key)
    success_elevenlabs = creds.store_elevenlabs_key(elevenlabs_key)

    if success_anthropic and success_elevenlabs:
        print()
        print("✓ Credentials stored successfully!")
        print()
        print("Your API keys are now securely stored in Windows Credential Manager.")
        print("You can now run Mully Mouth without setting environment variables")
        print("or editing config files.")
        print()
        print("To start the application:")
        print("  • Double-click: run_tray.bat")
        print("  • Or run: python -m src.cli.tray_app")
        print()
    else:
        print()
        print("✗ Failed to store credentials")
        print()
        print("Please make sure:")
        print("  1. You have 'keyring' installed: pip install keyring")
        print("  2. You're running on Windows")
        print("  3. You have permission to access Windows Credential Manager")
        print()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
