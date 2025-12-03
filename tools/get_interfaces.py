"""
MCP Tool: Get Interfaces
Retrieves interface information from Cisco device
"""

from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from netmiko_connector import CiscoDeviceConnector
from config import DEVNET_DEVICE


def get_interfaces() -> Dict[str, Any]:
    """
    Get list of all interfaces and their status from the Cisco device
    
    Returns:
        dict: Contains success status, output, and any error messages
    """
    try:
        with CiscoDeviceConnector(DEVNET_DEVICE) as connector:
            # Execute 'show ip interface brief' command
            output = connector.execute_command("show ip interface brief")
            
            if output:
                return {
                    "success": True,
                    "command": "show ip interface brief",
                    "output": output,
                    "message": "Successfully retrieved interface information"
                }
            else:
                return {
                    "success": False,
                    "error": "No output received from device"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get interfaces: {str(e)}"
        }


def get_interface_detail(interface_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific interface
    
    Args:
        interface_name: Name of the interface (e.g., 'GigabitEthernet1')
        
    Returns:
        dict: Contains success status, output, and any error messages
    """
    try:
        with CiscoDeviceConnector(DEVNET_DEVICE) as connector:
            # Execute detailed show command for specific interface
            command = f"show interface {interface_name}"
            output = connector.execute_command(command)
            
            if output:
                return {
                    "success": True,
                    "command": command,
                    "interface": interface_name,
                    "output": output,
                    "message": f"Successfully retrieved details for {interface_name}"
                }
            else:
                return {
                    "success": False,
                    "error": f"No output received for interface {interface_name}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get interface details: {str(e)}"
        }


# Test function for standalone execution
if __name__ == "__main__":
    print("Testing get_interfaces tool...")
    print("=" * 50)
    
    result = get_interfaces()
    
    if result["success"]:
        print("✅ SUCCESS")
        print(f"\nCommand: {result['command']}")
        print(f"\nOutput:\n{result['output']}")
    else:
        print("❌ FAILED")
        print(f"Error: {result['error']}")