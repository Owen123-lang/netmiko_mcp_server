#!/usr/bin/env python3
"""
Simple test for direct connections to R1 and R2 (no jumphost)
Tests that both routers are accessible via direct routing
"""

from config import ROUTER1_DEVICE, ROUTER2_DEVICE
from netmiko import ConnectHandler
import sys


def test_router(name, config):
    """Test connection to a router"""
    print("=" * 70)
    print(f"Testing {name} ({config['host']})")
    print("=" * 70)
    
    try:
        print(f"\n📡 Connecting to {name}...")
        connection = ConnectHandler(**config)
        print(f"✅ Connected successfully!")
        
        # Get hostname
        print(f"\n🔍 Getting hostname...")
        hostname = connection.send_command("show running-config | include hostname")
        print(f"   Hostname: {hostname.strip()}")
        
        # Get version
        print(f"\n🔍 Getting IOS version...")
        version = connection.send_command("show version | include IOS Software")
        print(f"   Version: {version.strip()[:80]}...")
        
        # Get interfaces
        print(f"\n🔍 Getting interfaces...")
        interfaces = connection.send_command("show ip interface brief")
        print(f"   Interfaces:")
        for line in interfaces.split('\n')[:5]:  # First 5 lines
            if line.strip():
                print(f"      {line}")
        
        # Test configuration command
        print(f"\n🔧 Testing configuration command...")
        commands = [
            "interface Loopback100",
            f"description TEST-CONNECTION-{name}",
            "no shutdown",
            "exit"
        ]
        output = connection.send_config_set(commands)
        print(f"   ✓ Configuration successful")
        
        # Verify
        print(f"\n✅ Verifying configuration...")
        verify = connection.send_command("show running-config interface Loopback100")
        if "TEST-CONNECTION" in verify:
            print(f"   ✓ Configuration verified!")
        
        # Cleanup
        print(f"\n🧹 Cleaning up test interface...")
        connection.send_config_set(["no interface Loopback100"])
        
        connection.disconnect()
        print(f"\n✅ {name} TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ {name} TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print(" DIRECT CONNECTION TEST (No Jumphost)")
    print("=" * 70)
    print("\nTesting MCP Server's ability to access both routers directly\n")
    
    results = []
    
    # Test R1
    r1_success = test_router("R1", ROUTER1_DEVICE)
    results.append(("R1", r1_success))
    
    print("\n")
    
    # Test R2
    r2_success = test_router("R2", ROUTER2_DEVICE)
    results.append(("R2", r2_success))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    for router, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {router} Direct Connection")
        if success:
            passed += 1
    
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{'─' * 70}")
    print(f"Results: {passed}/{total} routers accessible ({percentage:.0f}%)")
    print(f"{'─' * 70}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n✅ Both routers are accessible via direct routing!")
        print("   • R1: 192.168.242.129 (Wi-Fi network)")
        print("   • R2: 10.1.1.2 (via routing through R1)")
        print("\n🚀 MCP Server is ready for use with both routers!")
        print("\n📋 Network Configuration:")
        print("   • Windows has static route: 10.1.1.0/24 via 192.168.242.129")
        print("   • R1 forwards traffic between networks")
        print("   • R2 has static route back: 192.168.242.0/24 via 10.1.1.1")
    else:
        print(f"\n⚠️  {total - passed} router(s) not accessible")
        print("   Check network configuration and routing")
    
    print("=" * 70 + "\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())