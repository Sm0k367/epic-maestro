# Epic Maestro SOTA - Tmux Session Guide

## 🎬 Overview

The `start-sota-tmux.sh` script creates a fully organized tmux session with **6 synchronized windows**, each monitoring a different aspect of the SOTA stack.

Perfect for developers who want a unified view of the entire system.

---

## 🚀 Quick Start

### Install Tmux (if needed)

**Ubuntu/Debian:**
```bash
sudo apt-get install tmux
```

**macOS:**
```bash
brew install tmux
```

**Windows (WSL2):**
```bash
sudo apt-get install tmux
```

### Launch SOTA Tmux Session

```bash
cd epic-maestro
./start-sota-tmux.sh
```

That's it! A complete 6-window session will open automatically.

---

## 📋 Window Layout

| Window | Name | Purpose | Refresh |
|--------|------|---------|---------|
| 0 | **Docker** | Live docker-compose logs | Real-time |
| 1 | **Maestro** | API health checks | Every 5s |
| 2 | **SOTA** | Chat endpoint status | Every 10s |
| 3 | **Stats** | CPU/Memory usage | Every 2s |
| 4 | **Shell** | Interactive bash | On-demand |
| 5 | **Browser** | Web UI links | One-time |

---

## 🎮 Tmux Shortcuts

### Navigate Between Windows

| Shortcut | Action |
|----------|--------|
| `Ctrl+B n` | Next window |
| `Ctrl+B p` | Previous window |
| `Ctrl+B 0-5` | Jump to specific window (0=Docker, 1=Maestro, etc.) |
| `Ctrl+B w` | Window list (interactive) |

### Split Panes (Advanced)

| Shortcut | Action |
|----------|--------|
| `Ctrl+B %` | Split pane vertically |
| `Ctrl+B "` | Split pane horizontally |
| `Ctrl+B x` | Close current pane |
| `Ctrl+B Arrow` | Navigate between panes |

### Session Management

| Shortcut | Action |
|----------|--------|
| `Ctrl+B d` | Detach (leaves session running) |
| `Ctrl+B [` | Enter scroll mode (press `q` to exit) |
| `Ctrl+B ,` | Rename current window |
| `Ctrl+B $` | Rename current session |

---

## 🔄 Common Workflows

### Monitor Everything While Coding

1. Run: `./start-sota-tmux.sh`
2. Press `Ctrl+B 4` to go to **Shell** window
3. Edit code, run tests, etc.
4. Press `Ctrl+B 0` to check **Docker** logs anytime
5. Press `Ctrl+B 1` to verify **Maestro** API is healthy

### Detach and Reattach

Leave the session running in the background:
```bash
# In tmux, press Ctrl+B d (detach)
```

Reconnect later:
```bash
tmux attach -t SOTA
```

### View All Windows at Once

Split a pane and arrange windows:
```bash
# In tmux:
# Ctrl+B 3    -> Go to Stats window
# Ctrl+B %    -> Split vertically
# Ctrl+B "    -> Split horizontally
# Now you have Stats + another pane visible
```

### Kill the Session

```bash
tmux kill-session -t SOTA
```

Or in tmux:
```bash
Ctrl+B :  (enter command mode)
kill-session
```

---

## 📊 What Each Window Shows

### 1. Docker (Window 0)
```
Live streaming logs from all containers:
- epic-maestro-master
- ollama
- acer-worker
- lenovo-gateway

Shows real-time events, errors, API requests
```

### 2. Maestro (Window 1)
```
Health check loop (every 5 seconds):
✓ API is UP   (if /docs responds)
✗ API is DOWN (if no response)

Watch this window to know when API is ready
```

### 3. SOTA (Window 2)
```
Chat endpoint status (every 10 seconds):
Sends test message: {"user_id":"monitor","message":"status"}
Shows JSON response or "Waiting for SOTA..."

Confirms chat agent is responsive
```

### 4. Stats (Window 3)
```
Container resource usage (updates every 2 seconds):
epic-maestro-master  0.12%   245MB
ollama              2.45%   1.2GB
acer-worker         0.08%   156MB
lenovo-gateway      0.04%   89MB

Monitor for memory leaks or CPU spikes
```

### 5. Shell (Window 4)
```
Interactive bash shell in epic-maestro directory

Available commands:
- docker ps
- docker logs <container>
- curl -s http://localhost:8800/docs
- python3 test_sota.py
- etc.
```

### 6. Browser (Window 5)
```
Opens SOTA web UI automatically:
- http://localhost:8800/chat
- http://localhost:8800/docs

On WSL2: Shows the URLs (open manually)
```

---

## 🔧 Troubleshooting

### "tmux: command not found"
Install tmux (see Quick Start section above)

### Script doesn't run: "Permission denied"
```bash
chmod +x start-sota-tmux.sh
./start-sota-tmux.sh
```

### Session won't start: "Docker is not running"
```bash
# Start Docker first
docker-compose up -d
```

### Panes show "Waiting for SOTA..."
- Docker container is still booting
- Wait 15-30 seconds for Maestro to fully start
- Check Docker window (Ctrl+B 0) for errors

### Can't detach session
Make sure you're using `Ctrl+B` (not `Ctrl+A`):
- Hold `Ctrl`
- Press `B`
- Release both
- Press `d`

### Reconnect to session after closing terminal
```bash
tmux attach -t SOTA
```

If that doesn't work:
```bash
tmux list-sessions  # See all active sessions
tmux attach -t SOTA
```

---

## 🎨 Customizing the Session

Edit `start-sota-tmux.sh` to add or modify windows:

```bash
# Add a new window for testing
tmux new-window -t $SESSION -n "Tests"
tmux send-keys -t $SESSION:Tests "cd '$REPO_DIR' && python3 -m pytest -v" Enter
```

Or change window refresh intervals:
```bash
# Change Maestro check from 5s to 10s
sleep 10  # instead of sleep 5
```

---

## 📚 Useful Links

- **Tmux Manual**: `man tmux`
- **Cheat Sheet**: https://tmuxcheatsheet.com/
- **SOTA Chat UI**: http://localhost:8800/chat
- **API Docs**: http://localhost:8800/docs

---

## ⚡ Pro Tips

1. **Use `Ctrl+B [` to scroll** - See old log messages you missed
2. **Name windows** - `Ctrl+B ,` to rename for clarity
3. **Save session layout** - `tmux list-windows` shows structure
4. **Copy text** - `Ctrl+B [`, navigate, hold Shift+click to select, `Ctrl+C`
5. **Resize panes** - `Ctrl+B :` then type `resize-pane -Z` to zoom

---

## 🎯 Complete Example Session

```bash
# Terminal 1: Start SOTA with tmux
$ cd ~/epic-maestro
$ ./start-sota-tmux.sh

# You see 6 windows appear
# Docker window shows: "Pulling image epic-maestro-maestro..."
# After 30 seconds:
# Maestro window shows: "✓ API is UP"
# SOTA window shows: JSON response with status
# Stats shows CPU/memory

# Switch to Shell (Ctrl+B 4)
# Run manual tests:
$ curl http://localhost:8800/docs
$ docker ps

# Switch to Browser (Ctrl+B 5)
# Opens http://localhost:8800/chat automatically

# Detach when done (Ctrl+B d)
# Session keeps running

# Later, reconnect:
$ tmux attach -t SOTA
```

---

**Everything SOTA in one organized terminal!** 🎉
