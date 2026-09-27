"""
Integration Test Suite for KYRON CodeAgent (OpenHands Selective Port).

Tests:
1. Sandboxing Wrapper:
   - Verifies command execution and output capture.
   - Verifies path traversal protection (rejects paths escaping sandbox).
2. BookMyGaadi Bug Detection & Baseline Failure:
   - Sets up buggy vehicle rental pricing calculator.
   - Verifies test runner detects failure (exit_code != 0).
3. Autonomous ReAct Fix & Self-Correction Loop:
   - CodeAgent observes failing test output.
   - Synthesizes root cause fix.
   - Applies patch in sandbox.
   - Re-runs test until verified 100% green.
4. REST API Endpoint:
   - Verifies /api/kyron/code-agent/status and /api/kyron/code-agent/run.
"""

import os
import sys
import shutil
import pytest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.code_agent import CodeAgent, SandboxEnvironment, CodeAgentRunResult
from services.llm_client import LLMClient
from routes.code_agent import get_code_agent_status, run_code_agent, RunCodeAgentRequest


class MockBookMyGaadiNIMClient:
    """Mock NIM client simulating intelligent ReAct bug diagnosis for deterministic testing."""

    def __init__(self):
        self.provider = "nvidia"
        self.default_model = "nvidia/llama-3.1-nemotron-70b-instruct"
        self.nvidia_api_key = "mock_key"
        self.call_count = 0

    def complete(self, messages, **kwargs):
        self.call_count += 1
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")

        # Simulate ReAct reasoning on the BookMyGaadi failure trace
        thought = (
            "The failure trace indicates 'discount_amount is 10.0, expected 2000.0'. "
            "In pricing_calculator.py, discount_amount is set to discount_pct directly, "
            "which treats a 10% discount as flat 10 rupees instead of base * (discount_pct / 100.0). "
            "I will fix discount_amount to base * (discount_pct / 100.0)."
        )

        fixed_code = '''def calculate_rental_price(daily_rate: float, days: int, discount_pct: float = 0.0, gst_pct: float = 18.0) -> dict:
    base = daily_rate * days
    discount_amount = base * (discount_pct / 100.0)
    taxable = base - discount_amount
    gst_amount = taxable * (gst_pct / 100.0)
    total = round(taxable + gst_amount, 2)
    return {
        "base_price": base,
        "discount_amount": discount_amount,
        "taxable_amount": taxable,
        "gst_amount": gst_amount,
        "total_amount": total
    }
'''
        return {
            "success": True,
            "content": f"### THOUGHT:\n{thought}\n\n```python\n{fixed_code}\n```",
        }


def setup_bookmygaadi_sandbox(sandbox_dir: Path):
    """Create a realistic BookMyGaadi repository sandbox with a pricing bug."""
    if sandbox_dir.exists():
        shutil.rmtree(sandbox_dir, ignore_errors=True)
    sandbox_dir.mkdir(parents=True, exist_ok=True)

    # 1. Buggy code: discount_pct is subtracted directly instead of percentage calculation
    buggy_code = '''"""BookMyGaadi Vehicle Rental Pricing Calculator."""

def calculate_rental_price(daily_rate: float, days: int, discount_pct: float = 0.0, gst_pct: float = 18.0) -> dict:
    base = daily_rate * days
    # BUG: Flat discount instead of percentage calculation!
    discount_amount = discount_pct
    taxable = base - discount_amount
    gst_amount = taxable * (gst_pct / 100.0)
    total = round(taxable + gst_amount, 2)
    return {
        "base_price": base,
        "discount_amount": discount_amount,
        "taxable_amount": taxable,
        "gst_amount": gst_amount,
        "total_amount": total
    }
'''
    (sandbox_dir / "pricing_calculator.py").write_text(buggy_code, encoding="utf-8")

    # 2. Strict test suite
    test_code = '''import sys
from pricing_calculator import calculate_rental_price

def run_tests():
    # 10 days @ 2000/day = 20,000 base. 10% discount = 2,000. Taxable = 18,000. 18% GST = 3,240. Total = 21,240.
    res = calculate_rental_price(daily_rate=2000.0, days=10, discount_pct=10.0, gst_pct=18.0)
    expected_discount = 2000.0
    expected_total = 21240.0
    if res["discount_amount"] != expected_discount:
        print(f"FAILED: discount_amount is {res['discount_amount']}, expected {expected_discount}")
        sys.exit(1)
    if res["total_amount"] != expected_total:
        print(f"FAILED: total_amount is {res['total_amount']}, expected {expected_total}")
        sys.exit(1)
    print("PASS: BookMyGaadi pricing calculation verified 100%!")
    sys.exit(0)

if __name__ == "__main__":
    run_tests()
'''
    (sandbox_dir / "test_pricing.py").write_text(test_code, encoding="utf-8")


def test_sandboxing_security_and_execution():
    print("\n--- [TEST 1] Sandboxing Wrapper: Security & Isolation ---")
    test_dir = backend_dir / "storage" / "test_sandbox_sec"
    test_dir.mkdir(parents=True, exist_ok=True)
    sandbox = SandboxEnvironment(workspace_dir=test_dir, use_docker_if_available=False)

    # 1. Test basic write and read
    sandbox.write_file("hello.txt", "Hello KYRON Sandbox")
    assert sandbox.read_file("hello.txt") == "Hello KYRON Sandbox"
    print(" [PASS] Sandbox file read/write operational.")

    # 2. Path traversal security check
    traversal_blocked = False
    try:
        sandbox.resolve_path("../../windows/system32/cmd.exe")
    except ValueError as e:
        traversal_blocked = True
        print(f" [PASS] Path traversal attempt blocked: {e}")
    assert traversal_blocked, "Sandbox allowed path traversal outside workspace!"

    # 3. Command execution in sandbox
    res = sandbox.execute_command("python -c 'print(40 + 2)'")
    assert res["exit_code"] == 0
    assert "42" in res["output"]
    print(" [PASS] Sandboxed python command executed successfully.")


