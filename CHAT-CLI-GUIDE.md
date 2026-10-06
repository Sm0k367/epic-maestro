# SOTA Chat CLI - Complete User Guide

**Interactive Command-Line Chat with SOTA**

Chat with the State-of-the-Art Orchestration Agent directly from your terminal - no browser required!

## Quick Start (30 seconds)

### Windows (CMD)
```cmd
cd "C:\Users\Epic Tech\Desktop\Epic-Maestro-Setup\epic-maestro"
python SOTA-Chat-CLI.py
```

### Linux / Mac / WSL2
```bash
cd ~/epic-maestro
python3 SOTA-Chat-CLI.py
```

### Features (immediately available)
- ✅ Real-time interactive chat
- ✅ Color-coded messages (user in green, SOTA in magenta)
- ✅ Conversation history tracking
- ✅ System commands (/help, /status, /history, /clear, /exit)
- ✅ Timestamps on every message
- ✅ Connection status monitoring
- ✅ Session tracking with unique IDs

## Running the Chat Client

### Command Syntax
```
python SOTA-Chat-CLI.py [OPTIONS]
```

### Options
- `--api URL` — SOTA API endpoint (default: `http://localhost:8800`)
- `--user ID` — Session user ID for history tracking (default: auto-generated)

### Examples

**Default (localhost)**
```cmd
python SOTA-Chat-CLI.py
```

**Custom API endpoint**
```cmd
python SOTA-Chat-CLI.py --api http://192.168.1.100:8800
```

**Custom user ID for tracking**
```cmd
python SOTA-Chat-CLI.py --user "optimization-session-001"
```

**Both parameters**
```cmd
python SOTA-Chat-CLI.py --api http://10.0.0.5:8800 --user "worker-1-chat"
```

## Available Commands

Type these commands in the chat to control the interface:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands and example queries |
| `/clear` | Clear the screen |
| `/status` | Display connection status and session info |
| `/history` | Retrieve your full conversation history |
| `/exit` | Exit the chat gracefully |

## Example Queries

Try these natural language requests:

**Infrastructure & Status**
- "System health" — Check infrastructure status
- "Check system health" — Detailed health report
- "What's running?" — See current processes

**Decision Making**
- "Infer best approach" — Get reasoning about tasks
- "What should I do?" — Get recommendations
- "Analyze this" — Detailed analysis

**Media Operations**
- "Stitch video files" — Process video stitching
- "Combine videos" — Video processing
- "Process media" — Media workflows

**Distributed Work**
- "Broadcast to workers" — Send tasks to nodes
- "Distribute work" — Load balancing
- "Scale across cluster" — Multi-node processing

**Learning & Optimization**
- "Learn patterns" — Train on workflow patterns
- "What patterns do you see?" — Pattern analysis
- "Improve performance" — Performance optimization
- "Detect failures" — Find issues
- "Root cause analysis" — Debug problems

**Small Talk**
- "What's your name?" — Introduction
- "How do you work?" — Technical explanation
- "Explain your reasoning" — Decision transparency

## Session Information

When you start the chat, you'll see:

```
══════════════════════════════════════════════════════════════
 SOTA Chat CLI - Interactive Terminal Interface
 State-of-the-Art Orchestration Agent
══════════════════════════════════════════════════════════════

[HH:MM:SS] ℹ Session ID: cli-user-1791253830.196269
[HH:MM:SS] ℹ API URL: http://localhost:8800
[HH:MM:SS] ℹ Testing connection to SOTA API...
[HH:MM:SS] ✓ Connected to SOTA API at http://localhost:8800
[HH:MM:SS] ✓ Type '/help' for commands or start chatting!
```

**Session ID** is used to retrieve your conversation history later.

## Usage Examples

### Example 1: System Health Check

```
You > System health

┌─ You [21:30:45]
│ System health
└─

[21:30:46] ℹ Sending to SOTA...

┌─ SOTA [21:30:47]
│ All systems nominal. Lenovo hub (82% CPU, 64% mem), Ollama 
│ running 20 models, Acer worker responsive, gateway stable.
└─

You >
```

### Example 2: Using Commands

```
You > /status

[21:31:37] ℹ Connection Status:
User ID: cli-user-1791253830.196269
API: http://localhost:8800
Messages Sent: 5
Session Uptime: 0:01:02

You >
```

### Example 3: Retrieving History

```
You > /history

[21:32:10] ℹ Fetching conversation history...

══════════════════════════════════════════════════════════════
Conversation History
══════════════════════════════════════════════════════════════

You: System health
SOTA: All systems nominal...
You: Infer best approach
SOTA: Based on current load, recommend...
You: /status

You >
```

## Color Coding

The chat uses terminal colors for clarity:

- 🟢 **Green** — Your messages and status
- 🟣 **Magenta** — SOTA responses
- 🔵 **Cyan** — Information and headers
- 🟡 **Yellow** — Warnings and busy status
- 🔴 **Red** — Errors

## Status Indicators

Messages show status symbols:

| Symbol | Meaning | Example |
|--------|---------|---------|
| ✓ | Success | "[21:30:34] ✓ Connected to SOTA API" |
| ✗ | Error | "[21:31:56] ✗ Failed to get response" |
| ℹ | Information | "[21:30:34] ℹ Sending to SOTA..." |
| ⚠ | Warning | "[21:32:10] ⚠ Connection slow" |
| ⟳ | Busy/Loading | "[21:30:46] ⟳ Processing request..." |

