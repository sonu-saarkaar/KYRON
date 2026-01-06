"""
KYRON CORE BRAIN - Memory & Knowledge Layer

Maintains:
1. Master Profile (Permanent Memory)
2. Execution State (Short-Term Memory)
3. Experience Memory (Learning Memory)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """Types of memory"""
    MASTER_PROFILE = "master_profile"
    EXECUTION_STATE = "execution_state"
    EXPERIENCE = "experience"

@dataclass
class MasterProfile:
    """Permanent memory - User's master profile"""
    user_id: str
    personal_details: Dict[str, Any] = field(default_factory=dict)
    identity_documents: Dict[str, Any] = field(default_factory=dict)
    contact_details: Dict[str, Any] = field(default_factory=dict)
    education_details: Dict[str, Any] = field(default_factory=dict)
    bank_details: Dict[str, Any] = field(default_factory=dict)
    uploaded_documents: List[Dict[str, Any]] = field(default_factory=list)
    verified_data: Dict[str, bool] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["last_updated"] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MasterProfile':
        """Create from dictionary"""
        if "last_updated" in data and isinstance(data["last_updated"], str):
            data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        return cls(**data)

@dataclass
class ExecutionState:
    """Short-term memory - Current execution state"""
    session_id: str
    service_id: str
    current_step_id: str = ""
    current_step_index: int = 0
    completed_steps: List[str] = field(default_factory=list)
    filled_fields: Dict[str, Any] = field(default_factory=dict)  # field_id -> value
    active_tab_id: Optional[str] = None
    active_iframe_id: Optional[str] = None
    current_url: str = ""
    current_page_type: str = ""
    pause_checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    error_history: List[Dict[str, Any]] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    is_paused: bool = False
    is_stopped: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["started_at"] = self.started_at.isoformat()
        data["last_activity"] = self.last_activity.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ExecutionState':
        """Create from dictionary"""
        if "started_at" in data and isinstance(data["started_at"], str):
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        if "last_activity" in data and isinstance(data["last_activity"], str):
            data["last_activity"] = datetime.fromisoformat(data["last_activity"])
        return cls(**data)
    
    def create_checkpoint(self, step_id: str, step_data: Dict):
        """Create a pause checkpoint"""
        checkpoint = {
            "step_id": step_id,
            "step_index": self.current_step_index,
            "timestamp": datetime.now().isoformat(),
            "filled_fields": self.filled_fields.copy(),
            "current_url": self.current_url,
            "page_type": self.current_page_type,
            "step_data": step_data
        }
        self.pause_checkpoints.append(checkpoint)
        logger.info(f"Created checkpoint at step {step_id}")
    
    def restore_from_checkpoint(self, checkpoint_index: int = -1) -> Optional[Dict]:
        """Restore state from checkpoint"""
        if not self.pause_checkpoints:
            return None
        
        checkpoint = self.pause_checkpoints[checkpoint_index]
        self.current_step_id = checkpoint["step_id"]
        self.current_step_index = checkpoint["step_index"]
        self.filled_fields = checkpoint.get("filled_fields", {}).copy()
        self.current_url = checkpoint.get("current_url", "")
        self.current_page_type = checkpoint.get("page_type", "")
        logger.info(f"Restored from checkpoint: step {self.current_step_id}")
        return checkpoint

