#!/usr/bin/env python3
"""
Enable IP forwarding on R1 to allow Windows host to reach R2
"""

from config import ROUTER1_DEVICE
from netmiko import ConnectHandler

def enable_proxy_arp():
    """Enable Proxy ARP on R1's external interface"""
    
    print("=" * 60)
    print("🔧 Enabling IP Forwarding on R1...")
    print("=" * 60)
    
    # Connect to R1
    print(f"\n📡 Connecting to R1 ({ROUTER1_DEVICE['host']})...")
    try:
        connection = ConnectHandler(**ROUTER1_DEVICE)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Check current proxy-arp status
    print("\n" + "=" * 60)
    print("1️⃣  Checking current Proxy ARP status...")
    print("=" * 60)
    output = connection.send_command("show ip interface FastEthernet0/0 | include Proxy ARP")
    print(output)
    
    # Enable proxy-arp on Fa0/0 (external interface)
    print("\n" + "=" * 60)
    print("2️⃣  Enabling Proxy ARP on FastEthernet0/0...")
    print("=" * 60)
    
    config_commands = [
        "interface FastEthernet0/0",
        "ip proxy-arp"
    ]
    
    try:
        output = connection.send_config_set(config_commands)
        print(output)
        print("✅ Proxy ARP enabled!")
    except Exception as e:
        print(f"❌ Failed to enable Proxy ARP: {e}")
        connection.disconnect()
        return False
    
    # Verify proxy-arp is enabled
    print("\n" + "=" * 60)
    print("3️⃣  Verifying Proxy ARP status...")
    print("=" * 60)
    output = connection.send_command("show ip interface FastEthernet0/0 | include Proxy ARP")
    print(output)
    
    if "Proxy ARP is enabled" in output:
        print("✅ Verification successful!")
    else:
        print("⚠️  Proxy ARP may not be enabled properly")
    
    # Save configuration
    print("\n" + "=" * 60)
    print("4️⃣  Saving configuration...")
    print("=" * 60)
    try:
        save_output = connection.send_command("write memory")
        print(save_output)
        print("✅ Configuration saved!")
    except Exception as e:
        print(f"⚠️  Failed to save: {e}")
    
    # Test connectivity from R1 to R2
    print("\n" + "=" * 60)
    print("5️⃣  Testing R1 → R2 connectivity...")
    print("=" * 60)
    output = connection.send_command("ping 10.1.1.2", delay_factor=2)
    print(output)
    
    # Disconnect
    connection.disconnect()
    
    print("\n" + "=" * 60)
    print("✅ Configuration Complete!")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("   1. Test from Windows: ping 10.1.1.2")
    print("   2. If still failing, run: python test_connectivity.py")
    print("   3. If working, test MCP: python test_jumphost.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = enable_proxy_arp()
    if success:
        print("\n🎉 SUCCESS! Now test from Windows:")
        print("   ping 10.1.1.2")
    else:
        print("\n❌ FAILED! Check the error messages above.")