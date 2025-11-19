"""Unit tests for LearningService."""
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.models.correction import UserCorrection
from src.models.outcome import Outcome
from src.services.learning_service import LearningService


@pytest.fixture
def learning_service():
    """Create a temporary learning service for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        corrections_file = Path(tmpdir) / "corrections.json"
        examples_file = Path(tmpdir) / "examples.json"
        service = LearningService(
            corrections_file=str(corrections_file),
            examples_file=str(examples_file),
            max_examples_per_outcome=5,
        )
        yield service


def test_learning_service_initialization(learning_service):
    """Test learning service initialization."""
    assert learning_service is not None
    assert len(learning_service.corrections) == 0
    assert len(learning_service.few_shot_examples) == 0


def test_add_correction(learning_service):
    """Test adding a user correction."""
    correction = UserCorrection(
        original_outcome=Outcome.WATER,
        corrected_outcome=Outcome.BUNKER,
        timestamp=datetime.now(),
        user_notes="Ball was actually in bunker, not water",
    )

    learning_service.add_correction(correction)

    assert len(learning_service.corrections) == 1
    assert learning_service.corrections[0]["original_outcome"] == str(Outcome.WATER)
    assert learning_service.corrections[0]["corrected_outcome"] == str(Outcome.BUNKER)


def test_get_corrections(learning_service):
    """Test retrieving all corrections."""
    # Add multiple corrections
    for i in range(3):
        correction = UserCorrection(
            original_outcome=Outcome.ROUGH,
            corrected_outcome=Outcome.FAIRWAY,
            timestamp=datetime.now(),
        )
        learning_service.add_correction(correction)

    corrections = learning_service.get_corrections()
    assert len(corrections) == 3


def test_get_corrections_for_outcome(learning_service):
    """Test filtering corrections by outcome."""
    # Add corrections for different outcomes
    learning_service.add_correction(
        UserCorrection(
            original_outcome=Outcome.WATER,
            corrected_outcome=Outcome.GREEN,
            timestamp=datetime.now(),
        )
    )
    learning_service.add_correction(
        UserCorrection(
            original_outcome=Outcome.BUNKER,
            corrected_outcome=Outcome.GREEN,
            timestamp=datetime.now(),
        )
    )
    learning_service.add_correction(
        UserCorrection(
            original_outcome=Outcome.ROUGH,
            corrected_outcome=Outcome.FAIRWAY,
            timestamp=datetime.now(),
        )
    )

    # Filter by GREEN
    green_corrections = learning_service.get_corrections_for_outcome(Outcome.GREEN)
    assert len(green_corrections) == 2


def test_add_few_shot_example(learning_service):
    """Test adding few-shot examples."""
    learning_service.add_few_shot_example(
        outcome=Outcome.FAIRWAY,
        screenshot_hash="abc123",
        reasoning="Ball clearly on fairway",
        confidence=1.0,
    )

    assert "fairway" in learning_service.few_shot_examples
    assert len(learning_service.few_shot_examples["fairway"]) == 1


def test_max_examples_per_outcome(learning_service):
    """Test that max examples limit is enforced."""
    # Add 10 examples (max is 5)
    for i in range(10):
        learning_service.add_few_shot_example(
            outcome=Outcome.GREEN,
            screenshot_hash=f"hash{i}",
            reasoning=f"Example {i}",
            confidence=0.9,
        )

    # Should only keep 5 most recent
    assert len(learning_service.few_shot_examples["green"]) == 5


def test_get_few_shot_examples(learning_service):
    """Test retrieving few-shot examples."""
    # Add examples for different outcomes
    learning_service.add_few_shot_example(
        outcome=Outcome.WATER,
        screenshot_hash="water1",
        reasoning="Ball in water",
        confidence=1.0,
    )
    learning_service.add_few_shot_example(
        outcome=Outcome.BUNKER,
        screenshot_hash="bunker1",
        reasoning="Ball in sand",
        confidence=0.95,
    )

    # Get all examples
    examples = learning_service.get_few_shot_examples(limit=10)
    assert len(examples) >= 2

    # Get examples for specific outcome
    water_examples = learning_service.get_few_shot_examples(outcome=Outcome.WATER, limit=5)
    assert len(water_examples) == 1
    assert water_examples[0]["outcome"] == "water"


def test_get_learning_stats(learning_service):
    """Test getting learning statistics."""
    # Add corrections and examples
    learning_service.add_correction(
        UserCorrection(
            original_outcome=Outcome.WATER,
            corrected_outcome=Outcome.GREEN,
            timestamp=datetime.now(),
        )
    )
    learning_service.add_few_shot_example(
        outcome=Outcome.FAIRWAY,
        screenshot_hash="test1",
        reasoning="Test example",
        confidence=0.9,
    )

    stats = learning_service.get_learning_stats()

    assert stats["total_corrections"] == 1
    assert stats["total_examples"] == 1
    assert "corrections_by_outcome" in stats
    assert "examples_by_outcome" in stats


def test_promote_correction_to_example(learning_service):
    """Test promoting a correction to a few-shot example."""
    # Add correction
    correction = UserCorrection(
        original_outcome=Outcome.ROUGH,
        corrected_outcome=Outcome.TREES,
        timestamp=datetime.now(),
        user_notes="Actually hit trees",
    )
    learning_service.add_correction(correction)

    # Promote to example
    learning_service.promote_correction_to_example(0)

    # Should now have a few-shot example
    assert "trees" in learning_service.few_shot_examples
    assert len(learning_service.few_shot_examples["trees"]) == 1


def test_clear_corrections(learning_service):
    """Test clearing all corrections."""
    # Add corrections
    for i in range(3):
        learning_service.add_correction(
            UserCorrection(
                original_outcome=Outcome.WATER,
                corrected_outcome=Outcome.GREEN,
                timestamp=datetime.now(),
            )
        )

    # Clear
    learning_service.clear_corrections()

    assert len(learning_service.corrections) == 0


def test_clear_examples(learning_service):
    """Test clearing all few-shot examples."""
    # Add examples
    learning_service.add_few_shot_example(
        outcome=Outcome.FAIRWAY,
        screenshot_hash="test",
        reasoning="Test",
        confidence=0.9,
    )

    # Clear
    learning_service.clear_examples()

    assert len(learning_service.few_shot_examples) == 0


def test_persistence(learning_service):
    """Test that corrections and examples persist across instances."""
    # Add data
    learning_service.add_correction(
        UserCorrection(
            original_outcome=Outcome.BUNKER,
            corrected_outcome=Outcome.FAIRWAY,
            timestamp=datetime.now(),
        )
    )
    learning_service.add_few_shot_example(
        outcome=Outcome.GREEN,
        screenshot_hash="persist_test",
        reasoning="Persistence test",
        confidence=1.0,
    )

    # Files are auto-saved, create new instance
    new_service = LearningService(
        corrections_file=str(learning_service.corrections_file),
        examples_file=str(learning_service.examples_file),
    )

    # Should have loaded data
    assert len(new_service.corrections) == 1
    assert len(new_service.few_shot_examples) >= 1
