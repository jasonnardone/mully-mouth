# Tasks: AI Voice Caddy for GS Pro

**Input**: Design documents from `specs/001-golf-narration/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/service-interfaces.md

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are excluded from this implementation plan. Focus is on core functionality.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/`, `config/`, `data/` at repository root
- Paths follow structure defined in plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure (src/, tests/, config/, data/)
- [ ] T002 Initialize Python project with pyproject.toml and requirements.txt
- [ ] T003 [P] Create requirements.txt with dependencies: anthropic, elevenlabs, opencv-python, mss, pygetwindow, pynput, pyyaml, pydantic, imagehash, pytest
- [ ] T004 [P] Create .gitignore for Python project (venv/, __pycache__/, data/, config/config.yaml, .env)
- [ ] T005 [P] Create empty __init__.py files in src/models/, src/services/, src/cli/, src/lib/
- [ ] T006 [P] Create data directory structure: data/personalities/, data/training/images/, data/cache/, data/sessions/
- [ ] T007 [P] Create config/config.yaml template with placeholder API keys and default settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Create Outcome enum in src/models/outcome.py with values: fairway, green, water, bunker, rough, trees, out_of_bounds, tee_shot, unknown
- [ ] T009 [P] Create base ServiceError exception class in src/lib/exceptions.py
- [ ] T010 [P] Create service-specific exception classes in src/lib/exceptions.py: ScreenCaptureError, AIServiceError, VoiceServiceError, CacheError, LearningError
- [ ] T011 [P] Implement configuration management in src/lib/config.py using pydantic for validation
- [ ] T012 [P] Implement utility functions in src/lib/utils.py for UUID generation, timestamp handling, file I/O
- [ ] T013 Create default personality YAML files in data/personalities/: neutral.yaml, encouraging.yaml, sarcastic.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Shot Commentary (Priority: P1) 🎯 MVP

**Goal**: Automated shot detection and AI-powered commentary during gameplay

**Independent Test**: Launch GS Pro, play 3-5 shots, verify system automatically detects each shot and provides spoken commentary describing where the ball landed

### Implementation for User Story 1

**Models** (parallel within group):

- [ ] T014 [P] [US1] Create ShotEvent dataclass in src/models/shot_event.py with all attributes per data-model.md
- [ ] T015 [P] [US1] Add to_dict() and from_dict() methods to ShotEvent in src/models/shot_event.py
- [ ] T016 [P] [US1] Create Session dataclass in src/models/session.py with computed properties (total_api_calls, total_cost, cache_hit_rate, accuracy_rate)
- [ ] T017 [P] [US1] Add to_dict() and from_dict() methods to Session in src/models/session.py

**Services - Screen Capture** (sequential):

- [ ] T018 [US1] Implement IScreenCaptureService in src/services/screen_capture.py using MSS library
- [ ] T019 [US1] Implement find_gs_pro_window() method in src/services/screen_capture.py using pygetwindow
- [ ] T020 [US1] Implement capture_window() method in src/services/screen_capture.py to return RGB numpy array
- [ ] T021 [US1] Implement start_monitoring() and stop_monitoring() methods in src/services/screen_capture.py with background thread at 2 FPS
- [ ] T022 [US1] Implement get_latest_frame() method in src/services/screen_capture.py

**Services - Motion Detection** (sequential, depends on T018-T022):

- [ ] T023 [US1] Implement IMotionDetectorService in src/services/motion_detector.py using OpenCV frame differencing
- [ ] T024 [US1] Implement analyze_frame() method in src/services/motion_detector.py with adaptive thresholding
- [ ] T025 [US1] Implement is_ball_stopped() method in src/services/motion_detector.py (no motion for 1 second)
- [ ] T026 [US1] Implement on_shot_detected() callback registration in src/services/motion_detector.py
- [ ] T027 [US1] Implement reset() and set_threshold() methods in src/services/motion_detector.py

