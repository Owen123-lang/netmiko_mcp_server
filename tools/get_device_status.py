"""
MCP Tool: Get Device Status
Retrieves overall device status and information
"""

from typing import Dict, Any
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from netmiko_connector import CiscoDeviceConnector
from config import DEVNET_DEVICE


def get_device_status() -> Dict[str, Any]:
    """
    Get overall device status including version, uptime, and basic info
    
    Returns:
        dict: Contains success status, device information, and any error messages
    """
    try:
        with CiscoDeviceConnector(DEVNET_DEVICE) as connector:
            
            version_output = connector.execute_command("show version")
            
            
            hostname_output = connector.execute_command("show running-config | include hostname")
            
            if version_output:
                return {
                    "success": True,
                    "commands": ["show version", "show running-config | include hostname"],
                    "version_info": version_output,
                    "hostname": hostname_output.strip() if hostname_output else "Unknown",
                    "message": "Successfully retrieved device status"
                }
            else:
                return {
                    "success": False,
                    "error": "No output received from device"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get device status: {str(e)}"
        }


def get_device_uptime() -> Dict[str, Any]:
    """
    Get device uptime information
    
    Returns:
        dict: Contains success status, uptime info, and any error messages
    """
    try:
        with CiscoDeviceConnector(DEVNET_DEVICE) as connector:
            
            output = connector.execute_command("show version | include uptime")
            
            if output:
                return {
                    "success": True,
                    "command": "show version | include uptime",
                    "output": output,
                    "message": "Successfully retrieved uptime information"
                }
            else:
                return {
                    "success": False,
                    "error": "No output received from device"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get uptime: {str(e)}"
        }


def get_memory_cpu_usage() -> Dict[str, Any]:
    """
    Get CPU and memory usage information
    
    Returns:
        dict: Contains success status, resource usage info, and any error messages
    """
    try:
        with CiscoDeviceConnector(DEVNET_DEVICE) as connector:
           
            cpu_output = connector.execute_command("show processes cpu | include CPU")
            
          
            memory_output = connector.execute_command("show processes memory | include Processor")
            
            if cpu_output and memory_output:
                return {
                    "success": True,
                    "commands": ["show processes cpu", "show processes memory"],
                    "cpu_usage": cpu_output,
                    "memory_usage": memory_output,
                    "message": "Successfully retrieved resource usage"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to retrieve complete resource information"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get resource usage: {str(e)}"
        }



if __name__ == "__main__":
    print("Testing get_device_status tool...")
    print("=" * 50)
    
    print("\n1. Testing Device Status...")
    result = get_device_status()
    
    if result["success"]:
        print("✅ SUCCESS")
        print(f"\nHostname: {result['hostname']}")
        print(f"\nVersion Info:\n{result['version_info'][:300]}...")  # Print first 300 chars
    else:
        print("❌ FAILED")
        print(f"Error: {result['error']}")
    
    print("\n" + "=" * 50)
    print("\n2. Testing Device Uptime...")
    uptime_result = get_device_uptime()
    
    if uptime_result["success"]:
        print("✅ SUCCESS")
        print(f"\n{uptime_result['output']}")
    else:
        print("❌ FAILED")
        print(f"Error: {uptime_result['error']}")