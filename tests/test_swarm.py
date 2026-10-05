"""
Comprehensive test suite for swarm agents and group chat

Tests:
- Individual agent reasoning
- Group chat consensus
- Multi-round discussions
- Decision quality
- Fallback mechanisms
"""

import pytest
import asyncio
from datetime import datetime

# Add parent directory to path
import sys
sys.path.insert(0, '/workspace/epic-maestro')

from core.swarm import (
    SwarmAgent, VideoAgent, InferenceAgent, RoutingAgent, HealingAgent,
    GroupChat, SwarmConductor, AgentRole, Message
)


class TestVideoAgent:
    """Test VideoAgent expertise"""
    
    @pytest.mark.asyncio
    async def test_video_stitch_analysis(self):
        """VideoAgent should analyze video stitching correctly"""
        agent = VideoAgent()
        
        context = {
            "job_type": "video_stitch",
            "videos": ["v1.mp4", "v2.mp4", "v3.mp4"],
            "deadline_seconds": 5,
            "quality": "high"
        }
        
        message = await agent.analyze(context)
        
        assert message.role == AgentRole.VIDEO
        assert message.sender == "VideoExpert"
        assert message.confidence > 0.8
        assert len(message.content) > 0
    
    @pytest.mark.asyncio
    async def test_fast_video_recommendation(self):
        """Under tight deadline, should recommend fast encoding"""
        agent = VideoAgent()
        
        context = {
            "job_type": "video_stitch",
            "videos": ["v1.mp4"],
            "deadline_seconds": 3,
            "quality": "low"
        }
        
        message = await agent.analyze(context)
        
        # Should recommend FFmpeg copy mode
        assert "copy" in message.content.lower() or "fast" in message.content.lower()
        assert message.confidence > 0.9
    
    def test_expertise_scores(self):
        """VideoAgent should have high scores for video domains"""
        agent = VideoAgent()
        
        assert agent.get_expertise_score("video_stitching") == 1.0
        assert agent.get_expertise_score("encoding_optimization") == 0.95
        assert agent.get_expertise_score("unknown_domain") == 0.3


class TestInferenceAgent:
    """Test InferenceAgent expertise"""
    
    @pytest.mark.asyncio
    async def test_low_latency_inference(self):
        """Should recommend models for low latency"""
        agent = InferenceAgent()
        
        context = {
            "task": "sentiment_analysis",
            "model_options": ["bert", "distilbert", "roberta"],
            "latency_budget_ms": 100
        }
        
        message = await agent.analyze(context)
        
        # Should make some recommendation for fast inference
        assert len(message.content) > 0
        assert message.confidence > 0.7
    
    @pytest.mark.asyncio
    async def test_high_quality_inference(self):
        """Should recommend powerful models when time permits"""
        agent = InferenceAgent()
        
        context = {
            "task": "analysis",
            "model_options": [],
            "latency_budget_ms": 2000
        }
        
        message = await agent.analyze(context)
        
        assert "larger" in message.content.lower() or "llama" in message.content.lower()
        assert message.confidence > 0.8
    
    def test_expertise_scores(self):
        """InferenceAgent should have high scores for inference domains"""
        agent = InferenceAgent()
        
        assert agent.get_expertise_score("model_selection") == 1.0
        assert agent.get_expertise_score("inference_routing") == 0.88


class TestRoutingAgent:
    """Test RoutingAgent expertise"""
    
    @pytest.mark.asyncio
    async def test_load_balancing(self):
        """Should route to least busy node"""
        agent = RoutingAgent()
        
        context = {
            "job_type": "compute",
            "fleet_state": {
                "nodes": {
                    "ollama": {"utilization": 0.9},
                    "acer": {"utilization": 0.2},
                    "lenovo": {"utilization": 0.5}
                }
            },
            "priority": "normal"
        }
        
        message = await agent.analyze(context)
        
        # Should route to acer (lowest utilization)
        assert "acer" in message.content.lower()
        assert message.confidence > 0.70
    
    @pytest.mark.asyncio
    async def test_critical_priority(self):
        """Should handle critical priority jobs differently"""
        agent = RoutingAgent()
        
        context = {
            "job_type": "critical_inference",
            "fleet_state": {"nodes": {"acer": {"utilization": 0.3}}},
            "priority": "critical"
        }
        
        message = await agent.analyze(context)
        
        assert "critical" in message.content.lower() or "priority" in message.content.lower()


class TestHealingAgent:
    """Test HealingAgent failure prevention"""
    
    @pytest.mark.asyncio
    async def test_pattern_detection(self):
        """Should detect recurring failure patterns"""
        agent = HealingAgent()
        
        context = {
            "job_type": "video_encode",
            "failure_history": [
                {"error": "timeout", "time": "3h ago"},
                {"error": "timeout", "time": "2h ago"},
                {"error": "timeout", "time": "1h ago"},
            ],
            "fleet_state": {"nodes": {}}
        }
        
        message = await agent.analyze(context)
        
        # Should detect timeout pattern
        assert "pattern" in message.content.lower() or "timeout" in message.content.lower()
        assert message.confidence > 0.85
    
    @pytest.mark.asyncio
    async def test_resource_warnings(self):
        """Should warn about high resource utilization"""
        agent = HealingAgent()
        
        context = {
            "job_type": "inference",
            "failure_history": [],
            "fleet_state": {
                "nodes": {
                    "lenovo": {"utilization": 0.92}
                }
            }
        }
        
        message = await agent.analyze(context)
        
        # Should mention lenovo (which is at high utilization)
        assert "lenovo" in message.content.lower() or "avoid" in message.content.lower()


