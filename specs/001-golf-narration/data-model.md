# Data Model: AI Voice Caddy for GS Pro

**Date**: 2025-11-19
**Phase**: 1 - Design

## Overview

This document defines the core data entities for the AI Voice Caddy system. All entities are implemented as Python dataclasses for simplicity and type safety.

## Entity Definitions

### 1. Shot Event

Represents a detected golf shot with analysis results and generated commentary.

**Attributes**:

| Name | Type | Description | Constraints |
|------|------|-------------|-------------|
| `id` | `str` | Unique identifier (UUID) | Required, unique |
| `timestamp` | `datetime` | When shot was detected | Required |
| `screenshot` | `np.ndarray` | Captured frame (OpenCV format) | Required, RGB image |
| `screenshot_hash` | `str` | Perceptual hash for caching | Required, computed |
| `detected_outcome` | `str` | AI-identified outcome type | Required, enum |
| `confidence` | `float` | AI confidence score | Required, 0.0-1.0 |
| `commentary_text` | `str` | Generated commentary | Required |
| `was_cached` | `bool` | If result came from cache | Required |
| `api_cost` | `float` | Cost of AI call (if any) | Required, USD |
| `correction` | `Optional[UserCorrection]` | If user corrected | Optional |

**Outcome Types** (enum):
- `fairway`
- `green`
- `water`
- `bunker`
- `rough`
- `trees`
- `out_of_bounds`
- `tee_shot`
- `unknown`

**Relationships**:
- Belongs to one `Session`
- May have one `UserCorrection`
- References one `TrainingExample` if cached

**Storage**: JSON files in `data/sessions/{session_id}/shots.json`

**Example**:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import numpy as np

