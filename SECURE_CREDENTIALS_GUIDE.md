# Secure Credentials Guide

## Why Use Secure Credential Storage?

When working with public GitHub repositories, you **never** want to commit API keys in plain text. This guide shows you how to securely store your API keys on your PC without putting them in any file that could be committed to Git.

## How It Works

Mully Mouth uses Windows Credential Manager to store your API keys:

1. **Encrypted Storage**: Windows encrypts your credentials using your Windows account
2. **Never in Files**: Keys are not stored in any text file, config file, or code
3. **Git Safe**: Nothing to accidentally commit to your public repo
4. **Persistent**: Keys remain stored between reboots and app restarts
5. **Secure**: Only your Windows user account can access the keys

## Priority Order

The application loads API keys in this priority order:

1. **Securely stored credentials** (Windows Credential Manager) ⭐
2. **Environment variables** (ANTHROPIC_API_KEY, ELEVENLABS_API_KEY)
3. **Config file** (config/config.yaml)

## Setup Instructions

### Step 1: Install keyring Library

The keyring library is required for secure credential storage:

```bash
pip install keyring
```

(This is already included in requirements.txt)

### Step 2: Run Credential Setup

```bash
python setup_credentials.py
```

The setup tool will:
1. Check if credentials already exist
2. Prompt you for your API keys (hidden input)
3. Store them securely in Windows Credential Manager
4. Confirm successful storage

### Step 3: Verify Storage

Your credentials are now stored! You can verify by:

**Option A: Run the app**
```bash
python -m src.cli.tray_app
```

If it starts without errors, your credentials are working!

**Option B: Check Windows Credential Manager**
1. Press `Win + R`
2. Type `control keymgr.dll`
3. Look for entries starting with "MullyMouthGolfCaddy"

## Using Your Credentials

Once stored, your credentials work automatically:

```bash
# System tray (recommended)
python -m src.cli.tray_app

# Or double-click
run_tray.bat
```

No need to:
- Set environment variables
- Edit config files
- Pass command-line arguments
- Remember to export keys before each session

## Managing Credentials

### View Stored Credentials

**Windows Credential Manager:**
1. Press `Win + R`
2. Type `control keymgr.dll` and press Enter
3. Click "Windows Credentials"
4. Look for "MullyMouthGolfCaddy" entries

### Update Credentials

Run the setup tool again:

```bash
python setup_credentials.py
```

It will detect existing credentials and ask if you want to update them.

### Delete Credentials

**Option A: Python Script**
```python
from src.lib.credentials import CredentialsManager

creds = CredentialsManager()
creds.clear_all()
print("Credentials cleared")
```

**Option B: Windows Credential Manager**
1. Open Credential Manager (see above)
2. Find "MullyMouthGolfCaddy" entries
3. Click each one and select "Remove"

## Security Benefits

### Safe for Public Repositories

Your API keys are **never** stored in:
- ✅ Source code files
- ✅ Config files (config/config.yaml can stay in .gitignore)
- ✅ Environment variable files (.env)
- ✅ Batch files (run_tray_with_keys.bat is .gitignored)
- ✅ Git history

### Windows Security

Windows Credential Manager uses:
- **DPAPI** (Data Protection API) for encryption
- **User-specific encryption** - only your Windows account can decrypt
- **System-level security** - protected by Windows authentication
- **No master password needed** - uses your Windows login

### Multi-User Support

Each Windows user account has separate credential storage:
- Developer account credentials stay separate from admin account
- Multiple users on same PC can have different API keys
- No credential mixing or conflicts

## Comparison of Methods

| Method | Security | Convenience | Git Safe | Multi-PC |
|--------|----------|-------------|----------|----------|
| **Secure Storage** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | Manual |
| Environment Vars | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ | Manual |
| Config File | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⚠️ | ✅ |
| Batch File | ⭐ | ⭐⭐⭐⭐ | ⚠️ | Manual |

**Legend:**
- **Security**: How secure the storage method is
- **Convenience**: How easy it is to use
- **Git Safe**: Safe to use with public GitHub repos
- **Multi-PC**: Easy to sync across multiple computers

**Recommendation:** Use **Secure Storage** for best security + convenience on single PC. Use **Environment Variables** if you need to sync config files across multiple PCs via Git.

## Troubleshooting

### "keyring library not available"

