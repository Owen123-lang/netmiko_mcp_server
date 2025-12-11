"""
Validate Configuration Tool - Zero-Touch Configuration
Allows LLM to verify and validate network configurations
"""

from netmiko_connector import CiscoDeviceConnector
from config import DEVICES
import logging
import re

logger = logging.getLogger(__name__)


def validate_interface_config(device_name: str, interface_name: str, expected_ip: str = None) -> dict:
    """
    Validate interface configuration and status
    
    Args:
        device_name: Router name (R1 or R2)
        interface_name: Interface to validate (e.g., 'FastEthernet0/0')
        expected_ip: Expected IP address (optional, for verification)
        
    Returns:
        dict: Validation result with interface status
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Validating interface {interface_name} on {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            # Get interface brief status
            brief_output = connector.execute_command(f"show ip interface brief | include {interface_name}")
            
            # Get detailed interface info
            detail_output = connector.execute_command(f"show interface {interface_name}")
            
            # Get IP interface info
            ip_output = connector.execute_command(f"show ip interface {interface_name}")
            
            # Parse status (simple parsing)
            is_up = "up" in brief_output.lower() if brief_output else False
            
            # Check if IP matches expected (if provided)
            ip_matches = True
            actual_ip = None
            
            if expected_ip and brief_output:
                # Extract IP from output (simple regex)
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', brief_output)
                if ip_match:
                    actual_ip = ip_match.group(1)
                    ip_matches = (actual_ip == expected_ip)
            
            validation_status = "PASS" if is_up and (not expected_ip or ip_matches) else "FAIL"
            
            return {
                "success": True,
                "validation_status": validation_status,
                "device": device_name,
                "interface": interface_name,
                "is_up": is_up,
                "expected_ip": expected_ip,
                "actual_ip": actual_ip,
                "ip_matches": ip_matches,
                "brief_output": brief_output,
                "detail_output": detail_output,
                "ip_interface_output": ip_output
            }
            
    except Exception as e:
        logger.error(f"Error validating interface: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def validate_connectivity(device_name: str, target_ip: str, count: int = 5) -> dict:
    """
    Validate network connectivity using ping
    
    Args:
        device_name: Router name (R1 or R2)
        target_ip: IP address to ping
        count: Number of ping packets (default: 5)
        
    Returns:
        dict: Ping result with success rate
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Testing connectivity from {device_name} to {target_ip}")
        
        with CiscoDeviceConnector(device_config) as connector:
            ping_output = connector.execute_command(f"ping {target_ip} repeat {count}")
            
            # Parse success rate
            success_match = re.search(r'Success rate is (\d+) percent', ping_output)
            success_rate = int(success_match.group(1)) if success_match else 0
            
            # Check if all pings succeeded
            connectivity_ok = (success_rate == 100)
            
            return {
                "success": True,
                "connectivity_ok": connectivity_ok,
                "device": device_name,
                "target_ip": target_ip,
                "success_rate": success_rate,
                "ping_count": count,
                "ping_output": ping_output
            }
            
    except Exception as e:
        logger.error(f"Error testing connectivity: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def validate_ospf_adjacency(device_name: str, expected_neighbors: list = None) -> dict:
    """
    Validate OSPF neighbor adjacencies
    
    Args:
        device_name: Router name (R1 or R2)
        expected_neighbors: List of expected neighbor IP addresses (optional)
        
    Returns:
        dict: OSPF validation result
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Validating OSPF adjacencies on {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            neighbor_output = connector.execute_command("show ip ospf neighbor")
            
            # Count neighbors in FULL state
            full_neighbors = neighbor_output.count("FULL") if neighbor_output else 0
            
            # Check if expected neighbors are present
            all_neighbors_found = True
            if expected_neighbors:
                for neighbor_ip in expected_neighbors:
                    if neighbor_ip not in neighbor_output:
                        all_neighbors_found = False
                        break
            
            validation_status = "PASS" if full_neighbors > 0 and all_neighbors_found else "FAIL"
            
            return {
                "success": True,
                "validation_status": validation_status,
                "device": device_name,
                "full_neighbors_count": full_neighbors,
                "expected_neighbors": expected_neighbors,
                "all_neighbors_found": all_neighbors_found,
                "neighbor_output": neighbor_output
            }
            
    except Exception as e:
        logger.error(f"Error validating OSPF adjacency: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def validate_routing_table(device_name: str, expected_routes: list = None) -> dict:
    """
    Validate routing table entries
    
    Args:
        device_name: Router name (R1 or R2)
        expected_routes: List of expected network prefixes (optional)
        
    Returns:
        dict: Routing table validation result
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Validating routing table on {device_name}")
        
        with CiscoDeviceConnector(device_config) as connector:
            route_output = connector.execute_command("show ip route")
            ospf_routes = connector.execute_command("show ip route ospf")
            
            # Check for expected routes
            all_routes_found = True
            missing_routes = []
            
            if expected_routes:
                for route in expected_routes:
                    if route not in route_output:
                        all_routes_found = False
                        missing_routes.append(route)
            
            validation_status = "PASS" if all_routes_found else "FAIL"
            
            return {
                "success": True,
                "validation_status": validation_status,
                "device": device_name,
                "expected_routes": expected_routes,
                "all_routes_found": all_routes_found,
                "missing_routes": missing_routes,
                "routing_table": route_output,
                "ospf_routes": ospf_routes
            }
            
    except Exception as e:
        logger.error(f"Error validating routing table: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }


def comprehensive_validation(device_name: str) -> dict:
    """
    Perform comprehensive validation of device configuration
    
    Args:
        device_name: Router name (R1 or R2)
        
    Returns:
        dict: Comprehensive validation report
    """
    try:
        if device_name not in DEVICES:
            return {
                "success": False,
                "error": f"Device '{device_name}' not found"
            }
        
        device_config = DEVICES[device_name]
        
        logger.info(f"Performing comprehensive validation on {device_name}")
        
        validation_results = {
            "device": device_name,
            "checks": []
        }
        
        with CiscoDeviceConnector(device_config) as connector:
            # Check 1: Device reachability
            validation_results["checks"].append({
                "name": "Device Reachability",
                "status": "PASS",
                "details": "Successfully connected to device"
            })
            
            # Check 2: Interface status
            interfaces = connector.execute_command("show ip interface brief")
            down_interfaces = interfaces.count("down") if interfaces else 0
            validation_results["checks"].append({
                "name": "Interface Status",
                "status": "PASS" if down_interfaces == 0 else "WARNING",
                "details": f"Down interfaces: {down_interfaces}",
                "output": interfaces
            })
            
            # Check 3: OSPF neighbors
            neighbors = connector.execute_command("show ip ospf neighbor")
            full_neighbors = neighbors.count("FULL") if neighbors else 0
            validation_results["checks"].append({
                "name": "OSPF Neighbors",
                "status": "PASS" if full_neighbors > 0 else "FAIL",
                "details": f"FULL neighbors: {full_neighbors}",
                "output": neighbors
            })
            
            # Check 4: Routing table
            routes = connector.execute_command("show ip route")
            has_routes = "Gateway of last resort" in routes if routes else False
            validation_results["checks"].append({
                "name": "Routing Table",
                "status": "PASS" if has_routes else "WARNING",
                "details": "Routing table populated",
                "output": routes
            })
            
            # Overall status
            failed_checks = sum(1 for check in validation_results["checks"] if check["status"] == "FAIL")
            validation_results["overall_status"] = "PASS" if failed_checks == 0 else "FAIL"
            validation_results["failed_checks"] = failed_checks
            validation_results["total_checks"] = len(validation_results["checks"])
            
            return {
                "success": True,
                "validation_results": validation_results
            }
            
    except Exception as e:
        logger.error(f"Error performing comprehensive validation: {str(e)}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}"
        }