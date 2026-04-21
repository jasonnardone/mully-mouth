# Implementation Plan: AI Voice Caddy for GS Pro

**Branch**: `001-golf-narration` | **Created**: 2025-11-19 | **Last Updated**: 2026-04-21
**Spec**: [spec.md](spec.md)

## Summary

Real-time golf commentary system for GS Pro simulator. Captures the screen, detects shots via motion analysis, classifies the outcome in a single Claude Haiku API call, and delivers personality-driven voice commentary via Grok TTS. Runs as a Windows system tray application targeting non-technical users on gaming PCs.

**Current Status**: Fully implemented and operational. This document reflects the as-built architecture.

---

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies** (as-built):
| Package | Purpose |
|---|---|
| `anthropic` | Claude Haiku Vision API (shot analysis) |
| `openai` | xAI Grok TTS (OpenAI-compatible client pointing to `api.x.ai`) |
| `httpx` | Direct POST to xAI `/v1/tts` endpoint |
| `pygame` | Audio playback of TTS MP3 output |
| `opencv-python` (cv2) | Motion detection, frame differencing, histogram comparison |
| `mss` | Fast screen capture |
| `pygetwindow` | Window detection |
| `pystray` | Windows system tray icon and menu |
| `keyring` | Windows Credential Manager API key storage |
| `pyyaml` | Personality and config file parsing |
| `imagehash` (PIL) | Perceptual hashing for pattern cache |
| `Pillow` | Image encoding and resizing |
| `numpy` | Frame array operations |
| `pytest` | Test suite |

**Removed Dependencies** (migrated away from):
- `elevenlabs` — replaced by xAI Grok TTS (94% cost reduction)
- `pyaudio` — replaced by pygame for audio playback

**Storage**: Local filesystem
- `config/config.yaml` — non-secret settings (personality, frequency, model, monitoring params)
- Windows Credential Manager — API keys (never in files)
- `data/personalities/*.yaml` — personality definitions
- `data/training/images/<outcome>/` — training screenshots per outcome type
- `data/cache/pattern_cache.json` — perceptual hash cache
- `data/sessions/*.json` — session history

**Target Platform**: Windows 10/11 (gaming PC, non-technical user)
**Primary UI**: Windows system tray icon (no terminal visible during normal use)
**Testing**: pytest for unit and integration tests

---

## Architecture

### Pipeline

```
Screen Capture (MSS, 2 FPS)
    │
    ▼
Screen Classifier (OpenCV histogram vs training images) ──► IDLE → reset motion detector, skip
    │ GAMEPLAY
    ▼
Motion Detector (OpenCV frame diff, vertical-motion filter)
    │ Motion detected → ball stopped (1s stillness)
    ▼
Pattern Cache (perceptual hash lookup)
    │ CACHE HIT → use cached outcome, skip AI
    │ CACHE MISS
    ▼
Claude Haiku (SINGLE unified API call)
    ├── is_idle: bool
    ├── player_name: str | null
    ├── achievement: str | null  (BIRDIE, EAGLE, PAR, etc.)
    ├── outcome: fairway/green/water/bunker/rough/trees/ob/tee_shot/unknown
    └── confidence: float
    │
    ▼
Commentary Decision (rolls against commentary_frequency %)
    │ Triggered
    ▼
Commentary Generator (Claude Haiku + personality YAML)
    │
    ▼
Grok TTS (xAI /v1/tts → MP3 → pygame playback)
```

### Key Design Decisions

**Unified API call**: All per-shot analysis (idle check, player name, achievement, outcome) combined into one Claude Haiku call returning JSON. Reduces from 4-5 calls to 1-2 per shot, cutting costs 80-90%.

**Pre-flight screen classifier**: Runs entirely in OpenCV using HSV histogram correlation against training images. Fires on every frame at ~1ms cost, zero API calls. Prevents motion detection from arming when the screen is a menu, setup screen, or unrelated application.

**Cache before AI**: Pattern cache is checked before any AI call. Cache hits are free — no API cost at all for repeat shot types.

**Commentary frequency**: Only a configurable percentage (default 20%) of detected shots trigger commentary generation. The other shots are analyzed but silent.

**Commentary length constraint**: All personality prompts instruct the AI to keep commentary under 80 characters (hard limit: 150). Short commentary = lower Grok TTS cost.

---

## Project Structure (as-built)