class TestGroupChat:
    """Test group chat and consensus"""
    
    @pytest.mark.asyncio
    async def test_single_round_discussion(self):
        """All agents should contribute in group chat"""
        agents = [
            VideoAgent(),
            InferenceAgent(),
            RoutingAgent(),
            HealingAgent()
        ]
        
        group = GroupChat(agents)
        
        context = {
            "job_type": "video_stitch",
            "videos": ["v1.mp4", "v2.mp4"],
            "deadline_seconds": 5,
            "latency_budget_ms": 2000,
            "fleet_state": {
                "nodes": {
                    "acer": {"utilization": 0.3},
                    "lenovo": {"utilization": 0.6}
                }
            },
            "failure_history": []
        }
        
        decision = await group.discuss(context, "Process video_stitch with deadline")
        
        # Should reach consensus
        assert decision.action is not None
        assert len(decision.reasoning_chain) == len(agents)
        assert decision.consensus_level > 0
        assert decision.confidence > 0
    
    @pytest.mark.asyncio
    async def test_multi_round_discussion(self):
        """Multi-round discussion should converge to better consensus"""
        agents = [
            VideoAgent(),
            InferenceAgent(),
            RoutingAgent()
        ]
        
        group = GroupChat(agents)
        
        context = {
            "job_type": "complex_analysis",
            "fleet_state": {"nodes": {"acer": {"utilization": 0.4}}},
            "failure_history": [],
            "deadline_seconds": 10
        }
        
        decision = await group.multi_round_discussion(
            context,
            "Complex multi-step task",
            rounds=3
        )
        
        assert decision.action is not None
        assert decision.consensus_level >= 0


class TestSwarmConductor:
    """Test master conductor orchestration"""
    
    @pytest.mark.asyncio
    async def test_orchestrate_simple_task(self):
        """Conductor should orchestrate swarm for simple task"""
        conductor = SwarmConductor()
        
        context = {
            "job_type": "video_stitch",
            "videos": ["v1.mp4"],
            "deadline_seconds": 5,
            "fleet_state": {
                "nodes": {
                    "acer": {"utilization": 0.2},
                    "lenovo": {"utilization": 0.5}
                }
            },
            "failure_history": []
        }
        
        decision = await conductor.orchestrate(
            "Create video stitch quickly",
            context
        )
        
        assert decision.action is not None
        assert decision.primary_agent is not None
        assert decision.confidence > 0
    
    @pytest.mark.asyncio
    async def test_orchestrate_complex_task(self):
        """Conductor should handle complex multi-domain tasks"""
        conductor = SwarmConductor()
        
        context = {
            "job_type": "inference",
            "task": "reasoning",
            "latency_budget_ms": 1000,
            "fleet_state": {"nodes": {}},
            "failure_history": [],
            "video_input": "test.mp4"
        }
        
        decision = await conductor.orchestrate(
            "Analyze video with inference and routing",
            context
        )
        
        assert decision.action is not None
        assert len(decision.reasoning_chain) > 0
    
    @pytest.mark.asyncio
    async def test_domain_extraction(self):
        """Should extract relevant domains from objectives"""
        conductor = SwarmConductor()
        
        domains = conductor._extract_domains("video_stitch and inference routing")
        
        assert "video_stitching" in domains
        assert "inference_routing" in domains
    
    def test_export_swarm_state(self):
        """Should export complete swarm state"""
        conductor = SwarmConductor()
        
        state = conductor.export_swarm_state()
        
        assert "agents" in state
        assert "group_chat_messages" in state
        assert len(state["agents"]) == 4


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestSwarmIntegration:
    """Integration tests for complete swarm workflows"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_with_failure_handling(self):
        """Complete workflow: detect -> decide -> prevent"""
        conductor = SwarmConductor()
        
        # Context with detected failure pattern
        context = {
            "job_type": "video_stitch",
            "videos": ["v1.mp4", "v2.mp4"],
            "deadline_seconds": 3,
            "quality": "high",
            "fleet_state": {
                "nodes": {
                    "acer": {"utilization": 0.8},  # High utilization
                    "lenovo": {"utilization": 0.4}
                }
            },
            "failure_history": [
                {"error": "timeout", "node": "acer"},
                {"error": "timeout", "node": "acer"},  # Pattern!
            ]
        }
        
        decision = await conductor.orchestrate(
            "Process stitch with known failure pattern",
            context
        )
        
        # Should avoid acer, route to lenovo, add safety margins
        assert decision.consensus_level > 0.75
        print(f"\nFull workflow decision: {decision.action}")
        print(f"Reasoning agents: {[m.sender for m in decision.reasoning_chain]}")
        print(f"Consensus: {decision.consensus_level:.0%}")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestSwarmPerformance:
    """Performance and concurrency tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_analysis(self):
        """Multiple agents can analyze simultaneously"""
        agents = [VideoAgent(), InferenceAgent(), RoutingAgent(), HealingAgent()]
        
        context = {
            "job_type": "video_stitch",
            "fleet_state": {"nodes": {}},
            "failure_history": [],
            "deadline_seconds": 5
        }
        
        # Run all analyses concurrently
        tasks = [agent.analyze(context) for agent in agents]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 4
        assert all(isinstance(r, Message) for r in results)
    
    @pytest.mark.asyncio
    async def test_fast_consensus_on_simple_task(self):
        """Simple tasks should reach consensus quickly"""
        conductor = SwarmConductor()
        
        context = {
            "job_type": "simple",
            "fleet_state": {"nodes": {}},
            "failure_history": []
        }
        
        import time
        start = time.time()
        
        decision = await conductor.orchestrate("Simple task", context)
        
        elapsed_ms = (time.time() - start) * 1000
        
        # Should complete within reasonable time
        assert elapsed_ms < 2000  # 2 seconds
        assert decision.action is not None


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
