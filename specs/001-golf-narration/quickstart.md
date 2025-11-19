# Quickstart Guide: AI Voice Caddy for GS Pro

**Target Audience**: Developers implementing the AI Voice Caddy
**Purpose**: Get a development environment running and test core functionality

## Prerequisites

- Python 3.11 or higher
- Windows 10/11 (primary platform)
- GS Pro golf simulator installed (for testing)
- Anthropic API key (Claude)
- ElevenLabs API key (TTS)
- Git

## Quick Setup (5 minutes)

### 1. Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd mully-mouth

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Create `config/config.yaml`:

```yaml
anthropic:
  api_key: ${ANTHROPIC_API_KEY}

elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}
  voice_id: "Antoni"

personality: "neutral"

hotkeys:
  toggle: "f10"
  correct: "ctrl+c"

monitoring:
  fps: 2
  motion_threshold: 0.02
```

Set environment variables:

```bash
# Windows
set ANTHROPIC_API_KEY=your-key-here
set ELEVENLABS_API_KEY=your-key-here

# Linux/Mac
export ANTHROPIC_API_KEY=your-key-here
export ELEVENLABS_API_KEY=your-key-here
```

### 3. Verify Installation

```bash
# Run setup wizard
python -m src.cli.setup

# Expected output:
# ✓ Anthropic API key valid
# ✓ ElevenLabs API key valid
# ✓ Configuration saved
# Ready to start!
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests (requires API keys)
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

### Testing Individual Components

#### 1. Screen Capture

```bash
python -m src.cli.test_capture
```

Expected behavior:
- Lists available windows
- Detects GS Pro window
- Captures screenshot
- Displays capture (if GUI available)

#### 2. Motion Detection

```bash
# Launch GS Pro, then:
python -m src.cli.test_motion
```

Expected behavior:
- Monitors GS Pro window
- Prints "Motion detected" when ball moves
- Prints "Shot complete" when ball stops
- Press Ctrl+C to exit

#### 3. AI Analysis

```bash
# Analyze a sample screenshot
python -m src.cli.test_ai samples/water_shot.png
```

Expected output:
```
Analyzing shot...
Outcome: water
Confidence: 0.92
Commentary: "That's in the water. Gonna need a penalty stroke."
API Cost: $0.0023
```

#### 4. Pattern Cache

```bash
python -m src.cli.test_cache
```

Expected behavior:
- Load existing cache
- Test hash matching
- Display cache statistics
- Add test pattern
- Verify persistence

#### 5. Text-to-Speech

```bash
python -m src.cli.test_voice "Nice shot!"
```

Expected behavior:
- Speaks the text
- Uses configured voice
- Completes within 1 second

### Running the Full Application

#### Setup Mode

```bash
python -m src.cli.setup
```

Walkthrough:
1. Welcome screen
2. API key validation
3. Personality selection
4. GS Pro window detection
5. Confirmation

#### Training Mode

```bash
python -m src.cli.train
```

Usage:
1. Upload screenshot (drag & drop or path)
2. Label outcome type
3. Repeat for 3-5 examples per outcome
4. Exit when satisfied

#### Monitor Mode (Live Commentary)

```bash
python -m src.cli.main
```

Expected flow:
1. Detects GS Pro window
2. Begins monitoring
3. Detects shots automatically
4. Provides commentary via TTS
5. Logs session statistics

Hotkeys:
- **F10**: Toggle commentary on/off
- **Ctrl+C**: Correct last prediction
- **Ctrl+Q**: Quit

## Development Tips

### Adding a New Personality

1. Create `data/personalities/my-personality.yaml`:

```yaml
name: "My Personality"
description: "Custom commentary style"
tone: "custom"
system_prompt: |
  You are a [describe personality] golf commentator.
  [Provide guidance for tone, style, examples]

example_phrases:
  water:
    - "Custom water commentary"
  bunker:
    - "Custom bunker commentary"
  # ... more outcomes
```

2. Test:

```bash
python -m src.cli.main --personality my-personality
```

### Adjusting Motion Detection

Edit `config/config.yaml`:

```yaml
monitoring:
  fps: 2  # Higher = more sensitive (but more CPU)
  motion_threshold: 0.02  # Lower = more sensitive
  ball_stop_duration: 1.0  # Seconds of stillness
```

### Cost Tracking

View session cost:

```bash
python -m src.cli.stats --session-id <session-id>
```

Output:
```
Session: abc-123
Shots: 82
API Calls: 18
Cache Hits: 64 (78%)
Total Cost: $0.041
Accuracy: 88%
```

### Debugging

Enable debug logging:

```bash
# Set environment variable
export MULLY_MOUTH_DEBUG=1

