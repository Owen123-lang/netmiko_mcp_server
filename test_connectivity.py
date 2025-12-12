#!/usr/bin/env python3
"""
Test connectivity from Windows host to both routers
"""

import subprocess
import platform

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error: {e}"

def test_connectivity():
    """Test network connectivity"""
    
    print("=" * 60)
    print("🌐 Testing Network Connectivity")
    print("=" * 60)
    
    # Determine ping command based on OS
    is_windows = platform.system().lower() == "windows"
    ping_count = "-n 2" if is_windows else "-c 2"
    
    # Test 1: Ping R1
    print("\n1️⃣  Testing connectivity to R1 (192.168.242.129)...")
    print("=" * 60)
    output = run_command(f"ping {ping_count} 192.168.242.129")
    print(output)
    
    if "TTL=" in output or "ttl=" in output:
        print("✅ R1 is reachable!")
    else:
        print("❌ Cannot reach R1")
        print("⚠️  This is a critical issue - MCP server needs R1 access")
        return False
    
    # Test 2: Ping R2
    print("\n2️⃣  Testing connectivity to R2 (10.1.1.2)...")
    print("=" * 60)
    output = run_command(f"ping {ping_count} 10.1.1.2")
    print(output)
    
    if "TTL=" in output or "ttl=" in output:
        print("✅ R2 is reachable!")
        r2_reachable = True
    else:
        print("❌ Cannot reach R2")
        print("⚠️  This needs to be fixed for 2-router topology")
        r2_reachable = False
    
    # Test 3: Check routing table
    print("\n3️⃣  Checking Windows routing table...")
    print("=" * 60)
    if is_windows:
        output = run_command("route print | findstr 10.1.1")
    else:
        output = run_command("ip route | grep 10.1.1")
    
    if output.strip():
        print("✅ Route to 10.1.1.0/24 exists:")
        print(output)
    else:
        print("❌ No route to 10.1.1.0/24 found")
        print("\n💡 FIX: Add route with this command:")
        if is_windows:
            print("   route add 10.1.1.0 mask 255.255.255.0 192.168.242.129")
        else:
            print("   sudo ip route add 10.1.1.0/24 via 192.168.242.129")
    
    # Test 4: Traceroute to R2
    if not r2_reachable:
        print("\n4️⃣  Traceroute to R2 (to diagnose where packets are lost)...")
        print("=" * 60)
        if is_windows:
            output = run_command("tracert -d -h 3 10.1.1.2")
        else:
            output = run_command("traceroute -n -m 3 10.1.1.2")
        print(output)
        
        if "192.168.242.129" in output:
            print("\n💡 ANALYSIS:")
            print("   ✅ Packets reach R1 (192.168.242.129)")
            print("   ❌ R1 is not forwarding to R2")
            print("\n🔧 FIX: Enable Proxy ARP on R1:")
            print("   python fix_r1_forwarding.py")
        else:
            print("\n💡 ANALYSIS:")
            print("   ❌ Packets don't even reach R1")
            print("   ⚠️  Problem with Windows routing or firewall")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 CONNECTIVITY SUMMARY")
    print("=" * 60)
    print(f"R1 (192.168.242.129): {'✅ OK' if True else '❌ FAILED'}")
    print(f"R2 (10.1.1.2):        {'✅ OK' if r2_reachable else '❌ FAILED'}")
    
    if r2_reachable:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📋 NEXT STEP:")
        print("   Update config.py and test MCP connection:")
        print("   python test_jumphost.py")
    else:
        print("\n⚠️  R2 NOT REACHABLE")
        print("\n📋 RECOMMENDED FIX:")
        print("   1. Run: python fix_r1_forwarding.py")
        print("   2. Test again: python test_connectivity.py")
    
    print("=" * 60)
    
    return r2_reachable

if __name__ == "__main__":
    test_connectivity()