## Troubleshooting

### "Failed to get response from SOTA"

**Problem**: API returned an error

**Solutions**:
1. Ensure SOTA containers are running:
   ```cmd
   docker ps
   ```

2. Restart containers:
   ```cmd
   docker-compose down
   docker-compose up -d
   ```

3. Check API is accessible:
   ```cmd
   curl http://localhost:8800/docs
   ```

### "ConnectionError: Failed to establish connection"

**Problem**: Can't reach SOTA API

**Solutions**:
1. Check SOTA is running:
   ```cmd
   docker-compose ps
   ```

2. Verify port 8800 is open:
   ```cmd
   netstat -an | findstr 8800
   ```

3. Try custom API endpoint:
   ```cmd
   python SOTA-Chat-CLI.py --api http://127.0.0.1:8800
   ```

### Chat freezes / hangs

**Problem**: Script waiting for response

**Solutions**:
1. Press `Ctrl+C` to interrupt
2. Restart the script
3. Check SOTA server logs:
   ```cmd
   docker logs epic-maestro-master --tail 50
   ```

### No colored output in terminal

**Problem**: Terminal doesn't support ANSI colors

**Solution**: Use a modern terminal:
- **Windows**: Windows Terminal (better than CMD)
  - Download from Microsoft Store
  - Run: `python SOTA-Chat-CLI.py`

- **Linux/Mac**: Default terminal usually works
  - Fallback: Use `script -q /dev/null` wrapper

## Performance Notes

- **Connection time**: ~200ms to SOTA API
- **Response time**: 1-3 seconds for most queries
- **Throughput**: ~10-20 messages per minute
- **Session duration**: Unlimited (session persists)

## Session Persistence

Your conversation history is saved automatically:

### Retrieve history later
```cmd
# Same session ID
python SOTA-Chat-CLI.py --user "cli-user-1791253830.196269"

# Then type:
/history
```

### Access via REST API
```bash
curl http://localhost:8800/api/chat/history/cli-user-1791253830.196269
```

Response format:
```json
{
  "user_id": "cli-user-1791253830.196269",
  "messages": [
    {
      "role": "user",
      "content": "System health",
      "timestamp": "2026-10-06T21:30:45"
    },
    {
      "role": "assistant",
      "content": "All systems nominal...",
      "timestamp": "2026-10-06T21:30:46"
    }
  ]
}
```

## Advanced Usage

### Batch Testing

```bash
# Test multiple queries in sequence
python SOTA-Chat-CLI.py <<EOF
System health
Infer best approach
/history
/exit
EOF
```

### Integration with Scripts

```python
# Python script using subprocess
import subprocess

result = subprocess.run(
    ["python", "SOTA-Chat-CLI.py", "--user", "integration-test"],
    input="System health\n/exit\n",
    capture_output=True,
    text=True
)

print(result.stdout)
print(result.stderr)
```

### Custom API Server

```cmd
# Point to different server
python SOTA-Chat-CLI.py --api http://production.internal:8800
```

## Requirements

- **Python**: 3.7+ (3.10+ recommended)
- **Libraries**: `requests` (included in most Python distributions)
- **Network**: Access to SOTA API on port 8800
- **Terminal**: Supports ANSI escape codes (Windows Terminal, Linux, Mac)

## System Resource Usage

- **Memory**: ~30-50 MB while running
- **CPU**: Minimal (event-driven)
- **Network**: ~1-5 KB per message
- **Disk**: Negligible (stateless client)

## File Locations

- **Script**: `epic-maestro/SOTA-Chat-CLI.py`
- **Documentation**: `epic-maestro/CHAT-CLI-GUIDE.md`
- **Related**: 
  - `POWERSHELL_CHAT_GUIDE.md` (PowerShell versions)
  - `STARTUP_GUIDE.md` (Container startup)
  - `README.md` (Project overview)

## Support

### Check if SOTA is running

```cmd
# View container status
docker ps

# View running containers for SOTA
docker ps | findstr "maestro"

# View logs for errors
docker logs epic-maestro-master --tail 20
```

### Common Issues

**Q: Chat client connects but messages fail**
A: SOTA containers may have crashed. Check logs:
```cmd
docker logs epic-maestro-master
```

**Q: `python` command not found**
A: Install Python or use full path:
```cmd
C:\Python312\python.exe SOTA-Chat-CLI.py
```

**Q: Colors don't show in terminal**
A: Use Windows Terminal or add to .bat file:
```cmd
@echo off
python SOTA-Chat-CLI.py %*
```

## Next Steps

1. ✅ Run the chat client: `python SOTA-Chat-CLI.py`
2. ✅ Try `/help` to see available commands
3. ✅ Send a test message: "System health"
4. ✅ Check session status: `/status`
5. ✅ View history: `/history`
6. ✅ Integrate into your workflows

## Related Files

- `POWERSHELL_CHAT_GUIDE.md` — PowerShell versions (PS1 scripts)
- `SOTA_CAPABILITIES_GUIDE.md` — What SOTA can do
- `STARTUP_GUIDE.md` — Container startup (BAT, PS1, Tmux)
- `QUICK_REFERENCE.md` — One-page cheat sheet
- `API` — `http://localhost:8800/docs` (Swagger)

---

**Version**: 1.0  
**Language**: Python 3.7+  
**Status**: Production Ready  
**License**: MIT  
**Last Updated**: October 6, 2026
