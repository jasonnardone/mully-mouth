# Idle Screen Training Images

This directory contains training images of **non-gameplay** screens that should trigger Mully Mouth to automatically pause commentary and skip analysis to save API costs.

## What to Put Here

Add screenshots of any screens where golf is NOT actively being played:

- **Setup/Configuration Screens**: Player setup, tee selection, club selection
- **Round Complete Screens**: Final scores, leaderboard, summary screens
- **Menu Screens**: Main menu, settings, course selection
- **Loading Screens**: Course loading, waiting screens
- **Pause Screens**: Game paused overlays
- **Other Non-Gameplay**: Any screen that's not an active shot

## How to Capture Training Images

1. **During gameplay**, when you see a non-gameplay screen (setup, round complete, etc.)
2. Take a screenshot (Print Screen or use Windows Snipping Tool)
3. Save the image to this directory with a descriptive name
4. Example names:
   - `round_complete_01.png`
   - `player_setup_01.png`
   - `course_selection_01.png`
   - `main_menu_01.png`

## File Formats

- Supported: `.png`, `.jpg`, `.jpeg`
- Any resolution (will be automatically resized during training)

## How It Works

When Mully Mouth detects motion and a "shot", it will first check if the screen matches any of these idle screen patterns. If it does, it will:

1. **Skip all analysis** (no AI calls = no cost)
2. **Skip commentary generation** (no unnecessary speech)
3. **Skip voice synthesis** (no ElevenLabs calls)
4. Print "Idle screen detected - skipping analysis to save costs"

The system automatically resumes normal operation when gameplay screens are detected.

## Training

The AI uses Claude Vision API to identify idle screens by comparing the current screenshot against the patterns learned from images in this directory. The more examples you provide, the better the detection will be.

## Tips

- Add at least 2-3 examples of each type of idle screen
- Capture screens from different courses and scenarios
- Include both full-screen and windowed mode screenshots if you use both
- The more variety, the better the detection accuracy
