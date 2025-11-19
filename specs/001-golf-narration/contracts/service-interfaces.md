# Service Interfaces: AI Voice Caddy for GS Pro

**Date**: 2025-11-19
**Phase**: 1 - Design

## Overview

This document defines the internal contracts (interfaces) for all services in the AI Voice Caddy system. These are Python protocols (abstract interfaces) that define expected behavior without implementation details.

## Service Contracts

### 1. Screen Capture Service

**Purpose**: Detect and capture screenshots from the GS Pro window.

**Interface**:
```python
from typing import Protocol, Optional
import numpy as np

class IScreenCaptureService(Protocol):
    """Interface for screen capture and window detection"""

    def find_gs_pro_window(self) -> Optional[str]:
        """
        Detect GS Pro window by title pattern.

        Returns:
            Window handle/ID if found, None otherwise
        """
        ...

    def capture_window(self, window_id: str) -> np.ndarray:
        """
        Capture screenshot of specified window.

        Args:
            window_id: Window handle from find_gs_pro_window()

        Returns:
            Screenshot as NumPy array (RGB format)

        Raises:
            WindowNotFoundError: If window no longer exists
            CaptureError: If screenshot fails
        """
        ...

    def start_monitoring(self, window_id: str, fps: int = 2) -> None:
        """
        Begin continuous screen capture at specified FPS.

        Args:
            window_id: Window to monitor
            fps: Frames per second (default: 2)

        Raises:
            WindowNotFoundError: If window doesn't exist
        """
        ...

    def stop_monitoring(self) -> None:
        """Stop continuous capture and release resources."""
        ...

    def get_latest_frame(self) -> Optional[np.ndarray]:
        """
        Get most recent captured frame.

        Returns:
            Latest screenshot or None if no frames captured
        """
        ...
```

**Expected Behavior**:
- Window detection case-insensitive ("GS Pro", "gspro", "GS PRO")
- Capture returns RGB format (OpenCV compatible)
- FPS defaults to 2 (adequate for motion detection)
- Monitoring runs in background thread
- Graceful handling of window minimize/close

---

### 2. Motion Detector Service

**Purpose**: Detect shot events through frame differencing.

**Interface**:
```python
from typing import Protocol, Callable
import numpy as np

class IMotionDetectorService(Protocol):
    """Interface for motion detection and shot event identification"""

    def analyze_frame(self, frame: np.ndarray) -> bool:
        """
        Analyze frame for motion.

        Args:
            frame: Current frame (RGB)

        Returns:
            True if motion detected, False otherwise
        """
        ...

    def is_ball_stopped(self) -> bool:
        """
        Check if ball has stopped moving (shot complete).

        Returns:
            True if no motion for configured duration (1 second default)
        """
        ...

    def reset(self) -> None:
        """Reset motion detector state (e.g., between rounds)."""
        ...

    def set_threshold(self, threshold: float) -> None:
        """
        Adjust motion sensitivity.

        Args:
            threshold: Pixel change ratio (0.0-1.0, default 0.02)
        """
        ...

    def on_shot_detected(self, callback: Callable[[np.ndarray], None]) -> None:
        """
        Register callback for shot completion events.

        Args:
            callback: Function to call with final frame when shot complete
        """
        ...
```

**Expected Behavior**:
- Frame differencing with adaptive thresholding
- Ball stopped = no motion for 1 second (configurable)
- Reset clears previous frame history
- Callback fired exactly once per shot

---

### 3. AI Analyzer Service

**Purpose**: Analyze shot outcomes using Claude Vision API.

