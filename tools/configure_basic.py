"""
Basic Configuration Tools - Simple demos for Zero-Touch Configuration
Tools for hostname, description, loopback - demonstrating Context-Aware behavior
"""

from netmiko_connector import CiscoDeviceConnector
from config import DEVICES
import logging

logger = logging.getLogger(__name__)


def get_hostname(device_name: str) -> dict:
    """
    Get current hostname from device
    
    Args:
        device_name: Router name (R1 or R2)
        
    Returns:
        dict: Current hostname information
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Getting hostname from {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            output = connector.execute_command("show running-config | include hostname")
            
            if output:
                hostname = output.split()[-1] if output.split() else "Unknown"
                
                return {
                    "success": True,
                    "device": device_name,
                    "hostname": hostname,
                    "output": output.strip()
                }
            else:
                return {
                    "success": False,
                    "error": "Could not retrieve hostname"
                }
                
    except Exception as e:
        logger.error(f"Error getting hostname: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def change_hostname(device_name: str, new_hostname: str) -> dict:
    """
    Change device hostname with context-aware safety check
    
    Args:
        device_name: Router name (R1 or R2)
        new_hostname: New hostname to set
        
    Returns:
        dict: Result of hostname change with before/after state
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Changing hostname on {device_name} to {new_hostname}")
        
        with CiscoDeviceConnector(device_config) as connector:
            # Context-Aware: Check current hostname first
            current_output = connector.execute_command("show running-config | include hostname")
            current_hostname = current_output.split()[-1] if current_output.split() else "Unknown"
            
            # Safety Check: Already configured?
            if current_hostname == new_hostname:
                return {
                    "success": True,
                    "device": device_name,
                    "message": f"Hostname already set to '{new_hostname}'. No change needed.",
                    "current_hostname": current_hostname,
                    "new_hostname": new_hostname,
                    "changed": False
                }
            
            # Apply configuration
            commands = [f"hostname {new_hostname}"]
            output = connector.execute_config_commands(commands)
            
            # Verify change
            verify_output = connector.execute_command("show running-config | include hostname")
            verify_hostname = verify_output.split()[-1] if verify_output.split() else "Unknown"
            
            success = (verify_hostname == new_hostname)
            
            return {
                "success": success,
                "device": device_name,
                "message": f"Hostname changed from '{current_hostname}' to '{new_hostname}'",
                "before_hostname": current_hostname,
                "after_hostname": verify_hostname,
                "changed": True,
                "config_output": output,
                "verification": verify_output.strip()
            }
            
    except Exception as e:
        logger.error(f"Error changing hostname: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def configure_interface_description(device_name: str, interface_name: str, description: str) -> dict:
    """
    Configure description on interface with context check
    
    Args:
        device_name: Router name (R1 or R2)
        interface_name: Interface name (e.g., 'FastEthernet0/1', 'Loopback0')
        description: Description text
        
    Returns:
        dict: Configuration result with before/after state
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Configuring description on {interface_name} of {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            # Context-Aware: Check if interface exists
            brief = connector.execute_command("show ip interface brief")
            
            if interface_name not in brief:
                return {
                    "success": False,
                    "error": f"Interface '{interface_name}' not found on {device_name}",
                    "available_interfaces": brief
                }
            
            # Get current description
            current_desc = connector.execute_command(
                f"show running-config interface {interface_name} | include description"
            )
            
            # Apply configuration
            commands = [
                f"interface {interface_name}",
                f"description {description}"
            ]
            output = connector.execute_config_commands(commands)
            
            # Verify
            new_desc = connector.execute_command(
                f"show running-config interface {interface_name} | include description"
            )
            
            success = (description in new_desc)
            
            return {
                "success": success,
                "device": device_name,
                "interface": interface_name,
                "message": f"Description configured on {interface_name}",
                "before_description": current_desc.strip() if current_desc.strip() else "(none)",
                "after_description": new_desc.strip(),
                "config_output": output
            }
            
    except Exception as e:
        logger.error(f"Error configuring description: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def create_loopback(device_name: str, loopback_number: int, ip_address: str, description: str = None) -> dict:
    """
    Create loopback interface with safety check against duplicates
    
    Args:
        device_name: Router name (R1 or R2)
        loopback_number: Loopback number (0-2147483647)
        ip_address: IP address for loopback (e.g., '1.1.1.1')
        description: Optional description
        
    Returns:
        dict: Creation result with safety check information
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        interface_name = f"Loopback{loopback_number}"
        
        logger.info(f"Creating {interface_name} on {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            # Safety Check: Does loopback already exist?
            check = connector.execute_command("show ip interface brief")
            
            if interface_name in check:
                # Get existing config
                existing_config = connector.execute_command(
                    f"show running-config interface {interface_name}"
                )
                
                return {
                    "success": False,
                    "device": device_name,
                    "error": f"{interface_name} already exists!",
                    "message": "SAFETY CHECK PREVENTED duplicate creation",
                    "existing_interface": interface_name,
                    "existing_config": existing_config,
                    "safety_check": "PASS - Prevented conflict"
                }
            
            # Create loopback
            commands = [
                f"interface {interface_name}",
                f"ip address {ip_address} 255.255.255.255",
                "no shutdown"
            ]
            
            if description:
                commands.insert(2, f"description {description}")
            
            output = connector.execute_config_commands(commands)
            
            # Verify creation
            verify_brief = connector.execute_command("show ip interface brief | include Loopback")
            verify_config = connector.execute_command(f"show running-config interface {interface_name}")
            
            success = (interface_name in verify_brief)
            
            return {
                "success": success,
                "device": device_name,
                "message": f"{interface_name} created successfully",
                "interface": interface_name,
                "ip_address": ip_address,
                "description": description,
                "config_output": output,
                "verification_brief": verify_brief.strip(),
                "verification_config": verify_config,
                "safety_check": "PASS - No conflict detected"
            }
            
    except Exception as e:
        logger.error(f"Error creating loopback: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def delete_loopback(device_name: str, loopback_number: int) -> dict:
    """
    Delete loopback interface with existence check
    
    Args:
        device_name: Router name (R1 or R2)
        loopback_number: Loopback number to delete
        
    Returns:
        dict: Deletion result
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        interface_name = f"Loopback{loopback_number}"
        
        logger.info(f"Deleting {interface_name} on {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            # Check if loopback exists
            check = connector.execute_command("show ip interface brief")
            
            if interface_name not in check:
                return {
                    "success": False,
                    "device": device_name,
                    "error": f"{interface_name} does not exist",
                    "message": "Nothing to delete"
                }
            
            # Delete loopback
            commands = [f"no interface {interface_name}"]
            output = connector.execute_config_commands(commands)
            
            # Verify deletion
            verify = connector.execute_command("show ip interface brief | include Loopback")
            
            success = (interface_name not in verify)
            
            return {
                "success": success,
                "device": device_name,
                "message": f"{interface_name} deleted successfully",
                "interface": interface_name,
                "config_output": output,
                "verification": verify.strip() if verify.strip() else "(no loopbacks remain)"
            }
            
    except Exception as e:
        logger.error(f"Error deleting loopback: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def set_banner(device_name: str, banner_text: str, banner_type: str = "motd") -> dict:
    """
    Configure login banner on device
    
    Args:
        device_name: Router name (R1 or R2)
        banner_text: Banner message text
        banner_type: Type of banner (motd, login, exec) - default is motd
        
    Returns:
        dict: Configuration result with verification
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        # Validate banner type
        valid_types = ["motd", "login", "exec"]
        if banner_type not in valid_types:
            return {
                "success": False,
                "error": f"Invalid banner type. Must be one of: {', '.join(valid_types)}"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Setting {banner_type} banner on {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            # Context-Aware: Check current banner
            current_banner = connector.execute_command(
                f"show running-config | section banner {banner_type}"
            )
            
            # Configure banner
            # Note: We use # as delimiter and ensure banner text doesn't contain #
            if '#' in banner_text:
                return {
                    "success": False,
                    "error": "Banner text cannot contain '#' character (used as delimiter)"
                }
            
            commands = [
                f"banner {banner_type} #",
                banner_text,
                "#"
            ]
            
            output = connector.execute_config_commands(commands)
            
            # Verify banner was set
            verify_banner = connector.execute_command(
                f"show running-config | section banner {banner_type}"
            )
            
            success = (banner_text in verify_banner)
            
            return {
                "success": success,
                "device": device_name,
                "message": f"Banner {banner_type} configured successfully",
                "banner_type": banner_type,
                "banner_text": banner_text,
                "before_banner": current_banner.strip() if current_banner.strip() else "(none)",
                "after_banner": verify_banner.strip(),
                "config_output": output
            }
            
    except Exception as e:
        logger.error(f"Error setting banner: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def remove_banner(device_name: str, banner_type: str = "motd") -> dict:
    """
    Remove login banner from device
    
    Args:
        device_name: Router name (R1 or R2)
        banner_type: Type of banner to remove (motd, login, exec)
        
    Returns:
        dict: Removal result
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        # Validate banner type
        valid_types = ["motd", "login", "exec"]
        if banner_type not in valid_types:
            return {
                "success": False,
                "error": f"Invalid banner type. Must be one of: {', '.join(valid_types)}"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Removing {banner_type} banner from {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            # Check if banner exists
            current_banner = connector.execute_command(
                f"show running-config | section banner {banner_type}"
            )
            
            if not current_banner.strip() or f"banner {banner_type}" not in current_banner:
                return {
                    "success": True,
                    "device": device_name,
                    "message": f"No {banner_type} banner configured. Nothing to remove.",
                    "banner_type": banner_type
                }
            
            # Remove banner
            commands = [f"no banner {banner_type}"]
            output = connector.execute_config_commands(commands)
            
            # Verify removal
            verify_banner = connector.execute_command(
                f"show running-config | section banner {banner_type}"
            )
            
            success = (f"banner {banner_type}" not in verify_banner)
            
            return {
                "success": success,
                "device": device_name,
                "message": f"Banner {banner_type} removed successfully",
                "banner_type": banner_type,
                "before_banner": current_banner.strip(),
                "after_banner": verify_banner.strip() if verify_banner.strip() else "(removed)",
                "config_output": output
            }
            
    except Exception as e:
        logger.error(f"Error removing banner: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }