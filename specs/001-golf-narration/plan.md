# Implementation Plan: AI Voice Caddy for GS Pro

**Branch**: `001-golf-narration` | **Date**: 2025-11-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-golf-narration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an AI-first voice caddy for GS Pro golf simulator that automatically detects shots, analyzes outcomes using Claude Vision, and provides personality-driven commentary via text-to-speech. The system uses zero-shot learning with optional few-shot training, operates continuously during gameplay, and learns from user corrections. Core requirements: <2 second response time, 90% shot detection, <$0.05 per round, 60% initial accuracy improving to 80%+ after one round.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- Anthropic Python SDK (Claude Vision API)
- ElevenLabs Python SDK (text-to-speech)
- OpenCV (cv2) for screen capture and motion detection
- PyAutoGUI or MSS for cross-platform screen capture
- Pynput for hotkey handling
- YAML for configuration (pyyaml)

**Storage**: Local filesystem (JSON/YAML for user preferences, training examples, pattern cache)
**Testing**: pytest for unit tests, integration tests, and cost validation
**Target Platform**: Windows 10/11 (primary), potential Linux/Mac support
**Project Type**: Single desktop application with CLI interface
**Performance Goals**:
- Shot detection latency: <500ms from ball stop
- AI analysis + TTS: <2 seconds total
- Screen capture: 1-2 fps during monitoring, adequate for motion detection
- Memory footprint: <200MB during operation

**Constraints**:
- API costs: <$0.05 per 18-hole round (~80 shots)
- Maximum 20 API calls per round through intelligent caching
- Must operate for 2+ hours continuously without degradation
- Zero manual screen region configuration
- Offline capability for cached patterns (online required for new analysis)

**Scale/Scope**:
- Single-user desktop application
- ~2,000-3,000 lines of Python code
- Support for 10+ shot outcome types
- 3 personality profiles
- Pattern cache of 50-100 learned examples per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. AI-First Development ✅ PASS

**Compliance**:
- Shot outcome detection delegated to Claude Vision (zero-shot, few-shot)
- Commentary generation handled by AI understanding context
- Pattern learning through AI, not rule-based matching
- Motion detection uses traditional OpenCV (appropriate: cheap, deterministic, not AI-suitable)

**Validation**: AI handles all complex pattern recognition and decision-making. Traditional methods only for cheap, repetitive operations (screen capture, motion detection).

### II. Natural Interaction Over Configuration ✅ PASS

**Compliance**:
- Training via screenshot upload + natural language labels
- User corrections via hotkey + conversational input ("that was rough, not bunker")
- Configuration limited to API keys and personality selection
- Zero screen region or pixel coordinate configuration
- No behavior flags or technical parameters exposed

**Validation**: Users interact through examples and corrections, not configuration files.

### III. Learning-Driven Systems ✅ PASS

**Compliance**:
- Zero-shot capability required (60% accuracy without training)
- Active learning from user corrections during gameplay
- Pattern cache grows from actual usage
- Confidence tracking triggers user confirmation when uncertain
- Progressive accuracy improvement measured and visible

**Validation**: System works immediately, improves through use, learns from real gameplay.

### IV. Cost-Conscious Intelligence ✅ PASS

**Compliance**:
- OpenCV motion detection filters 99% of frames (cheap)
- AI calls only on shot completion events
- Pattern cache reduces redundant AI analysis
- Confidence-based caching: high-confidence outcomes skip AI
- Target: <20 API calls per round, <$0.05 cost

**Validation**: Hybrid architecture with intelligent triggering meets cost targets.

### V. Simplicity & User Experience ✅ PASS

**Compliance**:
- Setup target: <10 minutes (SC-001)
- Training: 3-5 examples sufficient (few-shot)
- Error messages conversational, actionable
- Zero technical knowledge required
- Progress visible (accuracy improvement over rounds)

**Validation**: All UX requirements align with simplicity principle.

### Technical Standards ✅ PASS

**API Integration**:
- ✅ Claude Vision for image understanding
- ✅ ElevenLabs for text-to-speech (as specified)
- ✅ OpenCV for screen capture and motion detection

**Performance & Cost Targets**:
- ✅ Setup time: <10 minutes target
- ✅ API calls: <20 per session target
- ✅ Cost: <$0.05 per session target
- ✅ Accuracy: 60% → 80% → 90% progression
- ✅ Response latency: <2 seconds target

**Code Architecture**:
- ✅ Python-first (specified by user)
- ✅ Library-first design (importable modules)
- ✅ CLI interface for user interaction
- ✅ Minimal dependencies (AI SDK, screen capture, TTS)
- ✅ Clear separation: motion detection → AI analysis → TTS output

### Gate Decision: ✅ **PASSED - Proceed to Phase 0**

All constitutional principles satisfied. No violations requiring justification. Design fully aligns with AI-first, natural interaction, learning-driven, cost-conscious, and simple UX principles.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── shot_event.py          # Shot Event entity
│   ├── training_example.py    # Training Example entity
│   ├── correction.py           # User Correction entity
│   ├── personality.py          # Commentary Personality entity
│   └── session.py              # Session entity
├── services/
│   ├── screen_capture.py       # Window detection, screen capture
│   ├── motion_detector.py      # OpenCV-based motion/shot detection
│   ├── ai_analyzer.py          # Claude Vision integration
│   ├── pattern_cache.py        # Pattern matching and caching
│   ├── commentary_generator.py # Personality-based commentary
│   ├── voice_service.py        # ElevenLabs TTS integration
│   └── learning_service.py     # Active learning, corrections
├── cli/
│   ├── main.py                 # CLI entry point
│   ├── setup.py                # Setup wizard
│   ├── train.py                # Training mode
│   └── monitor.py              # Gameplay monitoring
└── lib/
    ├── config.py               # Configuration management
    ├── hotkeys.py              # Hotkey handling
    └── utils.py                # Shared utilities

