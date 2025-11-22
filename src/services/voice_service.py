"""Voice service for text-to-speech using ElevenLabs API."""
import threading
from typing import Optional

from elevenlabs import VoiceSettings, save
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

from src.lib.exceptions import VoiceServiceError


class VoiceService:
    """
    Voice service using ElevenLabs text-to-speech API.

    Supports streaming audio playback with configurable voice settings.
    """

    def __init__(
        self,
        api_key: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Default: Rachel voice
        model: str = "eleven_turbo_v2_5",  # Turbo v2.5 (free tier compatible)
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ):
        """
        Initialize voice service.

        Args:
            api_key: ElevenLabs API key
            voice_id: ElevenLabs voice ID (default: Rachel)
            model: TTS model to use
            stability: Voice stability (0.0-1.0)
            similarity_boost: Voice similarity boost (0.0-1.0)
        """
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        self.model = model
        self.voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
        )
        self.current_thread: Optional[threading.Thread] = None
        self.is_speaking = False
        self.should_stop = False

    def speak(self, text: str, blocking: bool = False) -> bool:
        """
        Speak text using ElevenLabs TTS.

        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete; if False, run in background

        Returns:
            True if speech started, False if skipped (already speaking)

        Raises:
            VoiceServiceError: If TTS fails
        """
        # Check if already speaking - skip if so to prevent overlap
        if self.is_speaking:
            return False

        if blocking:
            self._speak_sync(text)
        else:
            # Run in background thread
            self.current_thread = threading.Thread(
                target=self._speak_sync,
                args=(text,),
                daemon=True,
            )
            self.current_thread.start()

        return True

    def speak_streaming(self, text: str) -> None:
        """
        Speak text using streaming audio (lower latency).

        Args:
            text: Text to speak

        Raises:
            VoiceServiceError: If TTS fails
        """
        try:
            self.is_speaking = True

            # Generate audio
            audio_data = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model,
                voice_settings=self.voice_settings,
            )

            # Play audio using ElevenLabs play function
            play(audio_data)

            self.is_speaking = False

        except Exception as e:
            self.is_speaking = False
            raise VoiceServiceError(f"Failed to stream TTS audio: {e}")

    def update_voice(
        self,
        voice_id: Optional[str] = None,
        stability: Optional[float] = None,
        similarity_boost: Optional[float] = None,
    ) -> None:
        """
        Update voice settings dynamically.

        Args:
            voice_id: New voice ID (if None, keeps current)
            stability: New stability value (if None, keeps current)
            similarity_boost: New similarity boost (if None, keeps current)
        """
        if voice_id is not None:
            self.voice_id = voice_id

        if stability is not None or similarity_boost is not None:
            current_stability = self.voice_settings.stability
            current_similarity = self.voice_settings.similarity_boost

            self.voice_settings = VoiceSettings(
                stability=stability if stability is not None else current_stability,
                similarity_boost=similarity_boost if similarity_boost is not None else current_similarity,
            )

    def stop(self) -> None:
        """Stop current speech (if running in background)."""
        self.should_stop = True
        self.is_speaking = False

        if self.current_thread and self.current_thread.is_alive():
            # Note: Cannot forcefully stop mpv playback, but we can wait for it
            # Setting flags to prevent new speech from starting
            self.current_thread.join(timeout=2.0)

    def save_audio(self, text: str, file_path: str) -> None:
        """
        Generate TTS audio and save to file.

        Args:
            text: Text to convert
            file_path: Path to save audio file (e.g., "output.mp3")

        Raises:
            VoiceServiceError: If generation fails
        """
        try:
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model,
                voice_settings=self.voice_settings,
            )

            save(audio, file_path)

        except Exception as e:
            raise VoiceServiceError(f"Failed to save TTS audio: {e}")

    def list_voices(self) -> list:
        """
        List available ElevenLabs voices.

        Returns:
            List of voice dictionaries with id, name, category

        Raises:
            VoiceServiceError: If API call fails
        """
        try:
            voices = self.client.voices.get_all()
            return [
                {
                    "id": voice.voice_id,
                    "name": voice.name,
                    "category": voice.category,
                }
                for voice in voices.voices
            ]
        except Exception as e:
            raise VoiceServiceError(f"Failed to list voices: {e}")

    def set_voice(self, voice_id: str) -> None:
        """
        Change voice for TTS.

        Args:
            voice_id: ElevenLabs voice ID
        """
        self.voice_id = voice_id

    def set_voice_settings(self, stability: float, similarity_boost: float) -> None:
        """
        Update voice settings.

        Args:
            stability: Voice stability (0.0-1.0)
            similarity_boost: Voice similarity boost (0.0-1.0)

        Raises:
            VoiceServiceError: If values out of range
        """
        if not (0.0 <= stability <= 1.0):
            raise VoiceServiceError(f"Stability must be 0.0-1.0, got {stability}")
        if not (0.0 <= similarity_boost <= 1.0):
            raise VoiceServiceError(
                f"Similarity boost must be 0.0-1.0, got {similarity_boost}"
            )

        self.voice_settings = VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
        )

    def _speak_sync(self, text: str) -> None:
        """
        Synchronous speech (internal helper).

        Args:
            text: Text to speak

        Raises:
            VoiceServiceError: If TTS fails
        """
        try:
            self.is_speaking = True

            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model,
                voice_settings=self.voice_settings,
            )

            # Play audio using ElevenLabs play function
            play(audio)

            self.is_speaking = False

        except Exception as e:
            self.is_speaking = False

            # Check for quota exceeded error
            error_str = str(e)
            if "quota_exceeded" in error_str or "401" in error_str:
                print("  ⚠️  ElevenLabs quota exceeded - skipping voice synthesis")
                print("  💡 Commentary will continue without voice until quota resets")
                # Don't raise - just skip voice synthesis gracefully
                return

            # For other errors, raise
            raise VoiceServiceError(f"Failed to generate TTS audio: {e}")

    def estimate_cost(self, text: str) -> float:
        """
        Estimate API cost for speaking this text.

        Args:
            text: Text to estimate

        Returns:
            Estimated cost in USD
        """
        # ElevenLabs pricing (as of 2024):
        # ~$0.30 per 1000 characters for standard voices

        char_count = len(text)
        cost_per_1k_chars = 0.30

        return (char_count / 1000) * cost_per_1k_chars
