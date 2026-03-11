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
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error: {e}"


def test_connectivity():
    """Test network connectivity"""

    print("=" * 60)
    print("Testing Network Connectivity")
    print("=" * 60)

    # Determine ping command based on OS
    is_windows = platform.system().lower() == "windows"
    ping_count = "-n 2" if is_windows else "-c 2"

    # Test 1: Ping R1
    print("\n[1] Testing connectivity to R1 (192.168.242.129)...")
    print("=" * 60)
    output = run_command(f"ping {ping_count} 192.168.242.129")
    print(output)

    if "TTL=" in output or "ttl=" in output:
        print("[OK] R1 is reachable!")
    else:
        print("[FAIL] Cannot reach R1")
        print("[WARN] This is a critical issue - MCP server needs R1 access")
        return False

    # Test 2: Ping R2
    print("\n[2] Testing connectivity to R2 (10.1.1.2)...")
    print("=" * 60)
    output = run_command(f"ping {ping_count} 10.1.1.2")
    print(output)

    if "TTL=" in output or "ttl=" in output:
        print("[OK] R2 is reachable!")
        r2_reachable = True
    else:
        print("[FAIL] Cannot reach R2")
        print("[WARN] This needs to be fixed for 2-router topology")
        r2_reachable = False

    # Test 3: Check routing table
    print("\n[3] Checking Windows routing table...")
    print("=" * 60)
    if is_windows:
        output = run_command("route print | findstr 10.1.1")
    else:
        output = run_command("ip route | grep 10.1.1")

    if output.strip():
        print("[OK] Route to 10.1.1.0/24 exists:")
        print(output)
    else:
        print("[FAIL] No route to 10.1.1.0/24 found")
        print("\nFIX: Add route with this command:")
        if is_windows:
            print("   route add 10.1.1.0 mask 255.255.255.0 192.168.242.129")
        else:
            print("   sudo ip route add 10.1.1.0/24 via 192.168.242.129")

    # Test 4: Traceroute to R2
    if not r2_reachable:
        print("\n[4] Traceroute to R2 (to diagnose where packets are lost)...")
        print("=" * 60)
        if is_windows:
            output = run_command("tracert -d -h 3 10.1.1.2")
        else:
            output = run_command("traceroute -n -m 3 10.1.1.2")
        print(output)

        if "192.168.242.129" in output:
            print("\nANALYSIS:")
            print("   [OK] Packets reach R1 (192.168.242.129)")
            print("   [FAIL] R1 is not forwarding to R2")
            print("\nFIX: Enable Proxy ARP on R1:")
            print("   python fix_r1_forwarding.py")
        else:
            print("\nANALYSIS:")
            print("   [FAIL] Packets don't even reach R1")
            print("   [WARN] Problem with Windows routing or firewall")

    # Summary
    print("\n" + "=" * 60)
    print("CONNECTIVITY SUMMARY")
    print("=" * 60)
    r1_status = "[OK]" if True else "[FAIL]"
    r2_status = "[OK]" if r2_reachable else "[FAIL]"
    print(f"R1 (192.168.242.129): {r1_status}")
    print(f"R2 (10.1.1.2):        {r2_status}")

    if r2_reachable:
        print("\nAll tests passed!")
        print("\nNext step:")
        print("   Update config.py and test MCP connection:")
        print("   python test_jumphost.py")
    else:
        print("\nR2 NOT REACHABLE")
        print("\nRecommended fix:")
        print("   1. Run: python fix_r1_forwarding.py")
        print("   2. Test again: python test_connectivity.py")

    print("=" * 60)

    return r2_reachable


if __name__ == "__main__":
    test_connectivity()
