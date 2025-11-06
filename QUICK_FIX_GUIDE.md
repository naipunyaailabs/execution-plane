# Quick Fix Guide - Ollama Connection Issue

## Problem
```
ERROR: Failed to connect to Ollama. Please check that Ollama is downloaded, running and accessible.
```

## Root Cause
Ollama service was not running when the backend started, so the memory service failed to initialize.

---

## ✅ Solution (Already Applied)

Ollama has been started for you. Now you need to restart your backend.

---

## Steps to Restart Backend

### If Running in Terminal

1. **Stop the backend**: Press `Ctrl + C` in the terminal where backend is running

2. **Start it again**:
```bash
cd backend
source venv/bin/activate
python main.py
```

3. **Verify Ollama is running** (should show models):
```bash
ollama list
```

Expected output:
```
NAME                    ID              SIZE    MODIFIED
qwen3-embedding:0.6b    ac6da0dfba84    639 MB  ...
```

---

## Verify Memory Service Works

After restarting backend, you should see:
```
INFO:services.memory_service:Mem0 Memory initialized with Qdrant (path=/tmp/qdrant) and Ollama embeddings (qwen3-embedding:0.6b)
```

No more "Failed to connect to Ollama" errors ✓

---

## Test Session Memory

1. **Open chat interface**: http://localhost:5173 (or your frontend port)

2. **Chat with agent**:
   ```
   User: "My name is Alice"
   Agent: "Nice to meet you, Alice!"
   
   User: "What's my name?"
   Agent: "Your name is Alice" ✓ (memory works)
   ```

3. **Refresh page**

4. **Ask again**:
   ```
   User: "What's my name?"
   Agent: "I don't have that information" ✓ (memory cleared)
   ```

---

## If Ollama Stops Again

**Start Ollama manually**:
```bash
ollama serve
```

Or run in background:
```bash
ollama serve > /dev/null 2>&1 &
```

**Check if Ollama is running**:
```bash
curl http://localhost:11434/api/tags
```

Should return JSON with models list.

---

## Auto-Start Ollama (Optional)

### On macOS

Add to `~/.zshrc` or `~/.bash_profile`:
```bash
# Auto-start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve > /dev/null 2>&1 &
fi
```

Then reload:
```bash
source ~/.zshrc
```

### System Service (Better)

Ollama should auto-start if installed via the official installer. If not:

1. Download from: https://ollama.com/download
2. Install the .dmg file
3. Ollama will start automatically on login

---

## Troubleshooting

### Issue: Port 11434 already in use
```bash
# Kill existing Ollama process
pkill ollama
# Wait 2 seconds
sleep 2
# Start again
ollama serve &
```

### Issue: Embedding model missing
```bash
# Pull the model
ollama pull qwen3-embedding:0.6b
```

### Issue: Backend still shows error after restart
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Check backend logs for "Mem0 Memory initialized"
3. If still failing, check Qdrant: `ls -la /tmp/qdrant`

---

## Summary

✅ **Ollama is now running**  
✅ **Memory service tested and working**  
⚠️ **Action required**: Restart your backend server

After restart, session-based memory will work as expected!
