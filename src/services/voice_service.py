"""Voice service for text-to-speech using xAI Grok TTS API."""
import io
import os
import sys
import tempfile
import threading
from typing import Optional

from openai import OpenAI

from src.lib.exceptions import VoiceServiceError

# Platform-specific volume control
if sys.platform == 'win32':
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        WINDOWS_VOLUME_AVAILABLE = True
    except ImportError:
        WINDOWS_VOLUME_AVAILABLE = False
else:
    WINDOWS_VOLUME_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class VoiceService:
    """Voice service using xAI Grok TTS API."""

    AVAILABLE_VOICES = ["eve", "ara", "rex", "sal", "leo"]

    def __init__(
        self,
        api_key: str,
        voice_id: str = "leo",
        model: str = "grok-tts-preview",
        volume_boost: float = 0.0,
        **kwargs,  # Absorb legacy ElevenLabs params (stability, similarity_boost, etc.)
    ):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )
        self.voice_id = voice_id
        self.model = model
        self.volume_boost = volume_boost
        self.current_thread: Optional[threading.Thread] = None
        self.is_speaking = False
        self.should_stop = False

        if PYGAME_AVAILABLE and not pygame.mixer.get_init():
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()

    def speak(self, text: str, blocking: bool = False) -> bool:
        if self.is_speaking:
            return False

        if blocking:
            self._speak_sync(text)
        else:
            self.current_thread = threading.Thread(
                target=self._speak_sync,
                args=(text,),
                daemon=True,
            )
            self.current_thread.start()

        return True

    def speak_streaming(self, text: str) -> None:
        try:
            self.is_speaking = True
            self._generate_and_play(text)
            self.is_speaking = False
        except Exception as e:
            self.is_speaking = False
            raise VoiceServiceError(f"Failed to stream TTS audio: {e}")

    def update_voice(
        self,
        voice_id: Optional[str] = None,
        **kwargs,  # Absorb legacy ElevenLabs params for compatibility
    ) -> None:
        if voice_id is not None:
            self.voice_id = voice_id

    def stop(self) -> None:
        self.should_stop = True
        self.is_speaking = False

        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=2.0)

    def save_audio(self, text: str, file_path: str) -> None:
        try:
            response = self.client.audio.speech.create(
                model=self.model,
                voice=self.voice_id,
                input=text,
            )
            with open(file_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            raise VoiceServiceError(f"Failed to save TTS audio: {e}")

    def list_voices(self) -> list:
        return [
            {"id": v, "name": v.capitalize(), "category": "standard"}
            for v in self.AVAILABLE_VOICES
        ]

    def set_voice(self, voice_id: str) -> None:
        self.voice_id = voice_id

    def set_voice_settings(self, stability: float, similarity_boost: float) -> None:
        # No-op: Grok TTS does not have stability/similarity parameters
        pass

    def estimate_cost(self, text: str) -> float:
        # xAI Grok TTS: $4.20 per 1M characters
        return (len(text) / 1_000_000) * 4.20

    def _generate_and_play(self, text: str) -> None:
        # Use direct API call to xAI's TTS endpoint instead of OpenAI SDK
        import httpx

        response = httpx.post(
            "https://api.x.ai/v1/tts",
            headers={
                "Authorization": f"Bearer {self.client.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "voice_id": self.voice_id,
                "language": "en"
            },
            timeout=30.0
        )
        response.raise_for_status()
        audio_bytes = response.content

        if PYGAME_AVAILABLE:
            self._play_with_pygame(audio_bytes)
        else:
            self._play_with_tempfile(audio_bytes)

    def _play_with_pygame(self, audio_bytes: bytes) -> None:
        audio_io = io.BytesIO(audio_bytes)
        pygame.mixer.music.load(audio_io)
        pygame.mixer.music.play()

        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            if self.should_stop:
                pygame.mixer.music.stop()
                break
            clock.tick(10)

    def _play_with_tempfile(self, audio_bytes: bytes) -> None:
        # Fallback: write to temp file and use subprocess
        import subprocess
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["powershell", "-c",
                     f"Add-Type -AssemblyName presentationCore; "
                     f"$mp = [System.Windows.Media.MediaPlayer]::new(); "
                     f"$mp.Open([Uri]::new('{temp_path}')); "
                     f"$mp.Play(); Start-Sleep -s 10"],
                    check=False, timeout=30,
                )
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def _set_system_volume(self, boost_db: float) -> Optional[float]:
        if not WINDOWS_VOLUME_AVAILABLE or boost_db == 0.0:
            return None

        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))

            current_volume = volume.GetMasterVolumeLevelScalar()

            if boost_db == 10.0:
                boost_multiplier = 1.5
            elif boost_db == 20.0:
                boost_multiplier = 2.0
            else:
                boost_multiplier = 1.0

            new_volume = min(1.0, current_volume * boost_multiplier)
            volume.SetMasterVolumeLevelScalar(new_volume, None)

            return current_volume
        except Exception:
            return None

    def _restore_system_volume(self, previous_volume: Optional[float]) -> None:
        if not WINDOWS_VOLUME_AVAILABLE or previous_volume is None:
            return

        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(previous_volume, None)
        except Exception:
            pass

    def _speak_sync(self, text: str) -> None:
        previous_volume = None
        try:
            self.is_speaking = True
            self.should_stop = False
            previous_volume = self._set_system_volume(self.volume_boost)

            self._generate_and_play(text)

            self._restore_system_volume(previous_volume)
            self.is_speaking = False

        except Exception as e:
            self._restore_system_volume(previous_volume)
            self.is_speaking = False

            error_str = str(e)
            if "401" in error_str or "403" in error_str or "quota" in error_str.lower() or "insufficient_quota" in error_str or "not authorized" in error_str.lower():
                print("  ⚠️  xAI TTS error - skipping voice synthesis")
                print("  💡 Voice requires TTS access at console.x.ai")
                print("  💡 Check if your plan includes Grok TTS or request beta access")
                return

            raise VoiceServiceError(f"Failed to generate TTS audio: {e}")
