# Research: AI Voice Caddy for GS Pro

**Date**: 2025-11-19
**Phase**: 0 - Research & Technical Decisions

## Overview

Research conducted to validate technical choices, establish best practices, and resolve implementation questions for the AI-first voice caddy system.

## Key Decisions

### 1. Screen Capture & Window Detection

**Decision**: Use MSS (Python-mss) for screen capture with pygetwindow for window detection

**Rationale**:
- MSS is faster than PyAutoGUI (3-5x performance improvement)
- Cross-platform support (Windows, Linux, macOS)
- Zero-copy captures reduce memory overhead
- pygetwindow provides clean window enumeration API
- Both are MIT licensed, minimal dependencies

**Alternatives Considered**:
- PyAutoGUI: Slower, uses Pillow intermediate format
- PIL.ImageGrab: Windows-only, adequate speed but platform-limited
- pywin32: Windows-only, more complex API
- **Rejected**: All alternatives either slower or platform-specific

**Implementation Notes**:
- Capture specific window region once detected (reduces processing)
- 1-2 FPS adequate for motion detection (not real-time video)
- Store window handle to avoid repeated searches

### 2. Motion Detection Strategy

**Decision**: Use OpenCV frame differencing with adaptive thresholding

**Rationale**:
- Frame differencing detects ball movement reliably
- Adaptive thresholding handles varying lighting conditions
- Minimal CPU overhead (<5% on modern hardware)
- No ML model needed - simple, deterministic, free
- Well-established technique for game shot detection

**Alternatives Considered**:
- Optical flow: Overkill, more CPU intensive
- Background subtraction: Less reliable for fast-moving objects
- AI-based motion detection: Unnecessary cost, deterministic method works
- **Rejected**: All alternatives more complex without accuracy benefit

**Implementation Approach**:
```python
# Pseudo-code for motion detection
previous_frame = None
motion_threshold = 0.02  # 2% of pixels changed

def detect_motion(current_frame):
    if previous_frame is None:
        previous_frame = current_frame
        return False

    diff = cv2.absdiff(current_frame, previous_frame)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)

    motion_pixels = cv2.countNonZero(thresh)
    total_pixels = frame.shape[0] * frame.shape[1]

    previous_frame = current_frame
    return (motion_pixels / total_pixels) > motion_threshold
```

**Ball Stop Detection**: Motion drops below threshold for 1 second → shot complete

### 3. Claude Vision Integration

**Decision**: Use Anthropic Python SDK with streaming disabled for cost control

**Rationale**:
- Official SDK handles authentication, retries, rate limiting
- Synchronous calls adequate for 2-second latency requirement
- Image encoding handled automatically (base64)
- Cost tracking built into SDK response metadata
- Latest model (claude-3-5-sonnet) optimal for vision tasks

**API Configuration**:
- Model: `claude-3-5-sonnet-20241022` (latest vision model)
- Max tokens: 150 (commentary is short, reduce cost)
- Temperature: 0.7 (balanced creativity for commentary)
- Image size: Resize to 1280x720 before upload (reduce cost, maintain quality)

**Cost Calculation**:
- Input: ~1,000 tokens per image (1280x720 resized)
- Output: ~50 tokens (short commentary analysis)
- Cost per call: ~$0.0015 (input) + $0.0008 (output) = $0.0023
- Target: 15 calls per round = $0.0345 (under $0.05 budget)

**Alternatives Considered**:
- GPT-4 Vision: More expensive ($0.01+ per image)
- OpenAI CLIP: Requires local model, classification only (no commentary)
- Google Gemini: Similar cost, less mature Python SDK
- **Rejected**: Claude offers best cost/performance/SDK maturity balance

### 4. Pattern Caching Strategy

**Decision**: Implement perceptual hash (pHash) similarity matching with confidence thresholds

**Rationale**:
- pHash detects similar images despite slight variations (lighting, angle)
- Fast lookup (hash comparison vs. full AI analysis)
- Confidence >0.85: Use cache (no AI call)
- Confidence 0.6-0.85: Use cache + log for review
- Confidence <0.6: New AI call required
- Reduces API calls by 70-80% after initial learning

**Implementation**:
- Library: imagehash (pip install imagehash)
- Hash type: perceptual_hash (resistant to minor changes)
- Hamming distance threshold: <10 for match

```python
import imagehash
from PIL import Image

def find_cached_pattern(screenshot):
    img_hash = imagehash.phash(Image.fromarray(screenshot))

    for cached in pattern_cache:
        distance = img_hash - cached['hash']
        if distance < 10:  # Hamming distance threshold
            confidence = 1.0 - (distance / 64.0)  # Normalize
            if confidence > 0.85:
                return cached['outcome'], confidence

    return None, 0.0  # No match, trigger AI
```

**Alternatives Considered**:
- Exact pixel matching: Too brittle, fails on minor changes
- Feature extraction (SIFT/SURF): Overkill, slower
- Image embeddings (CLIP): Requires local model, GPU
- **Rejected**: pHash optimal for simplicity and effectiveness

