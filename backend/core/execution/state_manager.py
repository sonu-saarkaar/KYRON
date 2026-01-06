"""
KYRON Execution Engine - StateManager

Maintains full execution memory
Restores flow after pause, refresh, or interruption
"""

from typing import Dict, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

class StateManager:
    """
    Manages execution state persistence and restoration
    """
    
    def __init__(self, memory_layer):
        self.memory_layer = memory_layer
    
    def save_state(self, session_id: str, execution_state: Any, roadmap: Any):
        """Save complete execution state"""
        try:
            # Save execution state
            self.memory_layer.save_execution_state(session_id, execution_state)
            
            # Save roadmap
            if hasattr(self.memory_layer, 'save_roadmap'):
                self.memory_layer.save_roadmap(session_id, roadmap)
            
            logger.debug(f"State saved for session {session_id}")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def restore_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Restore execution state"""
        try:
            execution_state = self.memory_layer.get_execution_state(session_id)
            if not execution_state:
                return None
            
            roadmap = None
            if hasattr(self.memory_layer, 'get_roadmap'):
                roadmap = self.memory_layer.get_roadmap(session_id)
            
            return {
                "execution_state": execution_state,
                "roadmap": roadmap
            }
        except Exception as e:
            logger.error(f"Error restoring state: {e}")
            return None
    
    def create_checkpoint(self, session_id: str, step_id: str, step_data: Dict):
        """Create a checkpoint for pause/resume"""
        self.memory_layer.pause_execution(session_id, step_id, step_data)
        logger.info(f"Checkpoint created at step {step_id}")
    
    def restore_from_checkpoint(self, session_id: str) -> Optional[Dict]:
        """Restore from checkpoint"""
        checkpoint = self.memory_layer.resume_execution(session_id)
        if checkpoint:
            logger.info(f"Restored from checkpoint: step {checkpoint.get('step_id')}")
        return checkpoint

