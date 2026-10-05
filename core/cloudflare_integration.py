"""
Epic Maestro Cloudflare Integration

All computation happens LOCALLY on Lenovo.
Cloudflare is used for:
- Optional cloud sync (decisions, patterns, analytics)
- Public API gateway (optional)
- Backup storage (R2)
- Historical archive (D1)

Local-first architecture:
- Lenovo runs everything (swarm, ensemble, reasoning)
- Cloudflare mirrors state (eventual consistency)
- Works 100% offline if needed
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
import aiohttp
from enum import Enum


class CloudflareService(Enum):
    """Cloudflare services available"""
    KV = "kv"           # Distributed cache
    D1 = "d1"           # SQLite database
    R2 = "r2"           # Object storage
    WORKERS = "workers" # Serverless compute


@dataclass
class CloudflareConfig:
    """Cloudflare configuration"""
    account_id: str
    api_token: str
    namespace_id: str  # For KV
    database_id: str   # For D1
    r2_bucket: str
    enabled: bool = True  # Can disable for offline mode
    sync_interval_seconds: int = 60


class CloudflareKVStore:
    """Cloudflare KV - distributed cache for hot data"""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{config.account_id}/storage/kv/namespaces/{config.namespace_id}"
        self.local_cache: Dict[str, Any] = {}  # Local fallback
    
    async def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Store value in KV (with local fallback)"""
        
        # Always store locally first
        self.local_cache[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "ttl": ttl_seconds
        }
        
        # Try cloud sync if enabled
        if not self.config.enabled:
            return True
        
        try:
            headers = {"Authorization": f"Bearer {self.config.api_token}"}
            data = json.dumps(value)
            
            url = f"{self.base_url}/values/{key}"
            if ttl_seconds:
                url += f"?expiration_ttl={ttl_seconds}"
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, data=data, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"KV sync failed (local cache active): {e}")
            return True  # Local cache ensures no data loss
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from KV (local first, then cloud)"""
        
        # Try local cache first
        if key in self.local_cache:
            cached = self.local_cache[key]
            return cached["value"]
        
        # Try cloud if enabled
        if not self.config.enabled:
            return None
        
        try:
            headers = {"Authorization": f"Bearer {self.config.api_token}"}
            url = f"{self.base_url}/values/{key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Cache locally
                        self.local_cache[key] = data
                        return data
        except Exception as e:
            print(f"KV retrieval failed (using local cache): {e}")
        
        return None
    
    async def delete(self, key: str) -> bool:
        """Delete from KV"""
        
        if key in self.local_cache:
            del self.local_cache[key]
        
        if not self.config.enabled:
            return True
        
        try:
            headers = {"Authorization": f"Bearer {self.config.api_token}"}
            url = f"{self.base_url}/values/{key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"KV delete failed: {e}")
            return True
    
    def export_local_cache(self) -> Dict[str, Any]:
        """Export local cache state"""
        return {
            "cached_keys": len(self.local_cache),
            "keys": list(self.local_cache.keys())
        }


class CloudflareD1Database:
    """Cloudflare D1 - persistent database for decision history & patterns"""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{config.account_id}/d1/database/{config.database_id}"
        self.local_queue: List[Dict[str, Any]] = []  # Local queue for offline mode
    
    async def init_schema(self) -> bool:
        """Initialize database schema"""
        
        schema_statements = [
            """
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                agents TEXT,
                action TEXT,
                consensus_level REAL,
                reasoning TEXT,
                created_at TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS failures (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                node TEXT,
                error TEXT,
                context TEXT,
                created_at TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS patterns (
                id TEXT PRIMARY KEY,
                pattern_name TEXT,
                occurrences INTEGER,
                first_seen TEXT,
                last_seen TEXT,
                metadata TEXT,
                created_at TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS query_performance (
                id TEXT PRIMARY KEY,
                model TEXT,
                latency_ms REAL,
                quality REAL,
                task_type TEXT,
                timestamp TEXT,
                created_at TEXT
            )
            """
        ]
        
        for statement in schema_statements:
            await self.execute(statement)
        
        return True
    
    async def execute(self, sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Execute SQL statement (with local queue fallback)"""
        
        # Queue for local processing
        self.local_queue.append({
            "sql": sql,
            "params": params or [],
            "timestamp": datetime.now().isoformat()
        })
        
        # Try cloud sync if enabled
        if not self.config.enabled:
            return {"status": "queued_local"}
        
        try:
            headers = {"Authorization": f"Bearer {self.config.api_token}"}
            payload = {
                "sql": sql,
                "params": params or []
            }
            
            url = f"{self.base_url}/query"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"D1 query failed (queued locally): {e}")
        
        return {"status": "queued_local"}
    
    async def insert_decision(self, decision_id: str, agents: List[str], action: str, 
                             consensus: float, reasoning: str) -> bool:
        """Store decision in database"""
        
        sql = """
        INSERT INTO decisions (id, timestamp, agents, action, consensus_level, reasoning, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = [
            decision_id,
            datetime.now().isoformat(),
            json.dumps(agents),
            action,
            consensus,
            reasoning,
            datetime.now().isoformat()
        ]
        
        result = await self.execute(sql, params)
        return result.get("status") != "error"
    
    async def insert_failure(self, failure_id: str, node: str, error: str, context: Dict) -> bool:
        """Store failure event"""
        
        sql = """
        INSERT INTO failures (id, timestamp, node, error, context, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        params = [
            failure_id,
            datetime.now().isoformat(),
            node,
            error,
            json.dumps(context),
            datetime.now().isoformat()
        ]
        
        return await self.execute(sql, params)
    
    async def insert_pattern(self, pattern_id: str, pattern_name: str, metadata: Dict) -> bool:
        """Store detected pattern"""
        
        sql = """
        INSERT INTO patterns (id, pattern_name, occurrences, first_seen, last_seen, metadata, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = [
            pattern_id,
            pattern_name,
            1,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            json.dumps(metadata),
            datetime.now().isoformat()
        ]
        
        return await self.execute(sql, params)
    
    def get_local_queue_size(self) -> int:
        """Get size of local queue (for monitoring)"""
        return len(self.local_queue)


class CloudflareR2Storage:
    """Cloudflare R2 - object storage for videos, models, artifacts"""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.base_url = f"https://{config.r2_bucket}.r2.cloudflarestorage.com"
        self.local_storage: Dict[str, bytes] = {}  # Local fallback
    
    async def upload_file(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> bool:
        """Upload file to R2 (with local fallback)"""
        
        # Store locally
        self.local_storage[key] = data
        
        # Try cloud sync if enabled
        if not self.config.enabled:
            return True
        
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_token}",
                "Content-Type": content_type
            }
            
            url = f"{self.base_url}/{key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, data=data, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    return resp.status in [200, 201]
        except Exception as e:
            print(f"R2 upload failed (stored locally): {e}")
            return True
    
    async def download_file(self, key: str) -> Optional[bytes]:
        """Download file from R2 (local first, then cloud)"""
        
        # Try local storage first
        if key in self.local_storage:
            return self.local_storage[key]
        
        # Try cloud if enabled
        if not self.config.enabled:
            return None
        
        try:
            headers = {"Authorization": f"Bearer {self.config.api_token}"}
            url = f"{self.base_url}/{key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        self.local_storage[key] = data
                        return data
        except Exception as e:
            print(f"R2 download failed: {e}")
        
        return None
    
    async def delete_file(self, key: str) -> bool:
        """Delete file from R2"""
        
        if key in self.local_storage:
            del self.local_storage[key]
        
        if not self.config.enabled:
            return True
        
        try:
            headers = {"Authorization": f"Bearer {self.config.api_token}"}
            url = f"{self.base_url}/{key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    return resp.status == 204
        except Exception as e:
            print(f"R2 delete failed: {e}")
            return True
    
    def get_local_storage_usage(self) -> Dict[str, Any]:
        """Get local storage stats"""
        total_bytes = sum(len(data) for data in self.local_storage.values())
        return {
            "objects": len(self.local_storage),
            "total_bytes": total_bytes,
            "total_mb": total_bytes / (1024 * 1024)
        }


class CloudflareSync:
    """Manage syncing between local Lenovo and Cloudflare"""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.kv = CloudflareKVStore(config)
        self.d1 = CloudflareD1Database(config)
        self.r2 = CloudflareR2Storage(config)
        self.sync_history: List[Dict[str, Any]] = []
        self.is_syncing = False
    
    async def sync_decision(self, decision_id: str, decision_data: Dict[str, Any]) -> bool:
        """Sync decision to cloud"""
        
        # Store in KV for quick access
        await self.kv.put(f"decision:{decision_id}", decision_data, ttl_seconds=86400)
        
        # Store in D1 for history
        agents = decision_data.get("supporting_agents", [])
        action = decision_data.get("action", "")
        consensus = decision_data.get("consensus_level", 0)
        reasoning = decision_data.get("reasoning", "")
        
        await self.d1.insert_decision(decision_id, agents, action, consensus, reasoning)
        
        self.sync_history.append({
            "type": "decision",
            "id": decision_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    async def sync_failure(self, failure_id: str, node: str, error: str, context: Dict) -> bool:
        """Sync failure event to cloud"""
        
        # Store in KV for monitoring
        await self.kv.put(f"failure:{failure_id}", {
            "node": node,
            "error": error,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }, ttl_seconds=604800)  # 7 days
        
        # Store in D1 for analysis
        await self.d1.insert_failure(failure_id, node, error, context)
        
        self.sync_history.append({
            "type": "failure",
            "id": failure_id,
            "node": node,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    async def sync_pattern(self, pattern_id: str, pattern_name: str, metadata: Dict) -> bool:
        """Sync detected pattern to cloud"""
        
        await self.kv.put(f"pattern:{pattern_id}", metadata)
        await self.d1.insert_pattern(pattern_id, pattern_name, metadata)
        
        self.sync_history.append({
            "type": "pattern",
            "id": pattern_id,
            "name": pattern_name,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    async def periodic_sync(self, interval_seconds: int = 60):
        """Periodically sync state to cloud"""
        
        while True:
            await asyncio.sleep(interval_seconds)
            
            if not self.config.enabled:
                continue
            
            try:
                self.is_syncing = True
                # Sync operations would happen here
                self.is_syncing = False
            except Exception as e:
                print(f"Periodic sync error: {e}")
                self.is_syncing = False
    
    def export_sync_state(self) -> Dict[str, Any]:
        """Export current sync state"""
        
        return {
            "cloudflare_enabled": self.config.enabled,
            "kv_local_cache": self.kv.export_local_cache(),
            "d1_local_queue": self.d1.get_local_queue_size(),
            "r2_local_storage": self.r2.get_local_storage_usage(),
            "sync_history_count": len(self.sync_history),
            "is_syncing": self.is_syncing,
            "last_syncs": self.sync_history[-5:] if self.sync_history else []
        }


class LocalLenovoHub:
    """
    Lenovo runs EVERYTHING locally.
    Cloudflare is optional cloud sync.
    
    This is the heart of the system - all computation here.
    """
    
    def __init__(self, cloudflare_config: Optional[CloudflareConfig] = None):
        self.cloudflare_sync = CloudflareSync(cloudflare_config) if cloudflare_config else None
        self.local_decisions: List[Dict[str, Any]] = []
        self.local_failures: List[Dict[str, Any]] = []
        self.local_patterns: List[Dict[str, Any]] = []
        self.node_name = "lenovo-master"
    
    async def record_decision(self, decision_data: Dict[str, Any]) -> str:
        """Record decision locally, optionally sync to cloud"""
        
        decision_id = f"dec_{len(self.local_decisions)}"
        
        # Store locally (primary)
        self.local_decisions.append({
            "id": decision_id,
            "data": decision_data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Sync to cloud if available
        if self.cloudflare_sync:
            await self.cloudflare_sync.sync_decision(decision_id, decision_data)
        
        return decision_id
    
    async def record_failure(self, node: str, error: str, context: Dict) -> str:
        """Record failure locally, optionally sync to cloud"""
        
        failure_id = f"fail_{len(self.local_failures)}"
        
        # Store locally (primary)
        self.local_failures.append({
            "id": failure_id,
            "node": node,
            "error": error,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        
        # Sync to cloud if available
        if self.cloudflare_sync:
            await self.cloudflare_sync.sync_failure(failure_id, node, error, context)
        
        return failure_id
    
    def export_hub_state(self) -> Dict[str, Any]:
        """Export local hub state"""
        
        state = {
            "node": self.node_name,
            "local_decisions": len(self.local_decisions),
            "local_failures": len(self.local_failures),
            "local_patterns": len(self.local_patterns),
        }
        
        if self.cloudflare_sync:
            state["cloudflare_sync"] = self.cloudflare_sync.export_sync_state()
        
        return state


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_local_first_with_optional_cloud():
    """Demonstrate local-first architecture with optional Cloudflare sync"""
    
    # Create Lenovo hub (local only)
    hub_local_only = LocalLenovoHub()
    
    print("=" * 70)
    print("LOCAL-FIRST MODE (Lenovo runs everything)")
    print("=" * 70)
    
    # Record decisions locally
    decision_id = await hub_local_only.record_decision({
        "action": "Route video_stitch to Acer worker",
        "agents": ["VideoExpert", "RoutingExpert"],
        "consensus_level": 0.94,
        "reasoning": "Acer has lowest CPU utilization"
    })
    print(f"✓ Decision recorded locally: {decision_id}")
    
    # Record failures locally
    failure_id = await hub_local_only.record_failure(
        "lenovo",
        "timeout",
        {"timeout_ms": 5000, "task": "video_encode"}
    )
    print(f"✓ Failure recorded locally: {failure_id}")
    
    print(f"\nLocal hub state: {json.dumps(hub_local_only.export_hub_state(), indent=2)}")
    
    # Now with Cloudflare sync enabled
    print("\n" + "=" * 70)
    print("LOCAL-FIRST + OPTIONAL CLOUDFLARE SYNC")
    print("=" * 70)
    
    cf_config = CloudflareConfig(
        account_id="your_account_id",
        api_token="your_api_token",
        namespace_id="your_namespace",
        database_id="your_database",
        r2_bucket="your_bucket",
        enabled=True  # Can set to False for offline mode
    )
    
    hub_with_cloud = LocalLenovoHub(cf_config)
    
    # Everything runs locally, with optional cloud sync
    decision_id = await hub_with_cloud.record_decision({
        "action": "Parallel inference across 3 models",
        "agents": ["InferenceExpert"],
        "consensus_level": 0.88
    })
    print(f"✓ Decision recorded (local + cloud sync): {decision_id}")
    
    print(f"\nHub with Cloudflare sync state: {json.dumps(hub_with_cloud.export_hub_state(), indent=2)}")


if __name__ == "__main__":
    asyncio.run(example_local_first_with_optional_cloud())
