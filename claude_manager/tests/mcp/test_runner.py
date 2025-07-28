#!/usr/bin/env python3
"""Quick test runner for MCP tests."""
import sys
import subprocess
from pathlib import Path


def run_mcp_tests():
    """Run all MCP tests and display results."""
    test_dir = Path(__file__).parent
    
    print("🧪 Running MCP Test Suite\n")
    print("=" * 60)
    
    # Test categories
    test_categories = [
        ("Unit Tests - Models", "unit/test_mcp_models.py"),
        ("Unit Tests - Config", "unit/test_mcp_config.py"),
        ("Unit Tests - Mock Server", "unit/test_mock_server.py"),
        ("Unit Tests - Events", "unit/test_mcp_events.py"),
        ("Integration Tests", "integration/test_mcp_integration.py"),
        ("Workflow Tests", "workflows/test_mcp_workflows.py")
    ]
    
    total_passed = 0
    total_failed = 0
    
    for category, test_file in test_categories:
        print(f"\n📁 {category}")
        print("-" * 40)
        
        test_path = test_dir / test_file
        if not test_path.exists():
            print(f"❌ Test file not found: {test_file}")
            continue
            
        # Run pytest for this file
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--no-header"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=test_dir.parent.parent.parent  # Project root
            )
            
            # Parse output for summary
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if " PASSED" in line:
                    print(f"✅ {line.strip()}")
                    total_passed += 1
                elif " FAILED" in line:
                    print(f"❌ {line.strip()}")
                    total_failed += 1
                elif " ERROR" in line:
                    print(f"💥 {line.strip()}")
                    total_failed += 1
                    
            # Show failures if any
            if result.returncode != 0 and result.stderr:
                print(f"\n⚠️  Errors in {test_file}:")
                print(result.stderr[:500])  # First 500 chars of error
                
        except Exception as e:
            print(f"💥 Error running tests: {e}")
            total_failed += 1
            
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📈 Total:  {total_passed + total_failed}")
    
    if total_failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total_failed} tests failed!")
        
    return total_failed == 0


if __name__ == "__main__":
    success = run_mcp_tests()
    sys.exit(0 if success else 1)