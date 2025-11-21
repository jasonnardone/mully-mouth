# Quick Training Guide

## Super Simple 3-Step Process

### 1. Take Screenshots During Golf ⛳
- Use any screenshot tool (Windows: Win+Shift+S)
- Save anywhere temporarily (desktop, downloads, etc.)
- Don't organize during your round - just play!

### 2. Organize After Your Round 📁
Drag screenshots into the right folder:
```
data/training/images/
├── fairway/       ← fairway shots go here
├── green/         ← green shots go here
├── water/         ← water shots go here
├── bunker/        ← bunker shots go here
├── rough/         ← rough shots go here
├── trees/         ← tree hits go here
└── out_of_bounds/ ← OB shots go here
```

### 3. Train the AI 🤖
```bash
python train_from_images.py
```

That's it! Next time you play, AI uses your examples.

## How Many Screenshots Do I Need?

- **Bare Minimum**: 1-2 per outcome type
- **Recommended**: 3-5 per outcome type
- **Excellent**: 5-10 per outcome type

You don't need hundreds - just a few good, clear examples!

## What Changed?

✅ **Removed**: Interactive correction system (typing during gameplay)
✅ **Removed**: Hotkey configuration
✅ **Added**: Simple image organization training
✅ **Added**: `train_from_images.py` script

## Full Documentation

See `TRAINING_GUIDE.md` for complete details.
