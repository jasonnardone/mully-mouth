"""Secure credentials management using Windows Credential Manager."""
import json
import platform
import sys
from typing import Optional

# Platform-specific credential storage
if platform.system() == "Windows":
    try:
        import keyring
        KEYRING_AVAILABLE = True
    except ImportError:
        KEYRING_AVAILABLE = False
else:
    KEYRING_AVAILABLE = False


class CredentialsManager:
    """
    Secure credentials manager.

    Stores API keys securely using Windows Credential Manager (via keyring library).
    Keys are encrypted by Windows and never stored in plain text files.
    """

    SERVICE_NAME = "MullyMouthGolfCaddy"
    ANTHROPIC_KEY = "anthropic_api_key"
    ELEVENLABS_KEY = "elevenlabs_api_key"

    def __init__(self):
        """Initialize credentials manager."""
        if not KEYRING_AVAILABLE:
            print("Warning: keyring library not available. Install with: pip install keyring")

    def store_anthropic_key(self, api_key: str) -> bool:
        """
        Store Anthropic API key securely.

        Args:
            api_key: Anthropic API key

        Returns:
            True if stored successfully
        """
        if not KEYRING_AVAILABLE:
            return False

        try:
            keyring.set_password(self.SERVICE_NAME, self.ANTHROPIC_KEY, api_key)
            return True
        except Exception as e:
            print(f"Failed to store Anthropic key: {e}")
            return False

    def store_elevenlabs_key(self, api_key: str) -> bool:
        """
        Store ElevenLabs API key securely.

        Args:
            api_key: ElevenLabs API key

        Returns:
            True if stored successfully
        """
        if not KEYRING_AVAILABLE:
            return False

        try:
            keyring.set_password(self.SERVICE_NAME, self.ELEVENLABS_KEY, api_key)
            return True
        except Exception as e:
            print(f"Failed to store ElevenLabs key: {e}")
            return False

    def get_anthropic_key(self) -> Optional[str]:
        """
        Retrieve Anthropic API key.

        Returns:
            API key if found, None otherwise
        """
        if not KEYRING_AVAILABLE:
            return None

        try:
            return keyring.get_password(self.SERVICE_NAME, self.ANTHROPIC_KEY)
        except Exception as e:
            print(f"Failed to retrieve Anthropic key: {e}")
            return None

    def get_elevenlabs_key(self) -> Optional[str]:
        """
        Retrieve ElevenLabs API key.

        Returns:
            API key if found, None otherwise
        """
        if not KEYRING_AVAILABLE:
            return None

        try:
            return keyring.get_password(self.SERVICE_NAME, self.ELEVENLABS_KEY)
        except Exception as e:
            print(f"Failed to retrieve ElevenLabs key: {e}")
            return None

    def clear_anthropic_key(self) -> bool:
        """
        Clear stored Anthropic API key.

        Returns:
            True if cleared successfully
        """
        if not KEYRING_AVAILABLE:
            return False

        try:
            keyring.delete_password(self.SERVICE_NAME, self.ANTHROPIC_KEY)
            return True
        except Exception:
            return False

    def clear_elevenlabs_key(self) -> bool:
        """
        Clear stored ElevenLabs API key.

        Returns:
            True if cleared successfully
        """
        if not KEYRING_AVAILABLE:
            return False

        try:
            keyring.delete_password(self.SERVICE_NAME, self.ELEVENLABS_KEY)
            return True
        except Exception:
            return False

    def has_credentials(self) -> bool:
        """
        Check if credentials are stored.

        Returns:
            True if both API keys are stored
        """
        return (
            self.get_anthropic_key() is not None and
            self.get_elevenlabs_key() is not None
        )

    def clear_all(self) -> None:
        """Clear all stored credentials."""
        self.clear_anthropic_key()
        self.clear_elevenlabs_key()
