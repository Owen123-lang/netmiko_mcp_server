"""
Configure Interface Tool - Zero-Touch Configuration
Allows LLM to configure IP addresses on router interfaces
"""

from netmiko_connector import CiscoDeviceConnector
from config import DEVICES
import logging

logger = logging.getLogger(__name__)


def configure_interface(device_name: str, interface_name: str, ip_address: str, subnet_mask: str, description: str = None) -> dict:
    """
    Configure IP address on a network interface
    
    Args:
        device_name: Router name (R1 or R2)
        interface_name: Interface to configure (e.g., 'FastEthernet0/0')
        ip_address: IP address to assign (e.g., '10.1.1.1')
        subnet_mask: Subnet mask (e.g., '255.255.255.0')
        description: Optional interface description
        
    Returns:
        dict: Configuration result with success status and output
    """
    try:
        # Validate device exists
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found. Available devices: {list(DEVICES.keys())}"
            }
        
        device_config = DEVICES[device_name]
        
        # Build configuration commands
        config_commands = [
            f"interface {interface_name}",
        ]
        
        if description:
            config_commands.append(f"description {description}")
        
        config_commands.extend([
            f"ip address {ip_address} {subnet_mask}",
            "no shutdown",
        ])
        
        logger.info(f"Configuring {interface_name} on {device_name} with IP {ip_address}/{subnet_mask}")
        
        # Execute configuration
        with CiscoDeviceConnector(device_config) as connector:
            output = connector.execute_config_commands(config_commands)
            
            if output is None:
                return {
                    "success": False,
                    "error": "Failed to execute configuration commands"
                }
            
            # Verify configuration
            verify_output = connector.execute_command(f"show ip interface brief | include {interface_name}")
            
            return {
                "success": True,
                "message": f"Interface {interface_name} configured successfully on {device_name}",
                "device": device_name,
                "interface": interface_name,
                "ip_address": ip_address,
                "subnet_mask": subnet_mask,
                "config_output": output,
                "verification": verify_output,
                "commands": config_commands
            }
            
    except Exception as e:
        logger.error(f"Error configuring interface: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def configure_default_gateway(device_name: str, gateway_ip: str) -> dict:
    """
    Configure default gateway (static route) on a device
    
    Args:
        device_name: Router name (R1 or R2)
        gateway_ip: Default gateway IP address
        
    Returns:
        dict: Configuration result
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        config_commands = [
            f"ip route 0.0.0.0 0.0.0.0 {gateway_ip}"
        ]
        
        logger.info(f"Configuring default gateway {gateway_ip} on {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            output = connector.execute_config_commands(config_commands)
            
            if output is None:
                return {
                    "success": False,
                    "error": "Failed to execute configuration"
                }
            
            # Verify
            verify_output = connector.execute_command("show ip route static")
            
            return {
                "success": True,
                "message": f"Default gateway configured on {device_name}",
                "device": device_name,
                "gateway": gateway_ip,
                "config_output": output,
                "verification": verify_output
            }
            
    except Exception as e:
        logger.error(f"Error configuring default gateway: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def configure_dns(device_name: str, dns_server: str = "8.8.8.8") -> dict:
    """
    Configure DNS server on a device
    
    Args:
        device_name: Router name (R1 or R2)
        dns_server: DNS server IP address (default: Google DNS 8.8.8.8)
        
    Returns:
        dict: Configuration result
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        config_commands = [
            "ip domain-lookup",
            f"ip name-server {dns_server}"
        ]
        
        logger.info(f"Configuring DNS server {dns_server} on {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            output = connector.execute_config_commands(config_commands)
            
            if output is None:
                return {
                    "success": False,
                    "error": "Failed to execute configuration"
                }
            
            return {
                "success": True,
                "message": f"DNS configured on {device_name}",
                "device": device_name,
                "dns_server": dns_server,
                "config_output": output
            }
            
    except Exception as e:
        logger.error(f"Error configuring DNS: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }