"""
Epic Maestro Master Server

Integrated system combining:
- Swarm agents (VideoAgent, InferenceAgent, RoutingAgent, HealingAgent)
- Model ensemble (HuggingFace + Ollama)
- Local-first Lenovo hub with optional Cloudflare sync
- WebSocket live streaming
- REST API endpoints

All computation runs locally on Lenovo.
Cloudflare syncs decisions and patterns (optional).
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

import sys
sys.path.insert(0, '/workspace/epic-maestro')

from core.swarm import SwarmConductor, Message
from core.model_ensemble import ModelEnsemble
from core.cloudflare_integration import LocalLenovoHub, CloudflareConfig, CloudflareSync


# ============================================================================
# GLOBAL STATE
# ============================================================================

class MaestroSystem:
    """Central Maestro system - all three components integrated"""
    
    def __init__(self):
        self.swarm = SwarmConductor()
        self.ensemble = ModelEnsemble()
        self.hub = LocalLenovoHub()  # Local-first, no cloud by default
        self.websocket_clients: List[WebSocket] = []
        self.decision_log: List[Dict[str, Any]] = []
    
    async def broadcast_to_websockets(self, message: Dict[str, Any]):
        """Broadcast decision to all connected WebSocket clients"""
        for client in self.websocket_clients:
            try:
                await client.send_json(message)
            except:
                pass
    
    async def execute_orchestration(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestration and return result"""
        
        # Swarm discusses the objective
        decision = await self.swarm.orchestrate(objective, context)
        
        # Select best model for this task
        model_id, profile = await self.ensemble.select_best_model(
            task_type=context.get("task_type", "general"),
            latency_budget_ms=context.get("latency_budget_ms", 1000),
            quality_required=context.get("quality_required", 0.8)
        )
        
        # Record in local hub (and optionally sync to cloud)
        decision_id = await self.hub.record_decision({
            "action": decision.action,
            "agents": decision.supporting_agents,
            "consensus_level": decision.consensus_level,
            "model": model_id,
            "reasoning": [m.reasoning for m in decision.reasoning_chain]
        })
        
        result = {
            "decision_id": decision_id,
            "action": decision.action,
            "primary_agent": decision.primary_agent,
            "consensus_level": decision.consensus_level,
            "confidence": decision.confidence,
            "model": model_id,
            "model_quality": profile.quality_score,
            "reasoning_chain_length": len(decision.reasoning_chain),
            "timestamp": datetime.now().isoformat()
        }
        
        # Log decision
        self.decision_log.append(result)
        
        # Broadcast to WebSocket clients
        await self.broadcast_to_websockets({
            "type": "decision",
            "data": result
        })
        
        return result


# Create global system
maestro_system = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown"""
    global maestro_system
    
    print("🚀 Epic Maestro starting up...")
    maestro_system = MaestroSystem()
    print("✓ Swarm initialized")
    print("✓ Model ensemble initialized")
    print("✓ Lenovo hub initialized (local-first)")
    
    yield
    
    print("💤 Epic Maestro shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Epic Maestro",
    description="Autonomous reasoning orchestration with swarm intelligence",
    version="2.0",
    lifespan=lifespan
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REST ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "location": "lenovo-master"
    }


@app.post("/orchestrate")
async def orchestrate(objective: str, context: Dict[str, Any] = None):
    """
    Execute orchestration
    
    POST /orchestrate?objective=Process%20video%20stitch
    {
        "task_type": "video_stitch",
        "latency_budget_ms": 5000,
        "quality_required": 0.95,
        "fleet_state": {...}
    }
    """
    
    if not objective:
        raise HTTPException(status_code=400, detail="Objective required")
    
    context = context or {}
    
    try:
        result = await maestro_system.execute_orchestration(objective, context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_model(prompt: str, task_type: str = "general", latency_budget_ms: float = 1000):
    """
    Query the model ensemble directly
    
    POST /query?prompt=What%20is%20AI&task_type=reasoning&latency_budget_ms=2000
    """
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt required")
    
    try:
        result = await maestro_system.ensemble.query(
            prompt,
            task_type=task_type,
            latency_budget_ms=latency_budget_ms
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/swarm/state")
async def swarm_state():
    """Get current swarm state"""
    return maestro_system.swarm.export_swarm_state()


@app.get("/ensemble/state")
async def ensemble_state():
    """Get model ensemble state"""
    return maestro_system.ensemble.export_ensemble_state()


@app.get("/hub/state")
async def hub_state():
    """Get Lenovo hub state"""
    return maestro_system.hub.export_hub_state()


@app.get("/decisions")
async def list_decisions(limit: int = 10):
    """List recent decisions"""
    return {
        "total": len(maestro_system.decision_log),
        "recent": maestro_system.decision_log[-limit:] if maestro_system.decision_log else []
    }


@app.post("/failure")
async def report_failure(node: str, error: str, context: Dict[str, Any] = None):
    """
    Report a failure for pattern detection
    
    POST /failure?node=acer&error=timeout
    {"timeout_ms": 5000}
    """
    
    if not node or not error:
        raise HTTPException(status_code=400, detail="Node and error required")
    
    context = context or {}
    
    try:
        failure_id = await maestro_system.hub.record_failure(node, error, context)
        return {
            "failure_id": failure_id,
            "node": node,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/system/info")
async def system_info():
    """Get complete system information"""
    return {
        "node": "lenovo-master",
        "architecture": "local-first with optional cloud sync",
        "components": {
            "swarm": maestro_system.swarm.export_swarm_state(),
            "ensemble": maestro_system.ensemble.export_ensemble_state(),
            "hub": maestro_system.hub.export_hub_state()
        },
        "decisions_made": len(maestro_system.decision_log),
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# WEBSOCKET ENDPOINT - LIVE STREAMING
# ============================================================================

@app.websocket("/ws/maestro")
async def websocket_maestro(websocket: WebSocket):
    """
    WebSocket for live decision streaming
    
    ws://localhost:8800/ws/maestro
    
    Receives real-time decisions as they happen
    """
    await websocket.accept()
    
    maestro_system.websocket_clients.append(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Epic Maestro live stream",
            "node": "lenovo-master"
        })
        
        # Keep connection alive and listen for commands
        while True:
            data = await websocket.receive_text()
            
            try:
                command = json.loads(data)
                
                if command.get("type") == "orchestrate":
                    # Execute orchestration and send result
                    result = await maestro_system.execute_orchestration(
                        command.get("objective", ""),
                        command.get("context", {})
                    )
                    await websocket.send_json({
                        "type": "decision",
                        "data": result
                    })
                
                elif command.get("type") == "query":
                    # Query model
                    result = await maestro_system.ensemble.query(
                        command.get("prompt", ""),
                        task_type=command.get("task_type", "general")
                    )
                    await websocket.send_json({
                        "type": "model_response",
                        "data": result
                    })
                
                elif command.get("type") == "status":
                    # Get status
                    await websocket.send_json({
                        "type": "status",
                        "data": await system_info()
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        maestro_system.websocket_clients.remove(websocket)


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

@app.post("/batch/orchestrate")
async def batch_orchestrate(operations: List[Dict[str, Any]]):
    """
    Execute multiple orchestrations in sequence
    
    POST /batch/orchestrate
    [
        {"objective": "...", "context": {...}},
        {"objective": "...", "context": {...}},
    ]
    """
    
    results = []
    for op in operations:
        try:
            result = await maestro_system.execute_orchestration(
                op.get("objective", ""),
                op.get("context", {})
            )
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})
    
    return {
        "count": len(results),
        "results": results
    }


@app.post("/batch/query")
async def batch_query(queries: List[Dict[str, Any]]):
    """
    Query multiple prompts
    
    POST /batch/query
    [
        {"prompt": "...", "task_type": "..."},
        {"prompt": "...", "task_type": "..."},
    ]
    """
    
    results = []
    for query in queries:
        try:
            result = await maestro_system.ensemble.query(
                query.get("prompt", ""),
                task_type=query.get("task_type", "general")
            )
            results.append(result)
        except Exception as e:
            results.append({"error": str(e)})
    
    return {
        "count": len(results),
        "results": results
    }


# ============================================================================
# ADVANCED FEATURES
# ============================================================================

@app.post("/enable-cloudflare-sync")
async def enable_cloudflare_sync(
    account_id: str,
    api_token: str,
    namespace_id: str,
    database_id: str,
    r2_bucket: str
):
    """
    Enable optional Cloudflare sync
    
    Local computation continues regardless.
    Cloudflare stores decisions and patterns for analytics.
    """
    
    cf_config = CloudflareConfig(
        account_id=account_id,
        api_token=api_token,
        namespace_id=namespace_id,
        database_id=database_id,
        r2_bucket=r2_bucket,
        enabled=True
    )
    
    # Create new hub with Cloudflare
    maestro_system.hub = LocalLenovoHub(cf_config)
    
    return {
        "status": "Cloudflare sync enabled",
        "note": "Local computation continues, decisions sync to cloud"
    }


@app.post("/parallel-ensemble")
async def parallel_ensemble(prompt: str, num_models: int = 3, task_type: str = "reasoning"):
    """
    Execute prompt on multiple models in parallel for ensemble reasoning
    
    POST /parallel-ensemble?prompt=Question&num_models=3&task_type=reasoning
    """
    
    results = await maestro_system.ensemble.parallel_query(
        prompt,
        num_models=num_models,
        task_type=task_type
    )
    
    return {
        "prompt": prompt,
        "num_models": num_models,
        "results": results
    }


# ============================================================================
# EXAMPLE USAGE SCRIPT
# ============================================================================

async def example_usage():
    """Example of how to use the Maestro system"""
    
    print("\n" + "=" * 70)
    print("EPIC MAESTRO - EXAMPLE USAGE")
    print("=" * 70)
    
    # Import for demonstration
    from core.swarm import SwarmConductor
    from core.model_ensemble import ModelEnsemble
    
    swarm = SwarmConductor()
    ensemble = ModelEnsemble()
    
    # Scenario 1: Orchestrate a video stitch
    print("\n1. ORCHESTRATE: Video Stitch Decision")
    print("-" * 70)
    
    context = {
        "job_type": "video_stitch",
        "videos": ["input_1.mp4", "input_2.mp4"],
        "deadline_seconds": 5,
        "quality": "high",
        "fleet_state": {
            "nodes": {
                "ollama": {"utilization": 0.3},
                "acer": {"utilization": 0.2},
                "lenovo": {"utilization": 0.5}
            }
        },
        "failure_history": []
    }
    
    decision = await swarm.orchestrate("Process video stitch with deadline", context)
    print(f"✓ Decision: {decision.action}")
    print(f"✓ Consensus: {decision.consensus_level:.0%}")
    print(f"✓ Primary Agent: {decision.primary_agent}")
    
    # Scenario 2: Model selection
    print("\n2. MODEL SELECTION: Best Model for Task")
    print("-" * 70)
    
    model_id, profile = await ensemble.select_best_model(
        task_type="reasoning",
        latency_budget_ms=2000,
        quality_required=0.90
    )
    
    print(f"✓ Selected Model: {model_id}")
    print(f"✓ Quality Score: {profile.quality_score:.0%}")
    print(f"✓ Expected Latency: {profile.latency_ms:.0f}ms")
    
    # Scenario 3: Parallel reasoning
    print("\n3. PARALLEL REASONING: Ensemble Decision")
    print("-" * 70)
    
    results = await ensemble.parallel_query(
        "How should we process this video pipeline?",
        num_models=3,
        task_type="reasoning"
    )
    
    print(f"✓ Executed on {len(results)} models in parallel")
    
    print("\n" + "=" * 70)
    print("Ready to deploy! Start server with:")
    print("  python3 -m uvicorn api.maestro_server:app --host 0.0.0.0 --port 8800")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
