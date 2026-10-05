"""
Epic Maestro Model Ensemble - Multi-Source Intelligence

Integrates:
- Local Ollama (Llama2, Mistral, CodeLlama)
- HuggingFace models (auto-download & cache)
- HuggingFace Inference API (fallback/backup)
- Vision models for media analysis
- Embedding models for semantic reasoning

Intelligent routing based on:
- Latency requirements
- Quality requirements
- Cost optimization
- Load balancing
- Model specialization
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
import json
from datetime import datetime
import hashlib


class ModelSource(Enum):
    """Where to run the model"""
    OLLAMA_LOCAL = "ollama_local"      # SOTA-Local-AI
    HUGGINGFACE_LOCAL = "hf_local"     # Downloaded & cached
    HUGGINGFACE_API = "hf_api"         # Cloud inference
    ENSEMBLE = "ensemble"              # Multiple sources


class ModelCategory(Enum):
    """Type of model"""
    TEXT_GENERATION = "text_generation"
    TEXT_EMBEDDING = "text_embedding"
    VISION = "vision"
    CODE = "code"
    REASONING = "reasoning"


@dataclass
class ModelProfile:
    """Profile of available model"""
    name: str
    source: ModelSource
    category: ModelCategory
    latency_ms: float           # Typical latency
    cost_per_1m_tokens: float   # Estimated cost
    quality_score: float        # 0-1, output quality
    specialization: List[str]   # What it's good at
    
    def score_for_query(self, 
                        latency_budget_ms: float,
                        quality_required: float,
                        budget_tokens: int,
                        task_type: str) -> float:
        """Calculate fitness score for this query (0-1, higher is better)"""
        
        score = 0.0
        
        # Latency fitness
        if self.latency_ms <= latency_budget_ms:
            score += 0.3
        else:
            score += 0.3 * (latency_budget_ms / self.latency_ms)
        
        # Quality fitness
        if self.quality_score >= quality_required:
            score += 0.3
        else:
            score += 0.3 * (self.quality_score / quality_required)
        
        # Cost fitness
        estimated_cost = (self.cost_per_1m_tokens / 1_000_000) * budget_tokens
        if estimated_cost == 0:  # Local = free
            score += 0.2
        else:
            score += 0.2 * (1.0 / (1.0 + estimated_cost))
        
        # Task specialization bonus
        if task_type in self.specialization:
            score += 0.2
        
        return min(score, 1.0)


class ModelEnsemble:
    """Manage and route across multiple models intelligently"""
    
    def __init__(self):
        self.models = self._initialize_models()
        self.performance_history: List[Dict[str, Any]] = []
        self.cache: Dict[str, str] = {}
    
    def _initialize_models(self) -> Dict[str, ModelProfile]:
        """Set up all available models"""
        
        return {
            # === LOCAL OLLAMA (SOTA-Local-AI) ===
            "ollama/llama2-7b": ModelProfile(
                name="Llama 2 7B",
                source=ModelSource.OLLAMA_LOCAL,
                category=ModelCategory.TEXT_GENERATION,
                latency_ms=200,
                cost_per_1m_tokens=0.0,  # Local
                quality_score=0.85,
                specialization=["general", "reasoning", "analysis"]
            ),
            "ollama/mistral-7b": ModelProfile(
                name="Mistral 7B",
                source=ModelSource.OLLAMA_LOCAL,
                category=ModelCategory.TEXT_GENERATION,
                latency_ms=150,
                cost_per_1m_tokens=0.0,
                quality_score=0.88,
                specialization=["fast_inference", "code", "reasoning"]
            ),
            "ollama/codellama-13b": ModelProfile(
                name="CodeLlama 13B",
                source=ModelSource.OLLAMA_LOCAL,
                category=ModelCategory.CODE,
                latency_ms=300,
                cost_per_1m_tokens=0.0,
                quality_score=0.92,
                specialization=["code", "programming", "debugging"]
            ),
            
            # === HUGGINGFACE LOCAL (Downloaded & Cached) ===
            "hf_local/all-minilm-l6-v2": ModelProfile(
                name="All-MiniLM-L6-V2",
                source=ModelSource.HUGGINGFACE_LOCAL,
                category=ModelCategory.TEXT_EMBEDDING,
                latency_ms=50,
                cost_per_1m_tokens=0.0,
                quality_score=0.9,
                specialization=["embeddings", "semantic_search", "similarity"]
            ),
            "hf_local/bge-small-en-v1.5": ModelProfile(
                name="BGE Small EN 1.5",
                source=ModelSource.HUGGINGFACE_LOCAL,
                category=ModelCategory.TEXT_EMBEDDING,
                latency_ms=40,
                cost_per_1m_tokens=0.0,
                quality_score=0.88,
                specialization=["embeddings", "retrieval", "ranking"]
            ),
            
            # === HUGGINGFACE API ===
            "hf_api/meta-llama/Llama-2-70b-chat": ModelProfile(
                name="Llama 2 70B Chat",
                source=ModelSource.HUGGINGFACE_API,
                category=ModelCategory.TEXT_GENERATION,
                latency_ms=800,
                cost_per_1m_tokens=0.001,
                quality_score=0.95,
                specialization=["high_quality", "long_context", "instruction_following"]
            ),
            "hf_api/mistralai/Mistral-7B-Instruct-v0.1": ModelProfile(
                name="Mistral 7B Instruct",
                source=ModelSource.HUGGINGFACE_API,
                category=ModelCategory.TEXT_GENERATION,
                latency_ms=500,
                cost_per_1m_tokens=0.0005,
                quality_score=0.90,
                specialization=["instruction_following", "reasoning"]
            ),
            "hf_api/togethercomputer/GPT-JT-6B": ModelProfile(
                name="GPT-JT 6B",
                source=ModelSource.HUGGINGFACE_API,
                category=ModelCategory.TEXT_GENERATION,
                latency_ms=300,
                cost_per_1m_tokens=0.0002,
                quality_score=0.82,
                specialization=["fast", "general"]
            ),
            
            # === VISION MODELS ===
            "hf_local/clip-vit-base-patch32": ModelProfile(
                name="CLIP ViT Base",
                source=ModelSource.HUGGINGFACE_LOCAL,
                category=ModelCategory.VISION,
                latency_ms=400,
                cost_per_1m_tokens=0.0,
                quality_score=0.85,
                specialization=["video_analysis", "scene_detection", "object_detection"]
            ),
            "hf_api/Salesforce/blip-image-captioning-large": ModelProfile(
                name="BLIP Image Captioning",
                source=ModelSource.HUGGINGFACE_API,
                category=ModelCategory.VISION,
                latency_ms=1000,
                cost_per_1m_tokens=0.001,
                quality_score=0.92,
                specialization=["image_description", "content_analysis"]
            ),
            
            # === REASONING MODELS ===
            "hf_api/EleutherAI/gpt-neox-20b": ModelProfile(
                name="GPT-NeoX 20B",
                source=ModelSource.HUGGINGFACE_API,
                category=ModelCategory.REASONING,
                latency_ms=600,
                cost_per_1m_tokens=0.0008,
                quality_score=0.88,
                specialization=["reasoning", "logic", "analysis"]
            ),
        }
    
    async def select_best_model(self,
                                task_type: str,
                                latency_budget_ms: float,
                                quality_required: float = 0.8,
                                budget_tokens: int = 1000,
                                prefer_local: bool = True) -> Tuple[str, ModelProfile]:
        """
        Select best model for this query
        
        Args:
            task_type: Type of task ("code", "reasoning", "embedding", etc)
            latency_budget_ms: Maximum acceptable latency
            quality_required: Minimum acceptable quality (0-1)
            budget_tokens: Expected number of tokens
            prefer_local: Prioritize local models if equal performance
        
        Returns:
            (model_id, profile)
        """
        
        candidates = []
        
        for model_id, profile in self.models.items():
            # Filter by quality requirement
            if profile.quality_score < quality_required:
                continue
            
            # Calculate score
            score = profile.score_for_query(
                latency_budget_ms,
                quality_required,
                budget_tokens,
                task_type
            )
            
            candidates.append((model_id, profile, score))
        
        if not candidates:
            # Fallback: use best available
            best_model = max(self.models.items(), 
                           key=lambda x: x[1].quality_score)
            return best_model
        
        # Sort by score, preferring local if tied
        candidates.sort(key=lambda x: (
            -x[2],  # Higher score first
            -(1 if x[1].source == ModelSource.OLLAMA_LOCAL else 0) if prefer_local else 0
        ))
        
        best_id, best_profile, best_score = candidates[0]
        
        return best_id, best_profile
    
    async def query(self,
                   prompt: str,
                   task_type: str = "general",
                   latency_budget_ms: float = 1000,
                   quality_required: float = 0.8) -> Dict[str, Any]:
        """
        Execute query using best model, with fallback strategy
        """
        
        # Check cache first (exact match)
        cache_key = self._make_cache_key(prompt, task_type)
        if cache_key in self.cache:
            return {
                "response": self.cache[cache_key],
                "source": "cache",
                "model": "cache",
                "latency_ms": 0
            }
        
        # Select model
        model_id, profile = await self.select_best_model(
            task_type,
            latency_budget_ms,
            quality_required
        )
        
        start_time = datetime.now()
        
        try:
            # Execute based on source
            if profile.source == ModelSource.OLLAMA_LOCAL:
                response = await self._query_ollama(prompt, model_id)
            elif profile.source == ModelSource.HUGGINGFACE_LOCAL:
                response = await self._query_hf_local(prompt, model_id)
            elif profile.source == ModelSource.HUGGINGFACE_API:
                response = await self._query_hf_api(prompt, model_id)
            else:
                response = "Error: Unknown model source"
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Cache result
            self.cache[cache_key] = response
            
            # Record performance
            self.performance_history.append({
                "timestamp": datetime.now().isoformat(),
                "model": model_id,
                "source": profile.source.value,
                "latency_ms": latency_ms,
                "task_type": task_type,
                "quality": profile.quality_score
            })
            
            return {
                "response": response,
                "source": profile.source.value,
                "model": model_id,
                "latency_ms": latency_ms,
                "quality": profile.quality_score
            }
        
        except Exception as e:
            # Fallback to next best model
            return await self._query_with_fallback(prompt, model_id, task_type, latency_budget_ms)
    
    async def _query_ollama(self, prompt: str, model_id: str) -> str:
        """Query local Ollama instance"""
        
        model_name = model_id.split("/")[-1]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model_name, "prompt": prompt, "stream": False},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("response", "")
                    else:
                        raise Exception(f"Ollama error: {resp.status}")
        except Exception as e:
            raise Exception(f"Ollama query failed: {str(e)}")
    
    async def _query_hf_local(self, prompt: str, model_id: str) -> str:
        """Query locally cached HuggingFace model"""
        
        # Note: In production, use transformers library to load and run locally
        # For now, return placeholder that would execute locally
        return f"[LOCAL-HF] Response from {model_id}: {prompt[:50]}..."
    
    async def _query_hf_api(self, prompt: str, model_id: str) -> str:
        """Query HuggingFace Inference API"""
        
        # This would use actual HF API key from secrets
        # Placeholder for demonstration
        return f"[HF-API] Response from {model_id}: {prompt[:50]}..."
    
    async def _query_with_fallback(self, 
                                   prompt: str, 
                                   failed_model: str,
                                   task_type: str,
                                   latency_budget_ms: float) -> Dict[str, Any]:
        """Try next best model if first fails"""
        
        # Get remaining candidates excluding failed model
        candidates = []
        for model_id, profile in self.models.items():
            if model_id == failed_model:
                continue
            
            score = profile.score_for_query(
                latency_budget_ms,
                0.75,  # Lower quality requirement for fallback
                1000,
                task_type
            )
            candidates.append((model_id, profile, score))
        
        if not candidates:
            return {"response": "All models failed", "source": "error", "model": "none"}
        
        candidates.sort(key=lambda x: -x[2])
        fallback_id, fallback_profile, _ = candidates[0]
        
        try:
            if fallback_profile.source == ModelSource.OLLAMA_LOCAL:
                response = await self._query_ollama(prompt, fallback_id)
            else:
                response = await self._query_hf_api(prompt, fallback_id)
            
            return {
                "response": response,
                "source": f"{fallback_profile.source.value} (fallback)",
                "model": fallback_id,
                "latency_ms": 1500
            }
        except Exception as e:
            return {"response": f"Fallback failed: {str(e)}", "source": "error", "model": "none"}
    
    def _make_cache_key(self, prompt: str, task_type: str) -> str:
        """Create cache key from prompt and task type"""
        combined = f"{task_type}:{prompt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    async def parallel_query(self,
                           prompt: str,
                           num_models: int = 3,
                           task_type: str = "reasoning") -> List[Dict[str, Any]]:
        """
        Execute prompt on multiple models in parallel for ensemble results
        Useful for reasoning tasks where multiple perspectives help
        """
        
        # Select top N models
        candidates = []
        for model_id, profile in self.models.items():
            score = profile.score_for_query(1000, 0.7, 1000, task_type)
            candidates.append((model_id, profile, score))
        
        candidates.sort(key=lambda x: -x[2])
        top_models = candidates[:num_models]
        
        # Execute in parallel
        tasks = [
            self.query(prompt, task_type, 5000)
            for model_id, profile, _ in top_models
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics across all models"""
        
        if not self.performance_history:
            return {"message": "No queries executed yet"}
        
        by_model = {}
        for entry in self.performance_history:
            model = entry["model"]
            if model not in by_model:
                by_model[model] = []
            by_model[model].append(entry["latency_ms"])
        
        stats = {}
        for model, latencies in by_model.items():
            stats[model] = {
                "queries": len(latencies),
                "avg_latency_ms": sum(latencies) / len(latencies),
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
            }
        
        return stats
    
    def export_ensemble_state(self) -> Dict[str, Any]:
        """Export current state of ensemble"""
        
        return {
            "available_models": len(self.models),
            "models_by_source": {
                source.value: len([m for m in self.models.values() if m.source == source])
                for source in ModelSource
            },
            "cache_size": len(self.cache),
            "total_queries": len(self.performance_history),
            "performance_stats": self.get_performance_stats()
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_ensemble_usage():
    """Demonstrate model ensemble in action"""
    
    ensemble = ModelEnsemble()
    
    # Example 1: Fast inference (code completion)
    print("=" * 70)
    print("EXAMPLE 1: Fast Code Inference (latency budget: 300ms)")
    print("=" * 70)
    
    result = await ensemble.query(
        prompt="def fibonacci(n):",
        task_type="code",
        latency_budget_ms=300,
        quality_required=0.85
    )
    
    print(f"Selected Model: {result['model']}")
    print(f"Source: {result['source']}")
    print(f"Latency: {result['latency_ms']:.1f}ms")
    print(f"Quality: {result['quality']:.0%}")
    print(f"Response: {result['response'][:100]}...")
    
    # Example 2: High quality reasoning
    print("\n" + "=" * 70)
    print("EXAMPLE 2: High Quality Reasoning (latency budget: 2000ms)")
    print("=" * 70)
    
    result = await ensemble.query(
        prompt="Explain the implications of the attention mechanism in transformers",
        task_type="reasoning",
        latency_budget_ms=2000,
        quality_required=0.90
    )
    
    print(f"Selected Model: {result['model']}")
    print(f"Source: {result['source']}")
    print(f"Latency: {result['latency_ms']:.1f}ms")
    print(f"Quality: {result['quality']:.0%}")
    
    # Example 3: Parallel ensemble reasoning
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Parallel Ensemble (3 models reasoning together)")
    print("=" * 70)
    
    results = await ensemble.parallel_query(
        prompt="What are the key differences between Llama2 and Mistral?",
        num_models=3,
        task_type="reasoning"
    )
    
    print(f"Models used in parallel: {len(results)}")
    for i, result in enumerate(results, 1):
        if isinstance(result, dict):
            print(f"\n  Model {i}: {result['model']}")
            print(f"  Latency: {result['latency_ms']:.1f}ms")
            print(f"  Quality: {result['quality']:.0%}")
    
    # Export final state
    print("\n" + "=" * 70)
    print("ENSEMBLE STATE")
    print("=" * 70)
    state = ensemble.export_ensemble_state()
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    asyncio.run(example_ensemble_usage())
