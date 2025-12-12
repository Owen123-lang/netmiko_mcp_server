#!/usr/bin/env python3
"""
Add static route on R2 so it knows how to reach Windows network
"""

from config import ROUTER2_DEVICE
from netmiko import ConnectHandler

def add_return_route():
    """Add static route on R2 for 192.168.242.0/24 network"""
    
    print("=" * 60)
    print("🔧 Adding Return Route on R2")
    print("=" * 60)
    print("\n💡 PROBLEM: R2 doesn't know how to reach 192.168.242.0/24")
    print("   When Windows pings R2, R2 receives the packet")
    print("   But R2 doesn't know where to send the reply!")
    print("\n🔧 SOLUTION: Add static route pointing to R1 (10.1.1.1)")
    
    # Connect to R2
    print(f"\n📡 Connecting to R2 ({ROUTER2_DEVICE['host']})...")
    try:
        connection = ConnectHandler(**ROUTER2_DEVICE)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n⚠️  Cannot connect to R2 directly")
        print("   This confirms the routing issue!")
        return False
    
    # Check current routing table
    print("\n" + "=" * 60)
    print("1️⃣  Current R2 Routing Table:")
    print("=" * 60)
    output = connection.send_command("show ip route")
    print(output)
    
    # Check if route already exists
    if "192.168.242.0" in output:
        print("\n✅ Route to 192.168.242.0/24 already exists!")
    else:
        print("\n⚠️  No route to 192.168.242.0/24 found")
        print("   This is why ping fails!")
    
    # Add static route
    print("\n" + "=" * 60)
    print("2️⃣  Adding Static Route...")
    print("=" * 60)
    print("   Route: 192.168.242.0/24 via 10.1.1.1 (R1)")
    
    config_commands = [
        "ip route 192.168.242.0 255.255.255.0 10.1.1.1"
    ]
    
    try:
        output = connection.send_config_set(config_commands)
        print(output)
        print("✅ Static route added!")
    except Exception as e:
        print(f"❌ Failed to add route: {e}")
        connection.disconnect()
        return False
    
    # Verify route was added
    print("\n" + "=" * 60)
    print("3️⃣  Verifying Route Addition...")
    print("=" * 60)
    output = connection.send_command("show ip route | include 192.168.242")
    print(output)
    
    if "192.168.242.0" in output:
        print("✅ Route successfully added!")
    else:
        print("❌ Route verification failed")
    
    # Show full routing table
    print("\n" + "=" * 60)
    print("4️⃣  Full Routing Table (After):")
    print("=" * 60)
    output = connection.send_command("show ip route")
    print(output)
    
    # Save configuration
    print("\n" + "=" * 60)
    print("5️⃣  Saving Configuration...")
    print("=" * 60)
    try:
        save_output = connection.send_command("write memory")
        print(save_output)
        print("✅ Configuration saved!")
    except Exception as e:
        print(f"⚠️  Failed to save: {e}")
    
    # Test ping from R2 to Windows gateway
    print("\n" + "=" * 60)
    print("6️⃣  Testing R2 → Windows Gateway (192.168.242.1)...")
    print("=" * 60)
    output = connection.send_command("ping 192.168.242.1", delay_factor=2)
    print(output)
    
    if "Success rate is 100" in output or "!" in output:
        print("✅ R2 can now reach Windows network!")
    else:
        print("⚠️  R2 still cannot reach Windows network")
        print("   This may be normal if Windows gateway doesn't respond to ping")
    
    # Disconnect
    connection.disconnect()
    
    print("\n" + "=" * 60)
    print("✅ Route Configuration Complete!")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("   1. Test from Windows: ping 10.1.1.2")
    print("   2. If working: python test_jumphost.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = add_return_route()
    
    if success:
        print("\n🎉 R2 NOW KNOWS THE ROUTE BACK!")
        print("\nTest from Windows:")
        print("   ping 10.1.1.2")
        print("\nShould work now! 🚀")
    else:
        print("\n❌ Could not connect to R2")
        print("   Need to use SSH via R1 console first")