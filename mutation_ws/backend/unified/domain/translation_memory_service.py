"""
Translation Memory Service
==========================

Provides memory and learning capabilities for the LLM translation system.
Stores successful translations, user corrections, and domain knowledge.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from pathlib import Path

from ..core.result_enhanced import Result, Success, Failure
from ..core.error_types import AppError, Errors
from ..core.functional_utils import safe_result

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of translation memories."""
    TRANSLATION_PAIR = "translation_pair"
    USER_CORRECTION = "user_correction"
    DOMAIN_PATTERN = "domain_pattern"
    USER_PREFERENCE = "user_preference"
    CLARIFICATION = "clarification"
    SUCCESSFUL_PATTERN = "successful_pattern"


@dataclass
class TranslationMemory:
    """A single translation memory entry."""
    id: str
    memory_type: MemoryType
    source_text: str
    target_text: str
    metadata: Dict[str, any]
    confidence: float
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None


@dataclass
class MemorySearchResult:
    """Result of memory search."""
    memories: List[TranslationMemory]
    exact_match: Optional[TranslationMemory]
    similar_matches: List[TranslationMemory]
    relevance_scores: Dict[str, float]


class TranslationMemoryService:
    """
    Service for managing translation memories and learning.
    
    Features:
    - Store successful translations
    - Learn from user corrections
    - Build domain knowledge
    - Track user preferences
    - Provide contextual suggestions
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize memory service."""
        self.config = config or {}
        
        # Storage configuration
        self.memory_dir = Path(self.config.get('memory_dir', './data/translation_memory'))
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory limits
        self.max_memories_per_type = self.config.get('max_memories_per_type', 10000)
        self.memory_retention_days = self.config.get('memory_retention_days', 365)
        
        # In-memory cache for performance
        self._memory_cache: Dict[MemoryType, Dict[str, TranslationMemory]] = {
            mem_type: {} for mem_type in MemoryType
        }
        
        # Similarity threshold
        self.similarity_threshold = self.config.get('similarity_threshold', 0.7)
        
        # Load existing memories
        self._load_memories()
    
    def remember_translation(
        self,
        source: str,
        target: str,
        confidence: float,
        metadata: Optional[Dict] = None,
        user_id: Optional[str] = None
    ) -> Result[TranslationMemory, AppError]:
        """Remember a successful translation."""
        memory = self._create_memory(
            MemoryType.TRANSLATION_PAIR,
            source,
            target,
            confidence,
            metadata or {},
            user_id
        )
        
        return self._store_memory(memory)
    
    def remember_correction(
        self,
        original_source: str,
        incorrect_target: str,
        correct_target: str,
        user_id: Optional[str] = None
    ) -> Result[TranslationMemory, AppError]:
        """Remember a user correction."""
        metadata = {
            'incorrect_translation': incorrect_target,
            'correction_time': datetime.utcnow().isoformat()
        }
        
        memory = self._create_memory(
            MemoryType.USER_CORRECTION,
            original_source,
            correct_target,
            1.0,  # User corrections have high confidence
            metadata,
            user_id
        )
        
        return self._store_memory(memory)
    
    def remember_clarification(
        self,
        original_text: str,
        clarification: str,
        final_translation: str,
        user_id: Optional[str] = None
    ) -> Result[TranslationMemory, AppError]:
        """Remember a clarification interaction."""
        metadata = {
            'clarification': clarification,
            'interaction_time': datetime.utcnow().isoformat()
        }
        
        memory = self._create_memory(
            MemoryType.CLARIFICATION,
            f"{original_text} | Clarification: {clarification}",
            final_translation,
            0.9,
            metadata,
            user_id
        )
        
        return self._store_memory(memory)
    
    def search_memories(
        self,
        text: str,
        memory_types: Optional[List[MemoryType]] = None,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> Result[MemorySearchResult, AppError]:
        """Search for relevant memories."""
        return (
            self._validate_search_params(text, limit)
            .bind(lambda _: self._perform_search(text, memory_types, user_id, limit))
        )
    
    def get_user_preferences(
        self,
        user_id: str
    ) -> Result[Dict[str, any], AppError]:
        """Get user-specific preferences."""
        preferences = {}
        
        # Get user's preference memories
        user_prefs = [
            mem for mem in self._memory_cache[MemoryType.USER_PREFERENCE].values()
            if mem.user_id == user_id
        ]
        
        # Aggregate preferences
        for pref in user_prefs:
            pref_type = pref.metadata.get('preference_type', 'general')
            preferences[pref_type] = pref.metadata.get('preference_value')
        
        return Success(preferences)
    
    def update_memory_usage(
        self,
        memory_id: str
    ) -> Result[None, AppError]:
        """Update usage statistics for a memory."""
        # Find memory across all types
        for mem_type, memories in self._memory_cache.items():
            if memory_id in memories:
                memory = memories[memory_id]
                memory.usage_count += 1
                memory.last_used = datetime.utcnow()
                return self._persist_memory(memory)
        
        return Failure(Errors.not_found(f"Memory {memory_id} not found"))
    
    def _create_memory(
        self,
        memory_type: MemoryType,
        source: str,
        target: str,
        confidence: float,
        metadata: Dict,
        user_id: Optional[str]
    ) -> TranslationMemory:
        """Create a new memory entry."""
        import uuid
        
        return TranslationMemory(
            id=str(uuid.uuid4()),
            memory_type=memory_type,
            source_text=source,
            target_text=target,
            metadata=metadata,
            confidence=confidence,
            user_id=user_id
        )
    
    def _store_memory(
        self,
        memory: TranslationMemory
    ) -> Result[TranslationMemory, AppError]:
        """Store memory in cache and persist."""
        # Check limits
        if len(self._memory_cache[memory.memory_type]) >= self.max_memories_per_type:
            self._evict_old_memories(memory.memory_type)
        
        # Store in cache
        self._memory_cache[memory.memory_type][memory.id] = memory
        
        # Persist to disk
        return self._persist_memory(memory).map(lambda _: memory)
    
    def _perform_search(
        self,
        text: str,
        memory_types: Optional[List[MemoryType]],
        user_id: Optional[str],
        limit: int
    ) -> Result[MemorySearchResult, AppError]:
        """Perform memory search."""
        types_to_search = memory_types or list(MemoryType)
        all_matches = []
        
        # Search each memory type
        for mem_type in types_to_search:
            matches = self._search_memory_type(
                text,
                mem_type,
                user_id
            )
            all_matches.extend(matches)
        
        # Score and rank matches
        scored_matches = self._score_matches(text, all_matches)
        
        # Sort by relevance
        sorted_matches = sorted(
            scored_matches,
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # Extract results
        memories = [match[0] for match in sorted_matches]
        relevance_scores = {
            match[0].id: match[1] for match in sorted_matches
        }
        
        # Find exact match
        exact_match = None
        for memory in memories:
            if memory.source_text.lower() == text.lower():
                exact_match = memory
                break
        
        # Similar matches (excluding exact)
        similar_matches = [
            mem for mem in memories
            if mem != exact_match and relevance_scores[mem.id] >= self.similarity_threshold
        ]
        
        return Success(MemorySearchResult(
            memories=memories,
            exact_match=exact_match,
            similar_matches=similar_matches,
            relevance_scores=relevance_scores
        ))
    
    def _search_memory_type(
        self,
        text: str,
        memory_type: MemoryType,
        user_id: Optional[str]
    ) -> List[TranslationMemory]:
        """Search within a specific memory type."""
        memories = self._memory_cache[memory_type].values()
        
        # Filter by user if specified
        if user_id:
            memories = [
                mem for mem in memories
                if mem.user_id == user_id or mem.user_id is None
            ]
        
        # Basic substring matching (can be enhanced with better similarity)
        text_lower = text.lower()
        matches = []
        
        for memory in memories:
            if (text_lower in memory.source_text.lower() or
                memory.source_text.lower() in text_lower):
                matches.append(memory)
        
        return matches
    
    def _score_matches(
        self,
        query: str,
        matches: List[TranslationMemory]
    ) -> List[Tuple[TranslationMemory, float]]:
        """Score matches by relevance."""
        scored = []
        
        for match in matches:
            score = self._calculate_relevance_score(query, match)
            scored.append((match, score))
        
        return scored
    
    def _calculate_relevance_score(
        self,
        query: str,
        memory: TranslationMemory
    ) -> float:
        """Calculate relevance score for a memory."""
        # Simple scoring based on:
        # - Text similarity
        # - Confidence
        # - Usage count
        # - Recency
        
        # Text similarity (simple for now)
        query_lower = query.lower()
        source_lower = memory.source_text.lower()
        
        if query_lower == source_lower:
            text_score = 1.0
        elif query_lower in source_lower or source_lower in query_lower:
            text_score = 0.7
        else:
            # Calculate overlap
            query_words = set(query_lower.split())
            source_words = set(source_lower.split())
            overlap = len(query_words & source_words)
            total = len(query_words | source_words)
            text_score = overlap / total if total > 0 else 0.0
        
        # Confidence factor
        confidence_score = memory.confidence
        
        # Usage factor (normalized)
        usage_score = min(memory.usage_count / 10.0, 1.0)
        
        # Recency factor
        age_days = (datetime.utcnow() - memory.last_used).days
        recency_score = max(0.0, 1.0 - (age_days / 365.0))
        
        # Weighted combination
        final_score = (
            text_score * 0.5 +
            confidence_score * 0.2 +
            usage_score * 0.15 +
            recency_score * 0.15
        )
        
        return final_score
    
    def _evict_old_memories(self, memory_type: MemoryType) -> None:
        """Evict old memories to make room."""
        memories = list(self._memory_cache[memory_type].values())
        
        # Sort by last used date
        memories.sort(key=lambda m: m.last_used)
        
        # Remove oldest 10%
        to_remove = int(len(memories) * 0.1)
        for memory in memories[:to_remove]:
            del self._memory_cache[memory_type][memory.id]
            self._delete_persisted_memory(memory)
    
    def _persist_memory(self, memory: TranslationMemory) -> Result[None, AppError]:
        """Persist memory to disk."""
        try:
            file_path = self.memory_dir / f"{memory.memory_type.value}" / f"{memory.id}.json"
            file_path.parent.mkdir(exist_ok=True)
            
            data = {
                'id': memory.id,
                'memory_type': memory.memory_type.value,
                'source_text': memory.source_text,
                'target_text': memory.target_text,
                'metadata': memory.metadata,
                'confidence': memory.confidence,
                'usage_count': memory.usage_count,
                'created_at': memory.created_at.isoformat(),
                'last_used': memory.last_used.isoformat(),
                'user_id': memory.user_id
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return Success(None)
            
        except Exception as e:
            logger.error(f"Failed to persist memory: {e}")
            return Failure(Errors.io(f"Failed to persist memory: {e}"))
    
    def _delete_persisted_memory(self, memory: TranslationMemory) -> None:
        """Delete persisted memory file."""
        file_path = self.memory_dir / f"{memory.memory_type.value}" / f"{memory.id}.json"
        if file_path.exists():
            file_path.unlink()
    
    def _load_memories(self) -> None:
        """Load memories from disk on startup."""
        for memory_type in MemoryType:
            type_dir = self.memory_dir / memory_type.value
            if type_dir.exists():
                self._load_memory_type(memory_type, type_dir)
    
    def _load_memory_type(self, memory_type: MemoryType, type_dir: Path) -> None:
        """Load all memories of a specific type."""
        for file_path in type_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                memory = TranslationMemory(
                    id=data['id'],
                    memory_type=memory_type,
                    source_text=data['source_text'],
                    target_text=data['target_text'],
                    metadata=data['metadata'],
                    confidence=data['confidence'],
                    usage_count=data.get('usage_count', 0),
                    created_at=datetime.fromisoformat(data['created_at']),
                    last_used=datetime.fromisoformat(data['last_used']),
                    user_id=data.get('user_id')
                )
                
                # Check retention
                age_days = (datetime.utcnow() - memory.last_used).days
                if age_days <= self.memory_retention_days:
                    self._memory_cache[memory_type][memory.id] = memory
                else:
                    # Delete old memory
                    file_path.unlink()
                    
            except Exception as e:
                logger.warning(f"Failed to load memory from {file_path}: {e}")
    
    def _validate_search_params(self, text: str, limit: int) -> Result[None, AppError]:
        """Validate search parameters."""
        if not text or not text.strip():
            return Failure(Errors.validation("Search text cannot be empty"))
        
        if limit <= 0 or limit > 100:
            return Failure(Errors.validation("Limit must be between 1 and 100"))
        
        return Success(None)
    
    def export_memories(
        self,
        memory_types: Optional[List[MemoryType]] = None,
        user_id: Optional[str] = None
    ) -> Result[Dict[str, List[Dict]], AppError]:
        """Export memories for backup or analysis."""
        types_to_export = memory_types or list(MemoryType)
        export_data = {}
        
        for mem_type in types_to_export:
            memories = self._memory_cache[mem_type].values()
            
            if user_id:
                memories = [m for m in memories if m.user_id == user_id]
            
            export_data[mem_type.value] = [
                {
                    'source': m.source_text,
                    'target': m.target_text,
                    'confidence': m.confidence,
                    'usage_count': m.usage_count,
                    'metadata': m.metadata
                }
                for m in memories
            ]
        
        return Success(export_data)


class TauKnowledgeBase:
    """
    Knowledge base for Tau language patterns and successful translations.
    Learns from user interactions and builds a corpus of verified translations.
    """
    
    def __init__(self, memory_service: Optional[TranslationMemoryService] = None):
        """Initialize with memory service (≤10 lines)."""
        self.memory_service = memory_service or TranslationMemoryService()
        self.component_library = self._load_component_library()
        self.pattern_cache = {}
        self.confidence_threshold = 0.8
        
    def _load_component_library(self) -> Dict[str, Dict[str, Any]]:
        """Load pre-defined component specifications (≤10 lines)."""
        return {
            "1-bit-adder": {
                "patterns": ["1-bit adder", "one bit adder", "1 bit adder", "single bit adder"],
                "tau": "adder1(a, b, sum, carry) := (sum = a + b) && (carry = a & b).",
                "description": "Basic 1-bit adder with sum and carry outputs",
                "confidence": 1.0
            },
            "half-adder": {
                "patterns": ["half adder", "half-adder"],
                "tau": "half_adder(a, b, sum, carry) := (sum = a + b) && (carry = a & b).",
                "description": "Half adder (same as 1-bit adder)",
                "confidence": 1.0
            },
            "full-adder": {
                "patterns": ["full adder", "full-adder", "adder with carry in"],
                "tau": "full_adder(a, b, cin, sum, cout) := (sum = a + b + cin) && (cout = (a & b) | ((a + b) & cin)).",
                "description": "Full adder with carry input",
                "confidence": 1.0
            },
            "bit-definition": {
                "patterns": ["bit definition", "define bit", "bit constraint"],
                "tau": "bit(x) := (x = 0) || (x = 1).",
                "description": "Defines a bit constraint",
                "confidence": 1.0
            }
        }
    
    def find_component(self, query: str) -> Optional[Dict[str, Any]]:
        """Find matching component from library (≤10 lines)."""
        query_lower = query.lower().strip()
        
        for component_id, component in self.component_library.items():
            for pattern in component["patterns"]:
                if pattern in query_lower:
                    return {
                        "id": component_id,
                        "tau": component["tau"],
                        "description": component["description"],
                        "confidence": component["confidence"],
                        "source": "component_library"
                    }
        return None
    
    def learn_from_translation(self, english: str, tau: str, confidence: float) -> Result[bool, AppError]:
        """Learn from successful translation (≤10 lines)."""
        if confidence < self.confidence_threshold:
            return Success(False)  # Don't learn from low-confidence translations
            
        # Store in memory service
        memory = TranslationMemory(
            source_text=english,
            translated_text=tau,
            source_language="english",
            target_language="tau",
            user_id="system",
            confidence=confidence,
            metadata={"learned": True}
        )
        
        return self.memory_service.remember_translation(memory)
    
    def get_similar_translations(self, query: str, limit: int = 5) -> List[TranslationMemory]:
        """Get similar past translations (≤10 lines)."""
        search_params = MemorySearchParams(
            query=query,
            memory_types=[MemoryType.TRANSLATION],
            limit=limit,
            min_similarity=0.7
        )
        
        result = self.memory_service.search_memories(search_params)
        if isinstance(result, Success):
            return [m for m in result.unwrap() if m.target_language == "tau"]
        return []
    
    def get_tau_examples(self, concept: str) -> List[Dict[str, str]]:
        """Get Tau examples for a concept (≤10 lines)."""
        examples = []
        
        # Check component library
        component = self.find_component(concept)
        if component:
            examples.append({
                "description": component["description"],
                "tau": component["tau"],
                "confidence": component["confidence"]
            })
        
        # Check learned translations
        similar = self.get_similar_translations(concept, limit=3)
        for memory in similar:
            examples.append({
                "description": memory.source_text,
                "tau": memory.translated_text,
                "confidence": memory.confidence
            })
        
        return examples
