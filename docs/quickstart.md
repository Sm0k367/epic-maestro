# Epic Maestro - Quick Start

Get Maestro reasoning about your infrastructure in 10 minutes.

## Prerequisites

- Python 3.10+
- Your distributed fleet running (Ollama, Lenovo, Acer)
- Internet connection (for initial setup only)

## Installation

```bash
# Clone
git clone https://github.com/yourusername/epic-maestro
cd epic-maestro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -r requirements.txt
```

## Start Maestro

```bash
# Run the API server
python -m api.server

# You should see:
# INFO:     Started server process [1234]
# INFO:     Uvicorn running on http://0.0.0.0:8800
```

## First Reasoning

Open another terminal:

```bash
# Ask Maestro to reason
curl -X POST http://localhost:8800/api/v1/reason \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Create final video from 3 sources",
    "context": {
      "videos": ["video1.mp4", "video2.mp4", "video3.mp4"],
      "deadline": "2 minutes"
    }
  }'

# Response:
{
  "status": "reasoned",
  "decision": {
    "action": "stitch_videos",
    "target_node": "acer",
    "reason": "Acer has lowest utilization (20%). Using lossless copy mode for speed.",
    "confidence": 0.95,
    "risk_level": "low"
  }
}
```

## Queue Your First Job

```bash
curl -X POST http://localhost:8800/api/v1/jobs/queue \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "video_stitch",
    "inputs": ["video1.mp4", "video2.mp4"],
    "priority": 1
  }'

# Response:
{
  "job_id": "job_0_1728139200.123",
  "assigned_node": "acer",
  "decision_reason": "Acer has lowest utilization...",
  "status": "queued"
}
```

## Watch Maestro Think

```bash
# Get live dashboard
curl http://localhost:8800/api/v1/dashboard | python -m json.tool

# You'll see:
# - Fleet state (all nodes + utilization)
# - Recent decisions
# - Learned patterns
# - Prevention measures active
```

## From PowerShell

If you prefer Windows:

```powershell
# Import module
Import-Module .\core\windows_integration.ps1

# Ask Maestro what to do
$decision = Invoke-MaestroReasoning `
    -Objective "Create video" `
    -Context @{ videos = @("v1.mp4", "v2.mp4") }

Write-Host "Maestro says: $($decision.reason)"

# Queue a job
$job = Queue-MaestroJob `
    -JobType "video_stitch" `
    -Inputs @("v1.mp4", "v2.mp4") `
    -Priority 1

Write-Host "Job queued: $($job.job_id)"
```

## Define a Workflow

Your typical workflow is:
1. Inference (think)
2. Stitch (create)  
3. Broadcast (share)

```bash
curl -X POST http://localhost:8800/api/v1/workflows/chain \
  -H "Content-Type: application/json" \
  -d '{
    "name": "morning_workflow",
    "description": "Daily content creation",
    "jobs": [
      {
        "job_type": "inference",
        "inputs": ["daily_prompt"],
        "parameters": {"model": "mistral"}
      },
      {
        "job_type": "video_stitch",
        "inputs": ["content1.mp4", "content2.mp4"]
      },
      {
        "job_type": "broadcast",
        "inputs": ["final_video.mp4"]
      }
    ]
  }'

# Next time: Maestro auto-chains these
```

## Report a Failure (So It Learns)

```bash
curl -X POST http://localhost:8800/api/v1/failures/report \
  -H "Content-Type: application/json" \
  -d '{
    "error": "Lenovo gateway timeout",
    "context": {
      "queue_length": 52,
      "node": "lenovo",
      "job_id": "job_123"
    }
  }'

# Maestro learns: "When queue > 50, Lenovo times out"
# Next time: Routes to Acer early to prevent it
```

## Check Healing Status

```bash
curl http://localhost:8800/api/v1/healing/status

# Response shows:
# - How many failures learned
# - Patterns detected
# - Prevention strategies active
```

## Live Reasoning Stream

```bash
# Connect via WebSocket for live reasoning
# (Requires WebSocket client)

# URL: ws://localhost:8800/ws/maestro

# Receive events like:
# {"event": "reasoning", "action": "stitch_videos", ...}
# {"event": "learning", "pattern": "morning_workflow", ...}
# {"event": "healing", "prevented": "lenovo_timeout", ...}
```

## Next Steps

1. **Explore** — Check out `/docs` for detailed architecture
2. **Integrate** — Connect your applications to the API
3. **Learn** — Let Maestro observe your workflows for a week
4. **Optimize** — Watch it make smarter decisions over time
5. **Extend** — Add custom reasoning logic for your needs

## Troubleshooting

### "Connection refused" to Lenovo/Acer
```
Your infrastructure might not be running.
Start: SOTA-Local-AI, Lenovo gateway, Acer worker first
```

### "Module not found" errors
```
Ensure you're in virtual environment:
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
```

### API doesn't start
```
Check port 8800 is free:
lsof -i :8800  # Linux/Mac
netstat -ano | findstr :8800  # Windows
```

## Where to Go From Here

- **Architecture** — `docs/architecture.md`
- **API Reference** — `docs/api.md` (coming soon)
- **Examples** — `examples/` directory
- **Contributing** — `CONTRIBUTING.md`

---

**Congratulations! You now have an intelligent orchestration system.**

It will get smarter every time you use it.
