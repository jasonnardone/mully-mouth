"""Secure credentials management using Windows Credential Manager."""
import platform
from typing import Optional

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
    XAI_KEY = "xai_api_key"

    def __init__(self):
        if not KEYRING_AVAILABLE:
            print("Warning: keyring library not available. Install with: pip install keyring")

    def store_anthropic_key(self, api_key: str) -> bool:
        if not KEYRING_AVAILABLE:
            return False
        try:
            keyring.set_password(self.SERVICE_NAME, self.ANTHROPIC_KEY, api_key)
            return True
        except Exception as e:
            print(f"Failed to store Anthropic key: {e}")
            return False

    def store_xai_key(self, api_key: str) -> bool:
        if not KEYRING_AVAILABLE:
            return False
        try:
            keyring.set_password(self.SERVICE_NAME, self.XAI_KEY, api_key)
            return True
        except Exception as e:
            print(f"Failed to store xAI key: {e}")
            return False

    def get_anthropic_key(self) -> Optional[str]:
        if not KEYRING_AVAILABLE:
            return None
        try:
            return keyring.get_password(self.SERVICE_NAME, self.ANTHROPIC_KEY)
        except Exception as e:
            print(f"Failed to retrieve Anthropic key: {e}")
            return None

    def get_xai_key(self) -> Optional[str]:
        if not KEYRING_AVAILABLE:
            return None
        try:
            return keyring.get_password(self.SERVICE_NAME, self.XAI_KEY)
        except Exception as e:
            print(f"Failed to retrieve xAI key: {e}")
            return None

    def clear_anthropic_key(self) -> bool:
        if not KEYRING_AVAILABLE:
            return False
        try:
            keyring.delete_password(self.SERVICE_NAME, self.ANTHROPIC_KEY)
            return True
        except Exception:
            return False

    def clear_xai_key(self) -> bool:
        if not KEYRING_AVAILABLE:
            return False
        try:
            keyring.delete_password(self.SERVICE_NAME, self.XAI_KEY)
            return True
        except Exception:
            return False

    def has_credentials(self) -> bool:
        return (
            self.get_anthropic_key() is not None and
            self.get_xai_key() is not None
        )

    def clear_all(self) -> None:
        self.clear_anthropic_key()
        self.clear_xai_key()