**Solution:**
```bash
pip install keyring
```

### "Failed to store credentials"

**Possible causes:**
1. Not running on Windows (keyring works on other platforms but may need different backends)
2. Windows Credential Manager is disabled (group policy)
3. Insufficient permissions

**Solution:**
- Verify you're on Windows
- Check Windows Credential Manager is accessible: `control keymgr.dll`
- Run as administrator if needed

### Credentials not loading

**Check priority order:**
1. Are stored credentials set? Run `python setup_credentials.py` to check
2. Are environment variables set? Check with `echo %ANTHROPIC_API_KEY%`
3. Is config file present? Check `config/config.yaml` exists

**Debug:**
```python
from src.lib.credentials import CredentialsManager

creds = CredentialsManager()
print(f"Has credentials: {creds.has_credentials()}")
print(f"Anthropic key: {'SET' if creds.get_anthropic_key() else 'NOT SET'}")
print(f"ElevenLabs key: {'SET' if creds.get_elevenlabs_key() else 'NOT SET'}")
```

### Want to use config file instead

No problem! The app checks credentials in priority order. If you want to use config file:

1. Delete stored credentials (see "Delete Credentials" above)
2. Don't set environment variables
3. Create and edit `config/config.yaml` with your keys

The app will fall back to config file automatically.

## Best Practices

### For Public GitHub Repos

1. ✅ **DO**: Use secure credential storage
2. ✅ **DO**: Keep `config/config.yaml` in `.gitignore`
3. ✅ **DO**: Use environment variables for CI/CD
4. ❌ **DON'T**: Commit API keys in any file
5. ❌ **DON'T**: Put keys in code comments or documentation

### For Development

1. Use secure storage on your development PC
2. Use environment variables in CI/CD pipelines
3. Document which environment variables are needed
4. Provide config.yaml.template with placeholder values

### For Distribution

If distributing to non-technical users:

1. Provide `setup_credentials.py` script
2. Include clear instructions in README
3. Mention `run_tray.bat` for easy launching
4. Don't require users to edit config files

## Technical Details

### How keyring Works

The `keyring` library provides a unified interface to system credential storage:

**On Windows:**
- Uses Windows Credential Manager (DPAPI)
- Credentials stored in: `%USERPROFILE%\AppData\Local\Microsoft\Credentials`
- Encrypted with user's Windows login credentials

**On macOS:**
- Uses Keychain
- Credentials in Keychain Access app

**On Linux:**
- Uses Secret Service (Gnome Keyring, KWallet)
- May require additional packages

### Credential Keys

Credentials are stored with these identifiers:

- **Service**: `MullyMouthGolfCaddy`
- **Anthropic Key**: `anthropic_api_key`
- **ElevenLabs Key**: `elevenlabs_api_key`

### Code Reference

See `src/lib/credentials.py` for the implementation:
- `CredentialsManager` class
- Storage: `store_anthropic_key()`, `store_elevenlabs_key()`
- Retrieval: `get_anthropic_key()`, `get_elevenlabs_key()`
- Management: `clear_all()`, `has_credentials()`

See `src/lib/config.py` for priority loading:
- Line ~213: Attempts to load from credential store
- Line ~225: Falls back to environment variables
- Line ~230: Falls back to config file

## FAQ

**Q: Can I see my stored API keys?**
A: No, Windows Credential Manager only shows that they exist. You can't view the actual key values (by design, for security).

**Q: What if I forget my Windows password?**
A: Your credentials are tied to your Windows account. If you change your Windows password, you may need to re-enter credentials.

**Q: Can I export credentials to another PC?**
A: No, credentials are encrypted per-user, per-machine. You'll need to run `setup_credentials.py` on each PC.

**Q: Is this more secure than environment variables?**
A: Yes, because environment variables can leak in process listings, logs, or shell history. Credential Manager is specifically designed for secrets.

**Q: Do I need admin rights?**
A: No, standard user accounts can use Windows Credential Manager.

**Q: Will this work in Docker?**
A: No, use environment variables for containerized deployments.

---

## Summary

**For most users:** Use secure credential storage with `setup_credentials.py`. It's the safest and most convenient option for local development on Windows.

**For advanced users:** Environment variables or config files give you more control, but require careful Git hygiene to avoid committing secrets.

**For public repos:** Always use secure storage or environment variables - never commit API keys in any file!