def test_bookmygaadi_bug_fix_and_verification():
    print("\n--- [TEST 2] BookMyGaadi Real Bug Diagnosis, Repair & Verification ---")
    sandbox_dir = backend_dir / "storage" / "test_bookmygaadi_sandbox"
    setup_bookmygaadi_sandbox(sandbox_dir)

    mock_nim = MockBookMyGaadiNIMClient()
    agent = CodeAgent(
        workspace_dir=sandbox_dir,
        client=mock_nim,
        max_iterations=3,
        use_docker=False,
    )

    # Verify baseline failure first
    pre_test = agent.sandbox.execute_command("python test_pricing.py")
    assert pre_test["exit_code"] != 0, "Baseline test should fail before CodeAgent runs!"
    print(f" [PASS] Baseline bug detected: {pre_test['output'].strip()}")

    # Run CodeAgent ReAct repair loop with explicit apply=True
    result = agent.run_fix_loop(
        task_description="Fix BookMyGaadi discount calculation bug where discount_amount is incorrect",
        target_file="pricing_calculator.py",
        test_command="python test_pricing.py",
        diagnostic_hint="Check if discount is applied as flat amount or percentage of base price.",
        apply=True,
    )

    # Assertions
    assert result.success is True, f"CodeAgent failed to fix the bug! Summary: {result.summary}"
    assert result.applied is True
    assert result.iterations >= 1
    assert "pricing_calculator.py" in result.files_modified
    assert "PASS: BookMyGaadi pricing calculation verified 100%!" in result.final_test_output

    print(f" [PASS] CodeAgent successfully diagnosed and repaired BookMyGaadi bug in {result.iterations} iteration(s)!")
    print(f"        Summary: {result.summary}")
    print(f"        Final Test: {result.final_test_output.strip()}")


def test_code_agent_rest_endpoints():
    print("\n--- [TEST 3] CodeAgent REST API Endpoints ---")
    # 1. Test status endpoint
    status = get_code_agent_status()
    assert status["success"] is True
    assert "OpenHands" in status["agent"]
    print(f" [PASS] /api/kyron/code-agent/status OK (Provider: {status['llm_provider']}, Mode: {status['default_mode']})")

    # 2. Test run endpoint on sandbox in default DRY-RUN mode (apply=False)
    sandbox_dir = backend_dir / "storage" / "test_bookmygaadi_sandbox"
    setup_bookmygaadi_sandbox(sandbox_dir)
    original_code_before = (sandbox_dir / "pricing_calculator.py").read_text(encoding="utf-8")

    req_dry = RunCodeAgentRequest(
        task="Fix BookMyGaadi pricing bug via REST API (Dry Run)",
        target_file="pricing_calculator.py",
        test_command="python test_pricing.py",
        workspace_dir=str(sandbox_dir),
        max_iterations=3,
        apply=False,  # Default safety gate
    )

    import routes.code_agent as ca_route
    orig_llm = ca_route.llm_client
    ca_route.llm_client = MockBookMyGaadiNIMClient()

    try:
        dry_res = run_code_agent(req_dry)
        assert dry_res["success"] is True
        assert dry_res["applied"] is False, "Safety gate failed: file was marked applied in dry run!"
        assert dry_res["requires_confirmation"] is True
        assert len(dry_res["diff"]) > 0, "Diff was not generated in dry run!"
        assert "discount_amount" in dry_res["diff"]

        # CRITICAL SAFETY CHECK: Original file on disk must be UNTOUCHED!
        code_on_disk = (sandbox_dir / "pricing_calculator.py").read_text(encoding="utf-8")
        assert code_on_disk == original_code_before, "SAFETY BREACH: Disk file was modified during dry run!"
        print(" [PASS] Dry-run safety gate confirmed: Fix verified in sandbox but production file kept 100% UNTOUCHED.")
        print(f"        Unified Diff generated ({len(dry_res['diff'])} chars). Confirmation required.")

        # 3. Test explicit apply=True mode
        req_apply = RunCodeAgentRequest(
            task="Fix BookMyGaadi pricing bug via REST API (Apply Changes)",
            target_file="pricing_calculator.py",
            test_command="python test_pricing.py",
            workspace_dir=str(sandbox_dir),
            max_iterations=3,
            apply=True,  # Explicit confirmation
        )
        apply_res = run_code_agent(req_apply)
        assert apply_res["success"] is True
        assert apply_res["applied"] is True, "Apply mode failed to mark applied!"
        assert apply_res["requires_confirmation"] is False

        # Verify disk file is now updated
        updated_code = (sandbox_dir / "pricing_calculator.py").read_text(encoding="utf-8")
        assert "base * (discount_pct / 100.0)" in updated_code
        print(" [PASS] Explicit apply=true confirmed: Production file successfully patched and verified!")
    finally:
        ca_route.llm_client = orig_llm


def main():
    print("=" * 65)
    print("     KYRON - CODEAGENT (OPENHANDS PORT) INTEGRATION TEST SUITE")
    print("=" * 65)

    test_sandboxing_security_and_execution()
    test_bookmygaadi_bug_fix_and_verification()
    test_code_agent_rest_endpoints()

    print("\n" + "=" * 65)
    print("  ALL CODEAGENT TESTS + SAFETY GATES PASSED! (100% GREEN)")
    print("=" * 65)


if __name__ == "__main__":
    main()
