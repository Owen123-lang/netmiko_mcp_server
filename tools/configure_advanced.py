"""
Advanced Configuration Tools for 2-Router Topology
Includes: NAT, Static Routes, Backup/Restore, Monitoring

These tools are optimized for simple 2-router setups and provide:
- Internet sharing via NAT
- Static routing (alternative to OSPF)
- Configuration backup and restore
- Enhanced monitoring and troubleshooting
"""

from netmiko import ConnectHandler
import json
import os
from datetime import datetime
import re


# ==================== ROUTING TOOLS ====================

def configure_static_route(device_name, destination_network, subnet_mask, next_hop_ip, description=None):
    """
    Configure static route on router.
    
    Args:
        device_name: Router name (R1 or R2)
        destination_network: Destination network (e.g., "0.0.0.0" for default route)
        subnet_mask: Subnet mask (e.g., "0.0.0.0" for default route)
        next_hop_ip: Next hop IP address
        description: Optional description
    
    Returns:
        dict: Configuration result
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        # Read current routing table
        before_routes = connection.send_command("show ip route")
        
        # Build configuration commands
        commands = [
            "configure terminal",
            f"ip route {destination_network} {subnet_mask} {next_hop_ip}",
        ]
        
        if description:
            commands.insert(1, f"! {description}")
        
        commands.extend(["end", "write memory"])
        
        # Apply configuration
        output = connection.send_config_set(commands)
        
        # Verify route added
        after_routes = connection.send_command("show ip route")
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "destination": destination_network,
            "mask": subnet_mask,
            "next_hop": next_hop_ip,
            "message": "Static route configured successfully",
            "before_routes": before_routes,
            "after_routes": after_routes,
            "config_output": output
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Failed to configure static route: {str(e)}"
        }


def show_routing_table(device_name, protocol=None):
    """
    Show IP routing table with optional protocol filter.
    
    Args:
        device_name: Router name
        protocol: Optional protocol filter (static, ospf, connected, etc.)
    
    Returns:
        dict: Routing table information
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        # Get routing table
        if protocol:
            command = f"show ip route {protocol}"
        else:
            command = "show ip route"
        
        output = connection.send_command(command)
        
        # Parse routes
        routes = []
        for line in output.split('\n'):
            if line.strip() and not line.startswith('Codes:') and not line.startswith('Gateway'):
                if any(x in line for x in ['C', 'S', 'O', 'R', 'B', 'D']):
                    routes.append(line.strip())
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "protocol_filter": protocol,
            "route_count": len(routes),
            "routes": routes,
            "full_output": output
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Failed to retrieve routing table: {str(e)}"
        }


# ==================== NAT CONFIGURATION ====================

def configure_nat_overload(device_name, outside_interface, inside_network, inside_mask):
    """
    Configure NAT overload (PAT) for internet sharing.
    
    Args:
        device_name: Router name (typically R1)
        outside_interface: Interface connected to internet (e.g., "FastEthernet0/0")
        inside_network: Internal network to NAT (e.g., "10.1.1.0")
        inside_mask: Wildcard mask (e.g., "0.0.0.255")
    
    Returns:
        dict: NAT configuration result
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        # Check current NAT config
        before_nat = connection.send_command("show ip nat translations")
        
        # Build configuration
        commands = [
            "configure terminal",
            # Define ACL for NAT
            "access-list 1 permit " + inside_network + " " + inside_mask,
            # Configure NAT on outside interface
            f"interface {outside_interface}",
            "ip nat outside",
            "exit",
            # Configure NAT overload
            f"ip nat inside source list 1 interface {outside_interface} overload",
        ]
        
        # Find inside interfaces and configure them
        interfaces_output = connection.send_command("show ip interface brief")
        for line in interfaces_output.split('\n'):
            if inside_network.rsplit('.', 1)[0] in line:
                # Extract interface name
                interface_match = re.match(r'(\S+)\s+', line)
                if interface_match:
                    inside_interface = interface_match.group(1)
                    commands.extend([
                        f"interface {inside_interface}",
                        "ip nat inside",
                        "exit"
                    ])
        
        commands.extend(["end", "write memory"])
        
        # Apply configuration
        output = connection.send_config_set(commands)
        
        # Verify NAT configured
        after_nat = connection.send_command("show ip nat statistics")
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "outside_interface": outside_interface,
            "inside_network": f"{inside_network} {inside_mask}",
            "message": "NAT overload configured successfully",
            "before_nat": before_nat,
            "nat_statistics": after_nat,
            "config_output": output
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Failed to configure NAT: {str(e)}"
        }


def show_nat_translations(device_name):
    """
    Show NAT translations.
    
    Args:
        device_name: Router name
    
    Returns:
        dict: NAT translation information
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        translations = connection.send_command("show ip nat translations")
        statistics = connection.send_command("show ip nat statistics")
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "translations": translations,
            "statistics": statistics
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Failed to retrieve NAT info: {str(e)}"
        }


# ==================== BACKUP & RESTORE ====================

