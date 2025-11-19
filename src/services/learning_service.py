"""Learning service for managing few-shot examples and user corrections."""
import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from src.lib.exceptions import LearningError
from src.models.correction import UserCorrection
from src.models.outcome import Outcome


class LearningService:
    """
    Learning service for active learning and few-shot examples.

    Manages user corrections and few-shot example database to improve
    AI accuracy over time.
    """

    def __init__(
        self,
        corrections_file: str = "data/training/corrections.json",
        examples_file: str = "data/training/few_shot_examples.json",
        max_examples_per_outcome: int = 5,
    ):
        """
        Initialize learning service.

        Args:
            corrections_file: Path to corrections JSON file
            examples_file: Path to few-shot examples JSON file
            max_examples_per_outcome: Maximum examples to keep per outcome type
        """
        self.corrections_file = Path(corrections_file)
        self.examples_file = Path(examples_file)
        self.max_examples_per_outcome = max_examples_per_outcome

        # Ensure directories exist
        self.corrections_file.parent.mkdir(parents=True, exist_ok=True)
        self.examples_file.parent.mkdir(parents=True, exist_ok=True)

        # Load data
        self.corrections: List[Dict] = self._load_corrections()
        self.few_shot_examples: Dict[str, List[Dict]] = self._load_examples()

    def add_correction(self, correction: UserCorrection) -> None:
        """
        Record a user correction.

        Args:
            correction: UserCorrection instance
        """
        # Convert to dict and append
        correction_data = correction.to_dict()
        self.corrections.append(correction_data)

        # Persist
        self._save_corrections()

    def get_corrections(self) -> List[Dict]:
        """
        Get all recorded corrections.

        Returns:
            List of correction dictionaries
        """
        return self.corrections.copy()

    def get_corrections_for_outcome(self, outcome: Outcome) -> List[Dict]:
        """
        Get corrections where the corrected outcome matches.

        Args:
            outcome: Outcome to filter by

        Returns:
            List of matching corrections
        """
        return [
            c
            for c in self.corrections
            if c["corrected_outcome"] == str(outcome)
        ]

    def add_few_shot_example(
        self,
        outcome: Outcome,
        screenshot_hash: str,
        reasoning: str,
        confidence: float = 1.0,
    ) -> None:
        """
        Add a few-shot example for an outcome type.

        Args:
            outcome: Outcome type
            screenshot_hash: Hash of the screenshot
            reasoning: Explanation of why this is the correct outcome
            confidence: Confidence score (default: 1.0 for manual examples)
        """
        outcome_key = outcome.value

        # Initialize list if not exists
        if outcome_key not in self.few_shot_examples:
            self.few_shot_examples[outcome_key] = []

        # Add example
        example = {
            "screenshot_hash": screenshot_hash,
            "outcome": outcome_key,
            "reasoning": reasoning,
            "confidence": confidence,
        }

        self.few_shot_examples[outcome_key].append(example)

        # Limit to max examples per outcome
        if len(self.few_shot_examples[outcome_key]) > self.max_examples_per_outcome:
            # Keep most recent examples
            self.few_shot_examples[outcome_key] = self.few_shot_examples[outcome_key][
                -self.max_examples_per_outcome :
            ]

        # Persist
        self._save_examples()

    def get_few_shot_examples(
        self, outcome: Optional[Outcome] = None, limit: int = 3
    ) -> List[Dict]:
        """
        Get few-shot examples for prompting AI.

        Args:
            outcome: Optional outcome to filter by
            limit: Maximum number of examples to return

        Returns:
            List of example dictionaries
        """
        if outcome:
            outcome_key = outcome.value
            examples = self.few_shot_examples.get(outcome_key, [])
            return examples[-limit:]  # Most recent
        else:
            # Return examples across all outcomes
            all_examples = []
            for outcome_examples in self.few_shot_examples.values():
                all_examples.extend(outcome_examples[-2:])  # 2 per outcome
            return all_examples[:limit]

    def get_learning_stats(self) -> Dict:
        """
        Get learning statistics.

        Returns:
            Dictionary with total corrections, examples, accuracy improvement
        """
        total_corrections = len(self.corrections)
        total_examples = sum(len(ex) for ex in self.few_shot_examples.values())

        # Calculate accuracy improvement (corrections per outcome)
        correction_by_outcome: Dict[str, int] = {}
        for correction in self.corrections:
            outcome = correction["original_outcome"]
            correction_by_outcome[outcome] = correction_by_outcome.get(outcome, 0) + 1

        return {
            "total_corrections": total_corrections,
            "total_examples": total_examples,
            "corrections_by_outcome": correction_by_outcome,
            "examples_by_outcome": {
                k: len(v) for k, v in self.few_shot_examples.items()
            },
        }

    def promote_correction_to_example(self, correction_index: int) -> None:
        """
        Convert a correction into a few-shot example.

        Args:
            correction_index: Index of correction in corrections list

        Raises:
            LearningError: If index invalid
        """
        if correction_index < 0 or correction_index >= len(self.corrections):
            raise LearningError(f"Invalid correction index: {correction_index}")

        correction = self.corrections[correction_index]

        # Create few-shot example
        outcome = Outcome(correction["corrected_outcome"])
        reasoning = f"User correction: was {correction['original_outcome']}, actually {correction['corrected_outcome']}"

        if correction.get("user_notes"):
            reasoning += f". Notes: {correction['user_notes']}"

        self.add_few_shot_example(
            outcome=outcome,
            screenshot_hash="correction",  # Placeholder
            reasoning=reasoning,
            confidence=1.0,
        )

    def clear_corrections(self) -> None:
        """Clear all corrections (useful for testing or reset)."""
        self.corrections = []
        self._save_corrections()

    def clear_examples(self) -> None:
        """Clear all few-shot examples (useful for testing or reset)."""
        self.few_shot_examples = {}
        self._save_examples()

    def _load_corrections(self) -> List[Dict]:
        """Load corrections from JSON file."""
        if not self.corrections_file.exists():
            return []

        try:
            with open(self.corrections_file, "r") as f:
                data = json.load(f)
                return data.get("corrections", [])
        except Exception as e:
            raise LearningError(f"Failed to load corrections: {e}")

    def _save_corrections(self) -> None:
        """Save corrections to JSON file."""
        try:
            data = {"corrections": self.corrections}
            with open(self.corrections_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise LearningError(f"Failed to save corrections: {e}")

    def _load_examples(self) -> Dict[str, List[Dict]]:
        """Load few-shot examples from JSON file."""
        if not self.examples_file.exists():
            return {}

        try:
            with open(self.examples_file, "r") as f:
                data = json.load(f)
                return data.get("examples", {})
        except Exception as e:
            raise LearningError(f"Failed to load examples: {e}")

    def _save_examples(self) -> None:
        """Save few-shot examples to JSON file."""
        try:
            data = {"examples": self.few_shot_examples}
            with open(self.examples_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise LearningError(f"Failed to save examples: {e}")