@dataclass
class ExperienceMemory:
    """Learning memory - Patterns and strategies that worked"""
    selector_patterns: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)  # field_type -> successful selectors
    failed_patterns: Dict[str, List[str]] = field(default_factory=dict)  # field_type -> failed selectors
    website_behavior: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # website -> behavior patterns
    recovery_strategies: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)  # error_type -> strategies
    success_rate: Dict[str, float] = field(default_factory=dict)  # strategy -> success rate
    last_learned: datetime = field(default_factory=datetime.now)
    
    def record_success(self, field_type: str, selector: str, context: Dict):
        """Record successful selector pattern"""
        if field_type not in self.selector_patterns:
            self.selector_patterns[field_type] = []
        
        pattern = {
            "selector": selector,
            "context": context,
            "success_count": 1,
            "last_used": datetime.now().isoformat()
        }
        
        # Check if similar pattern exists
        existing = next(
            (p for p in self.selector_patterns[field_type] if p["selector"] == selector),
            None
        )
        if existing:
            existing["success_count"] += 1
            existing["last_used"] = datetime.now().isoformat()
        else:
            self.selector_patterns[field_type].append(pattern)
        
        self.last_learned = datetime.now()
    
    def record_failure(self, field_type: str, selector: str):
        """Record failed selector pattern"""
        if field_type not in self.failed_patterns:
            self.failed_patterns[field_type] = []
        
        if selector not in self.failed_patterns[field_type]:
            self.failed_patterns[field_type].append(selector)
    
    def get_best_selector(self, field_type: str, context: Dict) -> Optional[str]:
        """Get best selector for field type based on experience"""
        if field_type not in self.selector_patterns:
            return None
        
        patterns = self.selector_patterns[field_type]
        if not patterns:
            return None
        
        # Sort by success count and recency
        patterns.sort(key=lambda p: (
            p["success_count"],
            datetime.fromisoformat(p["last_used"])
        ), reverse=True)
        
        return patterns[0]["selector"]
    
    def record_recovery(self, error_type: str, strategy: str, success: bool):
        """Record recovery strategy outcome"""
        if error_type not in self.recovery_strategies:
            self.recovery_strategies[error_type] = []
        
        strategy_data = {
            "strategy": strategy,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        self.recovery_strategies[error_type].append(strategy_data)
        
        # Update success rate
        key = f"{error_type}:{strategy}"
        if key not in self.success_rate:
            self.success_rate[key] = 0.0
        
        # Calculate success rate
        all_attempts = [s for s in self.recovery_strategies[error_type] if s["strategy"] == strategy]
        successes = sum(1 for s in all_attempts if s["success"])
        self.success_rate[key] = successes / len(all_attempts) if all_attempts else 0.0

class MemoryKnowledgeLayer:
    """
    KYRON's Memory & Knowledge Layer
    
    Manages all types of memory: Master Profile, Execution State, Experience
    """
    
    def __init__(self):
        self.master_profiles: Dict[str, MasterProfile] = {}
        self.execution_states: Dict[str, ExecutionState] = {}
        self.experience_memory = ExperienceMemory()
    
    # Master Profile Operations
    def get_master_profile(self, user_id: str) -> Optional[MasterProfile]:
        """Get user's master profile"""
        return self.master_profiles.get(user_id)
    
    def save_master_profile(self, user_id: str, profile: MasterProfile):
        """Save master profile"""
        profile.last_updated = datetime.now()
        self.master_profiles[user_id] = profile
        logger.info(f"Saved master profile for user {user_id}")
    
    def update_master_profile(self, user_id: str, updates: Dict[str, Any]):
        """Update master profile with new data"""
        profile = self.get_master_profile(user_id)
        if not profile:
            profile = MasterProfile(user_id=user_id)
        
        # Update sections
        if "personal_details" in updates:
            profile.personal_details.update(updates["personal_details"])
        if "contact_details" in updates:
            profile.contact_details.update(updates["contact_details"])
        if "identity_documents" in updates:
            profile.identity_documents.update(updates["identity_documents"])
        
        profile.last_updated = datetime.now()
        self.master_profiles[user_id] = profile
        logger.info(f"Updated master profile for user {user_id}")
    
    # Execution State Operations
    def create_execution_state(self, session_id: str, service_id: str) -> ExecutionState:
        """Create new execution state"""
        state = ExecutionState(session_id=session_id, service_id=service_id)
        self.execution_states[session_id] = state
        logger.info(f"Created execution state for session {session_id}")
        return state
    
    def get_execution_state(self, session_id: str) -> Optional[ExecutionState]:
        """Get execution state"""
        return self.execution_states.get(session_id)
    
    def update_execution_state(self, session_id: str, updates: Dict[str, Any]):
        """Update execution state"""
        state = self.get_execution_state(session_id)
        if not state:
            return
        
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        state.last_activity = datetime.now()
        logger.debug(f"Updated execution state for session {session_id}")
    
    def save_execution_state(self, session_id: str, state: ExecutionState):
        """Save execution state"""
        state.last_activity = datetime.now()
        self.execution_states[session_id] = state
    
    def pause_execution(self, session_id: str, step_id: str, step_data: Dict):
        """Pause execution and create checkpoint"""
        state = self.get_execution_state(session_id)
        if state:
            state.is_paused = True
            state.create_checkpoint(step_id, step_data)
            logger.info(f"Paused execution at step {step_id}")
    
    def resume_execution(self, session_id: str) -> Optional[Dict]:
        """Resume execution from checkpoint"""
        state = self.get_execution_state(session_id)
        if state and state.pause_checkpoints:
            state.is_paused = False
            checkpoint = state.restore_from_checkpoint()
            logger.info(f"Resumed execution from checkpoint")
            return checkpoint
        return None
    
    # Experience Memory Operations
    def learn_selector_success(self, field_type: str, selector: str, context: Dict):
        """Learn from successful selector"""
        self.experience_memory.record_success(field_type, selector, context)
    
    def learn_selector_failure(self, field_type: str, selector: str):
        """Learn from failed selector"""
        self.experience_memory.record_failure(field_type, selector)
    
    def get_experienced_selector(self, field_type: str, context: Dict) -> Optional[str]:
        """Get selector based on experience"""
        return self.experience_memory.get_best_selector(field_type, context)
    
    def learn_recovery(self, error_type: str, strategy: str, success: bool):
        """Learn from recovery attempt"""
        self.experience_memory.record_recovery(error_type, strategy, success)
    
    def get_best_recovery_strategy(self, error_type: str) -> Optional[str]:
        """Get best recovery strategy for error type"""
        if error_type not in self.experience_memory.recovery_strategies:
            return None
        
        # Find strategy with highest success rate
        best_strategy = None
        best_rate = 0.0
        
        for key, rate in self.experience_memory.success_rate.items():
            if key.startswith(f"{error_type}:") and rate > best_rate:
                best_rate = rate
                best_strategy = key.split(":", 1)[1]
        
        return best_strategy
    
    # Serialization
    def serialize_state(self, session_id: str) -> Optional[str]:
        """Serialize execution state to JSON"""
        state = self.get_execution_state(session_id)
        if state:
            return json.dumps(state.to_dict(), indent=2)
        return None
    
    def deserialize_state(self, session_id: str, json_str: str) -> Optional[ExecutionState]:
        """Deserialize execution state from JSON"""
        try:
            data = json.loads(json_str)
            state = ExecutionState.from_dict(data)
            self.execution_states[session_id] = state
            return state
        except Exception as e:
            logger.error(f"Error deserializing state: {e}")
            return None

