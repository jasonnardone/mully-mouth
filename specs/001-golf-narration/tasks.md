# Tasks: AI Voice Caddy for GS Pro

**Last Updated**: 2026-04-21
**Status**: All original tasks complete. Post-spec features documented below.

---

## Phase 1: Setup ✅ COMPLETE

- [x] T001 Create project directory structure (src/, tests/, config/, data/)
- [x] T002 Initialize Python project with pyproject.toml and requirements.txt
- [x] T003 Create requirements.txt with core dependencies
- [x] T004 Create .gitignore (venv/, __pycache__/, data/cache/, config/config.yaml, *.bat with keys)
- [x] T005 Create empty __init__.py files in src/models/, src/services/, src/cli/, src/lib/
- [x] T006 Create data directory structure: data/personalities/, data/training/images/, data/cache/, data/sessions/
- [x] T007 Create config/config.yaml.template with placeholder settings (no API keys)

---

## Phase 2: Foundational ✅ COMPLETE

- [x] T008 Create Outcome enum in src/models/outcome.py: fairway, green, water, bunker, rough, trees, out_of_bounds, tee_shot, unknown
- [x] T009 Create base ServiceError and service-specific exceptions in src/lib/exceptions.py
- [x] T010 Implement configuration loading in src/lib/config.py (keyring → env → yaml priority)
- [x] T011 Implement utility functions in src/lib/utils.py (UUID, timestamps, file I/O)
- [x] T012 Create initial personality YAML files: neutral.yaml, encouraging.yaml, sarcastic.yaml

---

## Phase 3: User Story 1 — Basic Shot Commentary ✅ COMPLETE

- [x] T014 Create ShotEvent dataclass in src/models/shot_event.py
- [x] T015 Add to_dict() / from_dict() to ShotEvent
- [x] T016 Create Session dataclass in src/models/session.py (total_api_calls, total_cost, cache_hit_rate, accuracy_rate)
- [x] T017 Add to_dict() / from_dict() to Session
- [x] T018 Implement ScreenCaptureService in src/services/screen_capture.py using MSS
- [x] T019 Implement monitor selection (multi-monitor support)
- [x] T020 Implement capture_window() returning RGB numpy array
- [x] T021 Implement start_monitoring() / stop_monitoring() with background thread at 2 FPS
- [x] T022 Implement get_latest_frame() with thread-safe locking
- [x] T023 Implement MotionDetectorService in src/services/motion_detector.py using OpenCV frame differencing
- [x] T024 Implement analyze_frame() with Gaussian blur and threshold
- [x] T025 Implement vertical-motion filter (_is_primarily_vertical_motion) to distinguish real shots from aiming
- [x] T026 Implement is_ball_stopped() (1 second of stillness)
- [x] T027 Implement reset() and set_threshold() methods
- [x] T028 Implement PatternCacheService in src/services/pattern_cache.py using imagehash (perceptual hashing)
- [x] T029 Implement find_match() with Hamming distance threshold (<10)
- [x] T030 Implement add_pattern() and persist() / load() to data/cache/pattern_cache.json
- [x] T031 Add thread-safe locking to PatternCacheService
- [x] T032 Implement AIAnalyzerService in src/services/ai_analyzer.py using Anthropic SDK
- [x] T033 Implement analyze_shot() with image resize and base64 encoding
- [x] T034 Add outcome parsing and confidence extraction from AI response
- [x] T035 Implement CommentaryGeneratorService in src/services/commentary_generator.py
- [x] T036 Implement personality loading from YAML with system_prompt, voice_id, example_phrases
- [x] T037 Implement VoiceService in src/services/voice_service.py
- [x] T038 Implement speak() with non-blocking thread
- [x] T039 Implement stop(), is_speaking() methods
- [x] T040 Implement main monitoring loop in src/cli/monitor.py integrating all services
- [x] T041 Implement shot detection pipeline: motion → cache check → AI → commentary → TTS
- [x] T042 Implement session management and stats tracking
- [x] T043 Implement graceful shutdown: stop monitoring, save session, persist cache

