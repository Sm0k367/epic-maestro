# Epic Maestro - Deployment Guide

## Overview

Epic Maestro is a **local-first** intelligent orchestration system:
- **Primary Compute**: Runs 100% locally on Lenovo
- **Optional Cloud Sync**: Cloudflare mirrors decisions and patterns (optional)
- **Multi-Agent Reasoning**: Swarm of specialized agents collaborate via group chat
- **Model Ensemble**: HuggingFace + Ollama + local models automatically routed
- **Self-Healing**: Learns from failures, prevents recurrence

## Prerequisites

### Local Setup
- Lenovo machine with 16GB+ RAM
- Docker & Docker Compose (or Python 3.10+)
- FFmpeg for video processing
- Ollama for local LLMs (optional, system handles gracefully if offline)

### Cloudflare Setup (Optional)
- Cloudflare account
- API token with Workers, KV, D1, R2 permissions
- Namespace ID, Database ID, Bucket name

## Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate
cd epic-maestro

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f maestro

# Check health
curl http://localhost:8800/health

# Access live dashboard (coming soon)
# http://localhost:8800/dashboard
```

Services started:
- `maestro`: Main orchestration server (port 8800)
- `ollama`: Local LLM inference (port 11434)
- `acer-worker`: Simulated worker node (port 8780)
- `lenovo-gateway`: Gateway (port 18789)

### Option 2: Local Python Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start server
python3 -m uvicorn api.maestro_server:app --host 0.0.0.0 --port 8800

# Test endpoint
curl http://localhost:8800/health
```

### Option 3: Cloudflare Deployment

```bash
# Install Wrangler
npm install -g wrangler

# Configure Cloudflare
wrangler login

# Deploy
wrangler deploy
```

## Configuration

### Local Mode (Default)
```python
from core.cloudflare_integration import LocalLenovoHub

hub = LocalLenovoHub()  # 100% local, no cloud
```

### With Cloudflare Sync
```bash
# POST to enable Cloudflare
curl -X POST http://localhost:8800/enable-cloudflare-sync \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "your_account_id",
    "api_token": "your_api_token",
    "namespace_id": "your_namespace",
    "database_id": "your_database",
    "r2_bucket": "your_bucket"
  }'
```

Or set environment variables:
```bash
CLOUDFLARE_ACCOUNT_ID=xxx
CLOUDFLARE_API_TOKEN=xxx
CLOUDFLARE_NAMESPACE_ID=xxx
CLOUDFLARE_DATABASE_ID=xxx
CLOUDFLARE_R2_BUCKET=xxx
```

## API Usage

### REST Endpoints

#### 1. Orchestrate Decision
```bash
curl -X POST 'http://localhost:8800/orchestrate?objective=Process%20video%20stitch' \
  -H 'Content-Type: application/json' \
  -d '{
    "task_type": "video_stitch",
    "latency_budget_ms": 5000,
    "quality_required": 0.95,
    "fleet_state": {
      "nodes": {
        "acer": {"utilization": 0.2},
        "lenovo": {"utilization": 0.5}
      }
    }
  }'
```

#### 2. Query Model
```bash
curl -X POST 'http://localhost:8800/query?prompt=What%20is%20AI&task_type=reasoning' \
  -H 'Content-Type: application/json'
```

#### 3. Report Failure
```bash
curl -X POST 'http://localhost:8800/failure?node=acer&error=timeout' \
  -H 'Content-Type: application/json' \
  -d '{"timeout_ms": 5000}'
```

#### 4. Get System Status
```bash
curl http://localhost:8800/system/info | jq .
```

#### 5. List Recent Decisions
```bash
curl http://localhost:8800/decisions?limit=20 | jq .
```

### WebSocket - Live Streaming

```python
import asyncio
import websockets
import json

async def livestream():
    async with websockets.connect("ws://localhost:8800/ws/maestro") as ws:
        # Receive initial connection
        msg = await ws.recv()
        print(f"Connected: {msg}")
        
        # Send orchestration request
        await ws.send(json.dumps({
            "type": "orchestrate",
            "objective": "Process video with deadline",
            "context": {"deadline_seconds": 5}
        }))
        
        # Receive decision in real-time
        decision = await ws.recv()
        print(f"Decision: {decision}")

asyncio.run(livestream())
```

### Batch Operations

