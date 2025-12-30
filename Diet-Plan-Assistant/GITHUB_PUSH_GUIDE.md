# GitHub Push Guide

## Authentication Issue Fix

You're getting an authentication error because GitHub no longer supports password authentication. You need to use a **Personal Access Token (PAT)** instead.

### Option 1: Use Personal Access Token (Recommended)

1. **Generate a Personal Access Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Give it a name: "Diet Plan Assistant"
   - Select scopes: Check `repo` (full control of private repositories)
   - Click "Generate token"
   - **IMPORTANT**: Copy the token immediately (you won't see it again!)

2. **Push using the token**:
   ```bash
   # Stop the current push (Ctrl+C if still running)
   
   # Push with token in URL (one-time)
   git push https://YOUR_TOKEN@github.com/TayyabAbbas802/Diet-Plan-Assistant.git main
   ```

3. **Or configure Git to remember credentials**:
   ```bash
   # Use credential helper
   git config --global credential.helper store
   
   # Then push (it will ask for username and token once)
   git push origin main
   # Username: TayyabAbbas802
   # Password: <paste your token here>
   ```

### Option 2: Use SSH (More Secure)

1. **Generate SSH key** (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   # Press Enter to accept default location
   # Press Enter for no passphrase (or set one)
   ```

2. **Add SSH key to GitHub**:
   ```bash
   # Copy your public key
   cat ~/.ssh/id_ed25519.pub
   # Copy the output
   ```
   
   - Go to: https://github.com/settings/keys
   - Click "New SSH key"
   - Paste your key
   - Click "Add SSH key"

3. **Change remote URL to SSH**:
   ```bash
   cd /Users/macbookpro/Documents/PythonProject1/Diet-Plan-Assistant
   git remote set-url origin git@github.com:TayyabAbbas802/Diet-Plan-Assistant.git
   git push origin main
   ```

## Quick Fix (Right Now)

The fastest way to fix your current issue:

```bash
# 1. Stop the current push (if still running)
# Press Ctrl+C in the terminal

# 2. Go to GitHub and create a token:
# https://github.com/settings/tokens/new

# 3. Push with the token:
cd /Users/macbookpro/Documents/PythonProject1/Diet-Plan-Assistant
git push https://YOUR_TOKEN_HERE@github.com/TayyabAbbas802/Diet-Plan-Assistant.git main
```

## Important: Protect Your API Keys

Your `.env` file contains sensitive API keys. Make sure it's NOT pushed to GitHub:

```bash
# Check if .env is in .gitignore
cat .gitignore | grep .env

# If you accidentally committed .env, remove it:
git rm --cached .env
git commit -m "Remove .env from tracking"
git push origin main
```

## After Successful Push

1. **Verify on GitHub**: Check https://github.com/TayyabAbbas802/Diet-Plan-Assistant

2. **Add a .env.example file** for others:
   ```bash
   cd /Users/macbookpro/Documents/PythonProject1/Diet-Plan-Assistant
   echo "USDA_API_KEY=your_usda_api_key_here" > .env.example
   echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env.example
   git add .env.example
   git commit -m "Add .env.example template"
   git push origin main
   ```

## Troubleshooting

### Port Already in Use
If you see "Port 5001 is in use":
```bash
# Find and kill the process
lsof -ti:5001 | xargs kill -9

# Or use a different port in app.py
# Change: app.run(debug=True, host='0.0.0.0', port=5002)
```

### Python Version Warnings
The warnings about Python 3.9 are harmless but you can upgrade:
```bash
# Check current version
python3 --version

# Upgrade to Python 3.10+ using Homebrew
brew install python@3.11
```

## Next Steps

After pushing successfully:

1. ✅ Add screenshots to README
2. ✅ Create a LICENSE file
3. ✅ Add GitHub topics/tags
4. ✅ Create a release/tag
5. ✅ Share your project!
