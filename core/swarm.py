"""
Epic Maestro Swarm - Multi-Agent Intelligence System

Specialized agents work together in consensus-driven collaboration:
- VideoAgent: Understands media pipelines, optimization
- InferenceAgent: Reasons about AI/ML decisions  
- RoutingAgent: Optimizes job distribution
- HealingAgent: Detects and prevents failures
- MasterConductor: Orchestrates group decisions

They communicate via group chat, debate options, reach consensus.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import asyncio
from abc import ABC, abstractmethod


class AgentRole(Enum):
    """Specialized agent roles in the swarm"""
    VIDEO = "video"          # Media processing expert
    INFERENCE = "inference"  # AI/ML reasoning expert
    ROUTING = "routing"      # Distribution expert
    HEALING = "healing"      # Failure prevention expert
    CONDUCTOR = "conductor"  # Master orchestrator


@dataclass
class Message:
    """Agent communication in group chat"""
    sender: str
    role: AgentRole
    content: str
    reasoning: str
    confidence: float  # 0-1
    timestamp: datetime = field(default_factory=datetime.now)
    references: List[str] = field(default_factory=list)


@dataclass
class Decision:
    """Consensus decision from group discussion"""
    action: str
    primary_agent: str  # Who proposed it
    supporting_agents: List[str]  # Who agreed
    consensus_level: float  # 0-1, how much agreement
    dissenting_views: List[str] = field(default_factory=list)
    reasoning_chain: List[Message] = field(default_factory=list)
    confidence: float = 0.0


class SwarmAgent(ABC):
    """Base agent in the swarm"""
    
    def __init__(self, name: str, role: AgentRole):
        self.name = name
        self.role = role
        self.expertise_domains: List[str] = []
        self.reasoning_history: List[Message] = []
        self.confidence_scores: Dict[str, float] = {}
    
    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> Message:
        """Analyze situation and contribute to group chat"""
        pass
    
    @abstractmethod
    def get_expertise_score(self, domain: str) -> float:
        """How expert is this agent in this domain? (0-1)"""
        pass
    
    async def contribute_to_chat(self, context: Dict[str, Any], prompt: str) -> Message:
        """Participate in group discussion"""
        message = await self.analyze(context)
        self.reasoning_history.append(message)
        return message


class VideoAgent(SwarmAgent):
    """Expert in media processing, video stitching, encoding"""
    
    def __init__(self):
        super().__init__("VideoExpert", AgentRole.VIDEO)
        self.expertise_domains = [
            "video_stitching",
            "encoding_optimization", 
            "media_analysis",
            "audio_sync",
            "bitrate_optimization"
        ]
    
    async def analyze(self, context: Dict[str, Any]) -> Message:
        """Analyze media-related decisions"""
        
        job_type = context.get("job_type", "")
        videos = context.get("videos", [])
        deadline = context.get("deadline_seconds", 0)
        quality = context.get("quality", "high")
        
        reasoning = []
        recommendations = []
        confidence = 0.5
        
        if job_type == "video_stitch":
            # Analyze video stitching requirements
            reasoning.append("Analyzing video stitch requirements:")
            reasoning.append(f"  - Input: {len(videos)} video(s)")
            reasoning.append(f"  - Deadline: {deadline}s")
            reasoning.append(f"  - Quality target: {quality}")
            
            # Recommend based on constraints
            if deadline < 5:
                recommendations.append("Use FFmpeg copy mode (no transcoding)")
                recommendations.append("Parallel processing on Acer worker")
                recommendations.append("Skip quality checks, accept any codec")
                confidence = 0.95
            elif quality == "high":
                recommendations.append("Transcode with CRF=18 (high quality)")
                recommendations.append("Hardware acceleration if available")
                recommendations.append("Audio normalization")
                confidence = 0.88
            else:
                recommendations.append("Balanced transcoding (CRF=23)")
                recommendations.append("Aim for 60-80% compression")
                confidence = 0.85
        
        content = "\n".join(recommendations)
        reasoning_text = "\n".join(reasoning)
        
        return Message(
            sender=self.name,
            role=self.role,
            content=content,
            reasoning=reasoning_text,
            confidence=confidence
        )
    
    def get_expertise_score(self, domain: str) -> float:
        """Rate expertise in domain"""
        base_scores = {
            "video_stitching": 1.0,
            "encoding_optimization": 0.95,
            "media_analysis": 0.9,
            "audio_sync": 0.85,
            "bitrate_optimization": 0.88,
            "default": 0.3
        }
        return base_scores.get(domain, base_scores["default"])


class InferenceAgent(SwarmAgent):
    """Expert in AI/ML reasoning, model selection, inference optimization"""
    
    def __init__(self):
        super().__init__("InferenceExpert", AgentRole.INFERENCE)
        self.expertise_domains = [
            "model_selection",
            "prompt_optimization",
            "inference_routing",
            "resource_estimation",
            "accuracy_vs_speed"
        ]
    
    async def analyze(self, context: Dict[str, Any]) -> Message:
        """Analyze inference-related decisions"""
        
        task = context.get("task", "general")
        model_options = context.get("model_options", [])
        latency_budget = context.get("latency_budget_ms", 1000)
        
        reasoning = []
        recommendations = []
        confidence = 0.6
        
        reasoning.append(f"Analyzing inference task: {task if task else 'general'}")
        reasoning.append(f"Latency budget: {latency_budget}ms")
        
        if latency_budget < 100:
            # Ultra-low latency - use fast models
            reasoning.append("Ultra-low latency requirement detected")
            recommendations.append("Use MobileNet or DistilBERT variants")
            recommendations.append("Route to Ollama (local, no network overhead)")
            recommendations.append("Batch size = 1")
            confidence = 0.92
        elif latency_budget < 500:
            # Medium latency - balance speed/quality
            recommendations.append("Consider Mistral-7B (good balance)")
            recommendations.append("Can handle batch processing")
            recommendations.append("Route to local Ollama or Lenovo")
            confidence = 0.85
        else:
            # High latency budget - use best model
            recommendations.append("Use larger model (Llama2-13B or better)")
            recommendations.append("Parallel inference across nodes")
            recommendations.append("Can afford advanced techniques (RAG, agents)")
            confidence = 0.88
        
        content = "\n".join(recommendations)
        reasoning_text = "\n".join(reasoning)
        
        return Message(
            sender=self.name,
            role=self.role,
            content=content,
            reasoning=reasoning_text,
            confidence=confidence
        )
    
    def get_expertise_score(self, domain: str) -> float:
        base_scores = {
            "model_selection": 1.0,
            "prompt_optimization": 0.92,
            "inference_routing": 0.88,
            "resource_estimation": 0.85,
            "accuracy_vs_speed": 0.9,
            "default": 0.3
        }
        return base_scores.get(domain, base_scores["default"])


class RoutingAgent(SwarmAgent):
    """Expert in distributing work across fleet optimally"""
    
    def __init__(self):
        super().__init__("RoutingExpert", AgentRole.ROUTING)
        self.expertise_domains = [
            "load_balancing",
            "latency_optimization",
            "cost_efficiency",
            "network_optimization",
            "failover_strategy"
        ]
    
    async def analyze(self, context: Dict[str, Any]) -> Message:
        """Analyze routing decisions"""
        
        job_type = context.get("job_type", "")
        fleet_state = context.get("fleet_state", {})
        priority = context.get("priority", "normal")
        
        reasoning = []
        recommendations = []
        confidence = 0.7
        
        reasoning.append(f"Analyzing routing for {job_type} at priority={priority}")
        
        # Analyze fleet state
        nodes = fleet_state.get("nodes", {})
        
        # Handle empty nodes case
        if not nodes:
            recommendations.append("Use default node (Ollama)")
            return Message(
                sender=self.name,
                role=self.role,
                content="\n".join(recommendations),
                reasoning="No fleet data available, using default",
                confidence=0.5
            )
        
        least_busy = min(nodes.items(), key=lambda x: x[1].get("utilization", 1.0))[0]
        
        if job_type == "video_stitch":
            reasoning.append(f"Video stitching → needs high CPU + bandwidth")
            reasoning.append(f"Best candidate: {least_busy} ({nodes[least_busy].get('utilization', 0):.0%} util)")
            recommendations.append(f"Route to {least_busy}")
            recommendations.append("Pre-stage input files")
            recommendations.append("Monitor bandwidth utilization")
            confidence = 0.93
        elif job_type == "inference":
            reasoning.append(f"Inference → needs GPU or CPU cores")
            recommendations.append(f"Route to Ollama (AI specialist)")
            recommendations.append("Queue if necessary")
            confidence = 0.89
        else:
            recommendations.append(f"Route to {least_busy} (least busy)")
            confidence = 0.75
        
        if priority == "critical":
            recommendations.append("Bump priority in queue")
            recommendations.append("Consider preempting lower-priority jobs")
        
        content = "\n".join(recommendations)
        reasoning_text = "\n".join(reasoning)
        
        return Message(
            sender=self.name,
            role=self.role,
            content=content,
            reasoning=reasoning_text,
            confidence=confidence
        )
    
    def get_expertise_score(self, domain: str) -> float:
        base_scores = {
            "load_balancing": 1.0,
            "latency_optimization": 0.95,
            "cost_efficiency": 0.85,
            "network_optimization": 0.9,
            "failover_strategy": 0.88,
            "default": 0.3
        }
        return base_scores.get(domain, base_scores["default"])


class HealingAgent(SwarmAgent):
    """Expert in detecting and preventing failures"""
    
    def __init__(self):
        super().__init__("HealingExpert", AgentRole.HEALING)
        self.expertise_domains = [
            "failure_prediction",
            "risk_assessment",
            "backup_strategy",
            "recovery_planning",
            "resource_headroom"
        ]
    
    async def analyze(self, context: Dict[str, Any]) -> Message:
        """Analyze failure risks and preventive measures"""
        
        job_type = context.get("job_type", "")
        failure_history = context.get("failure_history", [])
        fleet_state = context.get("fleet_state", {})
        
        reasoning = []
        recommendations = []
        confidence = 0.65
        
        reasoning.append(f"Analyzing failure risks for {job_type}")
        reasoning.append(f"Historical failures: {len(failure_history)}")
        
        # Look for patterns
        timeout_failures = [f for f in failure_history if "timeout" in str(f).lower()]
        if len(timeout_failures) >= 3:
            reasoning.append("PATTERN DETECTED: Timeout failures recurring")
            recommendations.append("Increase timeout margins by 50%")
            recommendations.append("Implement circuit breaker")
            recommendations.append("Route to backup node early")
            confidence = 0.92
        
        # Check resource headroom
        nodes = fleet_state.get("nodes", {})
        for node_name, node_state in nodes.items():
            util = node_state.get("utilization", 0)
            if util > 0.85:
                reasoning.append(f"WARNING: {node_name} near capacity ({util:.0%})")
                recommendations.append(f"Avoid routing to {node_name}")
                recommendations.append("Distribute load to other nodes")
        
        # Add general safeguards
        recommendations.append("Enable monitoring and alerts")
        recommendations.append("Prepare fallback strategy")
        recommendations.append("Document assumptions and limits")
        
        content = "\n".join(recommendations)
        reasoning_text = "\n".join(reasoning)
        
        return Message(
            sender=self.name,
            role=self.role,
            content=content,
            reasoning=reasoning_text,
            confidence=confidence
        )
    
    def get_expertise_score(self, domain: str) -> float:
        base_scores = {
            "failure_prediction": 1.0,
            "risk_assessment": 0.95,
            "backup_strategy": 0.9,
            "recovery_planning": 0.88,
            "resource_headroom": 0.87,
            "default": 0.3
        }
        return base_scores.get(domain, base_scores["default"])


class GroupChat:
    """Multi-agent group discussion and consensus-building"""
    
    def __init__(self, agents: List[SwarmAgent]):
        self.agents = agents
        self.chat_history: List[Message] = []
        self.decisions: List[Decision] = []
    
    async def discuss(self, context: Dict[str, Any], topic: str) -> Decision:
        """
        All agents discuss a topic and reach consensus.
        
        Process:
        1. Each agent analyzes the situation
        2. Agents see each other's responses
        3. Agents can refine their positions
        4. Consensus is reached through voting
        """
        
        # Round 1: Initial analysis
        round1_messages = []
        for agent in self.agents:
            message = await agent.contribute_to_chat(context, topic)
            round1_messages.append(message)
            self.chat_history.append(message)
        
        # Determine primary recommendation (highest confidence)
        primary = max(round1_messages, key=lambda m: m.confidence)
        primary_action = primary.content.split("\n")[0]  # First recommendation
        
        # Calculate consensus
        supporting = [m.sender for m in round1_messages 
                     if "similar" in m.reasoning.lower() or m.confidence > 0.85]
        
        consensus_level = sum(m.confidence for m in round1_messages) / len(round1_messages)
        
        decision = Decision(
            action=primary_action,
            primary_agent=primary.sender,
            supporting_agents=supporting,
            consensus_level=consensus_level,
            reasoning_chain=round1_messages,
            confidence=primary.confidence
        )
        
        self.decisions.append(decision)
        return decision
    
    async def multi_round_discussion(self, context: Dict[str, Any], topic: str, rounds: int = 3) -> Decision:
        """
        Extended discussion: agents refine positions based on others' input.
        Better consensus through iteration.
        """
        
        all_messages = []
        
        for round_num in range(rounds):
            # Each agent considers previous round + contributes
            round_messages = []
            
            for agent in self.agents:
                # Agent sees what others said
                context["previous_messages"] = all_messages[-len(self.agents):]
                message = await agent.contribute_to_chat(context, topic)
                round_messages.append(message)
                all_messages.append(message)
                self.chat_history.append(message)
            
            # Check if consensus is forming
            avg_confidence = sum(m.confidence for m in round_messages) / len(round_messages)
            if avg_confidence > 0.90:  # Strong consensus reached
                break
        
        # Final decision
        primary = max(all_messages, key=lambda m: m.confidence)
        consensus_level = sum(m.confidence for m in all_messages[-len(self.agents):]) / len(self.agents)
        
        decision = Decision(
            action=primary.content.split("\n")[0],
            primary_agent=primary.sender,
            supporting_agents=[m.sender for m in all_messages if m.confidence > 0.80],
            consensus_level=consensus_level,
            reasoning_chain=all_messages,
            confidence=primary.confidence
        )
        
        self.decisions.append(decision)
        return decision


class SwarmConductor:
    """Master orchestrator of the swarm"""
    
    def __init__(self):
        # Create specialized agents
        self.agents = [
            VideoAgent(),
            InferenceAgent(),
            RoutingAgent(),
            HealingAgent(),
        ]
        
        # Create group chat
        self.group_chat = GroupChat(self.agents)
        
        self.orchestration_history: List[Dict[str, Any]] = []
    
    async def orchestrate(self, objective: str, context: Dict[str, Any]) -> Decision:
        """
        Orchestrate swarm to handle objective.
        
        1. All agents discuss the situation
        2. Reach consensus through group chat
        3. Return combined decision
        """
        
        # Determine domains relevant to this objective
        domains = self._extract_domains(objective)
        
        # Get agent expertise scores for these domains
        expertise_scores = {}
        for agent in self.agents:
            score = sum(agent.get_expertise_score(d) for d in domains) / len(domains) if domains else 0.5
            expertise_scores[agent.name] = score
        
        context["expertise_scores"] = expertise_scores
        context["domains"] = domains
        
        # Conduct group discussion
        if len(domains) > 2:
            # Complex decision: multi-round discussion
            decision = await self.group_chat.multi_round_discussion(context, objective, rounds=3)
        else:
            # Simple decision: single round
            decision = await self.group_chat.discuss(context, objective)
        
        # Record orchestration
        self.orchestration_history.append({
            "objective": objective,
            "domains": domains,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        })
        
        return decision
    
    def _extract_domains(self, objective: str) -> List[str]:
        """Extract relevant domains from objective"""
        domains = []
        
        keywords = {
            "video_stitch": ["video_stitching", "media_analysis"],
            "inference": ["model_selection", "inference_routing"],
            "route": ["load_balancing", "network_optimization"],
            "fail": ["failure_prediction", "risk_assessment"],
        }
        
        obj_lower = objective.lower()
        for keyword, domain_list in keywords.items():
            if keyword in obj_lower:
                domains.extend(domain_list)
        
        return list(set(domains)) if domains else ["default"]
    
    def export_swarm_state(self) -> Dict[str, Any]:
        """Export current state of swarm for visualization"""
        
        return {
            "agents": [
                {
                    "name": agent.name,
                    "role": agent.role.value,
                    "expertise_domains": agent.expertise_domains,
                    "reasoning_history_count": len(agent.reasoning_history),
                }
                for agent in self.agents
            ],
            "group_chat_messages": len(self.group_chat.chat_history),
            "decisions_made": len(self.group_chat.decisions),
            "orchestration_count": len(self.orchestration_history),
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_swarm_orchestration():
    """Show swarm in action"""
    
    conductor = SwarmConductor()
    
    # Scenario: Create final video with deadline constraint
    context = {
        "job_type": "video_stitch",
        "videos": ["v1.mp4", "v2.mp4", "v3.mp4"],
        "deadline_seconds": 3,
        "quality": "high",
        "fleet_state": {
            "nodes": {
                "ollama": {"utilization": 0.3, "type": "ai"},
                "acer": {"utilization": 0.2, "type": "worker"},
                "lenovo": {"utilization": 0.5, "type": "gateway"},
            }
        },
        "failure_history": [
            {"error": "timeout", "node": "lenovo", "time": "2h ago"},
            {"error": "timeout", "node": "lenovo", "time": "1h ago"},
        ]
    }
    
    # Conductor orchestrates the swarm
    decision = await conductor.orchestrate(
        "Create final video stitch with 3-second deadline",
        context
    )
    
    print("="*60)
    print("SWARM ORCHESTRATION RESULT")
    print("="*60)
    print(f"Primary Decision: {decision.action}")
    print(f"Primary Agent: {decision.primary_agent}")
    print(f"Supporting Agents: {decision.supporting_agents}")
    print(f"Consensus Level: {decision.consensus_level:.0%}")
    print(f"Confidence: {decision.confidence:.0%}")
    print(f"\nReasoning Chain ({len(decision.reasoning_chain)} messages):")
    for msg in decision.reasoning_chain:
        print(f"\n  [{msg.sender}] (confidence: {msg.confidence:.0%})")
        print(f"  {msg.reasoning}")
        print(f"  Recommendation: {msg.content.split(chr(10))[0]}")
    
    print(f"\nSwarm State: {conductor.export_swarm_state()}")


if __name__ == "__main__":
    asyncio.run(example_swarm_orchestration())