```bash
# Multiple orchestrations
curl -X POST http://localhost:8800/batch/orchestrate \
  -H 'Content-Type: application/json' \
  -d '[
    {"objective": "Task 1", "context": {}},
    {"objective": "Task 2", "context": {}},
    {"objective": "Task 3", "context": {}}
  ]'

# Multiple queries
curl -X POST http://localhost:8800/batch/query \
  -H 'Content-Type: application/json' \
  -d '[
    {"prompt": "Question 1", "task_type": "reasoning"},
    {"prompt": "Question 2", "task_type": "reasoning"}
  ]'
```

## System Architecture

### Components

```
┌─────────────────────────────────────────┐
│         Lenovo Master (Local)           │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Swarm Agents                   │   │
│  │  ├─ VideoAgent                  │   │
│  │  ├─ InferenceAgent              │   │
│  │  ├─ RoutingAgent                │   │
│  │  └─ HealingAgent                │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Model Ensemble                 │   │
│  │  ├─ Ollama (local LLM)          │   │
│  │  ├─ HuggingFace (local cached)  │   │
│  │  └─ HF API (remote, fallback)   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  REST + WebSocket API           │   │
│  │  Port 8800                      │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
         ↓ (Optional)
┌─────────────────────────────────────────┐
│     Cloudflare Cloud Services           │
│  ├─ KV: Decision cache                  │
│  ├─ D1: Decision history                │
│  ├─ R2: Artifact storage                │
│  └─ Workers: API gateway                │
└─────────────────────────────────────────┘
```

### Data Flow

1. **Request comes in** → REST/WebSocket → Maestro API
2. **Swarm orchestrates** → All agents discuss → Consensus reached
3. **Model selected** → Ensemble routes to best model (local preferred)
4. **Decision recorded** → Local storage (always) + cloud sync (optional)
5. **Result returned** → WebSocket client notified in real-time
6. **Analytics** → Cloudflare D1 stores patterns for learning

## Monitoring

### Health Checks
```bash
# Basic health
curl http://localhost:8800/health

# Full system info
curl http://localhost:8800/system/info | jq .

# Swarm state
curl http://localhost:8800/swarm/state

# Model ensemble stats
curl http://localhost:8800/ensemble/state

# Lenovo hub status
curl http://localhost:8800/hub/state
```

### Docker Logs
```bash
# Maestro logs
docker-compose logs maestro -f

# All services
docker-compose logs -f

# Specific service
docker-compose logs ollama -f
```

## Performance Tuning

### For Low Latency
```bash
# Use fast local models only
curl -X POST 'http://localhost:8800/query' \
  -d '{
    "prompt": "Quick inference",
    "task_type": "general",
    "latency_budget_ms": 200
  }'
```

### For High Quality
```bash
# Use large models with time budget
curl -X POST 'http://localhost:8800/query' \
  -d '{
    "prompt": "Complex reasoning",
    "task_type": "reasoning",
    "latency_budget_ms": 5000,
    "quality_required": 0.95
  }'
```

### Parallel Reasoning
```bash
# Ensemble multiple models for decisions
curl -X POST 'http://localhost:8800/parallel-ensemble' \
  -d '{
    "prompt": "How to optimize?",
    "num_models": 3,
    "task_type": "reasoning"
  }'
```

## Troubleshooting

### Ollama Connection Issues
- Maestro works offline - system gracefully fallsback
- Check: `curl http://localhost:11434/api/models`
- Restart: `docker-compose restart ollama`

### High Latency
- Check node utilization: `curl http://localhost:8800/ensemble/state`
- Switch to faster model: reduce `latency_budget_ms`
- Enable parallel queries: `/parallel-ensemble`

### Cloudflare Sync Failures
- System continues locally regardless
- Check credentials: `POST /enable-cloudflare-sync`
- Verify KV/D1/R2 are created in Cloudflare dashboard

## Testing

```bash
# Run all tests
pytest tests/ -v

# Specific test file
pytest tests/test_swarm.py -v

# With coverage
pytest tests/ --cov=core

# Performance tests
pytest tests/ -k "Performance" -v
```

## Production Checklist

- [ ] Docker image built and tested
- [ ] All environment variables set
- [ ] Cloudflare sync configured (if using)
- [ ] SSL/TLS certificates configured
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Monitoring and logging configured
- [ ] Backup strategy for local decisions
- [ ] Rate limiting configured
- [ ] CORS settings appropriate

## Support

For issues:
1. Check logs: `docker-compose logs maestro`
2. Run tests: `pytest tests/ -v`
3. Check health: `curl http://localhost:8800/health`
4. Review system info: `curl http://localhost:8800/system/info`

## License

MIT - See LICENSE file