---

## Phase 4: User Story 2 — Personality Selection ✅ COMPLETE

- [x] T060 Implement personality switching in monitor without restarting application
- [x] T061 Implement personality settings persistence in config.yaml

---

## Phase 5: User Story 3 — Training by Examples ✅ COMPLETE

- [x] T064 Create UserCorrection dataclass in src/models/correction.py
- [x] T065 Implement LearningService in src/services/learning_service.py
- [x] T066 Implement add_correction(), get_corrections(), few-shot example management
- [x] T067 Implement corrections and examples persistence to data/training/
- [x] T068 Implement promote_correction_to_example() for active learning pipeline

---

## Phase 6: User Story 4 — Quick Setup ✅ COMPLETE

- [x] T087 Implement setup_wizard.py with step-by-step prompts for API keys, personality, voice, motion settings
- [x] T088 Store API keys in Windows Credential Manager (not in config files)
- [x] T089 Implement CredentialsManager in src/lib/credentials.py using keyring
- [x] T090 Implement first-launch detection: if no config exists, run setup wizard
- [x] T091 Create config/config.yaml template without API key fields

---

## Phase 7: Post-Spec Features ✅ ALL COMPLETE

These features were added after the original spec was written. Any rebuild must include them.

### Windows System Tray (replaces CLI as primary UI)

- [x] T107 Implement system tray icon and menu in src/cli/tray_app.py using pystray
- [x] T108 Add right-click menu: Start/Stop Monitoring, personality selector, commentary frequency slider, voice selector, monitor selector, exit
- [x] T109 Add single-instance enforcement (prevent duplicate tray processes)
- [x] T110 Create mully-mouth.bat launcher that runs tray_app.py via venv with no visible terminal
- [x] T111 Add tray icon state changes (active/idle/speaking visual feedback)

### Bundled Installation

- [x] T112 Create install.bat that auto-creates venv, installs all requirements, and creates desktop shortcut
- [x] T113 Create setup_credentials.bat as a user-friendly wrapper for credential entry
- [x] T114 Create INSTALL.md with step-by-step installation guide for non-technical users

### ElevenLabs → xAI Grok TTS Migration

- [x] T115 Rewrite VoiceService to use xAI Grok TTS via httpx POST to `https://api.x.ai/v1/tts`
- [x] T116 Add pygame audio playback (MP3 bytes → BytesIO → pygame.mixer)
- [x] T117 Add tempfile fallback playback for systems without pygame
- [x] T118 Update CredentialsManager: ELEVENLABS_KEY → XAI_KEY
- [x] T119 Update all 7 personality YAMLs with Grok voice IDs (leo/rex/ara/eve/sal)
- [x] T120 Update requirements.txt: remove elevenlabs, add openai>=1.0.0, pygame>=2.5.0, httpx

### 4 New Personalities

- [x] T121 Create data/personalities/jerk.yaml — profane, trash-talking, voice: rex
- [x] T122 Create data/personalities/documentary.yaml — Sir David Attenborough style, voice: leo
- [x] T123 Create data/personalities/ex-girlfriend.yaml — unhinged possessive ex, voice: eve
- [x] T124 Create data/personalities/unhinged.yaml — psychotic conspiracy theorist, voice: sal
- [x] T125 Add commentary safety prompt engineering to avoid AI refusals on profane personalities

### Grok TTS Intonation Tags

- [x] T126 Add per-personality intonation guidance to all system_prompts specifying which tags to use and when
- [x] T127 Add tagged example_phrases to each personality YAML as few-shot demonstrations:
  - documentary: `<whisper>` ~every 3rd phrase, `[breath]` before profound statements
  - sarcastic: `[tsk]` on bad shots, `[chuckle]` after landing a joke
  - encouraging: `[sigh]` on bad shots before uplift, `[chuckle]` for warmth
  - jerk: `[laugh]` on spectacular failures only
  - ex-girlfriend: `[sigh]` passive-aggressive, `[laugh]` manic mood swings
  - unhinged: `[laugh]` or `[breath]` randomly mid-rant
  - neutral: `[breath]` on exceptional outcomes only

