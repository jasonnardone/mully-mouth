# Mully Mouth Installation Guide

This guide will help you install and set up Mully Mouth Golf Caddy on your Windows system.

## Prerequisites

**Python Version Required:** Python 3.11, 3.12, or 3.13
- **Recommended:** Python 3.12.x for best compatibility
- Python 3.14+ is not yet fully supported by all dependencies

### Installing Python

If you don't have Python installed or need a compatible version:

1. Visit [Python Downloads](https://www.python.org/downloads/)
2. Download Python 3.12.x (recommended) or 3.11.x
3. Run the installer
4. **IMPORTANT:** Check "Add Python to PATH" during installation
5. Complete the installation

To verify your Python installation:
```cmd
python --version
```

## Quick Start (Recommended)

### Step 1: Install Dependencies

Double-click `install.bat` or run from command line:
```cmd
install.bat
```

This script will:
- Check your Python version
- Create a virtual environment in the `venv` folder
- Install all required dependencies
- Verify the installation

**Note:** If you see warnings about pygame or pycaw failing to install, this is usually due to Python version compatibility. The app will still work, but audio features may be limited.

### Step 2: Configure API Keys

Double-click `setup_credentials.bat` or run:
```cmd
setup_credentials.bat
```

You'll need:
- **Anthropic API Key** - Get from [Anthropic Console](https://console.anthropic.com/)
- **xAI API Key** - Get from [xAI Console](https://console.x.ai/)

Your credentials are stored securely in Windows Credential Manager.

### Step 3: Run the Application

Double-click `mully-mouth.bat` or run:
```cmd
mully-mouth.bat
```

Look for the gray "M" icon in your system tray (bottom-right corner of screen).

## Manual Installation (Advanced)

If you prefer to install manually:

### 1. Create Virtual Environment
```cmd
python -m venv venv
```

### 2. Activate Virtual Environment
```cmd
venv\Scripts\activate
```

### 3. Install Dependencies
```cmd
pip install -r requirements.txt
```

### 4. Configure Credentials
```cmd
python setup_credentials.py
```

### 5. Run Application
```cmd
python -m src.cli.tray_app
```

## Troubleshooting

### "Python is not installed or not in PATH"
- Reinstall Python and check "Add Python to PATH"
- Or manually add Python to your system PATH

### "Virtual environment not found"
- Run `install.bat` first
- Make sure the installation completed successfully

### "Module not found" errors
- Delete the `venv` folder
- Run `install.bat` again to recreate the environment

### pygame or pycaw installation fails
- This is usually due to Python version compatibility
- Try using Python 3.12 instead of newer versions
- The app will still work for most features without these packages

### API key errors
- Run `setup_credentials.bat` to configure your keys
- Make sure you have valid API keys from Anthropic and xAI

## Updating

To update to a new version:

1. Pull the latest code from Git
2. Run `install.bat` again
3. Choose to reinstall when prompted

## Uninstalling

To remove Mully Mouth:

1. Delete the `venv` folder
2. Delete the project folder
3. (Optional) Remove credentials from Windows Credential Manager:
   - Open "Credential Manager" from Windows Start menu
   - Look for entries starting with "mully-mouth"
   - Delete them

## Project Structure

```
mully-mouth/
├── venv/                    # Virtual environment (created by install.bat)
├── src/                     # Source code
├── config/                  # Configuration files
├── install.bat             # Installation script
├── setup_credentials.bat   # Credential setup wrapper
├── mully-mouth.bat         # Application launcher
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## Getting Help

- Check the main [README.md](README.md) for feature documentation
- See [SYSTEM_TRAY_GUIDE.md](SYSTEM_TRAY_GUIDE.md) for usage instructions
- Report issues on the project's GitHub repository
