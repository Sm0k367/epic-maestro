"""
Test suite for Cloudflare Integration

Tests:
- Local-first architecture
- Optional cloud sync
- Offline mode (works without Cloudflare)
- KV caching
- D1 persistence
- R2 storage
"""

import pytest
import asyncio
import json
from datetime import datetime

import sys
sys.path.insert(0, '/workspace/epic-maestro')

from core.cloudflare_integration import (
    CloudflareConfig, CloudflareKVStore, CloudflareD1Database,
    CloudflareR2Storage, CloudflareSync, LocalLenovoHub
)


class TestLocalFirstArchitecture:
    """Test that everything works locally without Cloudflare"""
    
    @pytest.mark.asyncio
    async def test_local_decision_recording(self):
        """Should record decisions locally"""
        hub = LocalLenovoHub()
        
        decision_data = {
            "action": "Route to Acer",
            "agents": ["RoutingExpert"],
            "consensus_level": 0.95
        }
        
        decision_id = await hub.record_decision(decision_data)
        
        assert decision_id is not None
        assert len(hub.local_decisions) == 1
        assert hub.local_decisions[0]["data"]["action"] == "Route to Acer"
    
    @pytest.mark.asyncio
    async def test_local_failure_recording(self):
        """Should record failures locally"""
        hub = LocalLenovoHub()
        
        failure_id = await hub.record_failure(
            "acer",
            "timeout",
            {"timeout_ms": 5000}
        )
        
        assert failure_id is not None
        assert len(hub.local_failures) == 1
        assert hub.local_failures[0]["node"] == "acer"
    
    @pytest.mark.asyncio
    async def test_offline_operation(self):
        """Hub should work 100% offline"""
        # Create hub with no Cloudflare config
        hub = LocalLenovoHub(cloudflare_config=None)
        
        # Record multiple decisions offline
        for i in range(5):
            await hub.record_decision({
                "action": f"Action {i}",
                "agents": ["Agent1"]
            })
        
        assert len(hub.local_decisions) == 5
        # No cloud sync attempted
        assert hub.cloudflare_sync is None


class TestCloudflareKV:
    """Test KV store with local fallback"""
    
    @pytest.mark.asyncio
    async def test_kv_local_cache(self):
        """Should store data in local cache"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False  # Offline mode
        )
        
        kv = CloudflareKVStore(config)
        
        # Store data
        await kv.put("test_key", {"data": "test_value"})
        
        # Retrieve from cache
        value = await kv.get("test_key")
        
        assert value is not None
        assert value["data"] == "test_value"
    
    @pytest.mark.asyncio
    async def test_kv_with_ttl(self):
        """Should handle TTL in local cache"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        kv = CloudflareKVStore(config)
        
        # Store with TTL
        await kv.put("ttl_key", {"temp": "data"}, ttl_seconds=60)
        
        # Should be retrievable
        value = await kv.get("ttl_key")
        assert value is not None
    
    @pytest.mark.asyncio
    async def test_kv_delete(self):
        """Should delete from cache"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        kv = CloudflareKVStore(config)
        
        await kv.put("delete_key", {"data": "test"})
        result = await kv.get("delete_key")
        assert result is not None
        
        await kv.delete("delete_key")
        result = await kv.get("delete_key")
        assert result is None
    
    def test_kv_local_cache_export(self):
        """Should export cache state"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        kv = CloudflareKVStore(config)
        kv.local_cache["key1"] = {"value": "data1"}
        kv.local_cache["key2"] = {"value": "data2"}
        
        state = kv.export_local_cache()
        
        assert state["cached_keys"] == 2
        assert "key1" in state["keys"]
        assert "key2" in state["keys"]


