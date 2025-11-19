<!--
SYNC IMPACT REPORT
==================
Version change: None → 1.0.0 (Initial constitution)
Ratification date: 2025-11-19

Modified principles: N/A (initial creation)
Added sections:
  - AI-First Development
  - Natural Interaction Over Configuration
  - Learning-Driven Systems
  - Cost-Conscious Intelligence
  - Simplicity & User Experience

Removed sections: N/A

Templates requiring updates:
  ✅ plan-template.md - Reviewed, compatible with AI-first principles
  ✅ spec-template.md - Reviewed, user story structure aligns with natural interaction principles
  ✅ tasks-template.md - Reviewed, compatible with incremental learning approach

Follow-up TODOs: None
-->

# Mully Mouth Constitution

## Core Principles

### I. AI-First Development

Modern AI capabilities (vision, language understanding, learning from examples) MUST be the primary implementation strategy before considering traditional rule-based or configuration-heavy approaches.

**Rules**:
- Every feature MUST explore AI solutions first, fallback to traditional methods only when AI is insufficient
- AI models MUST handle complexity that would otherwise require manual configuration
- Zero-shot and few-shot learning MUST be preferred over extensive training data requirements
- Code MUST delegate pattern recognition, context understanding, and decision-making to AI when feasible

**Rationale**: Claude Vision and similar models now possess capabilities that make manual feature engineering, complex configuration systems, and rule-based logic unnecessary for many tasks. Leveraging AI reduces development time, maintenance burden, and user complexity.

### II. Natural Interaction Over Configuration

Users MUST interact with systems through natural language and examples rather than through configuration files, forms, or technical interfaces.

**Rules**:
- Training and setup MUST use show-and-tell (upload examples + describe) instead of parameter configuration
- User corrections MUST be conversational (describe what's wrong) not technical (adjust thresholds)
- Configuration files MUST be minimal, containing only essential API keys and high-level preferences
- NO pixel coordinates, screen regions, behavior flags, or technical parameters in user-facing configuration
- Documentation MUST explain features through examples and conversations, not configuration syntax

**Rationale**: Users understand their domain better than technical systems. Natural language interaction removes the translation barrier between user knowledge and system configuration.

### III. Learning-Driven Systems

Systems MUST improve through usage rather than requiring upfront comprehensive configuration or training.

**Rules**:
- Systems MUST operate with minimal or zero training (zero-shot capability)
- Systems MUST accept corrections during operation and learn from them (active learning)
- Pattern memory MUST grow from actual usage examples, not synthetic training datasets
- Confidence levels MUST be tracked, triggering user confirmation when low
- Learning improvements MUST be visible to users (noticeably better accuracy over time)

**Rationale**: Users cannot anticipate all scenarios during setup. Systems that learn from real-world usage adapt to the user's specific environment and edge cases automatically.

### IV. Cost-Conscious Intelligence

AI API usage MUST be optimized through smart triggering, not disabled or limited to preserve quality.

**Rules**:
- Cheap traditional methods (OpenCV motion detection, simple heuristics) MUST handle high-frequency operations
- Expensive AI calls MUST only occur when necessary (uncertainty, new patterns, user-requested analysis)
- Pattern caching and confidence-based calls MUST reduce redundant AI invocations
- Per-operation costs MUST be measured and optimized to enable affordable sustained usage
- Target: AI-powered features should cost cents per session, not dollars

**Rationale**: AI is powerful but expensive at scale. Smart hybrid approaches using traditional methods for routine tasks and AI for complex decisions enable practical, affordable AI-first systems.

### V. Simplicity & User Experience

Every user-facing feature MUST be explainable in under 2 minutes and executable in under 10 minutes.

**Rules**:
- Setup workflows MUST complete in under 10 minutes for first-time users
- Features MUST work with 3-5 examples, not hundreds of training samples
- Error messages MUST be conversational and actionable, not technical
- Users MUST be able to explain the system to others without referring to documentation
- Progress and learning MUST be visible and understandable to non-technical users
- NO manual configuration of screen regions, thresholds, or algorithmic parameters

**Rationale**: If users need extensive documentation or technical knowledge, the AI hasn't done its job. Simplicity is a feature, not a compromise.

## Technical Standards

### API Integration

- Claude Vision API for image understanding and pattern recognition
- Text-to-speech for natural output (ElevenLabs, Google, Azure)
- Screen capture and basic computer vision (OpenCV) for event detection
- All external APIs MUST have fallback strategies or graceful degradation

### Performance & Cost Targets

- Setup time: <10 minutes (first launch to operational)
- API calls per session: <20 (through intelligent caching and traditional pre-filtering)
- Cost per session: <$0.05 (enabling daily use affordability)
- Accuracy targets: 60% zero-shot → 80% after 1 session → 90% after 3 sessions
- Response latency: <2 seconds for AI-powered commentary (acceptable for non-real-time use cases)

### Code Architecture

- Python-first for AI integration and rapid prototyping
- Library-first design: core functionality as importable modules
- CLI interface for user interaction
- Minimal dependencies: AI SDK, screen capture, TTS, standard libraries
- Clear separation: cheap event detection → AI analysis → user output

## Development Workflow

### Feature Development

1. **Validate AI Capability**: Prove the AI can handle the core task with zero or minimal examples
2. **Build Hybrid System**: Combine cheap traditional methods (filtering, detection) with expensive AI (analysis, understanding)
3. **Measure Costs**: Track API calls and costs per operation, optimize to target thresholds
4. **Test Learning**: Verify system improves from corrections and examples
5. **Simplify UX**: Remove any configuration that AI can infer or learn

### Testing Philosophy

- **Zero-shot tests**: Verify core functionality works with no training
- **Few-shot tests**: Verify learning from 3-5 examples
- **Active learning tests**: Verify corrections improve future accuracy
- **Cost tests**: Ensure API usage stays within target costs
- **User experience tests**: Setup and operation within time limits

### Prohibited Patterns

- ❌ Complex configuration files with technical parameters
- ❌ Manual screen region definition or pixel coordinate specification
- ❌ Behavior checkboxes or flag-based feature enabling
- ❌ Extensive training datasets or labeling interfaces
- ❌ Rules engines or pattern matching code that AI can handle
- ❌ Unoptimized AI calls on every frame or frequent event

## Governance

### Amendment Process

Constitution changes require:
1. Proposal documenting the principle change and rationale
2. Review of impact on existing features and templates
3. Version bump following semantic versioning
4. Update of all affected templates and documentation

### Versioning Policy

- **MAJOR (X.0.0)**: Removing or fundamentally redefining a core principle
- **MINOR (1.X.0)**: Adding new principles or significantly expanding guidance
- **PATCH (1.0.X)**: Clarifications, wording improvements, non-semantic changes

### Compliance

- All feature specifications MUST align with core principles
- Implementation plans MUST reference constitution principles in design decisions
- Code reviews MUST verify adherence to AI-first, natural interaction, and cost-conscious patterns
- Complexity (traditional approaches over AI) MUST be justified with specific rationale

### Future Evolution

As AI capabilities improve (faster, cheaper, more accurate):
- Configuration SHOULD migrate to AI inference
- Manual training SHOULD migrate to zero-shot
- User corrections SHOULD decrease as base models improve

This constitution reflects the AI-first era where models handle complexity that previously required code and configuration.

**Version**: 1.0.0 | **Ratified**: 2025-11-19 | **Last Amended**: 2025-11-19
