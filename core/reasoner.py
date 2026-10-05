"""
Epic Reasoner - AI-First Autonomous Decision Engine

Not orchestration. Not scheduling. REASONING.

Given your fleet state, available resources, and task objectives,
the Reasoner autonomously decides:
- What to do next
- Why to do it
- How to do it optimally
- What could go wrong
- How to prevent it

This is the thinking layer that makes Epic a true autonomous system.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime, timedelta


class NodeRole(Enum):
    """Node capabilities and roles"""
    GATEWAY = "gateway"  # Lenovo - coordinates work
    WORKER = "worker"    # Acer - executes work
    AI_ENGINE = "ai"     # Ollama - reasoning & inference
    MEDIA = "media"      # FFmpeg - video/audio processing


class TaskType(Enum):
    """Types of work the system can reason about"""
    INFERENCE = "inference"        # Ask Ollama to think
    VIDEO_STITCH = "video_stitch"  # Chain videos
    AUDIO_SYNC = "audio_sync"       # Sync audio tracks
    ENCODE = "encode"               # Re-encode video
    BROADCAST = "broadcast"         # Send to all nodes
    ANALYZE = "analyze"             # Analyze content
    GENERATE = "generate"           # Create new content


@dataclass
class ResourceSnapshot:
    """Current state of your infrastructure"""
    timestamp: datetime
    nodes: Dict[str, 'NodeState'] = field(default_factory=dict)
    available_bandwidth: float = 0.0  # MB/s
    queue_depth: int = 0
    error_count: int = 0


@dataclass
class NodeState:
    """Individual node status"""
    name: str
    role: NodeRole
    is_online: bool
    utilization: float  # 0-1
    queue_length: int
    last_error: Optional[str] = None
    error_timestamp: Optional[datetime] = None
    success_rate: float = 1.0


@dataclass
class Decision:
    """The result of reasoning"""
    action: str
    target_node: str
    reason: str
    confidence: float  # 0-1
    alternatives: List[str] = field(default_factory=list)
    predicted_duration: float = 0.0  # seconds
    risk_level: str = "low"  # low, medium, high
    recovery_strategy: str = ""


class PatterRecognition:
    """
    Learns patterns from your workflows.
    
    After you:
    1. Stitch videos at 9 AM every day
    2. Always follow with audio encoding
    3. Then broadcast at 10 AM
    
    Reasoner learns: "Morning workflow: stitch → encode → broadcast"
    
    Next time: Automatically chains them, pre-stages resources.
    """
    
    def __init__(self):
        self.patterns: Dict[str, List[str]] = {}  # workflow patterns
        self.timing_patterns: Dict[str, List[datetime]] = {}  # when things happen
        self.resource_patterns: Dict[str, Dict[str, float]] = {}  # what resources are needed
        self.failure_patterns: Dict[str, List[str]] = {}  # what goes wrong and when
    
    def record_execution(self, workflow: str, tasks: List[str], resources: Dict[str, float]):
        """Learn from what actually happened"""
        if workflow not in self.patterns:
            self.patterns[workflow] = []
        self.patterns[workflow].append(str(tasks))
        
        if workflow not in self.resource_patterns:
            self.resource_patterns[workflow] = {}
        self.resource_patterns[workflow].update(resources)
    
    def predict_next_steps(self, current_workflow: str) -> List[str]:
        """Based on patterns, what should happen next?"""
        if current_workflow in self.patterns:
            # Could use more sophisticated analysis
            # For now: return common next workflows
            return ["encode", "broadcast"]
        return []
    
    def predict_resource_needs(self, workflow: str) -> Dict[str, float]:
        """What resources will this workflow need?"""
        return self.resource_patterns.get(workflow, {})


class SelfHealer:
    """
    Detects failures and prevents recurrence.
    
    Day 1: "Lenovo gateway timeout when queue > 50"
           → Records failure, analyzes pattern
    Day 2: "Same condition detected early"
           → Routes to Acer instead, prevents timeout
    Day 3: "Proactively pre-stages workers when queue grows"
           → Failure prevented before it happens
    """
    
    def __init__(self):
        self.failure_history: List[Dict[str, Any]] = []
        self.failure_conditions: Dict[str, Dict[str, Any]] = {}
        self.preventive_measures: Dict[str, str] = {}
    
    def record_failure(self, error: str, context: Dict[str, Any]):
        """Learn from failures"""
        self.failure_history.append({
            "error": error,
            "context": context,
            "timestamp": datetime.now()
        })
        
        # Analyze: is this a pattern?
        self._analyze_failure_pattern(error, context)
    
    def _analyze_failure_pattern(self, error: str, context: Dict[str, Any]):
        """
        Detect if this failure has a clear cause-and-effect.
        
        If "queue > 50 AND Lenovo → timeout" happens 3x,
        it's a pattern. Next time, prevent it.
        """
        key = error[:50]  # use first 50 chars as pattern key
        if key not in self.failure_conditions:
            self.failure_conditions[key] = {"count": 0, "contexts": []}
        
        self.failure_conditions[key]["count"] += 1
        self.failure_conditions[key]["contexts"].append(context)
        
        # If same failure 3+ times with same conditions, it's a pattern
        if self.failure_conditions[key]["count"] >= 3:
            self._create_preventive_measure(key, context)
    
    def _create_preventive_measure(self, error_key: str, context: Dict[str, Any]):
        """Create a strategy to prevent this failure"""
        if "queue" in str(context) and "length > 50" in str(context):
            self.preventive_measures[error_key] = "route_to_backup_when_queue_high"
        elif "timeout" in error_key:
            self.preventive_measures[error_key] = "increase_timeout_early"
        else:
            self.preventive_measures[error_key] = "defer_work_to_idle_window"
    
    def get_preventive_action(self, error_condition: str) -> Optional[str]:
        """Should we prevent this before it happens?"""
        for key, measure in self.preventive_measures.items():
            if key in error_condition:
                return measure
        return None


class FleetIntelligence:
    """
    Understands your distributed system.
    
    - Which node is best for what task?
    - When is each node typically available?
    - What's the cost of moving data between nodes?
    - Should we process on Acer or Ollama?
    """
    
    def __init__(self, nodes: Dict[str, NodeState]):
        self.nodes = nodes
        self.node_capabilities: Dict[str, List[TaskType]] = {}
        self.inter_node_latency: Dict[tuple, float] = {}  # ms
    
    def best_node_for_task(self, task: TaskType, urgency: str = "normal") -> str:
        """
        Which node should do this task?
        
        For video_stitch: Acer is best
        For inference: Ollama is best
        For coordination: Lenovo
        """
        
        if task == TaskType.VIDEO_STITCH:
            # Check which has lowest utilization
            return min([n for n in self.nodes if self.nodes[n].role == NodeRole.WORKER],
                      key=lambda n: self.nodes[n].utilization)
        
        elif task == TaskType.INFERENCE:
            return next(n for n in self.nodes if self.nodes[n].role == NodeRole.AI_ENGINE)
        
        elif task == TaskType.BROADCAST:
            return next(n for n in self.nodes if self.nodes[n].role == NodeRole.GATEWAY)
        
        return self._least_busy_node()
    
    def _least_busy_node(self) -> str:
        """Which node is least busy right now?"""
        return min(self.nodes.keys(), key=lambda n: self.nodes[n].utilization)
    
    def can_do_task(self, node: str, task: TaskType) -> bool:
        """Does this node have capability to do this task?"""
        role = self.nodes[node].role
        
        capability_map = {
            NodeRole.GATEWAY: [TaskType.BROADCAST, TaskType.ANALYZE],
            NodeRole.WORKER: [TaskType.VIDEO_STITCH, TaskType.ENCODE, TaskType.AUDIO_SYNC],
            NodeRole.AI_ENGINE: [TaskType.INFERENCE, TaskType.ANALYZE, TaskType.GENERATE],
            NodeRole.MEDIA: [TaskType.VIDEO_STITCH, TaskType.ENCODE, TaskType.AUDIO_SYNC],
        }
        
        return task in capability_map.get(role, [])


class EpicReasoner:
    """
    The thinking engine for your autonomous system.
    
    Given state of your infrastructure, learns from patterns,
    makes intelligent decisions about what to do next.
    """
    
    def __init__(self, infrastructure: Dict[str, NodeState]):
        self.infrastructure = infrastructure
        self.pattern_engine = PatterRecognition()
        self.healer = SelfHealer()
        self.fleet_intelligence = FleetIntelligence(infrastructure)
        self.decision_history: List[Decision] = []
    
    def reason_about_task(self, objective: str, context: Dict[str, Any]) -> Decision:
        """
        Given an objective and context, reason about what to do.
        
        Example:
            objective = "Create final video from 3 sources"
            context = {
                "videos": ["video1.mp4", "video2.mp4", "video3.mp4"],
                "deadline": "2 minutes",
                "quality": "high",
            }
        
        Reasoner decides:
            - Use Acer for stitching (it's less busy)
            - Stitch with FFmpeg copy mode (fast, lossless)
            - Then broadcast to Lenovo for backup
        """
        
        # Step 1: Check if we've learned a pattern for this
        learned_pattern = self.pattern_engine.predict_next_steps(objective)
        
        # Step 2: Check if there's a known failure mode to prevent
        prevention = self.healer.get_preventive_action(objective)
        
        # Step 3: Assess fleet state right now
        best_node = self.fleet_intelligence.best_node_for_task(TaskType.VIDEO_STITCH)
        
        # Step 4: Build decision with reasoning
        decision = Decision(
            action="stitch_videos",
            target_node=best_node,
            reason=f"Objective: {objective}. {best_node} has lowest utilization ({self.infrastructure[best_node].utilization:.1%}). Using lossless copy mode for speed.",
            confidence=0.95,
            alternatives=[n for n in self.infrastructure if n != best_node],
            predicted_duration=2.5,
            risk_level="low" if prevention is None else "medium",
            recovery_strategy=prevention or "retry_on_different_node"
        )
        
        self.decision_history.append(decision)
        return decision
    
    def reflect_on_decision(self, decision: Decision, outcome: Dict[str, Any]):
        """
        After action completes, learn from result.
        
        If it worked: great, reinforce this decision pattern
        If it failed: analyze why, prevent recurrence
        """
        
        if outcome.get("success"):
            # Reinforce this decision pattern
            self.pattern_engine.record_execution(
                decision.action,
                [decision.action],  # simplified for now
                outcome.get("resources_used", {})
            )
        else:
            # Learn from failure
            self.healer.record_failure(
                outcome.get("error", "Unknown"),
                {"decision": decision, "outcome": outcome}
            )
    
    def export_reasoning(self) -> Dict[str, Any]:
        """Explain all reasoning to user"""
        return {
            "decision_history": [
                {
                    "action": d.action,
                    "target": d.target_node,
                    "reason": d.reason,
                    "confidence": d.confidence,
                } for d in self.decision_history[-10:]  # last 10
            ],
            "learned_patterns": self.pattern_engine.patterns,
            "failure_patterns": self.healer.failure_patterns,
            "preventive_measures": self.healer.preventive_measures,
        }


if __name__ == "__main__":
    # Example: Your infrastructure
    nodes = {
        "ollama": NodeState("ollama", NodeRole.AI_ENGINE, True, 0.3),
        "lenovo": NodeState("lenovo", NodeRole.GATEWAY, True, 0.5),
        "acer": NodeState("acer", NodeRole.WORKER, True, 0.2),
    }
    
    reasoner = EpicReasoner(nodes)
    
    # You want to create a video
    decision = reasoner.reason_about_task(
        "Create final video from 3 sources",
        {
            "videos": ["video1.mp4", "video2.mp4", "video3.mp4"],
            "deadline": "2 minutes",
            "quality": "high",
        }
    )
    
    print("REASONER DECISION:")
    print(f"  Action: {decision.action}")
    print(f"  Target: {decision.target_node}")
    print(f"  Reason: {decision.reason}")
    print(f"  Confidence: {decision.confidence:.0%}")
    print(f"  Risk: {decision.risk_level}")
    print(f"  Recovery: {decision.recovery_strategy}")
    
    # Later, when it completes, tell reasoner how it went
    reasoner.reflect_on_decision(decision, {
        "success": True,
        "duration": 2.3,
        "resources_used": {"bandwidth": 250.0, "cpu": 0.8}
    })
    
    # Check what reasoner learned
    print("\nREASONER LEARNING:")
    print(json.dumps(reasoner.export_reasoning(), indent=2, default=str))
