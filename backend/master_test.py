import asyncio
import sys
import logging
from services.orchestrator import master_orchestrator
from services.approval_queue import approval_queue

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

async def run_master_test():
    print("=== STARTING MASTER ORCHESTRATOR TEST ===\n")
    
    # Mocking for stable deterministic test
    from services.code_agent import CodeAgentRunResult
    master_orchestrator.code_agent.run = lambda *args, **kwargs: CodeAgentRunResult(
        task="Find and fix the null pointer bug",
        success=True, applied=False, iterations=1, summary="Fixed null pointer exception in driver_signup.py", diff="""--- driver_signup.py
+++ driver_signup.py
@@ -10,3 +10,3 @@
-        if driver.license:
+        if driver and driver.license:
""", proposed_code="", files_modified={"driver_signup.py"}, final_test_output="", trajectory=[]
    )
    
    # Let Orchestrator use real LLM to route, but intercept the System Agent call to simulate pause
    from routes.system_control import ExecuteSystemCommandRequest
    import routes.orchestrator # just to ensure imports
    import routes.system_control
    
    # We will hook into ApprovalQueueManager.register_pending_action to auto-confirm actions
    original_register = approval_queue.register_pending_action
    def hooked_register(*args, **kwargs):
        action_id = original_register(*args, **kwargs)
        async def simulate_user_click():
            await asyncio.sleep(1)
            print(f"\n[Simulated User] Clicking 'Confirm & Execute' in UI for {action_id}...")
            approval_queue.resolve_action(action_id, "executed_confirmed")
        asyncio.create_task(simulate_user_click())
        return action_id
    approval_queue.register_pending_action = hooked_register
    
    async def mock_execute_system(req):
        if "whatsapp" in req.command.lower():
            # simulate irreversible pause
            action_id = approval_queue.register_pending_action(
                agent_type="SYSTEM",
                description=f"Send WhatsApp message: {req.command}",
                payload={"content": "BookMyGaadi driver-signup is fixed", "target_contact": "DevTeam"},
                risk_level="high"
            )
            return {"success": True, "status": "waiting_confirmation", "requires_confirmation": True, "pending_action": approval_queue.get_action(action_id), "action_id": action_id}
        return {"success": True}
        
    import services.orchestrator
    services.orchestrator.execute_system_command = mock_execute_system
    
    # User's complex multi-agent command
    command = "BookMyGaadi driver-signup (file driver_signup.py) me null pointer bug dhundh kar fix karo, aur uske baad WhatsApp par DevTeam ko 'BookMyGaadi driver-signup is fixed' message bhej do"
    
    print(f"Command: {command}\n")
    
    print("[1] Routing via Master Orchestrator...")
    # This will trigger LLM to route, which will dispatch CODE_AGENT and SYSTEM_AGENT tasks
    result = await master_orchestrator.route_command(command)
    
    print("\n=== EXECUTION RESULT ===")
    import pprint
    pprint.pprint(result)
    
    print("\n[2] Checking Unified Approval Queue for Pending Tasks...")
    pending = approval_queue.get_all_pending()
    print(f"Pending actions in queue: {len(pending)}")
    
    for action in pending:
        print(f" -> Found Pending Action (Agent: {action['agent_type']}): {action['payload'].get('description') or action['payload'].get('content')}")
        
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    asyncio.run(run_master_test())
