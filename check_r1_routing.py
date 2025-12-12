#!/usr/bin/env python3
"""
Check and fix R1 routing configuration
"""

from config import ROUTER1_DEVICE
from netmiko import ConnectHandler

def check_and_fix_r1():
    """Check R1 configuration and enable IP forwarding if needed"""
    
    print("=" * 60)
    print("🔍 Checking R1 Configuration...")
    print("=" * 60)
    
    # Connect to R1
    print(f"\n📡 Connecting to R1 ({ROUTER1_DEVICE['host']})...")
    try:
        connection = ConnectHandler(**ROUTER1_DEVICE)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Check interfaces
    print("\n" + "=" * 60)
    print("1️⃣  Checking Interfaces...")
    print("=" * 60)
    output = connection.send_command("show ip interface brief")
    print(output)
    
    # Check if ip routing is enabled
    print("\n" + "=" * 60)
    print("2️⃣  Checking IP Routing Status...")
    print("=" * 60)
    output = connection.send_command("show running-config | include ip routing")
    if output.strip():
        print("✅ IP routing is ENABLED")
        print(output)
    else:
        print("⚠️  IP routing is DISABLED")
        print("\n🔧 Enabling IP routing...")
        
        config_commands = [
            "ip routing"
        ]
        
        try:
            output = connection.send_config_set(config_commands)
            print(output)
            
            # Save config
            print("\n💾 Saving configuration...")
            save_output = connection.send_command("write memory")
            print(save_output)
            
            print("✅ IP routing enabled successfully!")
        except Exception as e:
            print(f"❌ Failed to enable IP routing: {e}")
    
    # Check static routes
    print("\n" + "=" * 60)
    print("3️⃣  Checking Static Routes...")
    print("=" * 60)
    output = connection.send_command("show ip route static")
    print(output)
    
    # Check if route to 10.1.1.0/24 exists
    print("\n" + "=" * 60)
    print("4️⃣  Checking Route to 10.1.1.0/24...")
    print("=" * 60)
    output = connection.send_command("show ip route 10.1.1.0")
    
    if "10.1.1.0" in output:
        print("✅ Route to 10.1.1.0/24 exists")
        print(output)
    else:
        print("⚠️  No route to 10.1.1.0/24 found")
        print("ℹ️  This network should be directly connected via an interface")
        print("ℹ️  Or you need to configure it manually in GNS3")
    
    # Check connectivity to 10.1.1.2
    print("\n" + "=" * 60)
    print("5️⃣  Testing Connectivity to R2 (10.1.1.2)...")
    print("=" * 60)
    output = connection.send_command("ping 10.1.1.2", delay_factor=2)
    print(output)
    
    if "Success rate is 100" in output or "!" in output:
        print("✅ R1 can reach R2!")
    else:
        print("❌ R1 cannot reach R2")
        print("\n⚠️  PROBLEM DETECTED:")
        print("   - R1 and R2 need to be on the same network OR")
        print("   - You need to configure an interface on R1 for 10.1.1.0/24 network")
        print("\n📋 SOLUTION OPTIONS:")
        print("   Option 1: Configure R1 interface in 10.1.1.0/24 network")
        print("             R1(config)# interface GigabitEthernet0/1")
        print("             R1(config-if)# ip address 10.1.1.1 255.255.255.0")
        print("             R1(config-if)# no shutdown")
        print("\n   Option 2: Use a different topology where both routers share a network")
    
    # Show full routing table
    print("\n" + "=" * 60)
    print("6️⃣  Full Routing Table...")
    print("=" * 60)
    output = connection.send_command("show ip route")
    print(output)
    
    # Disconnect
    connection.disconnect()
    print("\n" + "=" * 60)
    print("✅ Diagnostic Complete!")
    print("=" * 60)

if __name__ == "__main__":
    check_and_fix_r1()