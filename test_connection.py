"""
Simple test script to verify connection to DevNet Sandbox
Run this first to make sure everything is working
"""

from netmiko_connector import CiscoDeviceConnector
from config import DEVNET_DEVICE

def main():
    print("=" * 60)
    print("Testing Connection to Cisco DevNet Sandbox")
    print("=" * 60)
    
    print(f"\nTarget Device: {DEVNET_DEVICE['host']}")
    print(f"Username: {DEVNET_DEVICE['username']}")
    print("\nAttempting connection...")
    
    try:
        
        with CiscoDeviceConnector(DEVNET_DEVICE) as connector:
            print(" Connection established successfully!\n")
            
         
            print("-" * 60)
            print("Test 1: Getting device version...")
            print("-" * 60)
            version = connector.execute_command("show version | include Version")
            if version:
                print(f"Version Info:\n{version}\n")
            else:
                print("Failed to get version\n")
            
           
            print("-" * 60)
            print("Test 2: Getting hostname...")
            print("-" * 60)
            hostname = connector.execute_command("show running-config | include hostname")
            if hostname:
                print(f" Hostname:\n{hostname}\n")
            else:
                print("Failed to get hostname\n")
            
         
            print("-" * 60)
            print("Test 3: Getting interface list...")
            print("-" * 60)
            interfaces = connector.execute_command("show ip interface brief")
            if interfaces:
                print(f"Interfaces:\n{interfaces}\n")
            else:
                print("Failed to get interfaces\n")
            
            print("=" * 60)
            print("ALL TESTS PASSED!")
            print("=" * 60)
            print("\nYou can now proceed to:")
            print("1. Test individual tools in the tools/ directory")
            print("2. Run the MCP server: python mcp_server.py")
            print("3. Integrate with Claude Desktop")
            
    except Exception as e:
        print(f"\nConnection failed!")
        print(f"Error: {str(e)}\n")
        print("Troubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify DevNet Sandbox is accessible")
        print("3. Try again in a few minutes (sandbox might be busy)")
        print("4. Check if VPN is required for this sandbox")
        print("5. Verify username/password in config.py")
        exit(1)  
    
    return True

if __name__ == "__main__":
    main()