tests/
├── integration/
│   ├── test_shot_detection.py
│   ├── test_ai_analysis.py
│   ├── test_learning.py
│   └── test_cost.py            # API cost validation
└── unit/
    ├── test_motion_detector.py
    ├── test_pattern_cache.py
    └── test_commentary.py

config/
└── config.yaml                 # User configuration (API keys, preferences)

data/
├── personalities/              # Personality definitions
│   ├── encouraging.yaml
│   ├── neutral.yaml
│   └── sarcastic.yaml
├── training/                   # User training examples
└── cache/                      # Pattern cache
```

**Structure Decision**: Single project structure chosen. This is a desktop application with no frontend/backend split. All code is Python, organized into models (entities), services (business logic), CLI (user interface), and lib (utilities). Testing focuses on integration (end-to-end flows, cost validation) and unit (individual components).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All design decisions align with constitutional principles.

## Phase 0: Research Complete

**Artifacts Generated**:
- `research.md`: Technology decisions, best practices, implementation strategies
- All NEEDS CLARIFICATION items resolved

**Key Decisions**:
- Screen Capture: MSS library (fast, cross-platform)
- Motion Detection: OpenCV frame differencing
- Pattern Cache: Perceptual hashing (imagehash)
- AI: Claude 3.5 Sonnet via Anthropic SDK
- TTS: ElevenLabs streaming
- Configuration: YAML with pydantic validation
- Testing: pytest with cost tracking fixtures

## Phase 1: Design Complete

**Artifacts Generated**:
- `data-model.md`: Entity definitions and relationships
- `contracts/service-interfaces.md`: Service contracts and interfaces
- `quickstart.md`: Developer setup and testing guide
- `CLAUDE.md`: Agent context updated with technology stack

**Architecture Summary**:
- 5 core entities: ShotEvent, TrainingExample, UserCorrection, CommentaryPersonality, Session
- 7 service interfaces: ScreenCapture, MotionDetector, AIAnalyzer, PatternCache, CommentaryGenerator, Voice, Learning
- Single project structure: `src/{models,services,cli,lib}`, `tests/{unit,integration}`
- Data storage: Local JSON/YAML files
- API integrations: Anthropic (Claude Vision), ElevenLabs (TTS)

## Constitution Re-Check (Post-Design)

Re-evaluated after completing detailed design:

### I. AI-First Development ✅ PASS

**Design Validation**:
- Service interfaces delegate to AI: `IAIAnalyzerService.analyze_shot()`
- Pattern cache uses AI-generated outcomes, not rules
- Commentary generation uses AI with personality prompts
- Motion detection appropriately uses traditional OpenCV (cheap, deterministic)
- No rule-based shot classification

**Compliance**: Full AI-first design maintained.

### II. Natural Interaction Over Configuration ✅ PASS

**Design Validation**:
- Training via `ILearningService.create_training_example()` (screenshot + label)
- Corrections via `ILearningService.record_correction()` (conversational)
- Configuration in `config.yaml`: only API keys + personality name
- No screen region coordinates, thresholds, or flags exposed
- Personality defined in human-readable YAML

**Compliance**: Natural interaction design confirmed.

### III. Learning-Driven Systems ✅ PASS

**Design Validation**:
- Zero-shot: `analyze_shot()` works without training examples
- Few-shot: `few_shot_examples` parameter in `analyze_shot()`
- Active learning: `ILearningService` handles corrections → training
- Confidence tracking: `find_match()` returns confidence scores
- Progressive improvement: Session entity tracks accuracy over time

**Compliance**: Learning-driven architecture validated.

### IV. Cost-Conscious Intelligence ✅ PASS

**Design Validation**:
- Motion detection: OpenCV (free), filters frames before AI
- Pattern cache: `IPatternCacheService.find_match()` reduces AI calls
- Confidence-based caching: >0.85 confidence skips AI
- Cost tracking: `get_total_cost()` in AI service
- Image optimization: Resize to 1280x720 before API call

**Compliance**: Cost optimization baked into design.

### V. Simplicity & User Experience ✅ PASS

**Design Validation**:
- Setup wizard: `cli/setup.py` (API keys + personality only)
- Quick training: `cli/train.py` (upload + label)
- Automatic operation: `cli/main.py` (no intervention during play)
- Error messages: Service exceptions with user-friendly text
- Progress visible: Session entity exposes stats

**Compliance**: Simple UX design confirmed.

### Technical Standards ✅ PASS

**Design Validation**:
- APIs: Anthropic SDK, ElevenLabs SDK (as specified)
- Performance: Service contracts specify <2s total latency
- Cost: Cost tracking in services, session-level totals
- Architecture: Library-first (importable services), CLI interface
- Separation: Motion → AI → TTS pipeline clear in service contracts

**Compliance**: All technical standards met in design.

### Gate Decision: ✅ **PASSED - Ready for Implementation**

Design remains fully compliant with all constitutional principles. Service contracts enforce AI-first, natural interaction, learning-driven, cost-conscious, and simple UX requirements. No violations introduced during detailed design phase.
