#!/usr/bin/env python3
"""
Fix R1 NAT configuration - remove NAT to allow proper forwarding
"""

from config import ROUTER1_DEVICE
from netmiko import ConnectHandler

def fix_nat():
    """Remove or fix NAT configuration on R1"""
    
    print("=" * 60)
    print("🔧 Fixing R1 NAT Configuration")
    print("=" * 60)
    
    # Connect to R1
    print(f"\n📡 Connecting to R1 ({ROUTER1_DEVICE['host']})...")
    try:
        connection = ConnectHandler(**ROUTER1_DEVICE)
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Show current NAT config
    print("\n" + "=" * 60)
    print("1️⃣  Current NAT Configuration:")
    print("=" * 60)
    output = connection.send_command("show running-config | section nat")
    print(output)
    
    print("\n" + "=" * 60)
    print("2️⃣  Removing NAT Configuration...")
    print("=" * 60)
    print("⚠️  NAT is interfering with ICMP forwarding")
    print("    We'll remove NAT to allow direct forwarding")
    
    # Remove NAT configuration
    config_commands = [
        "no ip nat inside source static tcp 10.1.1.2 22 192.168.242.129 2222 extendable",
        "interface FastEthernet0/0",
        "no ip nat outside",
        "interface FastEthernet0/1", 
        "no ip nat inside",
    ]
    
    try:
        output = connection.send_config_set(config_commands)
        print(output)
        print("✅ NAT configuration removed!")
    except Exception as e:
        print(f"❌ Failed to remove NAT: {e}")
        connection.disconnect()
        return False
    
    # Verify NAT is removed
    print("\n" + "=" * 60)
    print("3️⃣  Verifying NAT Removal...")
    print("=" * 60)
    output = connection.send_command("show ip nat translations")
    if output.strip():
        print("⚠️  NAT translations still exist:")
        print(output)
    else:
        print("✅ NAT completely removed!")
    
    # Save configuration
    print("\n" + "=" * 60)
    print("4️⃣  Saving Configuration...")
    print("=" * 60)
    try:
        save_output = connection.send_command("write memory")
        print(save_output)
        print("✅ Configuration saved!")
    except Exception as e:
        print(f"⚠️  Failed to save: {e}")
    
    # Test R1 to R2
    print("\n" + "=" * 60)
    print("5️⃣  Testing R1 → R2 Connectivity...")
    print("=" * 60)
    output = connection.send_command("ping 10.1.1.2", delay_factor=2)
    print(output)
    
    # Disconnect
    connection.disconnect()
    
    print("\n" + "=" * 60)
    print("✅ NAT Fix Complete!")
    print("=" * 60)
    print("\n📋 NEXT STEPS:")
    print("   1. Test from Windows: ping 10.1.1.2")
    print("   2. If working: python test_jumphost.py")
    print("   3. Update config.py R2 to use direct IP (10.1.1.2)")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will remove NAT configuration from R1")
    print("   - Static NAT for SSH (port 2222) will be removed")
    print("   - Direct routing will be enabled instead")
    print("   - R2 will be accessible via 10.1.1.2:22 (not port 2222)")
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() == "yes":
        success = fix_nat()
        if success:
            print("\n🎉 SUCCESS!")
            print("\nNow test from Windows:")
            print("   ping 10.1.1.2")
    else:
        print("Operation cancelled.")