class TestCloudflareD1:
    """Test D1 database with local queuing"""
    
    @pytest.mark.asyncio
    async def test_d1_offline_queuing(self):
        """Should queue operations when offline"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        db = CloudflareD1Database(config)
        
        # Execute operations offline
        await db.execute("INSERT INTO decisions VALUES (?)", ["test_id"])
        await db.execute("INSERT INTO failures VALUES (?)", ["test_id"])
        
        # Should be queued
        assert db.get_local_queue_size() == 2
    
    @pytest.mark.asyncio
    async def test_d1_insert_decision(self):
        """Should insert decision"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        db = CloudflareD1Database(config)
        
        result = await db.insert_decision(
            "dec_001",
            ["Agent1", "Agent2"],
            "Route to Acer",
            0.95,
            "Best option for load"
        )
        
        assert result is True or result is None  # Queued or processed
        assert db.get_local_queue_size() > 0
    
    @pytest.mark.asyncio
    async def test_d1_insert_failure(self):
        """Should insert failure event"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        db = CloudflareD1Database(config)
        
        result = await db.insert_failure(
            "fail_001",
            "acer",
            "timeout",
            {"timeout_ms": 5000}
        )
        
        # Should be queued locally when offline
        assert result is not None


class TestCloudflareR2:
    """Test R2 object storage with local fallback"""
    
    @pytest.mark.asyncio
    async def test_r2_local_storage(self):
        """Should store objects locally"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        r2 = CloudflareR2Storage(config)
        
        # Upload file
        test_data = b"test video data"
        await r2.upload_file("video.mp4", test_data, "video/mp4")
        
        # Download from local storage
        retrieved = await r2.download_file("video.mp4")
        
        assert retrieved == test_data
    
    @pytest.mark.asyncio
    async def test_r2_storage_usage(self):
        """Should track storage usage"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        r2 = CloudflareR2Storage(config)
        
        # Store multiple files
        await r2.upload_file("file1.bin", b"1" * 1024)
        await r2.upload_file("file2.bin", b"2" * 2048)
        
        usage = r2.get_local_storage_usage()
        
        assert usage["objects"] == 2
        assert usage["total_bytes"] == 3072
        assert usage["total_mb"] > 0


class TestCloudflareSync:
    """Test cloud sync mechanism"""
    
    @pytest.mark.asyncio
    async def test_sync_decision(self):
        """Should sync decision data"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        sync = CloudflareSync(config)
        
        decision_data = {
            "action": "Route to Acer",
            "supporting_agents": ["Agent1"],
            "consensus_level": 0.95,
            "reasoning": "Best fit"
        }
        
        result = await sync.sync_decision("dec_001", decision_data)
        
        assert result is True
        assert len(sync.sync_history) > 0
    
    @pytest.mark.asyncio
    async def test_sync_failure(self):
        """Should sync failure data"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        sync = CloudflareSync(config)
        
        result = await sync.sync_failure(
            "fail_001",
            "acer",
            "timeout",
            {"timeout_ms": 5000}
        )
        
        assert result is True
        assert len(sync.sync_history) > 0
    
    @pytest.mark.asyncio
    async def test_sync_pattern(self):
        """Should sync pattern data"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        sync = CloudflareSync(config)
        
        result = await sync.sync_pattern(
            "pat_001",
            "timeout_on_acer",
            {"occurrences": 3}
        )
        
        assert result is True
    
    def test_sync_state_export(self):
        """Should export sync state"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False
        )
        
        sync = CloudflareSync(config)
        
        state = sync.export_sync_state()
        
        assert "cloudflare_enabled" in state
        assert "kv_local_cache" in state
        assert "d1_local_queue" in state
        assert "r2_local_storage" in state


class TestLenovoHub:
    """Test Lenovo hub with optional cloud"""
    
    @pytest.mark.asyncio
    async def test_hub_local_only(self):
        """Hub should work with local storage only"""
        hub = LocalLenovoHub()
        
        # Record multiple decisions
        for i in range(3):
            await hub.record_decision({
                "action": f"Action {i}",
                "consensus_level": 0.9
            })
        
        assert len(hub.local_decisions) == 3
    
    @pytest.mark.asyncio
    async def test_hub_with_cloudflare_sync(self):
        """Hub should sync with Cloudflare when enabled"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False  # Still test structure even when disabled
        )
        
        hub = LocalLenovoHub(config)
        
        await hub.record_decision({
            "action": "Test action",
            "consensus_level": 0.88
        })
        
        assert len(hub.local_decisions) == 1
        assert hub.cloudflare_sync is not None
    
    def test_hub_state_export(self):
        """Should export hub state"""
        hub = LocalLenovoHub()
        
        state = hub.export_hub_state()
        
        assert state["node"] == "lenovo-master"
        assert "local_decisions" in state
        assert "local_failures" in state
        assert "local_patterns" in state


# ============================================================================
# INTEGRATION TESTS - LOCAL + OPTIONAL CLOUD
# ============================================================================

class TestLocalFirstIntegration:
    """Integration tests for local-first with optional cloud"""
    
    @pytest.mark.asyncio
    async def test_complete_local_workflow(self):
        """Complete workflow: all local, no cloud dependency"""
        hub = LocalLenovoHub()  # No Cloudflare
        
        # Record decisions
        await hub.record_decision({"action": "Route to Acer", "consensus_level": 0.95})
        await hub.record_decision({"action": "Use Mistral model", "consensus_level": 0.88})
        
        # Record failures
        await hub.record_failure("acer", "timeout", {})
        
        # Verify everything is recorded locally
        assert len(hub.local_decisions) == 2
        assert len(hub.local_failures) == 1
        
        # Hub should work completely offline
        state = hub.export_hub_state()
        assert state["local_decisions"] == 2
        assert state["local_failures"] == 1
    
    @pytest.mark.asyncio
    async def test_workflow_with_optional_cloud(self):
        """Same workflow with optional cloud sync (disabled)"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False  # Cloud sync disabled
        )
        
        hub = LocalLenovoHub(config)
        
        # Same operations
        await hub.record_decision({"action": "Decision 1"})
        await hub.record_failure("node1", "error", {})
        
        # Should still work locally
        assert len(hub.local_decisions) == 1
        assert len(hub.local_failures) == 1
        
        # Cloudflare sync would be available if enabled
        assert hub.cloudflare_sync is not None
    
    @pytest.mark.asyncio
    async def test_graceful_cloud_fallback(self):
        """Should gracefully handle Cloudflare being down"""
        config = CloudflareConfig(
            account_id="invalid",
            api_token="invalid",
            namespace_id="invalid",
            database_id="invalid",
            r2_bucket="invalid",
            enabled=True  # Cloud enabled but invalid
        )
        
        hub = LocalLenovoHub(config)
        
        # Operations should still succeed locally
        dec_id = await hub.record_decision({"action": "Works locally"})
        
        assert dec_id is not None
        assert len(hub.local_decisions) == 1


# ============================================================================
# OFFLINE RESILIENCE TESTS
# ============================================================================

class TestOfflineResilience:
    """Test that system is fully resilient to network failures"""
    
    @pytest.mark.asyncio
    async def test_offline_operations(self):
        """All operations should work offline"""
        config = CloudflareConfig(
            account_id="test",
            api_token="test",
            namespace_id="test",
            database_id="test",
            r2_bucket="test",
            enabled=False  # Offline
        )
        
        hub = LocalLenovoHub(config)
        
        # All operations should complete successfully
        tasks = [
            hub.record_decision({"action": f"Decision {i}"})
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(r is not None for r in results)
        assert len(hub.local_decisions) == 10


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
