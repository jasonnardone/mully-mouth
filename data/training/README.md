# Training Images Directory

## Quick Start

1. **Organize your screenshots by outcome:**
   ```
   images/
   ├── fairway/shot1.jpg
   ├── green/shot2.jpg
   ├── water/shot3.jpg
   └── bunker/shot4.jpg
   ```

2. **Run the training script:**
   ```bash
   python train_from_images.py
   ```

3. **Done!** AI uses your examples automatically.

## Folder Structure

Create folders for outcomes you want to train:

- `fairway/` - Shots landing on fairway
- `green/` - Shots on the green
- `water/` - Water hazard shots
- `bunker/` - Bunker/sand shots
- `rough/` - Rough/tall grass shots
- `trees/` - Shots hitting trees
- `out_of_bounds/` - OB shots

## Tips

- Start with 3-5 images per outcome
- Use clear, centered screenshots
- Name files descriptively: `fairway_center_01.jpg`
- Add more examples for outcomes AI struggles with
- Re-run training script whenever you add new images

## Files Generated

- `few_shot_examples.json` - AI training data (auto-generated)
- `corrections.json` - Manual corrections (not used in simple workflow)

See `../../TRAINING_GUIDE.md` for complete documentation.