**Interface**:
```python
from typing import Protocol, Tuple
import numpy as np

class IAIAnalyzerService(Protocol):
    """Interface for AI-powered shot analysis"""

    def analyze_shot(
        self,
        screenshot: np.ndarray,
        personality_prompt: str,
        few_shot_examples: list = None
    ) -> Tuple[str, float, str, float]:
        """
        Analyze shot outcome and generate commentary.

        Args:
            screenshot: Shot completion frame
            personality_prompt: System prompt for personality
            few_shot_examples: Recent corrections for context (optional)

        Returns:
            Tuple of (outcome, confidence, commentary, api_cost)
            - outcome: Detected outcome type (enum value)
            - confidence: AI confidence (0.0-1.0)
            - commentary: Generated commentary text
            - api_cost: Cost of this API call in USD

        Raises:
            AIServiceError: If API call fails
            InvalidImageError: If screenshot invalid
        """
        ...

    def validate_api_key(self) -> bool:
        """
        Check if Anthropic API key is valid.

        Returns:
            True if key valid, False otherwise
        """
        ...

    def get_total_cost(self) -> float:
        """
        Get cumulative API cost for current session.

        Returns:
            Total cost in USD
        """
        ...

    def reset_cost_tracking(self) -> None:
        """Reset cost counter (e.g., new session)."""
        ...
```

**Expected Behavior**:
- Image automatically resized to 1280x720 before API call
- few_shot_examples include recent corrections
- Retry logic (3 attempts, exponential backoff)
- Cost tracking accumulates across calls
- Timeout after 10 seconds

---

### 4. Pattern Cache Service

**Purpose**: Cache shot outcomes using perceptual hashing.

**Interface**:
```python
from typing import Protocol, Optional, Tuple
import numpy as np

class IPatternCacheService(Protocol):
    """Interface for pattern matching and caching"""

    def find_match(self, screenshot: np.ndarray) -> Optional[Tuple[str, float]]:
        """
        Find cached match for screenshot.

        Args:
            screenshot: Frame to match

        Returns:
            Tuple of (outcome, confidence) if match found, None otherwise
            Confidence based on hash similarity (0.0-1.0)
        """
        ...

    def add_pattern(
        self,
        screenshot: np.ndarray,
        outcome: str,
        confidence: float = 1.0
    ) -> str:
        """
        Add pattern to cache.

        Args:
            screenshot: Frame to cache
            outcome: Correct outcome label
            confidence: Initial confidence (default 1.0 for user-provided)

        Returns:
            Perceptual hash of screenshot
        """
        ...

    def update_confidence(self, hash_value: str, new_confidence: float) -> None:
        """
        Update confidence for cached pattern.

        Args:
            hash_value: Pattern hash
            new_confidence: Updated confidence score
        """
        ...

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dict with keys: total_patterns, hit_rate, avg_confidence
        """
        ...

    def clear(self) -> None:
        """Clear all cached patterns (fresh start)."""
        ...

    def persist(self) -> None:
        """Save cache to disk."""
        ...

    def load(self) -> None:
        """Load cache from disk."""
        ...
```

**Expected Behavior**:
- Perceptual hash (imagehash library)
- Hamming distance <10 for match
- Confidence >0.85 → use cache, <0.6 → skip cache
- Auto-persist every 10 additions or on shutdown
- Thread-safe for concurrent access

---

### 5. Commentary Generator Service

**Purpose**: Generate personality-appropriate commentary.

**Interface**:
```python
from typing import Protocol

class ICommentaryGeneratorService(Protocol):
    """Interface for commentary generation"""

    def load_personality(self, personality_name: str) -> None:
        """
        Load personality configuration.

        Args:
            personality_name: Name matching YAML file

        Raises:
            PersonalityNotFoundError: If personality doesn't exist
        """
        ...

    def get_system_prompt(self) -> str:
        """
        Get system prompt for current personality.

        Returns:
            System prompt text for AI
        """
        ...

    def get_example_phrases(self, outcome: str) -> list[str]:
        """
        Get example phrases for outcome.

        Args:
            outcome: Outcome type

        Returns:
            List of example phrases (empty if none)
        """
        ...

    def list_personalities(self) -> list[str]:
        """
        List available personality names.

        Returns:
            List of personality names
        """
        ...
```

**Expected Behavior**:
- YAML files in `data/personalities/`
- Default to "neutral" if personality not found
- Cache loaded personalities in memory
- Validate YAML structure on load

---

### 6. Voice Service

