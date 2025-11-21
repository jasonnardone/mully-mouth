# Mully Mouth AI Training Guide

## Overview

The `data/training/` directory is used to improve AI accuracy over time through:
1. **Training images** - Screenshots you organize by outcome type
2. **Few-shot examples** - AI learns from your best examples (auto-generated from images)
3. **Pattern cache** - AI remembers successful detections automatically

## Directory Structure

```
data/training/
├── images/              # Organized screenshots by outcome
│   ├── fairway/        # Screenshots of fairway shots
│   ├── green/          # Screenshots of green shots
│   ├── water/          # Screenshots of water hazards
│   ├── bunker/         # Screenshots of bunker shots
│   ├── rough/          # Screenshots of rough shots
│   ├── trees/          # Screenshots hitting trees
│   └── out_of_bounds/  # Screenshots of OB shots
├── corrections.json     # Your manual corrections (auto-saved)
└── few_shot_examples.json  # Best examples fed to AI (auto-saved)
```

## How Training Works (Simple 3-Step Process)

### Step 1: Collect Screenshots During Golf
- Play your round normally
- Take screenshots of various outcomes (Windows: Win+Shift+S, or use any screenshot tool)
- Don't worry about organizing them during the round - just save them somewhere

### Step 2: Organize Screenshots by Outcome
After your round, organize screenshots into outcome folders:
```
data/training/images/
├── fairway/       ← Put fairway screenshots here
├── green/         ← Put green screenshots here
├── water/         ← Put water hazard screenshots here
├── bunker/        ← Put bunker screenshots here
├── rough/         ← Put rough screenshots here
├── trees/         ← Put tree hit screenshots here
└── out_of_bounds/ ← Put OB screenshots here
```

**Just drag and drop your screenshots into the correct folder!**

### Step 3: Train the AI
Run the training script:
```bash
python train_from_images.py
```

That's it! The AI will use your examples in the next session.

## What the Training Script Does

When you run `python train_from_images.py`:

1. **Scans your organized screenshots** in `data/training/images/`
2. **Generates few-shot examples** from up to 5 best images per outcome
3. **Saves to** `few_shot_examples.json`
4. **AI automatically loads** these examples on next startup

The AI shows these examples to Claude Vision API when analyzing new shots, helping it recognize similar patterns.

## Example Workflow

**Monday: Play and Collect**
```
1. Play golf with Mully Mouth running
2. Take screenshots: Win+Shift+S (Windows) or screenshot tool
3. Save them to desktop/downloads (anywhere temporary)
   - shot1.jpg, shot2.jpg, shot3.jpg, etc.
```

**Monday Evening: Organize and Train**
```
1. Organize screenshots:
   Move fairway shots → data/training/images/fairway/
   Move green shots → data/training/images/green/
   Move water shots → data/training/images/water/
   etc.

2. Run training:
   python train_from_images.py

3. Done! Next session uses your examples
```

**Tuesday: Improved AI**
```
AI now knows YOUR course and YOUR simulator setup!
```

## Best Practices

1. **Start with 3-5 examples per outcome** - Don't need hundreds
2. **Use clear, obvious examples** - Centered ball, good lighting
3. **Add more examples for problem outcomes** - If AI struggles with bunkers, add more bunker shots
4. **Re-train periodically** - Add new examples as you encounter edge cases
5. **Name files descriptively** - `bunker_left_greenside_01.jpg` helps you remember

## Advanced: Customizing Few-Shot Examples

The AI uses few-shot learning - showing it examples of correct outcomes. You can:

**Edit `few_shot_examples.json` manually:**
```json
{
  "examples": {
    "fairway": [
      {
        "screenshot_hash": "abc123",
        "outcome": "fairway",
        "reasoning": "Ball clearly on short grass, fairway texture visible",
        "confidence": 1.0
      }
    ]
  }
}
```

**Fields:**
- `screenshot_hash`: Identifier (can be filename or hash)
- `outcome`: One of: fairway, green, water, bunker, rough, trees, out_of_bounds
- `reasoning`: Why this is the correct outcome (helps AI learn)
- `confidence`: 0.0-1.0 (use 1.0 for manual examples)

## Cost Considerations

Few-shot examples are sent with each AI request:
- Each example adds ~150 tokens
- With prompt caching, this is very cheap (90% discount after first use)
- Limit is 5 examples per outcome to keep costs reasonable

## Future Enhancements

Potential improvements:
1. Auto-save screenshots on all corrections
2. Training mode to batch-label screenshots
3. Visual review tool to see AI mistakes
4. Export/import training data
5. Community-shared training sets

## Troubleshooting

**Training script says "No images found":**
- Check folder names match exactly: `fairway`, `green`, `water`, `bunker`, `rough`, `trees`, `out_of_bounds`
- Check images are .jpg, .jpeg, or .png
- Check path is `data/training/images/{outcome}/`

**AI still makes mistakes:**
- Need more examples for that outcome (add 2-3 more)
- Examples might not be clear enough (try different screenshots)
- Run training script again after adding images

**Want to reset training:**
- Delete `data/training/few_shot_examples.json`
- Delete all images from `data/training/images/`
- Start fresh

**How many examples do I need?**
- Minimum: 1-2 per outcome (better than nothing)
- Good: 3-5 per outcome (recommended)
- Excellent: 5-10 per outcome (diminishing returns after this)