def backup_config(device_name, backup_dir="backups"):
    """
    Backup device configuration to local file.
    
    Args:
        device_name: Router name
        backup_dir: Directory to store backups
    
    Returns:
        dict: Backup result
    """
    from netmiko_connector import get_device_config
    
    try:
        # Create backup directory if not exists
        os.makedirs(backup_dir, exist_ok=True)
        
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        # Get running config
        running_config = connection.send_command("show running-config")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{backup_dir}/{device_name}_config_{timestamp}.txt"
        
        # Save to file
        with open(filename, 'w') as f:
            f.write(f"# Backup of {device_name}\n")
            f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Device: {device_config['host']}\n\n")
            f.write(running_config)
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "filename": filename,
            "timestamp": timestamp,
            "size_bytes": os.path.getsize(filename),
            "message": f"Configuration backed up to {filename}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Backup failed: {str(e)}"
        }


def compare_configs(device_name):
    """
    Compare running config vs startup config.
    
    Args:
        device_name: Router name
    
    Returns:
        dict: Comparison result
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        running_config = connection.send_command("show running-config")
        startup_config = connection.send_command("show startup-config")
        
        # Simple diff detection
        running_lines = set(running_config.split('\n'))
        startup_lines = set(startup_config.split('\n'))
        
        added_lines = running_lines - startup_lines
        removed_lines = startup_lines - running_lines
        
        # Filter out timestamp and noise lines
        def filter_noise(lines):
            return [l for l in lines if l.strip() and 
                   not l.startswith('!') and 
                   not 'Last configuration change' in l and
                   not 'NVRAM config last updated' in l and
                   not 'Building configuration' in l]
        
        added = filter_noise(added_lines)
        removed = filter_noise(removed_lines)
        
        has_changes = len(added) > 0 or len(removed) > 0
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "has_unsaved_changes": has_changes,
            "added_lines": added,
            "removed_lines": removed,
            "added_count": len(added),
            "removed_count": len(removed),
            "message": "Unsaved changes detected!" if has_changes else "No unsaved changes"
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Comparison failed: {str(e)}"
        }


def save_config(device_name):
    """
    Save running config to startup config (write memory).
    
    Args:
        device_name: Router name
    
    Returns:
        dict: Save result
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        # Check for changes first
        comparison = compare_configs(device_name)
        
        if not comparison["has_unsaved_changes"]:
            connection.disconnect()
            return {
                "success": True,
                "device": device_name,
                "message": "No changes to save",
                "saved": False
            }
        
        # Save configuration
        output = connection.send_command("write memory")
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "message": "Configuration saved successfully",
            "saved": True,
            "changes_saved": comparison["added_count"] + comparison["removed_count"],
            "output": output
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Save failed: {str(e)}"
        }


# ==================== MONITORING TOOLS ====================

def get_interface_stats(device_name, interface_name=None):
    """
    Get interface statistics (packets, errors, traffic).
    
    Args:
        device_name: Router name
        interface_name: Optional specific interface
    
    Returns:
        dict: Interface statistics
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        if interface_name:
            command = f"show interfaces {interface_name}"
        else:
            command = "show interfaces"
        
        output = connection.send_command(command)
        
        # Parse statistics
        stats = []
        current_interface = None
        
        for line in output.split('\n'):
            if 'is up' in line or 'is down' in line:
                if current_interface:
                    stats.append(current_interface)
                current_interface = {"interface": line.split()[0], "raw": line}
            elif current_interface and ('packets input' in line or 'packets output' in line):
                current_interface["stats"] = line.strip()
        
        if current_interface:
            stats.append(current_interface)
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "interface_filter": interface_name,
            "statistics": stats,
            "full_output": output
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Failed to get interface stats: {str(e)}"
        }


def get_logs(device_name, lines=50):
    """
    Get recent syslog messages.
    
    Args:
        device_name: Router name
        lines: Number of log lines to retrieve
    
    Returns:
        dict: Log messages
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        output = connection.send_command(f"show logging | tail {lines}")
        
        # Parse logs
        logs = [line.strip() for line in output.split('\n') if line.strip()]
        
        # Categorize by severity
        errors = [l for l in logs if '%ERROR' in l or '%CRIT' in l]
        warnings = [l for l in logs if '%WARN' in l]
        info = [l for l in logs if '%INFO' in l or '%NOTICE' in l]
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "total_lines": len(logs),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "info_count": len(info),
            "errors": errors,
            "warnings": warnings,
            "recent_logs": logs[-20:],  # Last 20 lines
            "full_output": output
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Failed to retrieve logs: {str(e)}"
        }


if __name__ == "__main__":
    # Test functions
    print("=== Testing Advanced Configuration Tools ===\n")
    
    # Test static route
    print("1. Testing static route configuration...")
    result = configure_static_route("R1", "0.0.0.0", "0.0.0.0", "192.168.242.1", "Default route to internet")
    print(f"Result: {result.get('success')}")
    
    # Test show routing table
    print("\n2. Testing show routing table...")
    result = show_routing_table("R1")
    print(f"Routes found: {result.get('route_count')}")
    
    # Test backup
    print("\n3. Testing config backup...")
    result = backup_config("R1")
    print(f"Backup saved: {result.get('filename')}")