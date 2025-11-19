"""CLI monitor for coordinating shot detection and commentary."""
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

            # Find GS Pro window
            print("\nSearching for GS Pro window...")
            window_title = self.screen_capture.find_gs_pro_window()

            if not window_title:
                raise ServiceError("GS Pro window not found. Is GS Pro running?")

            print(f"Found window: {window_title}")

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
            print("Commands:")
            print("  Type 'correct' to correct the last shot")
            print("  Type 'stats' to show learning statistics")
            print("  Press Ctrl+C to stop.\n")

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

    def stop(self) -> None:
        """Stop monitoring and cleanup."""
        self.is_running = False

        # Stop screen capture
        if hasattr(self, "screen_capture"):
            self.screen_capture.stop_monitoring()

        # End session
        if self.session:
            self.session.end_time = datetime.now()

            # Print session stats
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
                print(f"Session saved: {self.session.id}")
            except Exception as e:
                print(f"Warning: Failed to save session: {e}")

            # Persist cache
            self.pattern_cache.persist()
            print("Pattern cache saved.")

        print("\nGoodbye!")

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

                # Estimate cost
                api_cost = self.ai_analyzer.estimate_cost(screenshot)

                print(f"  Outcome: {outcome.value} (confidence: {confidence:.2f})")

                # Add to cache if high confidence
                if confidence >= self.config.cache.min_confidence_to_cache:
                    self.pattern_cache.add_pattern(screenshot, outcome, confidence)

            # Generate commentary
            print("  Generating commentary...")
            commentary = self.commentary_generator.generate_commentary(
                outcome=outcome,
                confidence=confidence,
            )

            print(f"  Commentary: \"{commentary}\"")

            # Speak commentary (non-blocking)
            self.voice_service.speak(commentary, blocking=False)

            # Create shot event
            screenshot_hash = str(self.pattern_cache._compute_hash(screenshot))
            shot_event = ShotEvent(
                id=shot_id,
                timestamp=timestamp,
                screenshot=screenshot,
                screenshot_hash=screenshot_hash,
                detected_outcome=outcome,
                confidence=confidence,
                commentary_text=commentary,
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

    def correct_last_shot(self) -> None:
        """Prompt user to correct the last shot."""
        if not self.session or not self.session.shot_events:
            print("No shots to correct.")
            return

        last_shot = self.session.shot_events[-1]

        print("\n" + "=" * 50)
        print("CORRECT LAST SHOT")
        print("=" * 50)
        print(f"Detected outcome: {last_shot.detected_outcome.value}")
        print(f"Confidence: {last_shot.confidence:.2f}")
        print(f"Commentary: \"{last_shot.commentary_text}\"")
        print("\nAvailable outcomes:")

        outcomes = list(Outcome)
        for i, outcome in enumerate(outcomes, 1):
            print(f"  {i}. {outcome.value}")

        print("\nEnter the correct outcome number (or 0 to cancel): ", end="")

        try:
            choice = int(input())
            if choice == 0:
                print("Correction cancelled.")
                return

            if choice < 1 or choice > len(outcomes):
                print("Invalid choice.")
                return

            corrected_outcome = outcomes[choice - 1]

            # Optional notes
            print("Add notes (optional, press Enter to skip): ", end="")
            notes = input().strip()

            # Create correction
            correction = UserCorrection(
                original_outcome=last_shot.detected_outcome,
                corrected_outcome=corrected_outcome,
                timestamp=datetime.now(),
                user_notes=notes,
            )

            # Record correction
            self.learning_service.add_correction(correction)
            last_shot.correction = correction

            # Update pattern cache with correct outcome
            self.pattern_cache.add_pattern(
                last_shot.screenshot, corrected_outcome, confidence=1.0
            )

            # Promote to few-shot example
            self.learning_service.add_few_shot_example(
                outcome=corrected_outcome,
                screenshot_hash=last_shot.screenshot_hash,
                reasoning=f"User correction from {last_shot.detected_outcome.value}",
                confidence=1.0,
            )

            print(f"\nCorrection recorded: {corrected_outcome.value}")
            print("This will improve future accuracy.")
            print("=" * 50 + "\n")

        except ValueError:
            print("Invalid input.")
        except Exception as e:
            print(f"Error recording correction: {e}")

    def show_learning_stats(self) -> None:
        """Display learning statistics."""
        stats = self.learning_service.get_learning_stats()

        print("\n" + "=" * 50)
        print("LEARNING STATISTICS")
        print("=" * 50)
        print(f"Total corrections: {stats['total_corrections']}")
        print(f"Total few-shot examples: {stats['total_examples']}")

        if stats['corrections_by_outcome']:
            print("\nCorrections by outcome:")
            for outcome, count in stats['corrections_by_outcome'].items():
                print(f"  {outcome}: {count}")

        if stats['examples_by_outcome']:
            print("\nFew-shot examples by outcome:")
            for outcome, count in stats['examples_by_outcome'].items():
                print(f"  {outcome}: {count}")

        cache_stats = self.pattern_cache.get_stats()
        print(f"\nPattern cache:")
        print(f"  Total patterns: {cache_stats['total_patterns']}")
        print(f"  Total hits: {cache_stats['total_hits']}")
        print(f"  Hit rate: {cache_stats['hit_rate'] * 100:.1f}%")

        print("=" * 50 + "\n")