**Services - Pattern Cache** (parallel, can start anytime):

- [ ] T028 [P] [US1] Implement IPatternCacheService in src/services/pattern_cache.py using imagehash library
- [ ] T029 [US1] Implement find_match() method in src/services/pattern_cache.py with perceptual hash comparison (Hamming distance <10)
- [ ] T030 [US1] Implement add_pattern() method in src/services/pattern_cache.py
- [ ] T031 [US1] Implement persistence methods (persist(), load()) in src/services/pattern_cache.py to data/cache/pattern_cache.json
- [ ] T032 [US1] Implement get_stats(), update_confidence(), clear() methods in src/services/pattern_cache.py
- [ ] T033 [US1] Add thread-safe locking to PatternCacheService in src/services/pattern_cache.py

**Services - AI Analyzer** (parallel, can start anytime):

- [ ] T034 [P] [US1] Implement IAIAnalyzerService in src/services/ai_analyzer.py using Anthropic Python SDK
- [ ] T035 [US1] Implement analyze_shot() method in src/services/ai_analyzer.py with image resize to 1280x720
- [ ] T036 [US1] Add retry logic (3 attempts, exponential backoff) to analyze_shot() in src/services/ai_analyzer.py
- [ ] T037 [US1] Implement cost tracking methods (get_total_cost(), reset_cost_tracking()) in src/services/ai_analyzer.py
- [ ] T038 [US1] Implement validate_api_key() method in src/services/ai_analyzer.py
- [ ] T039 [US1] Add outcome parsing and confidence extraction from AI response in src/services/ai_analyzer.py

**Services - Commentary Generator** (parallel, can start anytime):

- [ ] T040 [P] [US1] Create CommentaryPersonality dataclass in src/models/personality.py
- [ ] T041 [US1] Add from_yaml() classmethod to CommentaryPersonality in src/models/personality.py
- [ ] T042 [US1] Implement ICommentaryGeneratorService in src/services/commentary_generator.py
- [ ] T043 [US1] Implement load_personality() method in src/services/commentary_generator.py with YAML parsing
- [ ] T044 [US1] Implement get_system_prompt() and get_example_phrases() methods in src/services/commentary_generator.py
- [ ] T045 [US1] Implement list_personalities() method in src/services/commentary_generator.py

**Services - Voice** (parallel, can start anytime):

- [ ] T046 [P] [US1] Implement IVoiceService in src/services/voice_service.py using ElevenLabs Python SDK
- [ ] T047 [US1] Implement speak() method in src/services/voice_service.py with streaming and non-blocking mode
- [ ] T048 [US1] Implement speech queue to avoid overlapping in src/services/voice_service.py
- [ ] T049 [US1] Implement stop(), is_speaking(), set_voice() methods in src/services/voice_service.py
- [ ] T050 [US1] Implement validate_api_key() and on_speech_complete() callback in src/services/voice_service.py

**CLI - Monitor (Main Application)** (depends on all services):

- [ ] T051 [US1] Implement main monitoring loop in src/cli/monitor.py that integrates all services
- [ ] T052 [US1] Add shot detection pipeline in src/cli/monitor.py: motion detection → AI analysis → pattern cache → commentary → TTS
- [ ] T053 [US1] Implement session management in src/cli/monitor.py: create Session on start, save shots, compute stats
- [ ] T054 [US1] Add session persistence in src/cli/monitor.py: save to data/sessions/{session_id}/session.json and shots.json
- [ ] T055 [US1] Implement graceful shutdown in src/cli/monitor.py: stop monitoring, save session, persist cache
- [ ] T056 [US1] Add cost tracking and budget monitoring in src/cli/monitor.py: halt if approaching $0.05 limit

**CLI - Entry Point** (depends on monitor):

- [ ] T057 [US1] Create main CLI entry point in src/cli/main.py that launches monitor mode
- [ ] T058 [US1] Add command-line argument parsing in src/cli/main.py for options (--personality, --config, etc.)
- [ ] T059 [US1] Implement error handling and user-friendly error messages in src/cli/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional - users can play golf and hear AI commentary

