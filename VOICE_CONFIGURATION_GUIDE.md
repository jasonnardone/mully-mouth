# Voice Configuration Guide

## Overview

Each personality in Mully Mouth can have its own unique ElevenLabs voice! This allows you to have different voices for different commentary styles - for example, a deep authoritative voice for neutral commentary, a playful voice for sarcastic commentary, and an energetic voice for encouraging commentary.

## How It Works

Voice settings are configured per-personality in the personality YAML files located in `data/personalities/`. When you switch personalities in the system tray, the voice automatically changes to match.

## Quick Start

### Step 1: Get ElevenLabs Voice IDs

1. Go to [ElevenLabs Voice Library](https://elevenlabs.io/app/voice-library)
2. Browse available voices
3. Click on a voice you like
4. Copy the **Voice ID** (it looks like: `21m00Tcm4TlvDq8ikWAM`)

**Popular Voice IDs:**
- `21m00Tcm4TlvDq8ikWAM` - Rachel (female, neutral)
- `ErXwobaYiN019PkySvjV` - Antoni (male, well-rounded)
- `VR6AewLTigWG4xSOukaG` - Arnold (male, crisp)
- `pNInz6obpgDQGcFmaJgB` - Adam (male, deep)
- `EXAVITQu4vr4xnSDxMaL` - Bella (female, soft)

### Step 2: Edit Personality Files

Edit the personality YAML file (e.g., `data/personalities/sarcastic.yaml`):

```yaml
name: "Sarcastic"
description: "Humorous, light-hearted ribbing"
tone: "sarcastic"

# ElevenLabs voice configuration
voice_id: "ErXwobaYiN019PkySvjV"  # Antoni - playful voice
voice_settings:
  stability: 0.5      # 0.0-1.0: Lower = more expressive
  similarity_boost: 0.75  # 0.0-1.0: Higher = more consistent
```

### Step 3: Restart or Switch Personalities

- If monitoring is running, the new voice will be used on the next shot
- Switch personalities from the system tray menu to test different voices
- Changes take effect immediately!

## Personality Voice Configuration Examples

### Neutral Personality (Professional)
```yaml
# data/personalities/neutral.yaml
voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam - deep, authoritative
voice_settings:
  stability: 0.7      # More stable for professional tone
  similarity_boost: 0.8  # Very consistent
```

### Sarcastic Personality (Playful)
```yaml
# data/personalities/sarcastic.yaml
voice_id: "ErXwobaYiN019PkySvjV"  # Antoni - well-rounded, versatile
voice_settings:
  stability: 0.4      # More expressive for sarcasm
  similarity_boost: 0.7  # Allow some variation
```

### Encouraging Personality (Energetic)
```yaml
# data/personalities/encouraging.yaml
voice_id: "EXAVITQu4vr4xnSDxMaL"  # Bella - soft, encouraging
voice_settings:
  stability: 0.6      # Balanced expressiveness
  similarity_boost: 0.8  # Consistent positivity
```

### Jerk Personality (Aggressive)
```yaml
# data/personalities/jerk.yaml
voice_id: "VR6AewLTigWG4xSOukaG"  # Arnold - crisp, assertive
voice_settings:
  stability: 0.3      # Very expressive, aggressive
  similarity_boost: 0.65  # Allow attitude variation
```

## Voice Settings Explained

### voice_id
The unique identifier for an ElevenLabs voice.

- **Required**: Yes (if you want personality-specific voice)
- **Format**: 20-character string
- **Default**: If not set or `null`, uses default voice from config.yaml

### stability (0.0 - 1.0)
Controls how stable/consistent the voice sounds.

- **Low (0.0-0.3)**: Very expressive, emotional, variable
  - Good for: Dramatic commentary, sarcasm, aggressive tones
  - Risk: May sound inconsistent or over-the-top

- **Medium (0.4-0.6)**: Balanced expressiveness
  - Good for: General use, encouraging commentary
  - Recommended starting point

- **High (0.7-1.0)**: Stable, consistent, controlled
  - Good for: Professional commentary, neutral tones
  - Risk: May sound flat or robotic

### similarity_boost (0.0 - 1.0)
Controls how closely the AI matches the original voice.

- **Low (0.0-0.4)**: More creative interpretation
  - More variation between outputs
  - May drift from original voice character

- **Medium (0.5-0.7)**: Balanced similarity
  - Good for most use cases
  - Some variation while staying recognizable

- **High (0.8-1.0)**: Very consistent with original
  - Minimal variation between outputs
  - Stays true to voice character

## Testing Voice Settings

### Quick Test
1. Edit personality YAML file
2. Switch to that personality in system tray menu
3. Hit a shot in golf
4. Listen to the commentary
5. Adjust settings and repeat

### Recommended Testing Process
1. **Start with defaults**: `stability: 0.5`, `similarity_boost: 0.75`
2. **Test a few shots**: Get a feel for the voice
3. **Adjust stability**: Too flat? Lower it. Too variable? Raise it.
4. **Adjust similarity**: Too generic? Raise it. Too rigid? Lower it.
5. **Fine-tune**: Make small changes (±0.1) until perfect

## Finding the Perfect Voice

### For Each Personality Type

**Neutral/Professional:**
- Look for: Clear, articulate, authoritative voices
- Gender: Male voices often sound more authoritative
- Age: Mature voices work well
- Accent: Neutral American or British

**Sarcastic/Playful:**
- Look for: Expressive, versatile voices
- Gender: Either works well
- Age: Younger voices can sound more playful
- Accent: Any, but American works well for sarcasm

**Encouraging/Supportive:**
- Look for: Warm, friendly, upbeat voices
- Gender: Female voices often sound more encouraging
- Age: Mid-range
- Accent: Friendly, approachable accents

**Aggressive/Jerk:**
- Look for: Strong, assertive, edgy voices
- Gender: Male voices often sound more aggressive
- Age: Mature
- Accent: Strong accents can add character

## Advanced: Voice Cloning

If you have an ElevenLabs paid plan, you can clone your own voice or create custom voices:

1. Go to ElevenLabs Voice Lab
2. Clone a voice or create a custom one
3. Copy the Voice ID
4. Add it to your personality YAML file

This allows you to use your own voice for commentary!

## Troubleshooting

### Voice doesn't change when switching personalities

**Check:**
1. Personality YAML file has `voice_id` set (not `null`)
2. Voice ID is correct (20 characters)
3. You've switched personalities after editing the file
4. No syntax errors in YAML (check indentation)

**Solution:**
- Restart the application
- Check console for errors
- Verify voice ID at ElevenLabs website

### Voice sounds wrong or robotic

**Adjust:**
1. **Lower stability** if it sounds too flat
2. **Raise stability** if it sounds too inconsistent
3. **Raise similarity_boost** if it doesn't sound like the original
4. Try a different voice entirely

### Cost concerns with multiple voices

**Cost is the same regardless of voice:**
- ElevenLabs charges per character, not per voice
- Using different voices doesn't cost more
- All voices on your plan are available

**To reduce costs:**
- Use commentary_frequency setting (set to 0.5 or lower)
- Same cost optimization applies to all voices

## Default Fallback

If a personality doesn't have a `voice_id` configured (or it's set to `null`), the system uses the default voice from `config/config.yaml`:

