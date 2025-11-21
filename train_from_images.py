#!/usr/bin/env python
"""
Train AI from manually organized screenshots.

Usage:
1. Organize screenshots into outcome folders:
   data/training/images/fairway/*.jpg
   data/training/images/green/*.jpg
   data/training/images/water/*.jpg
   etc.

2. Run this script:
   python train_from_images.py

3. AI will automatically use these examples in next session
"""

import io
import json
import sys
from pathlib import Path
from typing import Dict, List

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.models.outcome import Outcome


def scan_training_images(images_dir: Path) -> Dict[str, List[str]]:
    """
    Scan training images directory and organize by outcome.

    Args:
        images_dir: Path to images directory

    Returns:
        Dict mapping outcome to list of image paths
    """
    images_by_outcome = {}

    # Valid image extensions
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}

    # Scan each outcome folder
    for outcome in Outcome:
        outcome_dir = images_dir / outcome.value
        if not outcome_dir.exists():
            continue

        # Find all images in this folder
        images = []
        for ext in valid_extensions:
            images.extend(outcome_dir.glob(f"*{ext}"))
            images.extend(outcome_dir.glob(f"*{ext.upper()}"))

        if images:
            images_by_outcome[outcome.value] = [str(img) for img in images]

    return images_by_outcome


def generate_few_shot_examples(
    images_by_outcome: Dict[str, List[str]],
    max_per_outcome: int = 5
) -> Dict[str, List[Dict]]:
    """
    Generate few-shot examples from organized images.

    Args:
        images_by_outcome: Dict mapping outcome to image paths
        max_per_outcome: Maximum examples per outcome

    Returns:
        Few-shot examples dict
    """
    examples = {}

    for outcome, image_paths in images_by_outcome.items():
        outcome_examples = []

        # Use up to max_per_outcome images (most recent)
        selected_images = image_paths[-max_per_outcome:]

        for image_path in selected_images:
            example = {
                "screenshot_hash": Path(image_path).stem,  # Use filename as hash
                "outcome": outcome,
                "reasoning": f"Manual training example: {outcome}",
                "confidence": 1.0
            }
            outcome_examples.append(example)

        examples[outcome] = outcome_examples

    return examples


def save_examples(examples: Dict, output_file: Path) -> None:
    """Save examples to JSON file."""
    data = {"examples": examples}
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    """Main training script."""
    print("=" * 60)
    print("Mully Mouth AI Training - Image Scanner")
    print("=" * 60)

    # Paths
    images_dir = Path("data/training/images")
    output_file = Path("data/training/few_shot_examples.json")

    # Ensure directories exist
    images_dir.mkdir(parents=True, exist_ok=True)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Scan for images
    print(f"\nScanning: {images_dir}")
    images_by_outcome = scan_training_images(images_dir)

    if not images_by_outcome:
        print("\nNo training images found!")
        print("\nTo add training images:")
        print("1. Take screenshots during golf")
        print("2. Organize them into outcome folders:")
        print("   data/training/images/fairway/shot1.jpg")
        print("   data/training/images/green/shot2.jpg")
        print("   data/training/images/water/shot3.jpg")
        print("   etc.")
        print("3. Run this script again")
        return

    # Display found images
    total_images = sum(len(imgs) for imgs in images_by_outcome.values())
    print(f"\nFound {total_images} training images:\n")

    for outcome, images in sorted(images_by_outcome.items()):
        print(f"  {outcome:15s} {len(images):3d} images")

    # Generate examples
    print(f"\nGenerating few-shot examples...")
    examples = generate_few_shot_examples(images_by_outcome, max_per_outcome=5)

    # Save
    save_examples(examples, output_file)
    print(f"Saved to: {output_file}")

    # Summary
    total_examples = sum(len(ex) for ex in examples.values())
    print(f"\nTraining complete!")
    print(f"  Total examples: {total_examples}")
    print(f"  Max per outcome: 5")

    print("\n" + "=" * 60)
    print("AI will use these examples in your next session!")
    print("=" * 60)


if __name__ == "__main__":
    main()
