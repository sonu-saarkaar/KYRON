"""
KYRON CORE BRAIN - Decision & Adaptation Layer (Reflex Brain)

Before every action:
- Evaluate page readiness
- Predict possible failure
- Choose safest execution strategy

If something fails:
- Diagnose the reason
- Choose recovery strategy
- Retry intelligently
- Learn from the failure
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ActionStrategy(Enum):
    """Execution strategies"""
    DIRECT_CLICK = "direct_click"
    JAVASCRIPT_CLICK = "javascript_click"
    DISPATCH_EVENT = "dispatch_event"
    WAIT_AND_RETRY = "wait_and_retry"
    FALLBACK_SELECTOR = "fallback_selector"
    SEMANTIC_MATCH = "semantic_match"
    MANUAL_INTERVENTION = "manual_intervention"

class FailureReason(Enum):
    """Reasons for action failure"""
    ELEMENT_NOT_FOUND = "element_not_found"
    ELEMENT_NOT_VISIBLE = "element_not_visible"
    ELEMENT_NOT_ENABLED = "element_not_enabled"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    PAGE_CHANGED = "page_changed"
    DYNAMIC_CONTENT = "dynamic_content"
    IFRAME_CONTEXT = "iframe_context"
    POPUP_BLOCKED = "popup_blocked"
    UNKNOWN = "unknown"

@dataclass
class ActionDecision:
    """Decision about how to execute an action"""
    strategy: ActionStrategy
    selector: str
    confidence: float
    reasoning: str
    fallback_strategies: List[ActionStrategy] = None
    wait_before: float = 0.0  # seconds
    wait_after: float = 0.0  # seconds
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class FailureDiagnosis:
    """Diagnosis of why an action failed"""
    reason: FailureReason
    details: str
    recovery_strategies: List[ActionStrategy]
    can_recover: bool = True
    requires_manual_intervention: bool = False

class DecisionAdaptationLayer:
    """
    KYRON's Reflex Brain - Decision & Adaptation Layer
    
    Makes intelligent decisions before actions and adapts when failures occur
    """
    
    def __init__(self, memory_layer):
        self.memory_layer = memory_layer
        self.strategy_priorities = self._initialize_strategy_priorities()
    
    def _initialize_strategy_priorities(self) -> Dict[ActionStrategy, float]:
        """Initialize strategy priority scores"""
        return {
            ActionStrategy.DIRECT_CLICK: 1.0,  # Highest priority
            ActionStrategy.JAVASCRIPT_CLICK: 0.8,
            ActionStrategy.DISPATCH_EVENT: 0.6,
            ActionStrategy.WAIT_AND_RETRY: 0.5,
            ActionStrategy.FALLBACK_SELECTOR: 0.7,
            ActionStrategy.SEMANTIC_MATCH: 0.9,
            ActionStrategy.MANUAL_INTERVENTION: 0.1  # Last resort
        }
    
    def decide_action_strategy(
        self,
        field_metadata: Any,
        page_metadata: Any,
        execution_state: Any,
        experience_memory: Any
    ) -> ActionDecision:
        """
        Decide best strategy for executing an action
        
        Args:
            field_metadata: FieldMetadata object
            page_metadata: PageMetadata object
            execution_state: Current execution state
            experience_memory: Experience memory
            
        Returns:
            ActionDecision with chosen strategy
        """
        # Check if we have experience with this field type
        experienced_selector = None
        if experience_memory:
            experienced_selector = experience_memory.get_best_selector(
                field_metadata.field_type.value,
                {"label": field_metadata.label, "name": field_metadata.name}
            )
        
        # Choose selector
        if experienced_selector:
            selector = experienced_selector
            confidence = 0.9
            reasoning = "Using selector from experience memory"
        elif field_metadata.selectors:
            selector = field_metadata.selectors[0]  # Use first selector
            confidence = field_metadata.confidence
            reasoning = f"Using primary selector with {confidence:.0%} confidence"
        else:
            selector = f'[name="{field_metadata.name}"]' if field_metadata.name else f"#{field_metadata.field_id}"
            confidence = 0.5
            reasoning = "Using fallback selector"
        
        # Choose strategy based on field type and page state
        if field_metadata.field_type.value == "button" or field_metadata.field_type.value == "submit":
            strategy = ActionStrategy.DIRECT_CLICK
        elif page_metadata.has_dynamic_content:
            strategy = ActionStrategy.WAIT_AND_RETRY
        elif field_metadata.confidence > 0.8:
            strategy = ActionStrategy.DIRECT_CLICK
        else:
            strategy = ActionStrategy.JAVASCRIPT_CLICK
        
        # Set fallback strategies
        fallback_strategies = [
            ActionStrategy.JAVASCRIPT_CLICK,
            ActionStrategy.DISPATCH_EVENT,
            ActionStrategy.FALLBACK_SELECTOR
        ]
        
        # Determine wait times
        wait_before = 0.3 if page_metadata.has_dynamic_content else 0.1
        wait_after = 0.5 if field_metadata.field_type.value in ["select", "radio"] else 0.2
        
        decision = ActionDecision(
            strategy=strategy,
            selector=selector,
            confidence=confidence,
            reasoning=reasoning,
            fallback_strategies=fallback_strategies,
            wait_before=wait_before,
            wait_after=wait_after,
            max_retries=3
        )
        
        logger.info(f"Decision: {strategy.value} on {selector} ({confidence:.0%} confidence)")
        return decision
    
    def diagnose_failure(
        self,
        error: Exception,
        action_context: Dict[str, Any],
        page_metadata: Any
    ) -> FailureDiagnosis:
        """
        Diagnose why an action failed
        
        Args:
            error: Exception that occurred
            action_context: Context of the action
            page_metadata: Current page metadata
            
        Returns:
            FailureDiagnosis with recovery strategies
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Diagnose failure reason
        if "timeout" in error_str or "waiting" in error_str:
            reason = FailureReason.TIMEOUT
            recovery_strategies = [
                ActionStrategy.WAIT_AND_RETRY,
                ActionStrategy.FALLBACK_SELECTOR
            ]
            can_recover = True
        elif "not found" in error_str or "selector" in error_str:
            reason = FailureReason.ELEMENT_NOT_FOUND
            recovery_strategies = [
                ActionStrategy.FALLBACK_SELECTOR,
                ActionStrategy.SEMANTIC_MATCH,
                ActionStrategy.WAIT_AND_RETRY
            ]
            can_recover = True
        elif "not visible" in error_str or "hidden" in error_str:
            reason = FailureReason.ELEMENT_NOT_VISIBLE
            recovery_strategies = [
                ActionStrategy.WAIT_AND_RETRY,
                ActionStrategy.JAVASCRIPT_CLICK
            ]
            can_recover = True
        elif "not enabled" in error_str or "disabled" in error_str:
            reason = FailureReason.ELEMENT_NOT_ENABLED
            recovery_strategies = [
                ActionStrategy.WAIT_AND_RETRY,
                ActionStrategy.MANUAL_INTERVENTION
            ]
            can_recover = False
            requires_manual_intervention = True
        elif "network" in error_str or "connection" in error_str:
            reason = FailureReason.NETWORK_ERROR
            recovery_strategies = [
                ActionStrategy.WAIT_AND_RETRY
            ]
            can_recover = True
        elif "iframe" in error_str or "frame" in error_str:
            reason = FailureReason.IFRAME_CONTEXT
            recovery_strategies = [
                ActionStrategy.MANUAL_INTERVENTION
            ]
            can_recover = False
            requires_manual_intervention = True
        else:
            reason = FailureReason.UNKNOWN
            recovery_strategies = [
                ActionStrategy.WAIT_AND_RETRY,
                ActionStrategy.FALLBACK_SELECTOR,
                ActionStrategy.MANUAL_INTERVENTION
            ]
            can_recover = True
        
        diagnosis = FailureDiagnosis(
            reason=reason,
            details=f"{error_type}: {error_str}",
            recovery_strategies=recovery_strategies,
            can_recover=can_recover,
            requires_manual_intervention=requires_manual_intervention
        )
        
        logger.warning(f"Failure diagnosed: {reason.value} - {diagnosis.details}")
        return diagnosis
    
    def choose_recovery_strategy(
        self,
        diagnosis: FailureDiagnosis,
        experience_memory: Any,
        retry_count: int
    ) -> Optional[ActionStrategy]:
        """
        Choose recovery strategy based on diagnosis and experience
        
        Args:
            diagnosis: Failure diagnosis
            experience_memory: Experience memory
            retry_count: Number of retries already attempted
            
        Returns:
            ActionStrategy to try next, or None if should stop
        """
        if not diagnosis.can_recover:
            return None
        
        if retry_count >= 3:
            logger.warning("Max retries reached, stopping")
            return None
        
        # Check experience memory for best recovery strategy
        if experience_memory:
            best_strategy = experience_memory.get_best_recovery_strategy(diagnosis.reason.value)
            if best_strategy:
                # Map string to ActionStrategy
                for strategy in ActionStrategy:
                    if strategy.value == best_strategy:
                        logger.info(f"Using experienced recovery strategy: {strategy.value}")
                        return strategy
        
        # Use diagnosis recovery strategies
        if diagnosis.recovery_strategies:
            # Try strategies in order
            strategy = diagnosis.recovery_strategies[0]
            logger.info(f"Using recovery strategy: {strategy.value}")
            return strategy
        
        return None
    
    def evaluate_page_readiness(self, page_metadata: Any) -> Tuple[bool, str]:
        """
        Evaluate if page is ready for action
        
        Returns:
            Tuple of (is_ready, reason)
        """
        if not page_metadata.is_loaded:
            return (False, "Page not fully loaded")
        
        if page_metadata.page_type.value == "loading":
            return (False, "Page is still loading")
        
        if page_metadata.has_dynamic_content:
            return (True, "Page has dynamic content, will wait before actions")
        
        return (True, "Page is ready")
    
    def predict_failure_risk(
        self,
        action_decision: ActionDecision,
        page_metadata: Any,
        execution_state: Any
    ) -> float:
        """
        Predict risk of action failure (0.0 to 1.0)
        
        Returns:
            Risk score (higher = more risky)
        """
        risk = 0.0
        
        # Low confidence increases risk
        risk += (1.0 - action_decision.confidence) * 0.3
        
        # Dynamic content increases risk
        if page_metadata.has_dynamic_content:
            risk += 0.2
        
        # Unknown page type increases risk
        if page_metadata.page_type.value == "unknown":
            risk += 0.2
        
        # Multiple iframes increase risk
        if len(page_metadata.iframes) > 0:
            risk += 0.1
        
        # Already failed steps increase risk
        if execution_state and len(execution_state.error_history) > 0:
            risk += min(len(execution_state.error_history) * 0.1, 0.3)
        
        return min(risk, 1.0)
    
    def should_retry(
        self,
        retry_count: int,
        diagnosis: FailureDiagnosis,
        risk_score: float
    ) -> bool:
        """
        Decide if action should be retried
        
        Returns:
            True if should retry, False otherwise
        """
        if retry_count >= 3:
            return False
        
        if not diagnosis.can_recover:
            return False
        
        if diagnosis.requires_manual_intervention:
            return False
        
        if risk_score > 0.8:  # Very high risk
            return retry_count < 2  # Only retry once
        
        return True