**Purpose**: Text-to-speech via ElevenLabs.

**Interface**:
```python
from typing import Protocol, Callable

class IVoiceService(Protocol):
    """Interface for text-to-speech"""

    def speak(self, text: str, blocking: bool = False) -> None:
        """
        Speak commentary text.

        Args:
            text: Commentary to speak
            blocking: If True, wait for speech to complete (default: False)

        Raises:
            VoiceServiceError: If TTS fails
        """
        ...

    def stop(self) -> None:
        """Stop current speech immediately."""
        ...

    def is_speaking(self) -> bool:
        """
        Check if currently speaking.

        Returns:
            True if speech in progress
        """
        ...

    def set_voice(self, voice_id: str) -> None:
        """
        Change voice.

        Args:
            voice_id: ElevenLabs voice ID

        Raises:
            VoiceNotFoundError: If voice doesn't exist
        """
        ...

    def validate_api_key(self) -> bool:
        """
        Check if ElevenLabs API key is valid.

        Returns:
            True if key valid, False otherwise
        """
        ...

    def on_speech_complete(self, callback: Callable[[], None]) -> None:
        """
        Register callback for speech completion.

        Args:
            callback: Function to call when speech finishes
        """
        ...
```

**Expected Behavior**:
- Streaming mode for low latency
- Non-blocking by default (speak in background)
- Queue if already speaking (don't overlap)
- Interrupt previous if new shot detected

---

### 7. Learning Service

**Purpose**: Handle user corrections and active learning.

**Interface**:
```python
from typing import Protocol
import numpy as np
from models.correction import UserCorrection
from models.training_example import TrainingExample

class ILearningService(Protocol):
    """Interface for active learning and corrections"""

    def record_correction(
        self,
        shot_event_id: str,
        incorrect_prediction: str,
        correct_outcome: str,
        screenshot: np.ndarray,
        explanation: str = ""
    ) -> UserCorrection:
        """
        Record user correction.

        Args:
            shot_event_id: ID of corrected shot
            incorrect_prediction: What AI said
            correct_outcome: User-provided truth
            screenshot: Frame screenshot
            explanation: User explanation (optional)

        Returns:
            Created UserCorrection object

        Raises:
            InvalidCorrectionError: If correction invalid
        """
        ...

    def create_training_example(self, correction: UserCorrection) -> TrainingExample:
        """
        Create training example from correction.

        Args:
            correction: Correction to learn from

        Returns:
            Created TrainingExample

        Raises:
            StorageError: If save fails
        """
        ...

    def get_recent_corrections(self, limit: int = 5) -> list[UserCorrection]:
        """
        Get recent corrections for few-shot prompting.

        Args:
            limit: Max corrections to return (default 5)

        Returns:
            List of recent corrections, newest first
        """
        ...

    def get_correction_stats(self) -> dict:
        """
        Get correction statistics.

        Returns:
            Dict with keys: total_corrections, accuracy_rate, common_mistakes
        """
        ...
```

**Expected Behavior**:
- Corrections persisted immediately
- Training example auto-created from correction
- Pattern cache updated with correct outcome
- Recent corrections included in next AI prompt

---

## Service Dependencies

```
CLI Layer
    ├── main.py
    │   ├── → ScreenCaptureService
    │   ├── → MotionDetectorService
    │   ├── → AIAnalyzerService
    │   ├── → PatternCacheService
    │   ├── → CommentaryGeneratorService
    │   ├── → VoiceService
    │   └── → LearningService
    │
    ├── setup.py
    │   ├── → ScreenCaptureService (window detection)
    │   ├── → CommentaryGeneratorService (personality selection)
    │   ├── → AIAnalyzerService (validate API key)
    │   └── → VoiceService (validate API key)
    │
    └── train.py
        ├── → PatternCacheService (add examples)
        └── → LearningService (create training examples)

Service Layer Dependencies:
- AIAnalyzerService → None (external API only)
- PatternCacheService → None (filesystem only)
- MotionDetectorService → ScreenCaptureService (frame source)
- CommentaryGeneratorService → None (filesystem only)
- VoiceService → None (external API only)
- LearningService → PatternCacheService, filesystem
```

## Error Handling Contracts

All services must follow these error handling conventions:

**Service-Specific Exceptions**:
```python
class ServiceError(Exception):
    """Base exception for all service errors"""
    pass

class ScreenCaptureError(ServiceError):
    """Screen capture failures"""
    pass

class AIServiceError(ServiceError):
    """AI API failures"""
    pass

class VoiceServiceError(ServiceError):
    """TTS failures"""
    pass

class CacheError(ServiceError):
    """Pattern cache failures"""
    pass

class LearningError(ServiceError):
    """Learning service failures"""
    pass
```

**Error Response Pattern**:
- Log error details (DEBUG level)
- Raise typed exception with user-friendly message
- Include original exception as cause
- Never expose API keys or sensitive data in errors

## Testing Contracts

Each service interface must have:

1. **Unit Tests**:
   - Mock external dependencies
   - Test each method independently
   - Validate error handling

2. **Integration Tests**:
   - Test with real dependencies (controlled)
   - Validate end-to-end flows
   - Measure performance/cost

3. **Contract Tests**:
   - Verify interface compliance
   - Test all exception paths
   - Validate return types

**Example Contract Test**:
```python
def test_ai_analyzer_contract(ai_service: IAIAnalyzerService):
    """Verify AIAnalyzerService implements interface correctly"""
    # Test return type
    outcome, confidence, commentary, cost = ai_service.analyze_shot(
        screenshot=sample_screenshot,
        personality_prompt="You are a neutral commentator",
        few_shot_examples=[]
    )

    assert isinstance(outcome, str)
    assert 0.0 <= confidence <= 1.0
    assert isinstance(commentary, str)
    assert isinstance(cost, float) and cost >= 0.0

    # Test exceptions
    with pytest.raises(AIServiceError):
        ai_service.analyze_shot(invalid_screenshot, "", [])
```

## Performance Contracts

Services must meet these performance requirements:

| Service | Operation | Target Latency | Max Latency |
|---------|-----------|----------------|-------------|
| ScreenCapture | capture_window() | <50ms | 100ms |
| MotionDetector | analyze_frame() | <10ms | 20ms |
| AIAnalyzer | analyze_shot() | <1500ms | 3000ms |
| PatternCache | find_match() | <5ms | 10ms |
| CommentaryGenerator | get_system_prompt() | <1ms | 5ms |
| VoiceService | speak() (initiate) | <100ms | 200ms |
| LearningService | record_correction() | <50ms | 100ms |

**Total Pipeline Target**: Shot detection → commentary spoken < 2 seconds

## Thread Safety Requirements

**Thread-Safe Services** (must support concurrent access):
- PatternCacheService (read/write from multiple threads)
- LearningService (corrections during monitoring)

**Single-Thread Services** (called from one thread):
- ScreenCaptureService (monitoring thread only)
- MotionDetectorService (monitoring thread only)
- AIAnalyzerService (synchronous, sequential calls)
- VoiceService (speech queue, but internal locking)
- CommentaryGeneratorService (read-only, naturally thread-safe)

**Locking Strategy**:
- Use `threading.Lock` for critical sections
- Prefer `threading.RLock` for reentrant operations
- Document locking requirements in implementation

## Configuration Contracts

Services must accept configuration via:

1. **Constructor injection** (preferred):
   ```python
   class ScreenCaptureService:
       def __init__(self, config: ScreenCaptureConfig):
           self.fps = config.fps
           self.window_pattern = config.window_pattern
   ```

2. **Setter methods** (for runtime changes):
   ```python
   def set_threshold(self, threshold: float) -> None:
       ...
   ```

3. **Environment variables** (for secrets):
   ```python
   api_key = os.getenv('ANTHROPIC_API_KEY')
   ```

**Configuration Validation**:
- Validate on load (constructor or setter)
- Raise `ConfigurationError` for invalid values
- Provide sensible defaults
- Document all configuration options
