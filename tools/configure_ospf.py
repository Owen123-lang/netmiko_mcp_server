"""
Configure OSPF Tool - Zero-Touch Configuration
Allows LLM to configure OSPF routing protocol on routers
"""

from netmiko_connector import CiscoDeviceConnector
from config import DEVICES
import logging

logger = logging.getLogger(__name__)


def configure_ospf(device_name: str, process_id: int, networks: list, default_route: bool = False) -> dict:
    """
    Configure OSPF routing protocol on a device
    
    Args:
        device_name: Router name (R1 or R2)
        process_id: OSPF process ID (typically 1)
        networks: List of network dictionaries with format:
                  [{"network": "10.0.0.0", "wildcard": "0.255.255.255", "area": 0}]
        default_route: Whether to advertise default route (default-information originate)
        
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
        
        # Build OSPF configuration commands
        config_commands = [
            f"router ospf {process_id}",
        ]
        
        # Add network statements
        for net in networks:
            network = net.get("network")
            wildcard = net.get("wildcard")
            area = net.get("area", 0)
            
            if not network or not wildcard:
                logger.warning(f"Skipping invalid network entry: {net}")
                continue
            
            config_commands.append(f"network {network} {wildcard} area {area}")
        
        # Add default route advertisement if requested
        if default_route:
            config_commands.append("default-information originate")
        
        logger.info(f"Configuring OSPF process {process_id} on {device_name}")
        logger.info(f"Networks: {networks}")
        
        # Execute configuration
        with CiscoDeviceConnector(device_config) as connector:
            output = connector.execute_config_commands(config_commands)
            
            if output is None:
                return {
                    "success": False,
                    "error": "Failed to execute OSPF configuration commands"
                }
            
            # Verify OSPF configuration
            verify_ospf = connector.execute_command(f"show ip ospf {process_id}")
            verify_neighbors = connector.execute_command("show ip ospf neighbor")
            
            return {
                "success": True,
                "message": f"OSPF process {process_id} configured successfully on {device_name}",
                "device": device_name,
                "process_id": process_id,
                "networks": networks,
                "default_route_advertised": default_route,
                "config_output": output,
                "ospf_status": verify_ospf,
                "ospf_neighbors": verify_neighbors,
                "commands": config_commands
            }
            
    except Exception as e:
        logger.error(f"Error configuring OSPF: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def verify_ospf_neighbors(device_name: str) -> dict:
    """
    Verify OSPF neighbor relationships
    
    Args:
        device_name: Router name (R1 or R2)
        
    Returns:
        dict: OSPF neighbor information
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Verifying OSPF neighbors on {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            neighbors = connector.execute_command("show ip ospf neighbor")
            ospf_summary = connector.execute_command("show ip ospf")
            routes = connector.execute_command("show ip route ospf")
            
            return {
                "success": True,
                "message": f"OSPF verification completed for {device_name}",
                "device": device_name,
                "neighbors": neighbors,
                "ospf_summary": ospf_summary,
                "ospf_routes": routes
            }
            
    except Exception as e:
        logger.error(f"Error verifying OSPF neighbors: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def configure_ospf_interface(device_name: str, interface_name: str, cost: int = None, priority: int = None) -> dict:
    """
    Configure OSPF parameters on a specific interface
    
    Args:
        device_name: Router name (R1 or R2)
        interface_name: Interface to configure (e.g., 'FastEthernet0/1')
        cost: OSPF cost metric (optional)
        priority: OSPF priority for DR/BDR election (optional)
        
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
            f"interface {interface_name}",
        ]
        
        if cost is not None:
            config_commands.append(f"ip ospf cost {cost}")
        
        if priority is not None:
            config_commands.append(f"ip ospf priority {priority}")
        
        logger.info(f"Configuring OSPF parameters on {interface_name} of {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            output = connector.execute_config_commands(config_commands)
            
            if output is None:
                return {
                    "success": False,
                    "error": "Failed to execute configuration"
                }
            
            # Verify
            verify_output = connector.execute_command(f"show ip ospf interface {interface_name}")
            
            return {
                "success": True,
                "message": f"OSPF interface parameters configured on {interface_name}",
                "device": device_name,
                "interface": interface_name,
                "cost": cost,
                "priority": priority,
                "config_output": output,
                "verification": verify_output
            }
            
    except Exception as e:
        logger.error(f"Error configuring OSPF interface: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def clear_ospf_process(device_name: str) -> dict:
    """
    Clear OSPF process to re-establish neighbor relationships
    
    Args:
        device_name: Router name (R1 or R2)
        
    Returns:
        dict: Result of clearing OSPF process
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Clearing OSPF process on {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            # Note: This is a privileged EXEC command, not a config command
            output = connector.execute_command("clear ip ospf process", expect_string=r"[confirm]")
            # Send confirmation (just press Enter)
            if output and "[confirm]" in output:
                connector.connection.send_command_timing("\n")
            
            return {
                "success": True,
                "message": f"OSPF process cleared on {device_name}",
                "device": device_name,
                "output": output
            }
            
    except Exception as e:
        logger.error(f"Error clearing OSPF process: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }