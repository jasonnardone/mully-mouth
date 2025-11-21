# Mully Mouth System Tray Guide

## Quick Start

### For Non-Technical Users

1. **Install Requirements** (first time only):
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys** (choose ONE method):

   **Method: Secure Storage** (Recommended) ⭐
   ```bash
   python setup_credentials.py
   ```
   - Your API keys are stored securely in Windows Credential Manager
   - Encrypted by Windows, never saved in plain text files
   - Perfect for public GitHub repos!
   - Double-click `mully-mouth.bat` to start

   **Method C: Config File** (Not recommended for public repos)
   - Copy `config/config.yaml.template` to `config/config.yaml`
   - Edit `config/config.yaml` and add your API keys
   - Double-click `run_tray.bat` to start

   See [SECURE_CREDENTIALS_GUIDE.md](SECURE_CREDENTIALS_GUIDE.md) for detailed security information.

3. **Look for the gray "M" icon** in your system tray (bottom-right corner of screen, near the clock)

4. **Right-click the icon** and select **"Start Monitoring"** to begin

The application starts in stopped mode - you control when monitoring begins!

---

## System Tray Menu

### Start/Stop Monitoring
- Click to toggle monitoring on/off
- Green icon = monitoring active
- Gray icon = monitoring stopped

### Change Personality
Choose from available commentary personalities:
- **Neutral** - Professional, balanced commentary
- **Sarcastic** - Humorous, playful commentary
- **Encouraging** - Positive, supportive commentary
- And more...

### Adjust Settings

#### Commentary Frequency
How often commentary is generated:
- **Always (100%)** - Comment on every shot
- **Often (75%)** - Comment on most shots
- **Sometimes (50%)** - Comment on half the shots
- **Rarely (25%)** - Comment occasionally
- **Never (0%)** - No commentary (silent)

#### Name Frequency
How often player name is mentioned in commentary:
- **Always (100%)** - Include name in every comment
- **Often (75%)** - Include name most of the time
- **Sometimes (50%)** - Include name sometimes
- **Rarely (25%)** - Include name occasionally
- **Never (0%)** - Never mention player name

### Session Stats
View current session statistics:
- Total shots detected
- Total API cost
- Cache hit rate
- Accuracy rate
- Current settings

### Open Config File
Quick access to open `config/config.yaml` for advanced configuration

### Exit
Cleanly stop monitoring and exit the application

---

## How It Works

### Manual Start
When you launch the system tray app, it starts in **stopped mode** (gray icon). This prevents accidental monitoring and API costs.

**To start monitoring:**
1. Right-click the gray "M" icon
2. Select "Start Monitoring"
3. Icon turns green - now watching for shots!

### Icon States
- **Green "M"** - Monitoring is active, watching for shots
- **Gray "M"** - Monitoring is stopped

### Changing Settings
When you change any setting (personality, frequency, etc.):
1. Monitoring automatically stops
2. Setting is updated and saved to config
3. Monitoring automatically restarts (if it was running)

This ensures settings are applied cleanly without interruption.

### Session Management
- Each time you start monitoring, a new session is created
- Session data is automatically saved when you stop monitoring
- Stats are available in real-time via the "Session Stats" menu

---

## Troubleshooting

### "M" icon doesn't appear
1. Check if the application is running (look for Python in Task Manager)
2. Try restarting the application
3. Check Windows notification settings - system tray icons might be hidden

### Can't find system tray icon
1. Click the "^" arrow in system tray to show hidden icons
2. The "M" icon should be there
3. You can drag it to the visible area if desired

### Monitoring doesn't start
1. Check that your API keys are set in environment variables or config.yaml
2. Ensure your screen/video is fullscreen
3. Check the console window for error messages

### Settings changes don't persist
1. Make sure config/config.yaml is not read-only
2. Check file permissions
3. Manually verify changes were saved in config.yaml

### Want to use command line instead
The original CLI is still available:
```bash
python -m src.cli.main
```

---

## Advanced Usage

### Running at Windows Startup

**Option 1: Manual Shortcut**
1. Press `Win+R` and type `shell:startup`
2. Create a shortcut to `run_tray.bat` in this folder
3. The app will start automatically when Windows starts

**Option 2: Task Scheduler**
1. Open Task Scheduler
2. Create new task: Run `run_tray.bat` at logon
3. Configure to run whether user is logged on or not

### Environment Variables

Set API keys via environment variables (recommended for security):

**PowerShell:**
```powershell
$env:ANTHROPIC_API_KEY="your-key-here"
$env:ELEVENLABS_API_KEY="your-key-here"
```

**Command Prompt:**
```cmd
set ANTHROPIC_API_KEY=your-key-here
set ELEVENLABS_API_KEY=your-key-here
```

**System-wide (Windows Settings):**
1. Search "Environment Variables" in Windows
2. Add `ANTHROPIC_API_KEY` and `ELEVENLABS_API_KEY`
3. Restart application

### Multiple Monitors

The application uses your primary monitor for capture. If you need to change which monitor:
1. Open config.yaml
2. Adjust monitoring settings (coming soon)
3. Restart the application

---

## Comparison: CLI vs System Tray

### Command Line (CLI)
**Use when:**
- You're comfortable with terminals
- You want to see detailed logs
- You're debugging or developing
- You want to pipe output to logs

**Launch:**
```bash
python -m src.cli.main
```

### System Tray (GUI)
**Use when:**
- You want simple point-and-click interface
- You don't need to see logs
- You want it running in background
- You want easy access to settings

**Launch:**
- Double-click `run_tray.bat`
- Or: `python -m src.cli.tray_app`

Both versions have the same functionality - pick whichever you prefer!

---

## Tips & Best Practices

1. **Leave it running** - The system tray app is designed to run continuously during your golf session

2. **Check stats periodically** - Right-click icon → Session Stats to monitor costs and accuracy

3. **Adjust frequency** - If commentary gets annoying, reduce commentary_frequency to 25% or 50%

4. **Try personalities** - Experiment with different personalities to find your favorite

5. **Use shortcuts** - Pin `run_tray.bat` to taskbar for quick access

---

## Support

For issues or questions:
- Check console output if running from `run_tray.bat`
- Review error messages in Windows message boxes
- Consult main project README.md
- Check training guides for AI improvement tips

---

## What's Next?

Once you're comfortable with the system tray interface:
1. Try training the AI with custom screenshots (see QUICK_TRAINING.md)
2. Experiment with different personalities (see data/personalities/)
3. Fine-tune frequency settings to your preference
4. Monitor your API costs and optimize as needed

Happy golfing!