```yaml
elevenlabs:
  voice_id: "21m00Tcm4TlvDq8ikWAM"  # Default voice
  # ...
```

This ensures all personalities work even without custom voice configuration.

## Example: Complete Personality with Voice

```yaml
name: "Pro Announcer"
description: "Professional golf tournament commentary"
tone: "professional"

# Custom voice for this personality
voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam - deep, authoritative
voice_settings:
  stability: 0.75     # Very stable
  similarity_boost: 0.85  # Very consistent

system_prompt: |
  You are a professional golf announcer at a PGA tournament. Provide
  clear, articulate commentary with the gravitas of Sunday afternoon
  golf coverage. Be respectful, knowledgeable, and measured in your
  tone. Use golf terminology appropriately.

example_phrases:
  green:
    - "Beautiful approach. On the green in regulation."
    - "Finds the putting surface. Excellent shot."
  water:
    - "Oh no. That's found the water hazard."
    - "Into the hazard. A costly mistake."
  # ... more phrases
```

## Tips & Best Practices

1. **Match voice to personality**: Deep voice for serious, playful voice for sarcastic
2. **Test thoroughly**: Try different outcomes (water, bunker, birdie, etc.)
3. **Start conservative**: Use medium settings first, then adjust
4. **Save originals**: Keep a backup before making changes
5. **Document changes**: Add comments in YAML about why you chose settings
6. **Experiment**: Don't be afraid to try wildly different settings
7. **Get feedback**: Ask friends which voices they prefer

## FAQ

**Q: Can I use the same voice for multiple personalities?**
A: Yes! Just use the same voice_id in multiple YAML files. Adjust stability/similarity for different feels.

**Q: How many voices can I use?**
A: As many as your ElevenLabs plan allows. Free tier has access to many pre-made voices.

**Q: Do I need to restart the app after changing voice settings?**
A: No! Changes take effect on the next shot. Just switch personalities to test.

**Q: Can I preview voices before using them?**
A: Yes, on the ElevenLabs website. Click any voice in the Voice Library to hear a sample.

**Q: What if I delete the voice_id line?**
A: The personality will use the default voice from config.yaml.

**Q: Can I use custom voices I create?**
A: Yes! Create them in ElevenLabs Voice Lab, copy the ID, and add it to your personality file.

## Summary

**To add a voice to a personality:**
1. Find voice ID on ElevenLabs
2. Edit `data/personalities/[name].yaml`
3. Set `voice_id` to the ID
4. Adjust `stability` and `similarity_boost` as desired
5. Test and refine!

**Each personality can have:**
- ✅ Unique voice
- ✅ Custom stability
- ✅ Custom similarity boost
- ✅ Falls back to default if not configured

Make each personality truly unique with the perfect voice! 🎤⛳
