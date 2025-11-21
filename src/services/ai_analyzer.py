"""AI analyzer service for shot outcome detection using Claude Vision API."""
import base64
from io import BytesIO
from typing import Optional

import anthropic
import numpy as np
from PIL import Image

from src.lib.exceptions import AIServiceError
from src.models.outcome import Outcome


class AIAnalyzerService:
    """
    AI analyzer service using Claude Vision API.

    Analyzes GS Pro screenshots to detect shot outcomes using Claude's
    vision capabilities with structured output.
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5"):
        """
        Initialize AI analyzer.

        Args:
            api_key: Anthropic API key
            model: Claude model to use (default: claude-sonnet-4-5)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.system_prompt = self._build_system_prompt()

    def analyze_shot(
        self,
        screenshot: np.ndarray,
        few_shot_examples: Optional[list] = None,
    ) -> tuple[Outcome, float, dict]:
        """
        Analyze screenshot to detect shot outcome.

        Args:
            screenshot: Screenshot as RGB numpy array
            few_shot_examples: Optional list of few-shot examples for context

        Returns:
            Tuple of (outcome, confidence, raw_response)

        Raises:
            AIServiceError: If API call fails or response invalid
        """
        try:
            # Convert screenshot to base64
            image_data = self._encode_image(screenshot)

            # Build user prompt
            user_prompt = self._build_user_prompt(few_shot_examples)

            # Call Claude Vision API with prompt caching to reduce costs
            # System prompt is cached across requests
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=[
                    {
                        "type": "text",
                        "text": self.system_prompt,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": user_prompt,
                            },
                        ],
                    }
                ],
            )

            # Parse response
            outcome, confidence = self._parse_response(message)

            # Extract raw response for debugging
            raw_response = {
                "id": message.id,
                "model": message.model,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                },
                "content": message.content[0].text if message.content else "",
            }

            return (outcome, confidence, raw_response)

        except anthropic.APIError as e:
            raise AIServiceError(f"Anthropic API error: {e}")
        except Exception as e:
            raise AIServiceError(f"Failed to analyze shot: {e}")

    def extract_player_name(self, screenshot: np.ndarray) -> Optional[str]:
        """
        Extract player name from screenshot using Claude Vision API.

        Args:
            screenshot: Screenshot to analyze

        Returns:
            Player name if found, None otherwise

        Raises:
            AIServiceError: If API call fails
        """
        try:
            # Crop upper left corner for better focus and reduce image size
            height, width = screenshot.shape[:2]
            name_region = screenshot[0:int(height * 0.15), 0:int(width * 0.35)]

            # Further resize the name region to minimize tokens
            # Name extraction doesn't need high resolution
            from PIL import Image as PILImage
            import cv2
            name_img = PILImage.fromarray(name_region.astype("uint8"), "RGB")
            # Resize to max 400x150 - plenty for reading text
            name_img = name_img.resize((min(400, name_img.width), min(150, name_img.height)), PILImage.Resampling.LANCZOS)
            name_region = np.array(name_img)

            # Convert screenshot to base64
            image_data = self._encode_image(name_region)

            # Call Claude Vision API with specific prompt for name extraction
            message = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": "Look at the upper left corner of this golf simulator screen. What is the player's name displayed? Reply with ONLY the name, nothing else. If you cannot find a name, reply with 'NONE'.",
                            },
                        ],
                    }
                ],
            )

            # Parse response
            if not message.content:
                return None

            name = message.content[0].text.strip()

            # Check if name was found
            if name.upper() == "NONE" or not name:
                return None

            return name

        except anthropic.APIError as e:
            # API error, return None
            return None
        except Exception as e:
            return None

    def detect_score_achievement(self, screenshot: np.ndarray) -> Optional[str]:
        """
        Detect if screenshot shows a score achievement in the center (Birdie, Eagle, Par, Bogey, etc.).

        Args:
            screenshot: Screenshot to analyze

        Returns:
            Score achievement text if found (e.g., "Birdie", "Eagle"), None otherwise
        """
        try:
            # Crop center region where score achievements are typically displayed
            height, width = screenshot.shape[:2]
            # Center 40% x 40% region
            center_y = int(height * 0.3)
            center_x = int(width * 0.3)
            center_h = int(height * 0.4)
            center_w = int(width * 0.4)

            center_region = screenshot[center_y:center_y + center_h, center_x:center_x + center_w]

            # Resize to reduce tokens
            from PIL import Image as PILImage
            center_img = PILImage.fromarray(center_region.astype("uint8"), "RGB")
            center_img = center_img.resize((min(600, center_img.width), min(600, center_img.height)), PILImage.Resampling.LANCZOS)
            center_region = np.array(center_img)

            # Convert to base64
            image_data = self._encode_image(center_region)

            # Call Claude Vision API to detect score achievement
            message = self.client.messages.create(
                model=self.model,
                max_tokens=30,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": "Is there large text in the CENTER of this image showing a golf score achievement like 'Birdie', 'Eagle', 'Par', 'Bogey', 'Double Bogey', 'Albatross', or 'Hole in One'? Reply with ONLY the achievement word if found (e.g., 'Birdie'), or 'NONE' if not found.",
                            },
                        ],
                    }
                ],
            )

            # Parse response
            if not message.content:
                return None

            achievement = message.content[0].text.strip()

            # Check if achievement was found
            if achievement.upper() == "NONE" or not achievement:
                return None

            # Validate it's a known score achievement
            valid_achievements = [
                "birdie", "eagle", "par", "bogey", "double bogey",
                "albatross", "hole in one", "ace", "triple bogey"
            ]

            achievement_lower = achievement.lower()
            if any(valid in achievement_lower for valid in valid_achievements):
                return achievement

            return None

        except anthropic.APIError as e:
            return None
        except Exception as e:
            return None

    def estimate_cost(self, screenshot: np.ndarray, few_shot_examples: Optional[list] = None) -> float:
        """
        Estimate API cost for analyzing this screenshot.

        Args:
            screenshot: Screenshot to analyze
            few_shot_examples: Optional few-shot examples

        Returns:
            Estimated cost in USD
        """
        # Claude 3.5 Sonnet pricing (as of 2024):
        # Input: $3.00 / 1M tokens
        # Output: $15.00 / 1M tokens

        # Estimate tokens
        # Image: ~1000-1500 tokens for typical screenshot
        # System prompt: ~200 tokens
        # User prompt: ~100 tokens + few-shot examples
        # Output: ~50 tokens

        image_tokens = 1200
        system_tokens = 200
        user_tokens = 100
        few_shot_tokens = len(few_shot_examples) * 150 if few_shot_examples else 0
        output_tokens = 50

        input_tokens = image_tokens + system_tokens + user_tokens + few_shot_tokens

        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * 3.00
        output_cost = (output_tokens / 1_000_000) * 15.00

        return input_cost + output_cost

    def _build_system_prompt(self) -> str:
        """
        Build system prompt for shot analysis.

        Returns:
            System prompt string
        """
        return """You are an expert golf shot analyzer for the GS Pro golf simulator.

Your task is to analyze screenshots from GS Pro and determine the outcome of the golf shot.

Possible outcomes:
- fairway: Ball landed on the fairway
- green: Ball landed on the green
- water: Ball went into water hazard
- bunker: Ball landed in sand bunker
- rough: Ball landed in rough/long grass
- trees: Ball hit or landed near trees
- out_of_bounds: Ball went out of bounds (OB)
- tee_shot: Ball is still on the tee (no shot detected)
- unknown: Cannot determine outcome

Analyze the visual elements in the GS Pro interface:
- Ball position on the course
- Terrain type (grass, sand, water)
- Distance indicators
- Course overlay graphics
- Any text indicators

Respond in this exact format:
OUTCOME: <outcome>
CONFIDENCE: <0.0-1.0>
REASONING: <brief explanation>

Be concise and accurate. Use high confidence (>0.8) only when very certain."""

    def _build_user_prompt(self, few_shot_examples: Optional[list] = None) -> str:
        """
        Build user prompt with optional few-shot examples.

        Args:
            few_shot_examples: Optional list of examples

        Returns:
            User prompt string
        """
        prompt = "Analyze this GS Pro screenshot and determine the shot outcome.\n\n"

        if few_shot_examples:
            prompt += "Here are some reference examples:\n\n"
            for i, example in enumerate(few_shot_examples, 1):
                outcome = example.get("outcome", "unknown")
                reasoning = example.get("reasoning", "")
                prompt += f"Example {i}:\nOUTCOME: {outcome}\nREASONING: {reasoning}\n\n"

            prompt += "Now analyze the provided screenshot:\n"

        return prompt

    def _encode_image(self, screenshot: np.ndarray) -> str:
        """
        Encode screenshot to base64 JPEG with resizing to stay under 5 MB limit.

        Args:
            screenshot: RGB numpy array

        Returns:
            Base64-encoded JPEG string
        """
        # Convert to PIL Image
        img = Image.fromarray(screenshot.astype("uint8"), "RGB")

        # Resize more aggressively to save tokens (max 1280x720)
        # Golf shots don't need super high resolution for AI to detect outcomes
        max_width = 1280
        max_height = 720

        # Calculate new dimensions maintaining aspect ratio
        width, height = img.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Encode to JPEG with lower quality to save tokens (still good for AI)
        max_size = 4_800_000  # 4.8 MB to be safe (under 5 MB limit)
        quality = 75  # Lower quality, but still sufficient for AI analysis

        while quality > 20:
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            size = buffer.tell()

            if size <= max_size:
                break

            # Reduce quality and try again
            quality -= 10

        buffer.seek(0)

        # Base64 encode
        return base64.b64encode(buffer.read()).decode("utf-8")

    def _parse_response(self, message: anthropic.types.Message) -> tuple[Outcome, float]:
        """
        Parse Claude response to extract outcome and confidence.

        Args:
            message: Anthropic message response

        Returns:
            Tuple of (outcome, confidence)

        Raises:
            AIServiceError: If response format invalid
        """
        if not message.content:
            raise AIServiceError("Empty response from Claude API")

        text = message.content[0].text

        # Parse structured response
        lines = text.strip().split("\n")
        outcome_str = None
        confidence = 0.5  # Default confidence

        for line in lines:
            if line.startswith("OUTCOME:"):
                outcome_str = line.split(":", 1)[1].strip().lower()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    confidence = 0.5

        if not outcome_str:
            raise AIServiceError(f"Could not parse outcome from response: {text}")

        # Convert to Outcome enum
        try:
            outcome = Outcome(outcome_str)
        except ValueError:
            # Unknown outcome, default to UNKNOWN
            outcome = Outcome.UNKNOWN
            confidence = 0.3

        # Clamp confidence to [0.0, 1.0]
        confidence = max(0.0, min(1.0, confidence))

        return (outcome, confidence)
