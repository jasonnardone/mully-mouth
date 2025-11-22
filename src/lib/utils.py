"""Utility functions for Mully Mouth application."""
import uuid


def generate_uuid() -> str:
    """
    Generate a unique identifier.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())
