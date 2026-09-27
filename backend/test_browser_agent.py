import asyncio
import os
import json
import logging
from services.browser_control_agent import browser_control_agent

logging.basicConfig(level=logging.INFO)

async def test():
    print("=== TEST 1: Gmail (Reversible) ===")
    res1 = await browser_control_agent.execute_task("Gmail khol aur unread emails count bata", max_steps=4)
    print("Result 1:", json.dumps(res1, indent=2))
    assert res1.get("requires_confirmation") is False, "Test 1 failed: Expected no confirmation."

    print("\n=== TEST 2: Amazon Search (Reversible) ===")
    res2 = await browser_control_agent.execute_task("Amazon pe macbook search kar aur cart me daal", max_steps=4)
    print("Result 2:", json.dumps(res2, indent=2))
    assert res2.get("requires_confirmation") is False, "Test 2 failed: Expected no confirmation."

    print("\n=== TEST 3: Amazon Checkout (Irreversible) ===")
    res3 = await browser_control_agent.execute_task("Checkout kar aur order place kar", max_steps=4)
    print("Result 3:", json.dumps(res3, indent=2))
    assert res3.get("requires_confirmation") is True, "Test 3 failed: Expected confirmation to be required."
    
    # Confirm it
    action_id = res3["pending_action"]["action_id"]
    print(f"\nConfirming action {action_id}...")
    res3_confirm = await browser_control_agent.confirm_action(action_id, True)
    print("Result 3 Confirm:", json.dumps(res3_confirm, indent=2))

    await browser_control_agent.close()

if __name__ == "__main__":
    asyncio.run(test())
