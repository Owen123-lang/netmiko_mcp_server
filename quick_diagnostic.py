#!/usr/bin/env python3
"""
Quick diagnostic to check what's happening with R2
"""

import subprocess
import platform


def run_command(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.stdout + result.stderr
    except:
        return "Command failed"


print("=" * 70)
print("QUICK DIAGNOSTIC - R2 Connection Issue")
print("=" * 70)

# Test 1: Ping R1
print("\n[1] Ping R1 (192.168.242.129)...")
output = run_command("ping -n 2 192.168.242.129")
if "TTL=" in output:
    print("   [OK] R1 is reachable")
else:
    print("   [FAIL] R1 NOT reachable")
    print(output[:200])

# Test 2: Ping R2
print("\n[2] Ping R2 (10.1.1.2)...")
output = run_command("ping -n 2 10.1.1.2")
if "TTL=" in output:
    print("   [OK] R2 is reachable via ICMP")
else:
    print("   [FAIL] R2 NOT reachable via ICMP")
    print(output[:200])

# Test 3: Check if SSH port is open on R2
print("\n[3] Testing SSH port on R2 (telnet test)...")
output = run_command(
    'powershell -Command "Test-NetConnection -ComputerName 10.1.1.2 -Port 22 -InformationLevel Quiet"'
)
if "True" in output:
    print("   [OK] Port 22 is OPEN on R2")
else:
    print("   [FAIL] Port 22 is CLOSED or FILTERED on R2")

# Test 4: Check Windows firewall
print("\n[4] Checking Windows Firewall...")
output = run_command("netsh advfirewall show allprofiles state")
if "State                                 OFF" in output:
    print("   [OK] Firewall is OFF")
elif "State                                 ON" in output:
    print("   [WARN] Firewall is ON")
else:
    print("   [UNKNOWN] Cannot determine firewall status")

# Test 5: Check routing
print("\n[5] Checking route to 10.1.1.0/24...")
output = run_command("route print | findstr 10.1.1")
if "10.1.1.0" in output:
    print("   [OK] Route exists")
    print(f"   {output.strip()}")
else:
    print("   [FAIL] Route NOT found!")

print("\n" + "=" * 70)
print("RECOMMENDATION:")
print("=" * 70)

# Provide recommendation
if "TTL=" in run_command("ping -n 1 10.1.1.2"):
    print("[OK] ICMP works but SSH fails")
    print("   -> R2's SSH service may be down")
    print("   -> Check R2 console: 'show ip ssh'")
    print("   -> Restart SSH: 'ip ssh version 2'")
else:
    print("[FAIL] Even ICMP fails")
    print("   -> Check R2 is running in GNS3")
    print("   -> Check R2 has static route back")
    print("   -> Re-run: python add_r2_return_route.py")

print("=" * 70)
