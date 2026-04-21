"""Setup wizard for Mully Mouth Golf Caddy configuration."""
import os
import sys
from pathlib import Path


def print_header(text: str) -> None:
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60 + "\n")


def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default value."""
    if default:
        prompt += f" [{default}]"
    prompt += ": "

    value = input(prompt).strip()
    return value if value else default


def main() -> int:
    """Run setup wizard."""
    print_header("Mully Mouth Golf Caddy - Setup Wizard")

    print("Welcome! This wizard will help you configure Mully Mouth.")
    print("Press Ctrl+C at any time to exit.\n")

    try:
        # Step 1: API Keys
        print_header("Step 1: API Keys")

        print("You need two API keys to use Mully Mouth:")
        print("  1. Anthropic API key (for Claude AI shot analysis & commentary)")
        print("  2. xAI API key (for Grok TTS voice synthesis)\n")

        print("Get your Anthropic API key at: https://console.anthropic.com/")
        anthropic_key = get_input("Enter your Anthropic API key")

        if not anthropic_key:
            print("\nError: Anthropic API key is required.")
            return 1

        print("\nGet your xAI API key at: https://console.x.ai/")
        xai_key = get_input("Enter your xAI API key")

        if not xai_key:
            print("\nError: xAI API key is required.")
            return 1

        # Step 2: Personality
        print_header("Step 2: Commentary Personality")

        print("Available personalities:")
        print("  1. neutral      - Professional, informative (voice: leo)")
        print("  2. sarcastic    - Humorous, light-hearted ribbing (voice: eve)")
        print("  3. encouraging  - Supportive, motivational (voice: ara)")
        print("  4. jerk         - Brutally honest and profane (voice: rex)")
        print("  5. documentary  - Sir David Attenborough style (voice: leo)")
        print("  6. ex-girlfriend - Your unstable ex (voice: eve)")
        print("  7. unhinged     - Completely insane (voice: sal)\n")

        personality_choice = get_input("Choose personality (1-7)", "1")

        personality_map = {
            "1": "neutral",
            "2": "sarcastic",
            "3": "encouraging",
            "4": "jerk",
            "5": "documentary",
            "6": "ex-girlfriend",
            "7": "unhinged",
        }

        personality = personality_map.get(personality_choice, "neutral")

        # Step 3: Voice Settings (optional)
        print_header("Step 3: Voice Settings (Optional)")

        voice_defaults = {
            "neutral": "leo",
            "sarcastic": "eve",
            "encouraging": "ara",
            "jerk": "rex",
            "documentary": "leo",
            "ex-girlfriend": "eve",
            "unhinged": "sal",
        }

        default_voice = voice_defaults.get(personality, "leo")
        print(f"Default voice for '{personality}': {default_voice}")
        print("Available voices: leo (authoritative male), rex (confident male),")
        print("                  ara (warm female), eve (energetic female), sal (neutral)\n")

        use_custom_voice = get_input("Customize voice? (y/n)", "n").lower()
        voice_id = default_voice

        if use_custom_voice == "y":
            voice_id = get_input("Voice ID (leo/rex/ara/eve/sal)", default_voice)

        # Step 4: Motion Detection (optional)
        print_header("Step 4: Motion Detection (Optional)")

        print("Motion detection sensitivity can be adjusted.")
        print("Lower values = more sensitive (may detect false shots)")
        print("Higher values = less sensitive (may miss shots)\n")

        use_custom_motion = get_input("Customize motion settings? (y/n)", "n").lower()

        motion_threshold = "0.02"
        ball_stop_duration = "1.0"

        if use_custom_motion == "y":
            motion_threshold = get_input("Motion threshold (0.0-1.0)", motion_threshold)
            ball_stop_duration = get_input("Ball stop duration (seconds)", ball_stop_duration)

        # Step 5: Store credentials and generate config file
        print_header("Step 5: Creating Configuration")

        # Store API keys securely in Windows Credential Manager
        try:
            from src.lib.credentials import CredentialsManager
            creds = CredentialsManager()
            anthropic_stored = creds.store_anthropic_key(anthropic_key)
            xai_stored = creds.store_xai_key(xai_key)
            if anthropic_stored and xai_stored:
                print("API keys stored securely in Windows Credential Manager.")
            else:
                print("Warning: Could not store keys in Credential Manager.")
                print("         Keys will need to be re-entered on next run.")
        except Exception as e:
            print(f"Warning: Could not store credentials securely: {e}")

        config_content = f"""# Mully Mouth Configuration
# Generated by setup wizard
# API keys are stored in Windows Credential Manager, not here.

# Anthropic (Claude AI) Configuration
anthropic:
  model: claude-haiku-4-5-20251001

# xAI Grok TTS (Voice) Configuration
# Pricing: $4.20/1M characters (~$0.35/round at full settings)
grok_tts:
  voice_id: {voice_id}
  model: grok-tts-preview

# Commentary Personality
personality: {personality}

# Commentary Settings
commentary_frequency: 0.3
name_frequency: 0.3

# Monitoring Settings
monitoring:
  fps: 2
  motion_threshold: {motion_threshold}
  ball_stop_duration: {ball_stop_duration}

# Cache Settings
cache:
  pattern_cache_file: data/cache/pattern_cache.json
  hamming_threshold: 10
  min_confidence_to_cache: 0.7

# Cost Limits
cost:
  max_cost_per_round: 2.0
  warn_at_cost: 1.5

# Logging
logging:
  level: INFO
  file: logs/mully_mouth.log

# Hotkeys (optional)
hotkeys:
  toggle_voice: null
  force_analyze: null
  correction_mode: null
"""

        # Ensure config directory exists
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)

        # Write config file
        config_file = config_dir / "config.yaml"
        with open(config_file, "w") as f:
            f.write(config_content)

        print(f"Configuration saved to: {config_file}")

        # Create data directories
        print("\nCreating data directories...")
        for dir_path in [
            "data/cache",
            "data/sessions",
            "data/training",
            "logs",
        ]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

        print("Data directories created.")

        # Success
        print_header("Setup Complete!")

        print("Mully Mouth is now configured and ready to use.")
        print(f"\nVoice: {voice_id} | Personality: {personality}")
        print("\nTo start using Mully Mouth:")
        print("  1. Launch GS Pro")
        print("  2. Double-click mully-mouth.bat (or run: python -m src.cli.main)")
        print("  3. Play golf - commentary will be generated automatically\n")

        print("Cost estimate: ~$0.35/round at full settings (vs ~$6-7 with ElevenLabs)\n")

        return 0

    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        return 1
    except Exception as e:
        print(f"\nError during setup: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
