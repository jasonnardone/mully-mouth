# Feature Specification: AI Voice Caddy for GS Pro

**Feature Branch**: `001-golf-narration`
**Created**: 2025-11-19
**Last Updated**: 2026-04-21
**Status**: Implemented & Active
**Input**: User description: "Build an application that can narrate a round of golf in GS pro."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Shot Commentary (Priority: P1) ✅ COMPLETE

As a golfer playing GS Pro, I want to hear natural commentary on my shots so that I can get real-time feedback on my performance without looking away from the game.

**Acceptance Scenarios**:

1. **Given** GS Pro is running and the narration app is active, **When** I hit a shot that lands in the fairway, **Then** I hear commentary within 2 seconds of the ball stopping
2. **Given** GS Pro is running, **When** I hit into water, bunker, rough, trees, green, or OB, **Then** I hear commentary identifying the outcome
3. **Given** I complete a full 18-hole round, **Then** the system provided commentary on at least 90% of shots

---

### User Story 2 - Personality Selection (Priority: P2) ✅ COMPLETE

As a golfer, I want to choose between different commentator personalities so that the commentary matches my mood and makes the game more entertaining.

**Acceptance Scenarios**:

1. **Given** I'm in setup, **When** choosing a personality, **Then** I see 7 distinct options: Neutral, Sarcastic, Encouraging, Jerk, Sir David (documentary), Ex-Girlfriend, and Unhinged
2. **Given** I've selected any personality, **When** I hit shots, **Then** commentary tone, vocabulary, and voice consistently match the selected character
3. **Given** I want to change personality, **When** I right-click the system tray icon, **Then** I can switch personality without restarting
4. **Given** profane personalities (Jerk, Unhinged) are selected, **Then** commentary uses explicit language and stays in character
5. **Given** any personality is selected, **Then** commentary is 50-80 characters ideally, never exceeding 150 characters

---

### User Story 3 - Training by Examples (Priority: P3) ✅ COMPLETE

As a golfer, I want to teach the system to recognize specific shot outcomes from my simulator by showing it example screenshots, so that it becomes more accurate for my specific setup.

**Acceptance Scenarios**:

1. **Given** I place screenshots in `data/training/images/<outcome>/`, **Then** the system uses them as few-shot examples in AI analysis calls
2. **Given** I've trained on a shot type, **When** a similar shot occurs, **Then** recognition confidence is higher than without training
3. **Given** the AI makes an incorrect call, **When** I make a correction via the tray menu, **Then** the system learns from it
4. **Given** training images exist in the `idle/` folder, **Then** the screen pre-classifier uses them to suppress non-gameplay frames before motion detection fires

---

### User Story 4 - Quick Setup (Priority: P4) ✅ COMPLETE

As a first-time user, I want to complete setup in under 10 minutes with no command-line steps, so I can start using the app immediately.

**Acceptance Scenarios**:

1. **Given** I've just installed the app, **When** I run `install.bat`, **Then** all dependencies are installed automatically with no manual steps
2. **Given** I run `setup_wizard.py`, **When** I enter my Anthropic and xAI API keys, **Then** they are stored securely in Windows Credential Manager — not in any file
3. **Given** I launch `mully-mouth.bat`, **Then** the app starts as a system tray icon with no visible terminal window
4. **Given** I right-click the tray icon, **Then** I can change personality, adjust commentary frequency, and start/stop monitoring from the menu
5. **Given** setup is complete, **When** I return on another day, **Then** my API keys and settings are remembered without re-entry

---

### User Story 5 - Achievement & Score Commentary (Priority: P2) ✅ COMPLETE

As a golfer, I want to hear special commentary when I score a birdie, eagle, par, or bogey, so that scoring achievements feel rewarding and entertaining.

**Acceptance Scenarios**:

