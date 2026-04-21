# Mully Mouth Golf Caddy v3.1.0

AI-powered golf shot narration for GS Pro simulator using Claude Vision and xAI Grok TTS.

## Features

- **Windows System Tray UI**: User-friendly interface with no command line needed - just double-click to start
- **Manual Start/Stop Control**: Monitoring is OFF by default - you decide when to start
- **Automatic Shot Detection**: Uses motion detection to identify when shots are complete
- **AI Shot Analysis**: Claude Vision API analyzes screenshots to determine shot outcomes
- **Score Achievement Detection**: Recognizes and celebrates Birdies, Eagles, Pars, etc.
- **Player Name Recognition**: Extracts and mentions player names in commentary
- **Multiple Personalities**: Choose from Neutral, Sarcastic, Encouraging, or Jerk commentary styles
- **Voice Narration**: Natural speech synthesis using xAI Grok TTS (~$0.35/round)
- **Personality-Specific Voices**: Each personality has its own mapped Grok voice (leo/rex/ara/eve/sal)
- **Live Settings Adjustment**: Change commentary frequency, name frequency, and personality without restarting
- **Cost Optimization**: Pattern cache reduces AI API calls by 70-80%
- **Learning System**: Train AI with custom screenshots for improved accuracy

## Quick Start

### Prerequisites

- **Python 3.11, 3.12, or 3.13** (Python 3.12 recommended for best compatibility)
- GS Pro golf simulator
- Anthropic API key (Claude) — [console.anthropic.com](https://console.anthropic.com/)
- xAI API key (Grok TTS) — [console.x.ai](https://console.x.ai/)

### Installation

**Simple 3-Step Install:**

1. **Install Dependencies** - Double-click `install.bat`
   - Automatically creates a virtual environment
   - Installs all required packages
   - Checks Python version compatibility

2. **Configure API Keys** - Double-click `setup_credentials.bat`
   - Securely stores your Anthropic and xAI API keys
   - Uses Windows Credential Manager (encrypted)
   - Never saves keys in plain text files

3. **Run Application** - Double-click `mully-mouth.bat`
   - Launches the system tray application
   - Look for the gray "M" icon in your system tray

**For detailed installation instructions, troubleshooting, and manual setup, see [INSTALL.md](INSTALL.md)**

**Alternative Credential Methods:**
- **Environment Variables**: Set `ANTHROPIC_API_KEY` and `XAI_API_KEY` in Windows System Environment Variables
- **Config File**: Copy `config/config.yaml.template` to `config/config.yaml` and edit (not recommended for public repos)

### Usage

#### Recommended: System Tray Application

1. **Start GS Pro** and make your video fullscreen
2. **Double-click `mully-mouth.bat`** to launch the system tray app
3. Look for the **GRAY "M" icon** in your system tray (bottom-right corner)
4. **Right-click the icon** and select **"Start Monitoring"** to begin
5. Play golf - commentary will be generated automatically!

**System Tray Features:**
- **Start/Stop Monitoring**: Click to begin or pause commentary
- **Change Personality**: Switch between Neutral, Sarcastic, Encouraging, or Jerk on the fly
- **Adjust Settings**:
  - **Commentary Frequency** (0%-100%): How often to generate commentary
  - **Name Frequency** (0%-100%): How often to mention player names
- **Session Stats**: View shots, costs, cache hit rate, and accuracy
- **Open Config File**: Quick access to configuration

**Note**: The app starts in **stopped mode** by default - you control when monitoring begins.

**See [SYSTEM_TRAY_GUIDE.md](SYSTEM_TRAY_GUIDE.md) for detailed screenshots and instructions.**

#### Alternative: Command Line

1. Start GS Pro
2. Run Mully Mouth:
```bash
python -m src.cli.main
```

**Command-Line Options:**
```bash
# Use a specific personality
python -m src.cli.main --personality sarcastic

# List available personalities
python -m src.cli.main --list-personalities

# Use a custom config file
python -m src.cli.main --config path/to/config.yaml
```

### Available Personalities

- **Neutral**: Professional, informative commentary
- **Sarcastic**: Humorous, light-hearted ribbing with witty remarks
- **Encouraging**: Supportive, motivational, always positive
- **Jerk**: Brutally honest, snarky, and harsh (for those who like a challenge!)

Each personality has a pre-mapped Grok voice — see [VOICE_CONFIGURATION_GUIDE.md](VOICE_CONFIGURATION_GUIDE.md) for details and customization.

## Configuration

Most settings can be adjusted directly from the **system tray menu** without editing files:
- Commentary frequency (0%-100% in 10% increments)
- Name frequency (0%-100% in 10% increments)
- Personality selection

For advanced configuration, edit `config/config.yaml`:
- AI models (Claude Sonnet, Haiku, etc.)
- Motion detection sensitivity
- Cache settings
- Voice per personality (voice_id: leo/rex/ara/eve/sal)
- Cost limits and warnings
- Monitoring FPS and thresholds

**Note**: Settings changed via the system tray are saved immediately to `config.yaml`.

## Cost Estimates

- AI shot analysis: ~$0.002-0.004 per shot
- Commentary generation: ~$0.0016 per shot
- Voice synthesis (Grok TTS): ~$0.0008 per shot
- **Total per round (18 holes, ~80 shots, full settings)**: ~$0.35

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
6. **VoiceService**: Converts commentary to speech via xAI Grok TTS
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

### System tray icon doesn't appear
- Check Windows system tray overflow area (click the ^ arrow)
- Make sure Python and dependencies are installed correctly
- Try running `python -m src.cli.tray_app` directly to see any error messages

### GS Pro window not found
- Ensure GS Pro is running and visible
- Make your GS Pro video **fullscreen** for best capture
- The app captures the primary monitor - ensure GS Pro is on your main display

### API key errors when launching
- Run `python setup_wizard.py` to configure API keys securely
- Or set environment variables: `ANTHROPIC_API_KEY` and `XAI_API_KEY`
- Verify keys are valid at console.anthropic.com and console.x.ai

### Stop Monitoring doesn't stop commentary
- The system waits for any in-progress shot to complete (up to 10 seconds)
- If commentary is playing, it will finish before stopping completely

### Commentary frequency changes don't work
- Make sure you've selected a checkmark next to one of the frequency options
- The selected frequency should show a ✓ checkmark
- Changes apply immediately without restarting

### Motion detection too sensitive/not sensitive enough
- Adjust `monitoring.motion_threshold` in `config/config.yaml` (default: 0.02)
- Lower values = more sensitive, higher values = less sensitive
- Adjust `monitoring.ball_stop_duration` for how long the ball must be still (default: 1.0 second)

### Config file corruption
- If you see YAML errors, the config may have been corrupted
- Copy `config/config.yaml.template` to `config/config.yaml` and reconfigure
- Never edit the config file while the app is running

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or pull request.

## Acknowledgments

- Built with Claude (Anthropic)
- Voice synthesis by xAI Grok TTS
- Screen capture via MSS library
- Motion detection using OpenCV
