"""Commentary generator service for personality-driven shot commentary."""
import random
from pathlib import Path
from typing import Dict, List, Optional

import anthropic
import yaml

from src.lib.exceptions import CommentaryError
from src.models.outcome import Outcome


class CommentaryGeneratorService:
    """
    Commentary generator service.

    Generates personality-driven commentary using Claude API with
    personality-specific system prompts and example phrases.
    """

    def __init__(
        self,
        api_key: str,
        personality_name: str = "neutral",
        personalities_dir: str = "data/personalities",
        model: str = "claude-sonnet-4-5",
    ):
        """
        Initialize commentary generator.

        Args:
            api_key: Anthropic API key
            personality_name: Name of personality to use (e.g., "neutral", "sarcastic")
            personalities_dir: Directory containing personality YAML files
            model: Claude model to use
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.personality_name = personality_name
        self.personalities_dir = Path(personalities_dir)

        # Load personality configuration
        self.personality_config = self._load_personality(personality_name)

    def generate_commentary(
        self,
        outcome: Outcome,
        confidence: float,
        context: Optional[Dict] = None,
        player_name: Optional[str] = None,
    ) -> str:
        """
        Generate commentary for shot outcome.

        Args:
            outcome: Detected shot outcome
            confidence: Confidence score (0.0-1.0)
            context: Optional context (distance, club, previous shots, etc.)
            player_name: Optional player name to include in commentary

        Returns:
            Commentary text

        Raises:
            CommentaryError: If generation fails
        """
        try:
            # Low confidence: use fallback example phrases
            if confidence < 0.6:
                return self._generate_fallback_commentary(outcome)

            # High confidence: use Claude API for dynamic commentary
            system_prompt = self.personality_config.get("system_prompt", "")
            example_phrases = self.personality_config.get("example_phrases", {})

            # Build user prompt
            user_prompt = self._build_user_prompt(outcome, confidence, context, example_phrases, player_name)

            # Call Claude API with prompt caching to reduce costs
            # System prompt is cached across requests
            message = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
            )

            # Extract commentary
            if not message.content:
                raise CommentaryError("Empty response from Claude API")

            commentary = message.content[0].text.strip()

            # Ensure it's concise (1-2 sentences)
            sentences = commentary.split(". ")
            if len(sentences) > 2:
                commentary = ". ".join(sentences[:2]) + "."

            return commentary

        except anthropic.APIError as e:
            # Fallback to example phrases on API error
            return self._generate_fallback_commentary(outcome)
        except Exception as e:
            raise CommentaryError(f"Failed to generate commentary: {e}")

    def generate_achievement_commentary(
        self,
        achievement: str,
        player_name: Optional[str] = None,
    ) -> str:
        """
        Generate commentary for a score achievement (Birdie, Eagle, etc.).

        Args:
            achievement: Score achievement text (e.g., "Birdie", "Eagle")
            player_name: Optional player name to include in commentary

        Returns:
            Commentary text

        Raises:
            CommentaryError: If generation fails
        """
        try:
            system_prompt = self.personality_config.get("system_prompt", "")

            # Build user prompt for achievement
            prompt = f"Generate enthusiastic commentary for this golf score achievement:\n\n"
            prompt += f"ACHIEVEMENT: {achievement}\n"

            if player_name:
                prompt += f"PLAYER NAME: {player_name}\n"
                prompt += f"\nInclude the player's name '{player_name}' naturally in the commentary."

            prompt += "\nGenerate a concise (1-2 sentences), personality-appropriate, celebratory commentary that captures the excitement of this achievement."

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Extract commentary
            if not message.content:
                raise CommentaryError("Empty response from Claude API")

            commentary = message.content[0].text.strip()

            # Ensure it's concise (1-2 sentences)
            sentences = commentary.split(". ")
            if len(sentences) > 2:
                commentary = ". ".join(sentences[:2]) + "."

            return commentary

        except anthropic.APIError as e:
            # Fallback to simple achievement announcement
            if player_name:
                return f"{achievement} for {player_name}! Great job!"
            return f"{achievement}! Nice shot!"
        except Exception as e:
            # Fallback to simple achievement announcement
            if player_name:
                return f"{achievement} for {player_name}!"
            return f"{achievement}!"

    def get_personality_info(self) -> Dict:
        """
        Get current personality information.

        Returns:
            Dictionary with name, description, tone
        """
        return {
            "name": self.personality_config.get("name", "Unknown"),
            "description": self.personality_config.get("description", ""),
            "tone": self.personality_config.get("tone", "neutral"),
        }

    def list_available_personalities(self) -> List[str]:
        """
        List all available personality names.

        Returns:
            List of personality names (without .yaml extension)
        """
        try:
            yaml_files = self.personalities_dir.glob("*.yaml")
            return [f.stem for f in yaml_files]
        except Exception:
            return []

    def switch_personality(self, personality_name: str) -> None:
        """
        Switch to a different personality.

        Args:
            personality_name: Name of personality to switch to

        Raises:
            CommentaryError: If personality not found
        """
        self.personality_config = self._load_personality(personality_name)
        self.personality_name = personality_name

    def _load_personality(self, personality_name: str) -> Dict:
        """
        Load personality configuration from YAML file.

        Args:
            personality_name: Name of personality

        Returns:
            Personality configuration dict

        Raises:
            CommentaryError: If personality file not found or invalid
        """
        personality_file = self.personalities_dir / f"{personality_name}.yaml"

        if not personality_file.exists():
            raise CommentaryError(f"Personality not found: {personality_name}")

        try:
            with open(personality_file, "r") as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            raise CommentaryError(f"Failed to load personality config: {e}")

    def _build_user_prompt(
        self,
        outcome: Outcome,
        confidence: float,
        context: Optional[Dict],
        example_phrases: Dict,
        player_name: Optional[str] = None,
    ) -> str:
        """
        Build user prompt for commentary generation.

        Args:
            outcome: Shot outcome
            confidence: Confidence score
            context: Optional context
            example_phrases: Example phrases from personality config
            player_name: Optional player name to include

        Returns:
            User prompt string
        """
        prompt = f"Generate commentary for this golf shot:\n\n"
        prompt += f"OUTCOME: {outcome.value}\n"
        prompt += f"CONFIDENCE: {confidence:.2f}\n"

        if player_name:
            prompt += f"PLAYER NAME: {player_name}\n"

        if context:
            prompt += f"CONTEXT: {context}\n"

        # Add example phrases for this outcome
        outcome_key = outcome.value
        if outcome_key in example_phrases:
            phrases = example_phrases[outcome_key]
            prompt += f"\nExample phrases for '{outcome_key}':\n"
            for phrase in phrases[:3]:  # Limit to 3 examples
                prompt += f"- {phrase}\n"

        prompt += "\nGenerate a concise (1-2 sentences), personality-appropriate commentary."

        if player_name:
            prompt += f"\nInclude the player's name '{player_name}' naturally in the commentary."

        return prompt

    def _generate_fallback_commentary(self, outcome: Outcome) -> str:
        """
        Generate fallback commentary using example phrases.

        Args:
            outcome: Shot outcome

        Returns:
            Random example phrase for this outcome
        """
        example_phrases = self.personality_config.get("example_phrases", {})
        outcome_key = outcome.value

        # Get phrases for this outcome
        if outcome_key in example_phrases:
            phrases = example_phrases[outcome_key]
            if phrases:
                return random.choice(phrases)

        # Default fallback if no phrases available
        fallback_map = {
            Outcome.FAIRWAY: "Nice shot.",
            Outcome.GREEN: "On the green.",
            Outcome.WATER: "That's in the water.",
            Outcome.BUNKER: "In the bunker.",
            Outcome.ROUGH: "That's in the rough.",
            Outcome.TREES: "Hit the trees.",
            Outcome.OUT_OF_BOUNDS: "Out of bounds.",
            Outcome.TEE_SHOT: "Ready to tee off.",
            Outcome.UNKNOWN: "Interesting shot.",
        }

        return fallback_map.get(outcome, "Shot detected.")

    def estimate_cost(self) -> float:
        """
        Estimate API cost per commentary generation.

        Returns:
            Estimated cost in USD
        """
        # Claude 3.5 Sonnet pricing:
        # Input: $3.00 / 1M tokens (~200 tokens per commentary)
        # Output: $15.00 / 1M tokens (~50 tokens per commentary)

        input_tokens = 200
        output_tokens = 50

        input_cost = (input_tokens / 1_000_000) * 3.00
        output_cost = (output_tokens / 1_000_000) * 15.00

        return input_cost + output_cost