1. **Given** I sink a putt for birdie, **When** the Birdie overlay appears on screen, **Then** I hear personality-appropriate achievement commentary
2. **Given** I make an eagle or hole-in-one, **Then** the commentary is more enthusiastic/dramatic than for a birdie
3. **Given** an achievement overlay is detected, **Then** achievement commentary plays instead of (or before) the shot outcome commentary

---

### User Story 6 - Player Name Personalization (Priority: P3) ✅ COMPLETE

As a golfer, I want the commentator to occasionally use my name so that commentary feels more personal.

**Acceptance Scenarios**:

1. **Given** my name appears in the GS Pro HUD, **When** commentary is generated, **Then** it occasionally includes my first name
2. **Given** the name frequency setting is 30% (default), **Then** approximately 30% of commentary lines reference my name
3. **Given** name frequency is set to 0%, **Then** the commentator never uses my name

---

### User Story 7 - Non-Gameplay Screen Suppression (Priority: P2) ✅ COMPLETE

As a golfer, I want the app to stay completely silent when I'm in menus, setting up a round, or the GSPro window isn't active, so I don't hear commentary triggered by UI activity.

**Acceptance Scenarios**:

1. **Given** the app is running but GSPro is on a menu or setup screen, **Then** no commentary or API calls fire
2. **Given** I'm testing the app with no golf course visible, **Then** the monitor stays in idle state
3. **Given** I navigate from a menu back into active gameplay, **Then** commentary resumes automatically without restarting
4. **Given** training images exist in `data/training/images/idle/`, **Then** the screen classifier uses them to distinguish menus from gameplay

---

### Edge Cases

- What happens when GS Pro is minimized or not visible on screen? → Screen classifier suppresses all activity
- How does the system handle very fast shot sequences? → Motion detector requires 1 second of stillness before triggering
- What if the commentary is still speaking when the next shot is hit? → New speech interrupts or queues
- What happens if API keys are missing or invalid? → Tray icon shows warning; app continues running silently
- What if screen capture returns a non-gameplay screen? → Pre-flight classifier suppresses it without an API call
- What if the commentary would violate AI safety guidelines? → Prompt engineering avoids refusals; profane personalities have been tested

---

## Requirements *(mandatory)*

### Functional Requirements

**Core Commentary**
- **FR-001**: System MUST automatically detect when a shot has been completed by monitoring screen motion using OpenCV frame differencing
- **FR-002**: System MUST analyze the shot outcome within 2 seconds of the ball stopping
- **FR-003**: System MUST identify shot outcomes: fairway, green, water hazard, bunker, rough, trees, out of bounds, tee shot, unknown
- **FR-004**: System MUST generate natural language commentary appropriate to the identified outcome
- **FR-005**: System MUST deliver commentary via Grok TTS (xAI) within 2 seconds of shot completion
- **FR-006**: Commentary MUST be 50-80 characters ideally; NEVER exceed 150 characters
- **FR-007**: System MUST detect and provide special commentary for score achievements (Birdie, Eagle, Par, Bogey, Hole-in-One, etc.)

**Personality System**
- **FR-008**: System MUST support 7 distinct commentator personalities: Neutral, Sarcastic, Encouraging, Jerk, Sir David (documentary), Ex-Girlfriend, Unhinged
- **FR-009**: Each personality MUST use a specific Grok TTS voice: leo (Neutral/Documentary), rex (Jerk), ara (Encouraging), eve (Sarcastic/Ex-Girlfriend), sal (Unhinged)
- **FR-010**: Personality prompts MUST use Grok TTS inline expression tags sparingly and contextually: `[laugh]`, `[chuckle]`, `[sigh]`, `[tsk]`, `[breath]`, `<whisper>`, `<loud>`, `<slow>`, `<emphasis>`, `<soft>`
- **FR-011**: Commentary frequency MUST be user-configurable (default 20%); only this percentage of shots trigger commentary
- **FR-012**: Player name usage frequency MUST be separately configurable (default 30%)

