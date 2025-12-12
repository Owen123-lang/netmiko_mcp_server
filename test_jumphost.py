"""
Test script for SSH Jumphost functionality
Tests connection to R2 via R1 jumphost
"""

from netmiko_connector import get_connection, cleanup_jumphost_connections
import sys


def test_r1_direct():
    """Test direct connection to R1"""
    print("="*70)
    print("TEST 1: Direct Connection to R1")
    print("="*70)
    
    try:
        print("\n📡 Connecting to R1 (192.168.242.129)...")
        connection = get_connection("R1")
        
        print("✅ Connected successfully!")
        
        # Test command
        print("\n🔍 Executing: show version | include IOS")
        output = connection.send_command("show version | include IOS")
        print(f"Output: {output[:100]}...")
        
        # Get hostname
        print("\n🔍 Executing: show running-config | include hostname")
        hostname = connection.send_command("show running-config | include hostname")
        print(f"Hostname: {hostname}")
        
        connection.disconnect()
        print("\n✅ TEST 1 PASSED: R1 direct connection works!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {str(e)}")
        return False


def test_r2_via_jumphost():
    """Test connection to R2 via R1 jumphost"""
    print("\n" + "="*70)
    print("TEST 2: Connection to R2 via R1 Jumphost")
    print("="*70)
    
    try:
        print("\n📡 Connecting to R2 (10.1.1.2) via R1 jumphost...")
        print("   (Using automatic jumphost detection)")
        
        connection = get_connection("R2")
        
        print("✅ Connected successfully!")
        
        # Test command
        print("\n🔍 Executing: show version | include IOS")
        output = connection.send_command("show version | include IOS")
        print(f"Output: {output[:100]}...")
        
        # Get hostname
        print("\n🔍 Executing: show running-config | include hostname")
        hostname = connection.send_command("show running-config | include hostname")
        print(f"Hostname: {hostname}")
        
        # Get interfaces
        print("\n🔍 Executing: show ip interface brief")
        interfaces = connection.send_command("show ip interface brief")
        print(f"Interfaces:\n{interfaces}")
        
        connection.disconnect()
        print("\n✅ TEST 2 PASSED: R2 jumphost connection works!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_r2_connections():
    """Test multiple consecutive connections to R2"""
    print("\n" + "="*70)
    print("TEST 3: Multiple R2 Connections (Jumphost Reuse)")
    print("="*70)
    
    try:
        for i in range(2):  # Reduced to 2 to avoid channel limit on old IOS
            print(f"\n📡 Connection #{i+1} to R2...")
            
            connection = get_connection("R2")
            
            hostname = connection.send_command("show running-config | include hostname")
            print(f"   ✓ Connected! Hostname: {hostname.strip()}")
            
            connection.disconnect()
        
        print("\n✅ TEST 3 PASSED: Multiple connections successful (jumphost reused)!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {str(e)}")
        return False


def test_r1_and_r2_interleaved():
    """Test alternating between R1 and R2 connections"""
    print("\n" + "="*70)
    print("TEST 4: Interleaved R1 and R2 Connections")
    print("="*70)
    
    try:
        devices = ["R1", "R2", "R1", "R2"]
        
        for device in devices:
            print(f"\n📡 Connecting to {device}...")
            
            connection = get_connection(device)
            
            hostname = connection.send_command("show running-config | include hostname")
            print(f"   ✓ {device} Hostname: {hostname.strip()}")
            
            connection.disconnect()
        
        print("\n✅ TEST 4 PASSED: Interleaved connections successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {str(e)}")
        return False


def test_r2_configuration():
    """Test configuration command on R2 via jumphost"""
    print("\n" + "="*70)
    print("TEST 5: Configuration Command on R2 via Jumphost")
    print("="*70)
    
    try:
        print("\n📡 Connecting to R2...")
        connection = get_connection("R2")
        
        print("✅ Connected!")
        
        # Test configuration command (safe - just description)
        print("\n🔧 Testing configuration command...")
        print("   Command: Configure Loopback99 description")
        
        commands = [
            "interface Loopback99",
            "description TEST-JUMPHOST-CONNECTION",
            "no shutdown",
            "exit"
        ]
        
        output = connection.send_config_set(commands)
        print(f"   Config Output: {output[:200]}...")
        
        # Verify
        print("\n🔍 Verifying configuration...")
        verify = connection.send_command("show running-config interface Loopback99")
        print(f"   Verification:\n{verify}")
        
        # Cleanup
        print("\n🧹 Cleaning up test interface...")
        connection.send_config_set(["no interface Loopback99"])
        
        connection.disconnect()
        print("\n✅ TEST 5 PASSED: Configuration via jumphost works!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all jumphost tests"""
    print("\n" + "="*70)
    print(" SSH JUMPHOST FUNCTIONALITY TEST SUITE")
    print("="*70)
    print("\nTesting MCP Server's ability to access R2 via R1 jumphost\n")
    
    tests = [
        ("R1 Direct Connection", test_r1_direct),
        ("R2 via Jumphost", test_r2_via_jumphost),
        ("Multiple R2 Connections", test_multiple_r2_connections),
        ("Interleaved R1/R2", test_r1_and_r2_interleaved),
        ("R2 Configuration", test_r2_configuration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Unexpected error in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Cleanup
    print("\n" + "="*70)
    print("CLEANUP")
    print("="*70)
    print("\n🧹 Cleaning up jumphost connections...")
    cleanup_jumphost_connections()
    print("✅ Cleanup complete")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {test_name}")
        if success:
            passed += 1
    
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{'─'*70}")
    print(f"Results: {passed}/{total} tests passed ({percentage:.0f}%)")
    print(f"{'─'*70}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n✅ SSH Jumphost is working correctly!")
        print("   • R1 direct access: OK")
        print("   • R2 via jumphost: OK")
        print("   • Jumphost reuse: OK")
        print("   • Configuration commands: OK")
        print("\n🚀 MCP Server can now access both R1 and R2!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("   Check error messages above for details")
    
    print("="*70 + "\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())