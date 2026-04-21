# Mully Mouth Development Guidelines

AI-powered golf shot commentary for GSPro simulator.
Last updated: 2026-04-21

## Project Overview

Real-time golf commentary system using Claude Vision for shot analysis and Grok TTS
for voice synthesis. Runs as a Windows system tray app alongside GSPro simulator.
Target users: small friend group, non-technical, one-click install required.

## Active Technologies

- Python 3.11+
- Claude Vision API (shot analysis)
- Grok TTS API (voice synthesis) — xAI, $4.20/M characters
- OpenCV (motion detection)
- MSS (screen capture)
- pystray (system tray)
- keyring (Windows Credential Manager for API keys)

## Project Structure

    src/
      services/        # AI, Voice, Cache, Motion detection
      models/          # Data models
      cli/             # Tray app and CLI entry points
      lib/             # Config and utilities
    config/
    data/
      personalities/   # YAML personality definitions
      cache/           # Pattern cache
    tests/

## Commands

    pytest tests/
    ruff check .
    python -m src.cli.tray_app     # launch system tray app
    python setup_wizard.py         # first-run API key setup

## Cost Optimization Principles

This project runs on a small usage budget. Cost awareness is a first-class concern
in all suggestions. Follow these rules in every recommendation.

### API Model Selection

- Use claude-haiku for shot analysis unless the task genuinely requires
  Sonnet-level reasoning. Haiku is ~20x cheaper and fast enough for real-time use.
- Never suggest claude-opus for any automated or looping task. Reserve for
  one-off complex reasoning only.
- Grok TTS is billed per character. Shorter commentary = lower cost. Always
  optimize for brevity in personality prompts and generated responses.

### Commentary Length

- Target: 50-80 characters per commentary instance
- Hard limit: 150 characters maximum
- Avoid multi-sentence responses, scene-setting preamble, lengthy reactions
- Good example: "Into the water again. Classic." (32 chars)
- Bad example: "Oh no, it looks like that shot has found the water hazard on the
  left side of the fairway. Better luck on the next one!" (121 chars)

### Caching

- Pattern cache is critical — always preserve and extend caching logic
- Never suggest changes that would bypass or reduce cache hit rate
- Similar shots should reuse cached commentary, not generate new API calls
- Target: 70-80% cache hit rate per session

### API Call Reduction

- Motion detection gates all screen captures — never suggest polling approaches
- Image hashing before API calls prevents duplicate analysis
- Commentary frequency is user-controlled (default 20%) — respect this in all
  suggestions

## Grok TTS Speech Tags

Grok TTS supports inline expressive tags. Use these in personality prompts to
add character without adding characters to commentary length.

Inline tags: [laugh] [chuckle] [sigh] [tsk] [breath] [exhale]
Wrapping tags: <whisper>text</whisper> <loud>text</loud> <slow>text</slow>
               <emphasis>text</emphasis> <soft>text</soft>

Map tags to personality modes in system prompts, not in generated commentary text.

## Personality System

Personalities are defined in data/personalities/*.yaml. Each has:
- system_prompt: keeps commentary SHORT and in-character
- voice settings: Grok voice ID (ara, eve, leo, rex, sal)
- example_phrases: 50-80 char samples for few-shot guidance

When suggesting new personality prompts always include a character limit instruction:
"Keep all commentary under 80 characters. Punchy, not verbose."

## Windows Distribution Constraints

This app must install cleanly on a non-technical user's Windows gaming PC:
- No manual command line steps for end users
- API key entry via GUI wizard only (setup_wizard.py)
- All secrets stored in Windows Credential Manager via keyring
- System tray is the only UI — no terminal windows visible during use
- Git must be available for auto-update functionality
- No ffmpeg or other system-level media dependencies

## Code Style

- Python 3.11+, follow PEP 8
- Type hints on all public functions
- Fail silently on non-critical errors — commentary failure must never crash the app
- Background threads for all API calls — never block the main tray loop
- Config changes persist immediately to config.yaml

## What NOT to Suggest

- ffmpeg or other system-level media dependencies (not in the stack)
- Complex OCR or pixel-coordinate approaches (replaced by Claude Vision)
- Any solution requiring the user to edit config files manually
- Verbose logging that would fill disk during long sessions
- Synchronous API calls in the main thread
- Commentary longer than 150 characters
- Model upgrades that increase per-call cost without clear necessity
- Polling-based screen capture (motion detection handles this)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->