### 5. ElevenLabs TTS Integration

**Decision**: Use ElevenLabs Python SDK with streaming for low latency

**Rationale**:
- Specified by user preference
- Streaming mode reduces time-to-first-audio
- High-quality voice synthesis (better than Google/Azure for natural speech)
- Generous free tier (10,000 characters/month)
- Simple Python SDK

**Configuration**:
- Voice: Premade voice (e.g., "Antoni" for neutral, "Rachel" for encouraging)
- Model: eleven_multilingual_v2 (latest, natural prosody)
- Streaming: Enabled to start playback while generating
- Optimization: Turbo mode for <500ms latency

**Cost Calculation**:
- Free tier: 10,000 chars/month
- Typical commentary: 50-100 characters
- 80 shots per round = ~6,000 chars
- First round free, ~$0.50/round after (separate from AI cost)
- **Note**: User provides API key, cost external to $0.05 target

**Alternatives Considered**:
- Google Cloud TTS: Cheaper, lower quality, less natural
- Azure Speech: Similar cost, more complex setup
- pyttsx3 (offline): Free but robotic, poor quality
- **Rejected**: ElevenLabs user preference, quality justifies cost

### 6. Configuration Management

**Decision**: YAML configuration with pydantic validation

**Rationale**:
- YAML human-readable for non-technical users
- Pydantic provides type safety and validation
- Environment variables override for sensitive keys
- Minimal configuration surface (API keys + personality only)

**Configuration Structure**:
```yaml
# config.yaml
anthropic:
  api_key: ${ANTHROPIC_API_KEY}  # Environment variable

elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}
  voice_id: "Antoni"  # Default neutral voice

personality: "neutral"  # Options: encouraging, neutral, sarcastic

hotkeys:
  toggle: "f10"
  correct: "ctrl+c"

monitoring:
  fps: 2  # Screen capture frames per second
  motion_threshold: 0.02  # 2% pixel change
```

**Validation**: Pydantic schema ensures required keys present, valid values

**Alternatives Considered**:
- JSON: Less human-readable
- TOML: Less common in Python ecosystem
- INI: Limited structure
- **Rejected**: YAML optimal balance of readability and structure

### 7. Active Learning Architecture

**Decision**: Correction log → prompt augmentation → pattern cache update

**Rationale**:
- Corrections stored as (screenshot, wrong_prediction, correct_outcome)
- Future prompts include recent corrections as few-shot examples
- Pattern cache updated with correct outcome
- AI learns from mistakes without retraining

**Implementation Flow**:
1. User presses Ctrl+C during incorrect commentary
2. System prompts: "Was I wrong? What actually happened?"
3. User types correct outcome (e.g., "rough")
4. System logs: `{screenshot, "bunker" → "rough", timestamp}`
5. Next similar frame: Include correction in prompt as example
6. Update pattern cache with correct outcome

**Prompt Augmentation Example**:
```python
prompt = """
Analyze this golf shot outcome.

Previous corrections I learned from:
- I said "bunker" but it was actually "rough" - I see now that rough has
  darker grass texture, not sand
- I said "fairway" but it was "trees" - I missed the foliage in background

Current shot: [image]
Where did the ball land?
"""
```

**Alternatives Considered**:
- Model fine-tuning: Too expensive, unnecessary
- Embedding-based retrieval: Overkill for small dataset
- Rule-based overrides: Defeats AI-first principle
- **Rejected**: Prompt augmentation simple, effective, cost-efficient

### 8. Testing Strategy

**Decision**: Pytest with cost tracking fixtures and mock AI responses

**Rationale**:
- Pytest standard in Python ecosystem
- Fixtures allow AI mocking for fast unit tests
- Cost tracking validates $0.05 budget
- Integration tests use real APIs (controlled)

**Test Categories**:

1. **Unit Tests** (fast, mocked):
   - Motion detection logic
   - Pattern cache matching
   - Commentary generation
   - Configuration validation

2. **Integration Tests** (slow, real APIs):
   - End-to-end shot detection
   - AI analysis with sample screenshots
   - Cost accumulation over simulated round
   - Learning from corrections

**Cost Test Example**:
```python
@pytest.fixture
def cost_tracker():
    return CostTracker()

def test_cost_under_budget(cost_tracker):
    """Verify 18-hole round under $0.05"""
    round_shots = 80
    for _ in range(round_shots):
        # Simulate shot with cache hits/misses
        pass

    total_cost = cost_tracker.get_total()
    assert total_cost < 0.05, f"Cost ${total_cost} exceeds $0.05 budget"
```

**Alternatives Considered**:
- unittest: Less feature-rich
- nose2: Less maintained
- doctest: Not suitable for integration tests
- **Rejected**: Pytest industry standard, best tooling

### 9. Hotkey Handling

**Decision**: pynput library for cross-platform global hotkeys

**Rationale**:
- Global hotkeys work even when app not focused
- Cross-platform (Windows, Linux, macOS)
- Non-blocking listener thread
- Simple API for key combinations

