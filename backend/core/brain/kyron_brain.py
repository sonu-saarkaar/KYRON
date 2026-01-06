"""
KYRON CORE BRAIN - Main Orchestrator

Integrates all brain layers:
- Intent & Strategy Layer
- Memory & Knowledge Layer
- Perception Layer
- Decision & Adaptation Layer

Coordinates with Execution Engine
"""

from typing import Dict, Optional, Any
import logging

from .intent_strategy_layer import IntentStrategyLayer, ExecutionRoadmap
from .memory_knowledge_layer import MemoryKnowledgeLayer, MasterProfile, ExecutionState
from .perception_layer import PerceptionLayer, PageMetadata
from .decision_adaptation_layer import DecisionAdaptationLayer, ActionDecision
from .intelligence_integration import IntelligenceIntegration

logger = logging.getLogger(__name__)

class KYRONBrain:
    """
    KYRON's Complete Brain System
    
    Orchestrates all intelligence layers
    """
    
    def __init__(self):
        # Initialize all layers
        self.intent_strategy = IntentStrategyLayer()
        self.memory = MemoryKnowledgeLayer()
        self.perception = PerceptionLayer()
        self.decision = DecisionAdaptationLayer(self.memory)
        self.intelligence = IntelligenceIntegration()
        
        logger.info("KYRON Brain initialized with intelligence modules")
    
    # Intent & Strategy Operations
    def understand_intent(self, user_message: str, service_catalog: Dict) -> Optional[tuple]:
        """Understand user intent"""
        return self.intent_strategy.understand_intent(user_message, service_catalog)
    
    def build_roadmap(
        self,
        service_id: str,
        service_config: Dict,
        user_profile: Dict
    ) -> ExecutionRoadmap:
        """Build execution roadmap"""
        return self.intent_strategy.build_roadmap(service_id, service_config, user_profile)
    
    def adjust_roadmap(
        self,
        roadmap: ExecutionRoadmap,
        new_page_info: Dict,
        execution_state: ExecutionState
    ):
        """Adjust roadmap if flow changes"""
        self.intent_strategy.adjust_roadmap(roadmap, new_page_info, execution_state)
    
    # Memory Operations
    def get_master_profile(self, user_id: str) -> Optional[MasterProfile]:
        """Get user's master profile"""
        return self.memory.get_master_profile(user_id)
    
    def create_execution_state(self, session_id: str, service_id: str) -> ExecutionState:
        """Create execution state"""
        return self.memory.create_execution_state(session_id, service_id)
    
    def get_execution_state(self, session_id: str) -> Optional[ExecutionState]:
        """Get execution state"""
        return self.memory.get_execution_state(session_id)
    
    def save_checkpoint(self, session_id: str, step_id: str, step_data: Dict):
        """Save checkpoint"""
        self.memory.pause_execution(session_id, step_id, step_data)
    
    def restore_checkpoint(self, session_id: str) -> Optional[Dict]:
        """Restore from checkpoint"""
        return self.memory.resume_execution(session_id)
    
    # Perception Operations
    async def analyze_page(self, page) -> PageMetadata:
        """Analyze page structure"""
        return await self.perception.analyze_page(page)
    
    # Decision Operations
    def decide_action(
        self,
        field_metadata: Any,
        page_metadata: PageMetadata,
        execution_state: ExecutionState
    ) -> ActionDecision:
        """Decide action strategy"""
        return self.decision.decide_action_strategy(
            field_metadata,
            page_metadata,
            execution_state,
            self.memory.experience_memory
        )
    
    def diagnose_failure(
        self,
        error: Exception,
        action_context: Dict,
        page_metadata: PageMetadata
    ):
        """Diagnose failure"""
        return self.decision.diagnose_failure(error, action_context, page_metadata)
    
    def choose_recovery(
        self,
        diagnosis: Any,
        retry_count: int
    ) -> Optional[Any]:
        """Choose recovery strategy"""
        return self.decision.choose_recovery_strategy(
            diagnosis,
            self.memory.experience_memory,
            retry_count
        )
    
    # Learning Operations
    def learn_success(self, field_type: str, selector: str, context: Dict):
        """Learn from success"""
        self.memory.learn_selector_success(field_type, selector, context)
    
    def learn_failure(self, field_type: str, selector: str):
        """Learn from failure"""
        self.memory.learn_selector_failure(field_type, selector)
    
    def learn_recovery(self, error_type: str, strategy: str, success: bool):
        """Learn from recovery"""
        self.memory.learn_recovery(error_type, strategy, success)
    
    # Complete Workflow
    async def process_execution_step(
        self,
        page,
        session_id: str,
        roadmap: ExecutionRoadmap,
        execution_state: ExecutionState,
        master_profile: MasterProfile,
        service_config: Dict
    ) -> Dict[str, Any]:
        """
        Process a single execution step using all brain layers
        
        Returns:
            Dict with step result
        """
        # Get current step
        current_step = roadmap.get_current_step()
        if not current_step:
            return {"success": False, "message": "No more steps"}
        
        # Analyze page
        page_metadata = await self.analyze_page(page)
        
        # Update execution state
        execution_state.current_url = page_metadata.url
        execution_state.current_page_type = page_metadata.page_type.value
        
        # Find field for current step
        field_metadata = None
        for field in page_metadata.fields:
            if field.semantic_meaning == current_step.step_id or \
               current_step.step_name.lower() in field.label.lower():
                field_metadata = field
                break
        
        if not field_metadata:
            return {
                "success": False,
                "message": f"Field not found for step: {current_step.step_name}"
            }
        
        # Decide action strategy
        action_decision = self.decide_action(field_metadata, page_metadata, execution_state)
        
        # Get value for field
        from core.execution.field_mapper import FieldMapper
        field_mapper = FieldMapper(self.memory)
        field_mappings = field_mapper.map_fields_to_data(
            [field_metadata],
            master_profile,
            service_config
        )
        
        value = field_mappings.get(field_metadata.field_id, {}).get("value")
        if not value:
            return {
                "success": False,
                "message": f"No value found for field: {field_metadata.semantic_meaning}",
                "requires_user": True
            }
        
        # Execute action
        from core.execution.action_executor import ActionExecutor
        action_executor = ActionExecutor(self.decision, self.memory)
        
        success, error = await action_executor.execute_action(
            page,
            field_metadata,
            value,
            action_decision,
            page_metadata
        )
        
        if success:
            # Mark step as completed
            roadmap.mark_completed(current_step.step_id)
            execution_state.completed_steps.append(current_step.step_id)
            execution_state.filled_fields[field_metadata.field_id] = value
            
            # Learn from success
            self.learn_success(
                field_metadata.field_type.value,
                action_decision.selector,
                {"label": field_metadata.label}
            )
            
            return {
                "success": True,
                "step_id": current_step.step_id,
                "message": f"Completed: {current_step.step_name}"
            }
        else:
            # Mark step as failed
            roadmap.mark_failed(current_step.step_id)
            
            # Learn from failure
            self.learn_failure(
                field_metadata.field_type.value,
                action_decision.selector
            )
            
            return {
                "success": False,
                "step_id": current_step.step_id,
                "message": error or "Action failed",
                "error": error
            }

