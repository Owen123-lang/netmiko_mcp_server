"""
MCP Tool: Get Running Configuration
Retrieves running configuration from Cisco device
"""

from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from netmiko_connector import CiscoDeviceConnector
from config import DEVNET_DEVICE


def get_running_config(filter_keyword: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the running configuration from the device
    
    Args:
        filter_keyword: Optional keyword to filter config (e.g., 'interface', 'ip', 'router')
        
    Returns:
        dict: Contains success status, configuration, and any error messages
    """
    try:
        with CiscoDeviceConnector(DEVNET_DEVICE) as connector:
            # Build command based on filter
            if filter_keyword:
                command = f"show running-config | include {filter_keyword}"
                message = f"Successfully retrieved filtered config (keyword: {filter_keyword})"
            else:
                command = "show running-config"
                message = "Successfully retrieved full running configuration"
            
            output = connector.execute_command(command)
            
            if output:
                return {
                    "success": True,
                    "command": command,
                    "filter": filter_keyword,
                    "config": output,
                    "message": message
                }
            else:
                return {
                    "success": False,
                    "error": "No configuration received from device"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get running config: {str(e)}"
        }


def get_interface_config(interface_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific interface
    
    Args:
        interface_name: Name of the interface (e.g., 'GigabitEthernet1')
        
    Returns:
        dict: Contains success status, interface config, and any error messages
    """
    try:
        with CiscoDeviceConnector(DEVNET_DEVICE) as connector:
            # Get config for specific interface
            command = f"show running-config interface {interface_name}"
            output = connector.execute_command(command)
            
            if output:
                return {
                    "success": True,
                    "command": command,
                    "interface": interface_name,
                    "config": output,
                    "message": f"Successfully retrieved config for {interface_name}"
                }
            else:
                return {
                    "success": False,
                    "error": f"No configuration found for interface {interface_name}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get interface config: {str(e)}"
        }


def get_startup_config() -> Dict[str, Any]:
    """
    Get the startup configuration from the device
    
    Returns:
        dict: Contains success status, startup config, and any error messages
    """
    try:
        with CiscoDeviceConnector(DEVNET_DEVICE) as connector:
            command = "show startup-config"
            output = connector.execute_command(command)
            
            if output:
                return {
                    "success": True,
                    "command": command,
                    "config": output,
                    "message": "Successfully retrieved startup configuration"
                }
            else:
                return {
                    "success": False,
                    "error": "No startup configuration found"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get startup config: {str(e)}"
        }


def compare_configs() -> Dict[str, Any]:
    """
    Compare running config vs startup config
    
    Returns:
        dict: Contains success status and comparison info
    """
    try:
        with CiscoDeviceConnector(DEVNET_DEVICE) as connector:
            # Check if there are unsaved changes
            command = "show archive config differences system:running-config system:startup-config"
            output = connector.execute_command(command)
            
            if output is not None:  # Output can be empty string if no differences
                if output.strip() == "" or "No changes" in output:
                    return {
                        "success": True,
                        "command": command,
                        "has_differences": False,
                        "message": "No differences between running and startup config"
                    }
                else:
                    return {
                        "success": True,
                        "command": command,
                        "has_differences": True,
                        "differences": output,
                        "message": "Found differences between running and startup config"
                    }
            else:
                return {
                    "success": False,
                    "error": "Failed to compare configurations"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to compare configs: {str(e)}"
        }


# Test function for standalone execution
if __name__ == "__main__":
    print("Testing get_running_config tool...")
    print("=" * 50)
    
    print("\n1. Testing Filtered Config (interface)...")
    result = get_running_config(filter_keyword="interface")
    
    if result["success"]:
        print("✅ SUCCESS")
        print(f"\nCommand: {result['command']}")
        print(f"\nConfig:\n{result['config'][:500]}...")  # Print first 500 chars
    else:
        print("❌ FAILED")
        print(f"Error: {result['error']}")
    
    print("\n" + "=" * 50)
    print("\n2. Testing Interface Config...")
    interface_result = get_interface_config("GigabitEthernet1")
    
    if interface_result["success"]:
        print("✅ SUCCESS")
        print(f"\nConfig:\n{interface_result['config']}")
    else:
        print("❌ FAILED")
        print(f"Error: {interface_result['error']}")