# Mully Mouth Golf Caddy v3.0.0

AI-powered golf shot narration for GS Pro simulator using Claude Vision and ElevenLabs text-to-speech.

## Features

- **Automatic Shot Detection**: Uses motion detection to identify when shots are complete
- **AI Shot Analysis**: Claude Vision API analyzes screenshots to determine shot outcomes
- **Personality-Driven Commentary**: Multiple commentary personalities (neutral, sarcastic, encouraging)
- **Voice Narration**: Natural speech synthesis using ElevenLabs
- **Cost Optimization**: Pattern cache reduces AI API calls by 70-80%
- **Learning System**: User corrections improve future accuracy

## Quick Start

### Prerequisites

- Python 3.11 or higher
- GS Pro golf simulator
- Anthropic API key (Claude)
- ElevenLabs API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mully-mouth.git
cd mully-mouth
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the setup wizard (recommended):
```bash
python setup_wizard.py
```

The wizard will guide you through:
- Entering API keys
- Choosing a commentary personality
- Configuring voice settings
- Adjusting motion detection

**Alternative: Manual Configuration**

Copy the template and edit manually:
```bash
cp config/config.yaml.template config/config.yaml
```

Edit `config/config.yaml` and add your API keys:
```yaml
anthropic:
  api_key: ${ANTHROPIC_API_KEY}

elevenlabs:
  api_key: ${ELEVENLABS_API_KEY}
```

Or set environment variables:
```bash
export ANTHROPIC_API_KEY="your-key-here"
export ELEVENLABS_API_KEY="your-key-here"
```

### Usage

1. Start GS Pro

2. Run Mully Mouth:
```bash
python -m src.cli.main
```

3. Play golf in GS Pro - commentary will be generated automatically

### Command-Line Options

```bash
# Use a specific personality
python -m src.cli.main --personality sarcastic

# List available personalities
python -m src.cli.main --list-personalities

# Use a custom config file
python -m src.cli.main --config path/to/config.yaml
```

### Available Personalities

- **neutral**: Professional, informative commentary
- **sarcastic**: Humorous, light-hearted ribbing
- **encouraging**: Supportive, motivational commentary

## Configuration

Edit `config/config.yaml` to customize:

- API keys and models
- Commentary personality
- Motion detection sensitivity
- Cache settings
- Voice settings (voice ID, stability, similarity)
- Cost limits

## Cost Estimates

- AI shot analysis: ~$0.002-0.004 per shot
- Commentary generation: ~$0.0008 per shot
- Voice synthesis: ~$0.01-0.02 per shot
- **Total per round (18 holes, ~70 shots)**: ~$1.00-2.00

Pattern caching reduces AI costs by 70-80% for similar shots.

## Project Structure

```
mully-mouth/
├── src/
│   ├── models/          # Data models (Session, ShotEvent, Outcome)
│   ├── services/        # Core services (AI, Voice, Cache, etc.)
│   ├── cli/             # CLI interface and monitoring
│   └── lib/             # Utilities and configuration
├── config/              # Configuration files
├── data/
│   ├── personalities/   # Personality YAML files
│   ├── cache/           # Pattern cache storage
│   ├── sessions/        # Session history
│   └── training/        # Few-shot examples
└── tests/               # Unit and integration tests
```

## Architecture

The system follows a service-oriented architecture:

1. **ScreenCaptureService**: Monitors GS Pro window using MSS
2. **MotionDetectorService**: Detects shot completion via OpenCV frame differencing
3. **PatternCacheService**: Caches screenshot patterns using perceptual hashing
4. **AIAnalyzerService**: Analyzes shots using Claude Vision API
5. **CommentaryGeneratorService**: Generates personality-driven commentary
6. **VoiceService**: Converts commentary to speech via ElevenLabs
7. **Monitor**: Orchestrates all services in main loop

## Development

### Running Tests

```bash
pytest tests/
```

### Adding a New Personality

1. Create a YAML file in `data/personalities/`:
```yaml
name: "My Personality"
description: "Description here"
tone: "tone_type"
system_prompt: |
  Your system prompt here...

example_phrases:
  fairway:
    - "Example phrase 1"
    - "Example phrase 2"
  water:
    - "Example phrase 1"
```

2. Use with `--personality my_personality`

## Troubleshooting

### GS Pro window not found
- Ensure GS Pro is running
- Check that "GS Pro" appears in the window title

### No API key errors
- Set environment variables or edit `config/config.yaml`
- Verify keys are valid

### Motion detection too sensitive/not sensitive enough
- Adjust `monitoring.motion_threshold` in config (default: 0.02)
- Lower values = more sensitive

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or pull request.

## Acknowledgments

- Built with Claude (Anthropic)
- Voice synthesis by ElevenLabs
- Screen capture via MSS library
- Motion detection using OpenCV
