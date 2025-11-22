"""CLI monitor for coordinating shot detection and commentary."""
import random
import time
from datetime import datetime
from typing import Optional

import numpy as np

from src.lib.config import Config
from src.lib.exceptions import ServiceError
from src.lib.utils import generate_uuid
from src.models.correction import UserCorrection
from src.models.outcome import Outcome
from src.models.session import Session
from src.models.shot_event import ShotEvent
from src.services.ai_analyzer import AIAnalyzerService
from src.services.commentary_generator import CommentaryGeneratorService
from src.services.learning_service import LearningService
from src.services.motion_detector import MotionDetectorService
from src.services.pattern_cache import PatternCacheService
from src.services.screen_capture import ScreenCaptureService
from src.services.session_service import SessionService
from src.services.voice_service import VoiceService


class Monitor:
    """
    Main monitoring orchestrator.

    Coordinates screen capture, motion detection, AI analysis, commentary
    generation, and voice output for golf shot narration.
    """

    def __init__(self, config: Config):
        """
        Initialize monitor with configuration.

        Args:
            config: Application configuration
        """
        self.config = config
        self.session: Optional[Session] = None
        self.is_running = False

        # Initialize services
        self._init_services()

    def start(self) -> None:
        """
        Start monitoring GS Pro window.

        Raises:
            ServiceError: If services fail to start
        """
        try:
            print("Starting Mully Mouth Golf Caddy...")
            print(f"Personality: {self.config.personality}")

            # Use primary monitor for capture
            print("\nUsing primary monitor for capture...")
            monitor_info = self.screen_capture.find_gs_pro_window()

            if not monitor_info:
                raise ServiceError("Could not access primary monitor.")

            print(f"Capturing: {monitor_info}")
            print("Make your video fullscreen to capture it.")

            # Start screen capture
            fps = self.config.monitoring.fps
            print(f"Starting screen capture at {fps} FPS...")
            self.screen_capture.start_monitoring(fps=fps)

            # Create new session
            self.session = Session(
                id=generate_uuid(),
                start_time=datetime.now(),
                personality_name=self.config.personality,
            )

            print("\nMonitoring active. Waiting for shots...")
            print("Press Ctrl+C to stop.\n")

            # Main monitoring loop
            self.is_running = True
            self._monitoring_loop()

        except KeyboardInterrupt:
            print("\n\nStopping monitor...")
            self.stop()
        except Exception as e:
            print(f"\nError: {e}")
            self.stop()
            raise

    def stop(self, print_summary: bool = True) -> None:
        """
        Stop monitoring and cleanup.

        Args:
            print_summary: Whether to print session summary (default: True)
        """
        if not self.is_running:
            return

        self.is_running = False

        # Stop voice service (interrupt any ongoing speech)
        if hasattr(self, "voice_service"):
            self.voice_service.stop()

        # Stop screen capture
        if hasattr(self, "screen_capture"):
            self.screen_capture.stop_monitoring()

        # End session
        if self.session:
            self.session.end_time = datetime.now()

            # Print session stats
            if print_summary:
                print("\n" + "=" * 50)
                print("SESSION SUMMARY")
                print("=" * 50)
                print(f"Total shots: {len(self.session.shot_events)}")
                print(f"API calls: {self.session.total_api_calls}")
                print(f"Cache hit rate: {self.session.cache_hit_rate * 100:.1f}%")
                print(f"Total cost: ${self.session.total_cost:.4f}")
                print(f"Accuracy: {self.session.accuracy_rate * 100:.1f}%")
                print("=" * 50)

            # Save session
            try:
                self.session_service.save_session(self.session)
                if print_summary:
                    print(f"Session saved: {self.session.id}")
            except Exception as e:
                if print_summary:
                    print(f"Warning: Failed to save session: {e}")

            # Persist cache
            self.pattern_cache.persist()
            if print_summary:
                print("Pattern cache saved.")

        if print_summary:
            print("\nGoodbye!")

    def get_status(self) -> dict:
        """
        Get current monitoring status (thread-safe).

        Returns:
            Dictionary with status information
        """
        status = {
            "is_running": self.is_running,
            "session_active": self.session is not None,
            "total_shots": 0,
            "total_cost": 0.0,
            "cache_hit_rate": 0.0,
            "accuracy_rate": 0.0,
            "total_api_calls": 0,
            "personality": self.config.personality,
            "commentary_frequency": self.config.commentary_frequency,
            "name_frequency": self.config.name_frequency,
        }

        if self.session:
            status.update({
                "total_shots": len(self.session.shot_events),
                "total_cost": self.session.total_cost,
                "cache_hit_rate": self.session.cache_hit_rate,
                "accuracy_rate": self.session.accuracy_rate,
                "total_api_calls": self.session.total_api_calls,
            })

        return status

    def start_non_blocking(self) -> None:
        """
        Start monitoring in non-blocking mode (for system tray use).

        Raises:
            ServiceError: If services fail to start
        """
        try:
            # Use primary monitor for capture
            monitor_info = self.screen_capture.find_gs_pro_window()

            if not monitor_info:
                raise ServiceError("Could not access primary monitor.")

            # Start screen capture
            fps = self.config.monitoring.fps
            self.screen_capture.start_monitoring(fps=fps)

            # Create new session
            self.session = Session(
                id=generate_uuid(),
                start_time=datetime.now(),
                personality_name=self.config.personality,
            )

            # Main monitoring loop
            self.is_running = True
            self._monitoring_loop()

        except Exception as e:
            self.stop(print_summary=False)
            raise

    def _init_services(self) -> None:
        """Initialize all required services."""
        # Screen capture
        self.screen_capture = ScreenCaptureService()

        # Motion detector
        self.motion_detector = MotionDetectorService(
            threshold=self.config.monitoring.motion_threshold,
            ball_stop_duration=self.config.monitoring.ball_stop_duration,
        )

        # Pattern cache
        self.pattern_cache = PatternCacheService(
            cache_file=str(self.config.cache.pattern_cache_file),
            hamming_threshold=self.config.cache.hamming_threshold,
        )

        # AI analyzer
        self.ai_analyzer = AIAnalyzerService(
            api_key=self.config.anthropic.api_key,
            model=self.config.anthropic.model,
        )

        # Commentary generator
        self.commentary_generator = CommentaryGeneratorService(
            api_key=self.config.anthropic.api_key,
            personality_name=self.config.personality,
            model=self.config.anthropic.model,
        )

        # Voice service
        self.voice_service = VoiceService(
            api_key=self.config.elevenlabs.api_key,
            voice_id=self.config.elevenlabs.voice_id,
            model=self.config.elevenlabs.model,
            stability=self.config.elevenlabs.stability,
            similarity_boost=self.config.elevenlabs.similarity_boost,
        )

        # Learning service
        self.learning_service = LearningService(
            corrections_file="data/training/corrections.json",
            examples_file="data/training/few_shot_examples.json",
        )

        # Session service
        self.session_service = SessionService(sessions_dir="data/sessions")

    def _monitoring_loop(self) -> None:
        """
        Main monitoring loop.

        Continuously processes frames for motion detection and shot analysis.
        """
        while self.is_running:
            try:
                # Get latest frame
                frame = self.screen_capture.get_latest_frame()

                if frame is None:
                    time.sleep(0.1)
                    continue

                # Analyze for motion
                has_motion = self.motion_detector.analyze_frame(frame)

                # Check if ball stopped (shot complete)
                if self.motion_detector.is_ball_stopped():
                    # Process shot
                    self._process_shot(frame)

                    # Reset motion detector for next shot
                    self.motion_detector.reset()

                # Sleep to avoid busy loop
                time.sleep(0.1)

            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(1.0)

    def _calculate_api_cost(self, raw_response: dict) -> float:
        """
        Calculate actual API cost from response usage data.

        Args:
            raw_response: API response dict with usage info

        Returns:
            Cost in USD
        """
        try:
            usage = raw_response.get('usage', {})
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)

            # Claude Sonnet 4.5 pricing (as of Nov 2024):
            # Input: $3.00 / 1M tokens
            # Output: $15.00 / 1M tokens
            # Cache reads: $0.30 / 1M tokens (90% discount)
            # Cache writes: $3.75 / 1M tokens (25% surcharge)

            cache_read_tokens = usage.get('cache_read_input_tokens', 0)
            cache_creation_tokens = usage.get('cache_creation_input_tokens', 0)

            # Calculate costs
            regular_input = input_tokens - cache_read_tokens - cache_creation_tokens
            input_cost = (regular_input / 1_000_000) * 3.00
            cache_read_cost = (cache_read_tokens / 1_000_000) * 0.30
            cache_write_cost = (cache_creation_tokens / 1_000_000) * 3.75
            output_cost = (output_tokens / 1_000_000) * 15.00

            total_cost = input_cost + cache_read_cost + cache_write_cost + output_cost
            return total_cost

        except Exception as e:
            # Fallback to rough estimate if usage data unavailable
            return 0.005  # ~$0.005 per request as fallback

    def _extract_player_name(self, screenshot: np.ndarray) -> Optional[str]:
        """
        Extract player name from upper left corner of screenshot using Claude Vision API.

        Args:
            screenshot: Full screenshot

        Returns:
            Player name if found, None otherwise
        """
        try:
            # Use AI analyzer to extract player name
            player_name = self.ai_analyzer.extract_player_name(screenshot)
            return player_name

        except Exception as e:
            # Name extraction failed, continue without name
            return None

    def _process_shot(self, screenshot: np.ndarray) -> None:
        """
        Process detected shot: analyze, generate commentary, speak.

        Args:
            screenshot: Screenshot of shot result
        """
        try:
            shot_id = generate_uuid()
            timestamp = datetime.now()

            print(f"\n[{timestamp.strftime('%H:%M:%S')}] Shot detected!")

            # Extract player name from screenshot every time (if name_frequency > 0)
            player_name = None
            if self.config.name_frequency > 0:
                player_name = self._extract_player_name(screenshot)
                if player_name:
                    print(f"  Player: {player_name}")

            # Check for score achievement first (Birdie, Eagle, etc.)
            achievement = self.ai_analyzer.detect_score_achievement(screenshot)
            if achievement:
                print(f"  Achievement detected: {achievement}!")

                # Generate achievement commentary
                print("  Generating achievement commentary...")

                # Decide whether to include player name based on name_frequency
                include_name = player_name and (random.random() < self.config.name_frequency)
                name_to_use = player_name if include_name else None

                # Update voice settings for current personality (if configured)
                try:
                    voice_config = self.commentary_generator.get_voice_config()
                    if voice_config:
                        self.voice_service.update_voice(
                            voice_id=voice_config.get("voice_id"),
                            stability=voice_config.get("voice_settings", {}).get("stability"),
                            similarity_boost=voice_config.get("voice_settings", {}).get("similarity_boost"),
                        )
                        print(f"  Using voice: {voice_config.get('voice_id')[:8]}...")
                except Exception as e:
                    print(f"  Warning: Could not apply voice config: {e}")

                commentary = self.commentary_generator.generate_achievement_commentary(
                    achievement=achievement,
                    player_name=name_to_use,
                )

                print(f"  Commentary: \"{commentary}\"")

                # Speak commentary (non-blocking)
                spoke = self.voice_service.speak(commentary, blocking=False)
                if not spoke:
                    print("  (Skipped - previous commentary still playing)")

                # For achievements, we skip the normal shot analysis
                # and don't save to session since it's a screen overlay, not a shot
                return

            # Check pattern cache first
            cached_result = self.pattern_cache.find_match(screenshot)

            if cached_result:
                outcome, confidence = cached_result
                was_cached = True
                api_cost = 0.0
                print(f"  Outcome: {outcome.value} (cached, confidence: {confidence:.2f})")
            else:
                # Get few-shot examples from learning service
                few_shot_examples = self.learning_service.get_few_shot_examples(limit=3)

                # Call AI analyzer
                print("  Analyzing with AI...")
                outcome, confidence, raw_response = self.ai_analyzer.analyze_shot(
                    screenshot, few_shot_examples=few_shot_examples
                )
                was_cached = False

                # Calculate actual cost from API response
                api_cost = self._calculate_api_cost(raw_response)

                print(f"  Outcome: {outcome.value} (confidence: {confidence:.2f})")
                if api_cost > 0:
                    print(f"  API cost: ${api_cost:.4f}")

                # Add to cache if high confidence
                if confidence >= self.config.cache.min_confidence_to_cache:
                    self.pattern_cache.add_pattern(screenshot, outcome, confidence)

            # Generate commentary based on frequency setting
            should_comment = random.random() < self.config.commentary_frequency
            commentary = None

            if should_comment:
                print("  Generating commentary...")

                # Decide whether to include player name based on name_frequency
                include_name = player_name and (random.random() < self.config.name_frequency)
                name_to_use = player_name if include_name else None

                # Update voice settings for current personality (if configured)
                try:
                    voice_config = self.commentary_generator.get_voice_config()
                    if voice_config:
                        self.voice_service.update_voice(
                            voice_id=voice_config.get("voice_id"),
                            stability=voice_config.get("voice_settings", {}).get("stability"),
                            similarity_boost=voice_config.get("voice_settings", {}).get("similarity_boost"),
                        )
                        print(f"  Using voice: {voice_config.get('voice_id')[:8]}...")
                except Exception as e:
                    print(f"  Warning: Could not apply voice config: {e}")

                commentary = self.commentary_generator.generate_commentary(
                    outcome=outcome,
                    confidence=confidence,
                    player_name=name_to_use,
                )

                print(f"  Commentary: \"{commentary}\"")

                # Speak commentary (non-blocking) - skip if already speaking
                spoke = self.voice_service.speak(commentary, blocking=False)
                if not spoke:
                    print("  (Skipped - previous commentary still playing)")
            else:
                print(f"  Skipping commentary (frequency: {self.config.commentary_frequency})")

            # Create shot event
            screenshot_hash = str(self.pattern_cache._compute_hash(screenshot))
            shot_event = ShotEvent(
                id=shot_id,
                timestamp=timestamp,
                screenshot=screenshot,
                screenshot_hash=screenshot_hash,
                detected_outcome=outcome,
                confidence=confidence,
                commentary_text=commentary or "",
                was_cached=was_cached,
                api_cost=api_cost,
            )

            # Add to session
            if self.session:
                self.session.shot_events.append(shot_event)

                # Print running stats
                print(f"  Session stats: {len(self.session.shot_events)} shots, "
                      f"${self.session.total_cost:.4f} cost, "
                      f"{self.session.cache_hit_rate * 100:.0f}% cache hits")

        except Exception as e:
            print(f"  Error processing shot: {e}")
