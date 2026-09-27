import asyncio
import time
from services.coding_orchestrator import coding_orchestrator
from services.approval_queue import approval_queue

async def run_test():
    print("=== MUNDER DIFFLIN TEST ===")
    
    # 1. Connect Project
    res = coding_orchestrator.connect_project("c:/Users/pandi/Desktop/KYRON")
    print(f"Connected: {res}")
    
    # 2. Dispatch Task 1 (CodeAgent)
    t1 = await coding_orchestrator.dispatch_task("Fix bug in backend", "CodeAgent")
    print(f"Task 1 (CodeAgent) Dispatched: {t1}")
    
    # 3. Dispatch Task 2 (opencode)
    t2 = await coding_orchestrator.dispatch_task("Refactor frontend", "opencode")
    print(f"Task 2 (Opencode) Dispatched: {t2}")
    
    # Give workers time to hit the safety gate
    print("Waiting for workers to hit safety gate (6s)...")
    await asyncio.sleep(6)
    
    # Check unified queue
    pending = approval_queue.get_all_pending()
    print(f"\nPending Approvals: {len(pending)}")
    for p in pending:
        source = p['payload'].get('source', 'UNKNOWN')
        print(f" - Action ID: {p['action_id']} | Source: {source} | Status: {p['status']}")
        # Automatically confirm
        approval_queue.resolve_action(p['action_id'], 'executed_confirmed')
        print(f"   -> Confirmed action {p['action_id']}")
        
    # Wait for workers to complete
    await asyncio.sleep(2)
    
    print("\nFinal Worker States:")
    for w_id, w in coding_orchestrator.workers.items():
        print(f" - {w_id} ({w.backend}): {w.status}")
        
    print("\nTest completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_test())