---

## Phase 4: User Story 2 - Personality Selection (Priority: P2)

**Goal**: Users can choose between different commentator personalities to match their mood

**Independent Test**: Select each personality type during setup, play 5 shots, verify commentary tone matches selected personality

### Implementation for User Story 2

- [ ] T060 [P] [US2] Validate personality YAML structure in src/services/commentary_generator.py with schema checking
- [ ] T061 [US2] Implement personality switching in src/cli/monitor.py without restarting application
- [ ] T062 [US2] Add personality preview feature in src/cli/setup.py: load each personality and show example phrases
- [ ] T063 [US2] Implement personality settings persistence in src/lib/config.py: save and load selected personality

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can play with their chosen personality

---

## Phase 5: User Story 3 - Training by Examples (Priority: P3)

**Goal**: Users can teach the system to recognize specific shot outcomes by providing example screenshots

**Independent Test**: Enter training mode, upload 3-5 screenshots of water shots with labels, play a round, verify water shots recognized with higher confidence

### Implementation for User Story 3

**Models** (parallel):

- [ ] T064 [P] [US3] Create TrainingExample dataclass in src/models/training_example.py with all attributes per data-model.md
- [ ] T065 [P] [US3] Add to_dict() and from_dict() methods to TrainingExample in src/models/training_example.py
- [ ] T066 [P] [US3] Create UserCorrection dataclass in src/models/correction.py with all attributes per data-model.md
- [ ] T067 [P] [US3] Add to_dict() and from_dict() methods to UserCorrection in src/models/correction.py

**Services - Learning** (depends on models, can run parallel with hotkeys):

- [ ] T068 [US3] Implement ILearningService in src/services/learning_service.py
- [ ] T069 [US3] Implement record_correction() method in src/services/learning_service.py
- [ ] T070 [US3] Implement create_training_example() method in src/services/learning_service.py with screenshot saving
- [ ] T071 [US3] Implement get_recent_corrections() method in src/services/learning_service.py for few-shot prompting
- [ ] T072 [US3] Add corrections persistence in src/services/learning_service.py to data/corrections.json
- [ ] T073 [US3] Implement training examples persistence in src/services/learning_service.py to data/training/examples.json
- [ ] T074 [US3] Add thread-safe locking to LearningService in src/services/learning_service.py

**Library - Hotkeys** (parallel with learning service):

- [ ] T075 [P] [US3] Implement hotkey handler in src/lib/hotkeys.py using pynput library
- [ ] T076 [US3] Add global hotkey registration for F10 (toggle) and Ctrl+C (correction) in src/lib/hotkeys.py
- [ ] T077 [US3] Implement callback mechanism for hotkey events in src/lib/hotkeys.py

**CLI - Training Mode**:

- [ ] T078 [US3] Implement training mode in src/cli/train.py for uploading screenshots and labeling outcomes
- [ ] T079 [US3] Add screenshot upload interface in src/cli/train.py (drag-and-drop or file path input)
- [ ] T080 [US3] Implement outcome label input in src/cli/train.py with validation against Outcome enum
- [ ] T081 [US3] Add training example creation and pattern cache update in src/cli/train.py
- [ ] T082 [US3] Implement training session summary in src/cli/train.py showing examples added per outcome type

**CLI - Correction Integration**:

- [ ] T083 [US3] Integrate hotkey handler into monitor mode in src/cli/monitor.py
- [ ] T084 [US3] Implement correction flow in src/cli/monitor.py: Ctrl+C → pause → prompt user → record correction → resume
- [ ] T085 [US3] Add correction to few-shot examples in AI analyzer calls in src/services/ai_analyzer.py
- [ ] T086 [US3] Update pattern cache with corrected outcome in src/cli/monitor.py