# Or edit config/config.yaml
logging:
  level: DEBUG
  file: logs/debug.log
```

View logs:
```bash
tail -f logs/debug.log
```

## Common Tasks

### Reset Pattern Cache

```bash
python -m src.cli.cache --clear
```

Confirmation required. This removes all learned patterns.

### Export Session Data

```bash
python -m src.cli.export --session-id <id> --format json
```

Outputs: `exports/session-<id>.json`

### View Training Examples

```bash
python -m src.cli.train --list
```

Output:
```
Training Examples:
1. water (5 examples, 78% cache hit rate)
2. bunker (3 examples, 65% cache hit rate)
3. rough (4 examples, 82% cache hit rate)
...
```

### Benchmark Performance

```bash
python -m src.cli.benchmark
```

Tests:
- Screen capture FPS
- Motion detection latency
- AI analysis latency
- TTS latency
- End-to-end pipeline latency

Expected output:
```
Benchmark Results:
- Screen Capture: 45ms avg (22 FPS)
- Motion Detection: 8ms avg
- AI Analysis: 1,234ms avg
- TTS Initiation: 156ms avg
- Total Pipeline: 1,892ms avg ✓ (target: <2000ms)
```

## Troubleshooting

### Issue: GS Pro window not detected

**Solution**:
1. Verify GS Pro is running
2. Check window title matches pattern
3. Try manual selection:
   ```bash
   python -m src.cli.main --select-window
   ```

### Issue: API key invalid

**Solution**:
1. Verify environment variable set:
   ```bash
   echo $ANTHROPIC_API_KEY
   ```
2. Test key directly:
   ```bash
   python -m src.cli.test_api --anthropic
   ```
3. Check for extra spaces/quotes

### Issue: Motion detection too sensitive

**Solution**:
Increase `motion_threshold` in config:
```yaml
monitoring:
  motion_threshold: 0.05  # Higher = less sensitive
```

### Issue: Commentary too slow

**Solution**:
1. Check internet connection (API latency)
2. Enable streaming TTS (already default)
3. Reduce image size (edit `ai_analyzer.py`):
   ```python
   TARGET_SIZE = (960, 540)  # From (1280, 720)
   ```

### Issue: Cost exceeds budget

**Solution**:
1. Check cache hit rate:
   ```bash
   python -m src.cli.stats
   ```
2. If low, add more training examples
3. Increase cache confidence threshold:
   ```python
   CACHE_CONFIDENCE_THRESHOLD = 0.75  # From 0.85
   ```

### Issue: Corrections not improving accuracy

**Solution**:
1. Verify corrections saved:
   ```bash
   python -m src.cli.corrections --list
   ```
2. Check few-shot prompt includes corrections:
   ```bash
   python -m src.cli.test_ai --debug samples/water.png
   ```
3. Ensure corrections added to training examples

## Next Steps

Once development environment is working:

1. **Run full integration test**:
   ```bash
   pytest tests/integration/test_end_to_end.py
   ```

2. **Play a test round**:
   - Launch GS Pro
   - Start monitor mode
   - Play 9 holes
   - Review session stats

3. **Validate cost target**:
   ```bash
   python -m src.cli.cost_analysis --simulate 18holes
   ```

4. **Check constitution compliance**:
   - Zero configuration? ✓
   - <10 minute setup? ✓
   - <$0.05 per round? ✓
   - 60% zero-shot accuracy? (test)
   - Learning from corrections? (test)

## Development Checklist

Before considering MVP complete:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Cost per 18-hole round <$0.05
- [ ] Setup wizard completes in <10 minutes
- [ ] Shot detection rate >90%
- [ ] Zero-shot accuracy >60%
- [ ] After-correction accuracy improves measurably
- [ ] Commentary delivered <2 seconds
- [ ] All three personalities distinguishable
- [ ] Hotkeys work as expected
- [ ] Application runs for 2+ hours without crash
- [ ] Documentation complete

## Resources

- **API Documentation**:
  - Anthropic: https://docs.anthropic.com/claude/docs
  - ElevenLabs: https://docs.elevenlabs.io/

- **Libraries**:
  - OpenCV: https://docs.opencv.org/
  - imagehash: https://github.com/JohannesBuchner/imagehash
  - pytest: https://docs.pytest.org/

- **Project Files**:
  - Constitution: `.specify/memory/constitution.md`
  - Spec: `specs/001-golf-narration/spec.md`
  - Data Model: `specs/001-golf-narration/data-model.md`
  - Service Contracts: `specs/001-golf-narration/contracts/`

## Support

For questions or issues during development:
1. Check existing tests for usage examples
2. Review service interfaces in `contracts/`
3. Consult constitution for architectural decisions
4. Create issue in project repository
