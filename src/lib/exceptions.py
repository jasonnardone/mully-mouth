"""Custom exceptions for Mully Mouth application."""


class ServiceError(Exception):
    """Base exception for all service errors."""

    pass


class AIServiceError(ServiceError):
    """Exception raised by AI analysis service."""

    pass


class VoiceServiceError(ServiceError):
    """Exception raised by voice service."""

    pass


class CaptureError(ServiceError):
    """Exception raised during screen capture."""

    pass


class WindowNotFoundError(CaptureError):
    """Exception raised when GS Pro window is not found."""

    pass


class LearningError(ServiceError):
    """Exception raised by learning service."""

    pass


class CacheError(ServiceError):
    """Exception raised by pattern cache."""

    pass


class CommentaryError(ServiceError):
    """Exception raised during commentary generation."""

    pass
