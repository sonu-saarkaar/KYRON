"""
KYRON Execution Engine - ActionExecutor

Performs one action at a time
Verifies success after every action
Uses fallback strategies if action fails
"""

from typing import Dict, Optional, Any, Tuple
import asyncio
import logging

logger = logging.getLogger(__name__)

class ActionExecutor:
    """
    Executes actions with verification and fallback strategies
    """
    
    def __init__(self, decision_layer, memory_layer):
        self.decision_layer = decision_layer
        self.memory_layer = memory_layer
    
    async def execute_action(
        self,
        page,
        field_metadata: Any,
        value: Any,
        action_decision: Any,
        page_metadata: Any
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute an action with fallback strategies
        
        Returns:
            Tuple of (success, error_message)
        """
        retry_count = 0
        strategies = [action_decision.strategy] + action_decision.fallback_strategies
        
        for strategy in strategies:
            if retry_count >= action_decision.max_retries:
                break
            
            try:
                # Wait before action
                if action_decision.wait_before > 0:
                    await asyncio.sleep(action_decision.wait_before)
                
                # Execute based on strategy
                success = await self._execute_strategy(
                    page,
                    field_metadata,
                    value,
                    strategy,
                    action_decision.selector
                )
                
                if success:
                    # Wait after action
                    if action_decision.wait_after > 0:
                        await asyncio.sleep(action_decision.wait_after)
                    
                    # Verify action
                    verified = await self._verify_action(page, field_metadata, value)
                    
                    if verified:
                        # Record success in experience memory
                        if self.memory_layer and hasattr(self.memory_layer, 'experience_memory'):
                            self.memory_layer.experience_memory.record_success(
                                field_metadata.field_type.value,
                                action_decision.selector,
                                {"label": field_metadata.label, "strategy": strategy.value}
                            )
                        
                        logger.info(f"Action successful: {strategy.value} on {action_decision.selector}")
                        return (True, None)
                    else:
                        logger.warning(f"Action executed but verification failed: {strategy.value}")
                
                retry_count += 1
                
            except Exception as e:
                # Diagnose failure
                diagnosis = self.decision_layer.diagnose_failure(e, {}, page_metadata)
                
                # Learn from failure
                if self.memory_layer and hasattr(self.memory_layer, 'experience_memory'):
                    self.memory_layer.experience_memory.record_failure(
                        field_metadata.field_type.value,
                        action_decision.selector
                    )
                
                # Choose recovery strategy
                recovery_strategy = self.decision_layer.choose_recovery_strategy(
                    diagnosis,
                    self.memory_layer.experience_memory if self.memory_layer else None,
                    retry_count
                )
                
                if recovery_strategy and recovery_strategy != strategy:
                    # Try recovery strategy
                    strategies.insert(0, recovery_strategy)
                    continue
                
                retry_count += 1
                if retry_count >= action_decision.max_retries:
                    logger.error(f"Action failed after retries: {e}")
                    return (False, str(e))
        
        return (False, "All strategies exhausted")
    
    async def _execute_strategy(
        self,
        page,
        field_metadata: Any,
        value: Any,
        strategy: Any,
        selector: str
    ) -> bool:
        """Execute action using specific strategy"""
        try:
            element = await page.wait_for_selector(selector, timeout=5000, state='visible')
            if not element:
                return False
            
            if strategy.value == "direct_click":
                await element.click()
                return True
            
            elif strategy.value == "javascript_click":
                await element.evaluate("el => el.click()")
                return True
            
            elif strategy.value == "dispatch_event":
                await element.dispatch_event("click")
                return True
            
            elif strategy.value == "fill_field":
                if field_metadata.field_type.value == "select":
                    await element.select_option(value)
                else:
                    await element.fill(str(value))
                return True
            
            return False
        except Exception as e:
            logger.debug(f"Strategy {strategy.value} failed: {e}")
            return False
    
    async def _verify_action(self, page, field_metadata: Any, expected_value: Any) -> bool:
        """Verify that action was successful"""
        try:
            if field_metadata.field_type.value in ["select", "radio", "checkbox"]:
                # For selects, check if value is selected
                element = await page.query_selector(f"#{field_metadata.field_id}")
                if element:
                    actual_value = await element.input_value()
                    return str(actual_value) == str(expected_value)
            else:
                # For text fields, check if value is filled
                element = await page.query_selector(f"#{field_metadata.field_id}")
                if element:
                    actual_value = await element.input_value()
                    return str(actual_value).strip() == str(expected_value).strip()
        except:
            pass
        
        return False

