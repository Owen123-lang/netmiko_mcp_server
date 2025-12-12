#!/usr/bin/env python3
"""
Check if R1 has any access-lists blocking traffic
"""

from config import ROUTER1_DEVICE
from netmiko import ConnectHandler

def check_access_lists():
    """Check R1 for access-lists and NAT configuration"""
    
    print("=" * 60)
    print("🔍 Checking R1 Access Lists and NAT")
    print("=" * 60)
    
    # Connect to R1
    print(f"\n📡 Connecting to R1 ({ROUTER1_DEVICE['host']})...")
    try:
        connection = ConnectHandler(**ROUTER1_DEVICE)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Check access-lists
    print("\n" + "=" * 60)
    print("1️⃣  Checking Access Lists...")
    print("=" * 60)
    output = connection.send_command("show access-lists")
    if output.strip():
        print(output)
        print("⚠️  Access lists found - may be blocking traffic")
    else:
        print("✅ No access lists configured")
    
    # Check NAT configuration
    print("\n" + "=" * 60)
    print("2️⃣  Checking NAT Configuration...")
    print("=" * 60)
    output = connection.send_command("show ip nat translations")
    print(output)
    
    # Check NAT statistics
    print("\n" + "=" * 60)
    print("3️⃣  Checking NAT Statistics...")
    print("=" * 60)
    output = connection.send_command("show ip nat statistics")
    print(output)
    
    # Check interface NAT assignments
    print("\n" + "=" * 60)
    print("4️⃣  Checking Interface NAT Assignments...")
    print("=" * 60)
    output = connection.send_command("show running-config | include ip nat")
    if output.strip():
        print(output)
    else:
        print("✅ No NAT configured on interfaces")
    
    # Check if there's any route-map or policy blocking
    print("\n" + "=" * 60)
    print("5️⃣  Checking Route Maps...")
    print("=" * 60)
    output = connection.send_command("show route-map")
    if output.strip() and "route-map" in output:
        print(output)
    else:
        print("✅ No route-maps configured")
    
    # Check interface configurations
    print("\n" + "=" * 60)
    print("6️⃣  Checking Interface Configurations...")
    print("=" * 60)
    output = connection.send_command("show running-config | section interface")
    print(output)
    
    # Try to ping from R1 to Windows host
    print("\n" + "=" * 60)
    print("7️⃣  Testing R1 → Windows Host Connectivity...")
    print("=" * 60)
    # Get Windows IP from routing table
    output = connection.send_command("show ip route | include 192.168.242")
    print(output)
    
    # Disconnect
    connection.disconnect()
    
    print("\n" + "=" * 60)
    print("✅ Diagnostic Complete!")
    print("=" * 60)
    
    print("\n💡 ANALYSIS:")
    print("   If NAT is configured, it may be interfering with forwarding")
    print("   If access-lists exist, they may be blocking ICMP")
    print("\n📋 NEXT STEPS:")
    print("   1. Check Windows Firewall: python check_windows_firewall.py")
    print("   2. If firewall is the issue, disable it temporarily for testing")
    print("=" * 60)

if __name__ == "__main__":
    check_access_lists()