# Voice Configuration Guide

## Overview

Mully Mouth uses **xAI Grok TTS** for voice synthesis. Each personality has a pre-assigned Grok voice, and you can override them per-personality in the YAML files.

**Cost:** $4.20 per 1 million characters — approximately **$0.08/round** at full settings.

## Available Voices

| Voice | Gender | Character | Best For |
|-------|--------|-----------|----------|
| `leo` | Male | Authoritative, measured | Neutral, Documentary |
| `rex` | Male | Confident, assertive | Jerk |
| `ara` | Female | Warm, nurturing | Encouraging |
| `eve` | Female | Energetic, expressive | Sarcastic, Ex-Girlfriend |
| `sal` | Neutral | Androgynous, unpredictable | Unhinged |

## Default Personality → Voice Mapping

| Personality | Voice | Reason |
|-------------|-------|--------|
| neutral | `leo` | Authoritative male, professional broadcaster tone |
| documentary | `leo` | Calm, measured — suits Sir David Attenborough style |
| jerk | `rex` | Confident, dominant energy |
| encouraging | `ara` | Warm, supportive female |
| sarcastic | `eve` | Energetic female, snappy delivery |
| ex-girlfriend | `eve` | Volatile, expressive energy suits the mood swings |
| unhinged | `sal` | Neutral/androgynous — beyond normal human categorization |

## Changing a Personality's Voice

Edit the personality YAML file in `data/personalities/`:

```yaml
# data/personalities/sarcastic.yaml
name: "Sarcastic"
# Grok TTS voice configuration
voice_id: "eve"  # Change to any of: leo, rex, ara, eve, sal
```

Changes take effect on the next shot — no restart needed.

## Default Fallback

If a personality's `voice_id` is missing or `null`, the system uses the default voice from `config/config.yaml`:

```yaml
grok_tts:
  voice_id: "leo"  # Default fallback voice
```

## Switching the Default Voice

To change the default for all personalities, update `config/config.yaml`:

```yaml
grok_tts:
  api_key: your_key_here
  voice_id: "ara"        # New default
  model: grok-tts-preview
```

## Getting Your xAI API Key

1. Go to [console.x.ai](https://console.x.ai/)
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new key
5. Add it to `config/config.yaml` under `grok_tts.api_key`, or set the `XAI_API_KEY` environment variable

## Troubleshooting

### Voice doesn't change when switching personalities

1. Check that `voice_id` is set in the personality YAML (not `null`)
2. Use one of the five valid names: `leo`, `rex`, `ara`, `eve`, `sal`
3. Check for YAML syntax errors (indentation)

### No audio plays

1. Verify `XAI_API_KEY` is set and valid at console.x.ai
2. Check `logs/mully_mouth.log` for errors
3. Ensure `pygame` is installed: `pip install pygame>=2.5.0`

### Cost concerns

The Grok TTS pricing of $4.20/1M characters means:
- A 150-char commentary line costs $0.00063
- A full round (~100 TTS calls) costs ~$0.08
- You would need to run **~875 rounds** to spend $7

To reduce costs further, lower `commentary_frequency` in `config/config.yaml`.

## Adding a Custom Personality

Create a new YAML file in `data/personalities/`:

```yaml
name: "My Personality"
description: "Description here"
tone: "custom"

# Grok TTS voice configuration
voice_id: "leo"  # Pick: leo, rex, ara, eve, sal

system_prompt: |
  Your system prompt here...

example_phrases:
  fairway:
    - "Example phrase 1"
  water:
    - "Example phrase 1"
```

Use with `--personality my_personality` or select from the system tray.

## Migration from ElevenLabs

If upgrading from the ElevenLabs version:

1. Run `python setup_wizard.py` to reconfigure with your xAI API key
2. Old ElevenLabs voice IDs (long hex strings) are no longer valid — personalities have been pre-mapped to Grok voices
3. Remove `ELEVENLABS_API_KEY` from your environment and add `XAI_API_KEY`
4. To roll back: `git checkout v2.0-elevenlabs`