```
src/
  services/
    screen_capture.py       # MSS screen capture, monitor selection
    motion_detector.py      # OpenCV frame diff, vertical-motion filter
    screen_classifier.py    # Pre-flight HSV histogram classifier (NEW)
    ai_analyzer.py          # Claude Haiku unified analysis
    pattern_cache.py        # Perceptual hash cache
    commentary_generator.py # Personality-driven commentary generation
    voice_service.py        # Grok TTS via xAI API + pygame playback
    learning_service.py     # Few-shot examples, user corrections
    session_service.py      # Session persistence
  models/
    outcome.py              # Outcome enum
    shot_event.py           # Shot event dataclass
    session.py              # Session dataclass
    correction.py           # User correction dataclass
  cli/
    tray_app.py             # System tray icon and menu (PRIMARY ENTRY POINT)
    monitor.py              # Core monitoring orchestrator
    main.py                 # CLI entry point (secondary)
  lib/
    config.py               # Config loading (keyring → env → yaml priority)
    credentials.py          # Windows Credential Manager via keyring
    exceptions.py           # Service-specific exceptions
    utils.py                # UUID, timestamps, file I/O

config/
  config.yaml               # Non-secret settings (no API keys)
  config.yaml.template      # Template for fresh installs

data/
  personalities/            # 7 YAML personality definitions
    neutral.yaml
    sarcastic.yaml
    encouraging.yaml
    jerk.yaml
    documentary.yaml        # Sir David Attenborough style
    ex-girlfriend.yaml
    unhinged.yaml
  training/
    images/
      fairway/              # Training screenshots per outcome
      green/
      bunker/
      rough/
      trees/
      out_of_bounds/
      water/
      idle/                 # Menu/setup screens for screen classifier
    few_shot_examples.json
  cache/
    pattern_cache.json
  sessions/
    *.json

install.bat                 # One-click dependency installer
mully-mouth.bat             # Launcher (uses venv, no terminal visible)
setup_wizard.py             # First-run API key setup (stores to Credential Manager)
setup_credentials.bat       # Credential update wrapper
```

---

## Personality System (as-built)

| Personality | Voice | Character |
|---|---|---|
| Neutral | leo | Professional broadcaster |
| Sarcastic | eve | Witty, light ribbing |
| Encouraging | ara | Warm, supportive |
| Jerk | rex | Profane, trash-talking |
| Sir David (documentary) | leo | Nature documentary narrator |
| Ex-Girlfriend | eve | Unhinged, possessive ex |
| Unhinged | sal | Psychotic conspiracy theorist |

**Grok TTS expression tags** (used sparingly, mapped in system prompts):
- Inline: `[laugh]` `[chuckle]` `[sigh]` `[tsk]` `[breath]` `[exhale]`
- Wrapping: `<whisper>` `<loud>` `<slow>` `<emphasis>` `<soft>`

Each personality file specifies which tags to use and when (e.g., documentary uses `<whisper>` every ~3 phrases; jerk uses `[laugh]` only on spectacular failures).

---

## Cost Model (as-built)

| Component | Cost |
|---|---|
| Claude Haiku analysis (per shot, cache miss) | ~$0.0003 |
| Claude Haiku commentary (per triggered shot) | ~$0.0002 |
| Grok TTS (per commentary, ~70 chars avg) | ~$0.0003 |
| **Per round (80 shots, 20% freq, 70% cache hit)** | **~$0.10–0.40** |

Previous cost (ElevenLabs + Claude Sonnet, 4 calls/shot): ~$6–7/round. Current architecture is ~94% cheaper.

---

## API Key Priority Order

`load_config()` resolves API keys in this order:
1. Windows Credential Manager (via `keyring`) — always preferred
2. Environment variables (`ANTHROPIC_API_KEY`, `XAI_API_KEY`)
3. Config file fallback (for dev only; keys should never be committed)

---

## Screen Classifier Calibration

The `ScreenClassifier` builds averaged HSV hue/saturation histograms from all images in `data/training/images/` at startup. The gameplay vs idle decision uses:

```
is_gameplay = gameplay_correlation > idle_correlation + 0.15
```

The 0.15 bias was calibrated against the training set:
- Minimum gameplay gap: 0.206 (all 19 gameplay training images pass)
- Maximum idle gap: 0.090 (all 6 idle training images block)

Adding more training images in any category automatically improves the classifier on next restart — no code changes needed.

---

## Constitution Check

### I. AI-First Development ✅

- Shot outcome detection: Claude Haiku Vision (not rule-based)
- Commentary generation: Claude Haiku with personality prompts
- Motion detection and screen classification: OpenCV (appropriate — cheap, deterministic, not AI-suitable tasks)

### II. Natural Interaction Over Configuration ✅

- API keys: entered once in GUI wizard, stored in Credential Manager
- Personality: selected from tray menu, no config file editing
- Training: drop screenshots into folders, restart classifier
- No pixel coordinates, thresholds, or technical flags exposed to users

### III. Learning-Driven Systems ✅

- Zero-shot capability maintained (60%+ accuracy without training)
- Pattern cache grows from real gameplay
- Few-shot examples from `data/training/` improve AI accuracy
- User corrections via tray menu feed back into the learning pipeline

### IV. Cost-Conscious Intelligence ✅

- Pre-flight classifier gates every frame in ~1ms (zero API cost)
- Motion detection filters 99%+ of frames before any analysis
- Pattern cache skips AI entirely on repeat shots
- Unified API call: 4 analysis tasks → 1 call
- Haiku model (20x cheaper than Sonnet) used for all automated tasks
- Commentary frequency default 20% reduces TTS costs further

### V. Simplicity & User Experience ✅

- One-click install (install.bat)
- No terminal visible during normal use
- System tray is the only UI surface
- Setup wizard handles all first-run configuration
- Non-technical target audience: Windows gaming PC users