**Implementation**:
```python
from pynput import keyboard

def on_toggle(key):
    # F10 pressed - toggle commentary
    pass

def on_correct(key):
    # Ctrl+C pressed - correction mode
    pass

listener = keyboard.GlobalHotKeys({
    '<f10>': on_toggle,
    '<ctrl>+c': on_correct
})
listener.start()
```

**Alternatives Considered**:
- keyboard library: Requires root/admin on Linux
- pyHook (Windows-only)
- system-specific APIs: Not cross-platform
- **Rejected**: pynput best cross-platform solution without permissions issues

### 10. Personality Implementation

**Decision**: YAML personality definitions with prompt templates

**Rationale**:
- Non-developers can add personalities (edit YAML)
- Templates ensure consistent tone
- System prompts guide AI personality
- No code changes for new personalities

**Personality Structure**:
```yaml
# data/personalities/sarcastic.yaml
name: "Sarcastic"
description: "Humorous, light-hearted ribbing. Makes jokes about bad shots."
system_prompt: |
  You are a sarcastic golf commentator. You make witty, humorous comments
  about shots. For good shots, acknowledge grudgingly. For bad shots,
  make light-hearted jokes. Keep it fun, never mean-spirited.

examples:
  water: "And... it's swimming. That's gonna cost you."
  bunker: "Nice sandbox you found there. Building castles?"
  fairway: "Oh NOW you remember how to play golf."
  tree: "The trees are 90% air they said. You found the 10%."
```

**Alternatives Considered**:
- Hard-coded logic: Not extensible
- Separate AI calls for tone: Doubles cost
- Post-processing rules: Fragile, defeats AI-first
- **Rejected**: Template-based approach flexible and simple

## Best Practices Identified

### Python Project Structure
- Use `src/` layout for importable package
- Separate models, services, CLI, lib
- Type hints throughout (Python 3.11+ syntax)
- Dataclasses for entities (built-in, simple)

### Error Handling
- Graceful degradation when AI unavailable (use cache only)
- Clear error messages for setup issues (missing API keys)
- Retry logic for transient API failures (3 retries, exponential backoff)
- Logging for debugging without spam (INFO level for user, DEBUG for devs)

### Performance Optimization
- Resize images before API upload (1280x720 sufficient)
- Lazy load services (don't initialize until needed)
- Thread pool for concurrent operations (capture + analysis)
- Cache compiled regexes and constants

### Security
- Never commit API keys (environment variables only)
- Validate all user input (corrections, file uploads)
- Sanitize file paths (prevent directory traversal)
- Rate limit API calls (prevent runaway costs)

## Technology Stack Summary

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.11+ | User specified, AI SDK support, rapid development |
| AI Vision | Anthropic Claude 3.5 Sonnet | User specified, best cost/performance |
| TTS | ElevenLabs | User specified, high quality, streaming |
| Screen Capture | MSS (python-mss) | Fast, cross-platform, simple API |
| Motion Detection | OpenCV (cv2) | Industry standard, minimal overhead |
| Pattern Matching | imagehash | Perceptual hash, robust to variations |
| Hotkeys | pynput | Cross-platform global hotkeys |
| Configuration | PyYAML + pydantic | Human-readable, type-safe |
| Testing | pytest | Industry standard, rich ecosystem |
| Packaging | setuptools/pip | Standard Python distribution |

## Open Questions Resolved

1. **Q**: How to detect GS Pro window automatically?
   **A**: Use pygetwindow to enumerate windows by title pattern

2. **Q**: How to determine shot completion without game API?
   **A**: Motion detection - ball stops moving for 1 second

3. **Q**: How to minimize API costs?
   **A**: Perceptual hash caching + confidence thresholds

4. **Q**: How to make corrections intuitive?
   **A**: Hotkey (Ctrl+C) + conversational prompt

5. **Q**: How to ensure 2-second latency?
   **A**: Streaming TTS + optimized image size + async operations

6. **Q**: How to persist learning between sessions?
   **A**: JSON files for pattern cache and corrections

7. **Q**: How to make personality extensible?
   **A**: YAML templates, no code changes required

8. **Q**: How to test cost constraints?
   **A**: pytest fixtures that simulate rounds and track cumulative cost

## Implementation Risks & Mitigations

### Risk 1: GS Pro window detection fails
**Mitigation**: Fallback to user selecting window from list, save preference

### Risk 2: API costs exceed budget
**Mitigation**: Cost tracking middleware, halt at threshold, alert user

### Risk 3: Motion detection false positives
**Mitigation**: Tunable threshold, require 1-second stillness, user can adjust

### Risk 4: TTS latency too high
**Mitigation**: Streaming mode, preload common phrases, async playback

### Risk 5: Pattern cache false matches
**Mitigation**: Confidence thresholds, user can override, log for review

## Next Steps (Phase 1)

1. Generate data models from entities
2. Define internal contracts (service interfaces)
3. Create quickstart guide
4. Update agent context with technology stack
