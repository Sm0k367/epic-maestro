# Epic Maestro SOTA - Quick Reference Card

## 🎯 One-Minute Setup

Pick your platform:

### Windows (Easiest)
```batch
Double-click: START_SOTA.bat
```

### Windows (Terminal)
```powershell
.\Start-SOTA.ps1
```

### Linux / macOS / WSL2 (Developer)
```bash
./start-sota-tmux.sh
```

### Any Platform (Manual)
```bash
docker-compose up -d
```

Then open: **http://localhost:8800/chat**

---

## 🎮 Tmux Cheat Sheet

If using `./start-sota-tmux.sh`:

| Shortcut | Action |
|----------|--------|
| `Ctrl+B 0` | Docker logs |
| `Ctrl+B 1` | Maestro health |
| `Ctrl+B 2` | SOTA chat status |
| `Ctrl+B 3` | CPU/Memory stats |
| `Ctrl+B 4` | Interactive shell |
| `Ctrl+B 5` | Browser links |
| `Ctrl+B n` | Next window |
| `Ctrl+B d` | Detach session |
| `Ctrl+B [` | Scroll through logs |

Reconnect: `tmux attach -t SOTA`

---

## 🌐 Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **SOTA Chat** | http://localhost:8800/chat | Main web UI |
| **API Docs** | http://localhost:8800/docs | Swagger documentation |
| **Swagger UI** | http://localhost:8800/docs | Try API endpoints |

---

## 📦 Container Ports

| Container | Port | Service |
|-----------|------|---------|
| epic-maestro-master | 8800 | SOTA API + Chat UI |
| ollama | 11434 | Local LLM models |
| acer-worker | 8780 | Worker node |
| lenovo-gateway | 18789 | Gateway coordinator |

---

## 🔧 Useful Commands

### Check container status
```bash
docker ps -a --filter "name=epic"
```

### View logs for Maestro
```bash
docker logs epic-maestro-master -f
```

### Stop all containers
```bash
docker-compose down
```

### Full rebuild
```bash
docker-compose down
docker system prune -f
docker-compose up -d
```

### Test SOTA endpoint
```bash
curl -X POST http://localhost:8800/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","message":"Hello"}'
```

---

## 🆘 Troubleshooting

### Containers won't start
- Make sure Docker is running
- Check: `docker ps`

### API returns 404
- Containers still booting (wait 20 seconds)
- Check logs: `docker logs epic-maestro-master`

### SOTA says "Waiting for..."
- Maestro container still initializing
- Check Tmux window [1] (Maestro health)
- Or view: `docker logs epic-maestro-master`

### Can't connect to localhost:8800
- Verify containers are running: `docker ps`
- Check firewall (port 8800 should be open)
- Try: http://127.0.0.1:8800/chat

### Tmux won't attach
```bash
tmux list-sessions  # See all sessions
tmux attach -t SOTA
```

---

## 📚 Learn More

- **Full Startup Guide**: See `STARTUP_GUIDE.md`
- **Tmux Deep Dive**: See `TMUX_GUIDE.md`
- **API Reference**: Open http://localhost:8800/docs
- **GitHub**: https://github.com/Sm0k367/epic-maestro

---

## 🚀 What to Try First

1. Start SOTA using your preferred method (see above)
2. Open http://localhost:8800/chat in browser
3. Type: `"What can you do?"`
4. SOTA responds with capabilities
5. Try: `"System health"` to see container status
6. Explore: http://localhost:8800/docs for full API

---

**You're all set!** 🎉 Everything SOTA is running and ready.