@dataclass
class ShotEvent:
    id: str
    timestamp: datetime
    screenshot: np.ndarray
    screenshot_hash: str
    detected_outcome: str  # Outcome enum
    confidence: float
    commentary_text: str
    was_cached: bool
    api_cost: float
    correction: Optional['UserCorrection'] = None

    def to_dict(self) -> dict:
        """Serialize to JSON (exclude screenshot)"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'screenshot_hash': self.screenshot_hash,
            'detected_outcome': self.detected_outcome,
            'confidence': self.confidence,
            'commentary_text': self.commentary_text,
            'was_cached': self.was_cached,
            'api_cost': self.api_cost,
            'correction': self.correction.to_dict() if self.correction else None
        }
```

### 2. Training Example

Represents a user-provided screenshot with labeled outcome for few-shot learning.

**Attributes**:

| Name | Type | Description | Constraints |
|------|------|-------------|-------------|
| `id` | `str` | Unique identifier (UUID) | Required, unique |
| `screenshot_path` | `str` | Path to saved screenshot | Required, valid path |
| `screenshot_hash` | `str` | Perceptual hash | Required, indexed |
| `outcome_label` | `str` | User-provided label | Required, enum |
| `description` | `str` | User description | Optional |
| `created_at` | `datetime` | When added | Required |
| `usage_count` | `int` | Times used in cache match | Default: 0 |
| `last_used` | `Optional[datetime]` | Last match timestamp | Optional |

**Relationships**:
- Referenced by `ShotEvent` (when cached)
- Independent lifecycle (persists across sessions)

**Storage**: JSON metadata in `data/training/examples.json`, screenshots in `data/training/images/`

**Example**:
```python
@dataclass
class TrainingExample:
    id: str
    screenshot_path: str
    screenshot_hash: str
    outcome_label: str  # Outcome enum
    description: str
    created_at: datetime
    usage_count: int = 0
    last_used: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'screenshot_path': self.screenshot_path,
            'screenshot_hash': self.screenshot_hash,
            'outcome_label': self.outcome_label,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }
```

### 3. User Correction

Represents feedback when the AI misidentified a shot outcome.

**Attributes**:

| Name | Type | Description | Constraints |
|------|------|-------------|-------------|
| `id` | `str` | Unique identifier (UUID) | Required, unique |
| `shot_event_id` | `str` | Associated shot | Required, foreign key |
| `incorrect_prediction` | `str` | What AI said | Required, enum |
| `correct_outcome` | `str` | User-provided truth | Required, enum |
| `user_explanation` | `str` | Why AI was wrong | Optional |
| `timestamp` | `datetime` | When corrected | Required |
| `screenshot_hash` | `str` | For retraining | Required |

**Relationships**:
- Belongs to one `ShotEvent`
- Creates/updates one `TrainingExample`

**Storage**: JSON in `data/corrections.json`

**Example**:
```python
@dataclass
class UserCorrection:
    id: str
    shot_event_id: str
    incorrect_prediction: str  # Outcome enum
    correct_outcome: str  # Outcome enum
    user_explanation: str
    timestamp: datetime
    screenshot_hash: str

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'shot_event_id': self.shot_event_id,
            'incorrect_prediction': self.incorrect_prediction,
            'correct_outcome': self.correct_outcome,
            'user_explanation': self.user_explanation,
            'timestamp': self.timestamp.isoformat(),
            'screenshot_hash': self.screenshot_hash
        }
```

### 4. Commentary Personality

Represents a configurable style of narration.

**Attributes**:

| Name | Type | Description | Constraints |
|------|------|-------------|-------------|
| `name` | `str` | Personality name | Required, unique |
| `description` | `str` | User-facing description | Required |
| `system_prompt` | `str` | AI system prompt | Required |
| `example_phrases` | `Dict[str, List[str]]` | Examples per outcome | Required |
| `tone` | `str` | Tone descriptor | Required |

**Storage**: YAML files in `data/personalities/{name}.yaml`

**Example**:
```python
from typing import List, Dict

@dataclass
class CommentaryPersonality:
    name: str
    description: str
    system_prompt: str
    example_phrases: Dict[str, List[str]]
    tone: str

    @classmethod
    def from_yaml(cls, path: str) -> 'CommentaryPersonality':
        """Load from YAML file"""
        pass

    def get_examples_for(self, outcome: str) -> List[str]:
        """Get example phrases for outcome type"""
        return self.example_phrases.get(outcome, [])
```

**Personality YAML Structure**:
```yaml
name: "Sarcastic"
description: "Humorous, light-hearted ribbing"
tone: "sarcastic"
system_prompt: |
  You are a sarcastic golf commentator. Make witty, humorous comments
  about shots. Keep it fun, never mean-spirited.
example_phrases:
  water:
    - "And... it's swimming. That's gonna cost you."
    - "Nice splash! Hope you brought a towel."
  bunker:
    - "Found the beach. Too bad it's not vacation."
    - "Sandbox time. Building castles today?"
  fairway:
    - "Oh NOW you remember how to play golf."
    - "Finally. Took you long enough."
```

### 5. Session

Represents a single round of golf with aggregate statistics.

**Attributes**:

| Name | Type | Description | Constraints |
|------|------|-------------|-------------|
| `id` | `str` | Unique identifier (UUID) | Required, unique |
| `start_time` | `datetime` | When round started | Required |
| `end_time` | `Optional[datetime]` | When round ended | Optional |
| `personality_name` | `str` | Active personality | Required |
| `shot_events` | `List[ShotEvent]` | All shots in round | Required |
| `total_api_calls` | `int` | Number of AI calls | Computed |
| `total_cost` | `float` | Total AI spend | Computed, USD |
| `cache_hit_rate` | `float` | % cached shots | Computed, 0.0-1.0 |
| `accuracy_rate` | `float` | % correct (if corrected) | Computed, 0.0-1.0 |

**Relationships**:
- Has many `ShotEvent`
- References one `CommentaryPersonality`

**Storage**: JSON files in `data/sessions/{session_id}/session.json`

**Example**:
```python
from typing import List

@dataclass
class Session:
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    personality_name: str
    shot_events: List[ShotEvent]

    @property
    def total_api_calls(self) -> int:
        return sum(1 for shot in self.shot_events if not shot.was_cached)

    @property
    def total_cost(self) -> float:
        return sum(shot.api_cost for shot in self.shot_events)

    @property
    def cache_hit_rate(self) -> float:
        if not self.shot_events:
            return 0.0
        cached = sum(1 for shot in self.shot_events if shot.was_cached)
        return cached / len(self.shot_events)

    @property
    def accuracy_rate(self) -> float:
        corrected_shots = [s for s in self.shot_events if s.correction]
        if not corrected_shots:
            return 1.0  # No corrections = 100% accurate
        return 1.0 - (len(corrected_shots) / len(self.shot_events))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'personality_name': self.personality_name,
            'total_shots': len(self.shot_events),
            'total_api_calls': self.total_api_calls,
            'total_cost': self.total_cost,
            'cache_hit_rate': self.cache_hit_rate,
            'accuracy_rate': self.accuracy_rate
        }
```

## Entity Relationships

```
Session (1) ─── (many) ShotEvent
                         │
                         ├── (0..1) UserCorrection
                         │
                         └── (0..1) TrainingExample (via hash match)

TrainingExample (many) ─── referenced by ─── (many) ShotEvent

CommentaryPersonality (1) ─── used by ─── (many) Session
```

## Data Storage Structure

```
data/
├── sessions/
│   └── {session_id}/
│       ├── session.json          # Session metadata
│       └── shots.json             # Array of ShotEvent
├── training/
│   ├── examples.json              # Array of TrainingExample metadata
│   └── images/
│       └── {example_id}.png       # Training screenshots
├── cache/
│   └── pattern_cache.json         # Hash → outcome mappings
├── corrections.json               # Array of UserCorrection
└── personalities/
    ├── encouraging.yaml
    ├── neutral.yaml
    └── sarcastic.yaml
```

## Data Access Patterns

### Pattern 1: Shot Detection & Analysis
```python
# 1. Detect shot (motion stops)
# 2. Capture screenshot
# 3. Compute perceptual hash
# 4. Check pattern cache
if cached_outcome := pattern_cache.find_match(screenshot_hash):
    # Use cached result (no API call)
    shot_event = ShotEvent(cached=True, api_cost=0.0, ...)
else:
    # AI analysis required
    outcome, confidence = ai_analyzer.analyze(screenshot)
    shot_event = ShotEvent(cached=False, api_cost=0.0023, ...)
    pattern_cache.add(screenshot_hash, outcome, confidence)

# 5. Generate commentary
# 6. Speak via TTS
# 7. Save to session
```

### Pattern 2: User Correction
```python
# 1. User presses Ctrl+C
# 2. Prompt for correct outcome
correct_outcome = input("What actually happened? ")

# 3. Create correction record
correction = UserCorrection(
    shot_event_id=shot.id,
    incorrect_prediction=shot.detected_outcome,
    correct_outcome=correct_outcome,
    ...
)

# 4. Update shot event
shot.correction = correction

# 5. Create training example
training_example = TrainingExample(
    screenshot_hash=shot.screenshot_hash,
    outcome_label=correct_outcome,
    ...
)

# 6. Update pattern cache
pattern_cache.update(shot.screenshot_hash, correct_outcome, confidence=1.0)
```

### Pattern 3: Training Mode
```python
# 1. User uploads screenshot
# 2. User provides label
label = input("What outcome is this? ")

# 3. Compute hash
screenshot_hash = compute_perceptual_hash(screenshot)

# 4. Create training example
example = TrainingExample(
    screenshot_path=save_screenshot(screenshot),
    screenshot_hash=screenshot_hash,
    outcome_label=label,
    ...
)

# 5. Add to pattern cache immediately
pattern_cache.add(screenshot_hash, label, confidence=1.0)
```

## Validation Rules

### Shot Event
- `confidence` must be between 0.0 and 1.0
- `detected_outcome` must be valid enum value
- `api_cost` must be non-negative
- `screenshot` must be valid image array

### Training Example
- `screenshot_path` must exist on filesystem
- `outcome_label` must be valid enum value
- `screenshot_hash` must be unique in cache

### User Correction
- `correct_outcome` must differ from `incorrect_prediction`
- `shot_event_id` must reference existing shot

### Session
- `end_time` must be after `start_time` (if set)
- `personality_name` must reference valid personality file

## Migration Strategy

**Initial Setup**:
- Create data directory structure
- Copy default personality YAML files
- Initialize empty pattern cache
- Create empty corrections file

**Future Migrations**:
- Add migration scripts in `data/migrations/`
- Version data files with schema version
- Provide upgrade path for breaking changes

## Performance Considerations

**In-Memory Caching**:
- Pattern cache loaded at startup (hash → outcome mapping)
- Current session kept in memory
- Training examples indexed by hash

**Lazy Loading**:
- Historical sessions loaded on-demand
- Screenshots not kept in memory after analysis
- Training example images loaded only when needed

**Batch Operations**:
- Session writes batched (every 10 shots or 5 minutes)
- Pattern cache persisted on shutdown + periodic saves
- Corrections appended immediately (critical for learning)

## Security & Privacy

**Sensitive Data**:
- Screenshots may contain GS Pro UI (no personal data)
- No external data collection
- All data stored locally
- API keys in config, never in data files

**Data Retention**:
- Sessions: Keep indefinitely (user learning data)
- Screenshots: Keep training examples, discard session screenshots after 30 days
- Corrections: Keep indefinitely (valuable for accuracy)
- Cache: Keep indefinitely (accumulating knowledge)

**User Control**:
- Provide data export (JSON)
- Provide data deletion command
- Clear cache command for fresh start