**Screen Classification**
- **FR-013**: System MUST run a pre-flight screen classifier on every frame before engaging motion detection
- **FR-014**: The classifier MUST use color histogram comparison against training images (zero API calls)
- **FR-015**: If the screen does not resemble an active golf course, the motion detector MUST be reset and the frame skipped
- **FR-016**: The classifier MUST fail-open (assume gameplay) if no training images are present

**API Cost Management**
- **FR-017**: System MUST combine idle detection, player name extraction, achievement detection, and shot outcome analysis into a SINGLE Claude API call per shot
- **FR-018**: System MUST check the pattern cache BEFORE making any API call; cache hits skip all AI analysis
- **FR-019**: Motion detection MUST use vertical-motion filtering to distinguish real shots from aiming adjustments
- **FR-020**: System MUST use claude-haiku for all shot analysis (NOT claude-sonnet or claude-opus)
- **FR-021**: Target API cost per round: under $0.05 analysis + ~$0.35 TTS = under $0.40 total

**Windows Distribution**
- **FR-022**: System MUST run as a Windows system tray application with no visible terminal during use
- **FR-023**: API keys MUST be stored in Windows Credential Manager via `keyring`; they MUST NOT appear in any config file
- **FR-024**: System MUST provide a one-click installer (`install.bat`) that sets up all dependencies automatically
- **FR-025**: System MUST prevent multiple concurrent instances
- **FR-026**: System MUST support multi-monitor setups with selectable capture monitor

**Learning**
- **FR-027**: System MUST operate with zero training examples (zero-shot) with at least 60% accuracy
- **FR-028**: System MUST improve accuracy from user corrections stored in `data/training/`
- **FR-029**: Pattern cache MUST persist between sessions to reduce repeat API calls

---

### Key Entities

- **Shot Event**: timestamp, screenshot, detected outcome, confidence, generated commentary, API cost, was_cached flag, achievement detected
- **Training Example**: screenshot hash, outcome label, reasoning, confidence, source (user/auto)
- **User Correction**: original outcome, corrected outcome, user notes, timestamp
- **Commentary Personality**: name, voice_id, system_prompt (with TTS tag guidance), example_phrases per outcome type
- **Session**: start/end time, shots detected, total API calls, total cost, cache hit rate, accuracy rate
- **Screen Classifier**: gameplay histogram, idle histogram, calibration bias (built from training images at startup)

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users complete initial setup and hear first shot narrated in under 10 minutes from running `install.bat`
- **SC-002**: System detects and narrates at least 90% of shots during a typical 18-hole round
- **SC-003**: Shot outcome identification accuracy starts at 60% with zero training; improves with corrections
- **SC-004**: Commentary delivered within 2 seconds of ball stopping for 95% of shots
- **SC-005**: Total cost per 18-hole round under $0.40 (AI analysis + TTS)
- **SC-006**: All 7 personalities are distinctly recognizable in tone, vocabulary, and voice within 5 shots
- **SC-007**: No API calls fired while the screen shows menus, setup screens, or non-GSPro content
- **SC-008**: Zero API keys stored in plain text files on disk
- **SC-009**: System tray app runs for a full 4-hour session without errors or crashes
- **SC-010**: Commentary length stays under 150 characters 100% of the time

---

### Assumptions

- Users have a Windows 10/11 gaming PC running GS Pro golf simulator
- Users have a valid Anthropic API key (for Claude Haiku shot analysis)
- Users have a valid xAI API key (for Grok TTS voice synthesis, $4.20/1M characters)
- GS Pro is displayed fullscreen on a selectable monitor
- Users play at a normal pace with at least 1-2 seconds between shots
- No ffmpeg or other system-level media dependencies are available on the target PC
- Git is available on the system for auto-update functionality
- Users are non-technical (no manual config file editing, no terminal use during normal operation)
- Internet connectivity is available during gameplay for API calls