**Checkpoint**: All user stories (1, 2, 3) should now be independently functional - training and corrections work

---

## Phase 6: User Story 4 - Quick Setup (Priority: P4)

**Goal**: First-time users can complete entire setup in under 10 minutes with minimal technical knowledge

**Independent Test**: Time a new user from launch through first shot commentary, verify takes less than 10 minutes

### Implementation for User Story 4

- [ ] T087 [US4] Implement setup wizard in src/cli/setup.py with step-by-step prompts
- [ ] T088 [US4] Add welcome screen in src/cli/setup.py explaining the app in 1-2 sentences
- [ ] T089 [US4] Implement API key validation step in src/cli/setup.py: prompt for keys, validate using service methods
- [ ] T090 [US4] Add personality selection interface in src/cli/setup.py with descriptions of each personality
- [ ] T091 [US4] Implement GS Pro window detection in src/cli/setup.py with automatic search and fallback to manual selection
- [ ] T092 [US4] Add configuration persistence in src/cli/setup.py: save API keys to config.yaml, save preferences
- [ ] T093 [US4] Implement setup completion summary in src/cli/setup.py showing configuration and next steps
- [ ] T094 [US4] Add first-launch detection in src/cli/main.py: if no config exists, run setup wizard automatically

**Checkpoint**: Complete setup flow - new users can get from installation to first shot commentary in <10 minutes

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T095 [P] Add comprehensive logging in src/lib/utils.py with DEBUG, INFO, WARN, ERROR levels
- [ ] T096 [P] Implement logging throughout all services in src/services/*.py
- [ ] T097 [P] Add session statistics display in src/cli/monitor.py: show stats at end of round (shots, cost, accuracy, cache hit rate)
- [ ] T098 [P] Create README.md with installation instructions, quick start, and basic usage
- [ ] T099 [P] Add requirements documentation in docs/setup.md for API keys and GS Pro installation
- [ ] T100 Implement edge case handling in src/cli/monitor.py: GS Pro minimized, window closed, rapid shots
- [ ] T101 Implement cost warning system in src/cli/monitor.py: warn at 80% of budget, halt at 100%
- [ ] T102 Add graceful degradation in src/cli/monitor.py: if AI unavailable, use cache-only mode
- [ ] T103 Implement session export feature in src/cli/main.py: export session data to JSON
- [ ] T104 Add cache clearing command in src/cli/main.py for fresh start
- [ ] T105 Implement performance monitoring in src/cli/monitor.py: log latencies for each pipeline stage
- [ ] T106 Add user feedback prompts in src/cli/monitor.py: ask for accuracy feedback at end of round

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies (personality system is independent)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1 monitoring but is independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Uses services from US1/US2/US3 but setup wizard is independent

### Within Each User Story

**User Story 1 Task Dependencies**:
- Models (T014-T017) can run in parallel
- Screen Capture (T018-T022) must complete before Motion Detector (T023-T027)
- Pattern Cache (T028-T033), AI Analyzer (T034-T039), Commentary Generator (T040-T045), Voice (T046-T050) can all run in parallel
- CLI Monitor (T051-T056) depends on ALL services being complete
- CLI Entry Point (T057-T059) depends on Monitor being complete

**User Story 2 Task Dependencies**:
- All tasks (T060-T063) can run in parallel after US1 services are complete

**User Story 3 Task Dependencies**:
- Models (T064-T067) can run in parallel
- Learning Service (T068-T074) depends on models
- Hotkeys (T075-T077) can run in parallel with learning service
- Training Mode (T078-T082) depends on learning service
- Correction Integration (T083-T086) depends on hotkeys and learning service

**User Story 4 Task Dependencies**:
- All tasks (T087-T094) must run sequentially as they build the setup wizard flow

### Parallel Opportunities

**Phase 1 Setup**: All tasks can run in parallel (T001-T007)

**Phase 2 Foundational**: T009-T013 can run in parallel after T008

**Phase 3 User Story 1**:
- Models: T014-T017 (parallel)
- After Screen Capture complete: Pattern Cache (T028-T033), AI Analyzer (T034-T039), Commentary Generator (T040-T045), Voice (T046-T050) all parallel

**Phase 5 User Story 3**:
- Models: T064-T067 (parallel)
- Learning Service + Hotkeys: T068-T077 (two parallel tracks)

**Phase 7 Polish**: T095-T099, T103-T104 can all run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T013)
3. Complete Phase 3: User Story 1 (T014-T059)
4. **STOP and VALIDATE**: Test User Story 1 independently - play 3-5 shots and verify commentary
5. Deploy/demo if ready

**MVP Scope**: 59 tasks
**Estimated Complexity**: Medium-High (core services, AI integration, real-time monitoring)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (13 tasks)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! - 46 tasks)
3. Add User Story 2 → Test independently → Deploy/Demo (4 tasks)
4. Add User Story 3 → Test independently → Deploy/Demo (23 tasks)
5. Add User Story 4 → Test independently → Deploy/Demo (8 tasks)
6. Add Polish → Final release (12 tasks)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T013)
2. Once Foundational is done:
   - **Developer A**: User Story 1 Models + Screen Capture + Motion Detector (T014-T027)
   - **Developer B**: User Story 1 Pattern Cache + AI Analyzer (T028-T039)
   - **Developer C**: User Story 1 Commentary Generator + Voice (T040-T050)
3. When all services complete:
   - **Developer A**: CLI Monitor + Entry Point (T051-T059)
   - **Developer B**: User Story 2 (T060-T063)
   - **Developer C**: User Story 3 Models + Learning Service (T064-T074)
4. Continue with remaining stories and polish

---

## Parallel Example: User Story 1

Launch these tasks together after Screen Capture is complete:

```bash
# Parallel Track 1: Pattern Cache
Task T028: Implement IPatternCacheService in src/services/pattern_cache.py
Task T029: Implement find_match() method...
...

# Parallel Track 2: AI Analyzer
Task T034: Implement IAIAnalyzerService in src/services/ai_analyzer.py
Task T035: Implement analyze_shot() method...
...

# Parallel Track 3: Commentary Generator
Task T040: Create CommentaryPersonality dataclass in src/models/personality.py
Task T041: Add from_yaml() classmethod...
...

# Parallel Track 4: Voice Service
Task T046: Implement IVoiceService in src/services/voice_service.py
Task T047: Implement speak() method...
...
```

---

## Notes

- [P] tasks = different files, no dependencies within their group
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Tests not included**: Specification does not explicitly request TDD approach
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths are explicit and follow the structure in plan.md
- Service interfaces defined in contracts/ must be followed exactly
- Entity definitions in data-model.md must be implemented precisely

---

## Task Count Summary

- **Phase 1 (Setup)**: 7 tasks
- **Phase 2 (Foundational)**: 6 tasks
- **Phase 3 (User Story 1 - P1)**: 46 tasks
- **Phase 4 (User Story 2 - P2)**: 4 tasks
- **Phase 5 (User Story 3 - P3)**: 23 tasks
- **Phase 6 (User Story 4 - P4)**: 8 tasks
- **Phase 7 (Polish)**: 12 tasks

**Total Tasks**: 106 tasks

**MVP (US1 only)**: 59 tasks (Setup + Foundational + US1)
**MVP + Personality**: 63 tasks
**MVP + Personality + Training**: 86 tasks
**Full Feature Set**: 106 tasks

**Parallel Opportunities**: ~35 tasks marked [P] can run concurrently with proper team allocation

**Independent Test Criteria**:
- US1: Play 3-5 shots, hear commentary within 2 seconds
- US2: Switch personalities, notice different tone in 5 shots
- US3: Upload 5 training examples, observe improved accuracy
- US4: Complete setup from scratch in under 10 minutes