### Achievement & Score Commentary

- [x] T128 Add achievement detection to unified AI analysis call (BIRDIE, EAGLE, PAR, BOGEY, etc.)
- [x] T129 Implement achievement commentary generation with personality-appropriate reactions
- [x] T130 Route achievement commentary to voice before (or instead of) shot outcome commentary

### Player Name Personalization

- [x] T131 Add player_name extraction to unified AI analysis call (OCR of HUD upper-left)
- [x] T132 Add name_frequency config setting (default 30%): controls how often name is used in commentary
- [x] T133 Pass player name to commentary generator when name_frequency roll succeeds

### Unified API Call Optimization

- [x] T134 Implement analyze_shot_unified() in AIAnalyzerService returning JSON with all 4 analysis results in one call
- [x] T135 Move pattern cache check BEFORE AI call so cache hits skip all AI analysis
- [x] T136 Update _process_shot() in monitor.py to use unified analysis and extract all fields from single response
- [x] T137 Update cost calculation to Claude Haiku 4.5 pricing ($0.25/$1.25 per 1M tokens, cache discounts)

### Pre-Flight Screen Classifier

- [x] T138 Implement ScreenClassifier in src/services/screen_classifier.py
- [x] T139 On init, load all training images from data/training/images/, build averaged HSV histograms per category
- [x] T140 Implement is_gameplay_screen(frame) using cv2.compareHist (HISTCMP_CORREL) against gameplay/idle centroids
- [x] T141 Calibrate bias threshold to 0.15 (gameplay min gap 0.206, idle max gap 0.090 — clean separation)
- [x] T142 Fail-open behavior: if no training data found, always return True (assume gameplay)
- [x] T143 Wire ScreenClassifier into _monitoring_loop before motion detector: idle frames reset motion detector and skip
- [x] T144 Initialize ScreenClassifier in Monitor._init_services() with startup log message

### API Key Security

- [x] T145 Remove api_key fields from config/config.yaml and config.yaml.template entirely
- [x] T146 Update setup_wizard.py to call CredentialsManager.store_*_key() instead of writing keys to the config file
- [x] T147 Give AnthropicConfig.api_key a default of "" so config loading succeeds when key absent from file
- [x] T148 Audit and remove any API keys hardcoded in .claude/settings.local.json or other tracked files

### Commentary Frequency & Cost Controls

- [x] T149 Add commentary_frequency setting to config (default 20%)
- [x] T150 Add name_frequency setting to config (default 30%)
- [x] T151 Enforce 150-character hard limit in all personality system prompts
- [x] T152 Set target commentary length to 50-80 characters in all personality prompts

### Multi-Monitor Support

- [x] T153 Implement get_available_monitors() in ScreenCaptureService
- [x] T154 Add monitor_index to config and MonitoringConfig dataclass
- [x] T155 Add monitor selector to system tray menu

---

## If Rebuilding From Scratch — Checklist

In priority order:

1. **Core pipeline** (T001-T043): Screen capture → motion → cache → Claude Haiku → Grok TTS
2. **System tray** (T107-T111): This is the only UI — no CLI for end users
3. **Credential Manager** (T089, T145-T148): Keys never in files
4. **Bundled installer** (T112-T114): install.bat + mully-mouth.bat
5. **Unified API call** (T134-T137): 1 call per shot, not 4
6. **Screen classifier** (T138-T144): Pre-flight idle suppression, no API cost
7. **All 7 personalities** (T012, T121-T125): With Grok TTS voices
8. **Grok TTS** (T115-T120): Not ElevenLabs
9. **Intonation tags** (T126-T127): In system_prompts and example_phrases
10. **Achievements** (T128-T130): Birdie/Eagle/etc. commentary
11. **Player name** (T131-T133): Occasional name use at configurable frequency
12. **Commentary constraints** (T151-T152): 50-80 chars target, 150 hard max
