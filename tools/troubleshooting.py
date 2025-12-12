"""
Troubleshooting Tools for Network Diagnostics
Provides AI-powered network troubleshooting and diagnostics
"""

from netmiko import ConnectHandler
import re


def test_internet_connectivity(device_name, target="8.8.8.8", count=5):
    """
    Test internet connectivity from router.
    
    Args:
        device_name: Router name
        target: Target IP or hostname (default: 8.8.8.8 Google DNS)
        count: Number of ping packets
    
    Returns:
        dict: Connectivity test result
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        # Ping test
        ping_output = connection.send_command(f"ping {target} repeat {count}")
        
        # Parse success rate
        success_rate = 0
        if "Success rate is" in ping_output:
            match = re.search(r'Success rate is (\d+) percent', ping_output)
            if match:
                success_rate = int(match.group(1))
        
        has_internet = success_rate > 0
        
        # If successful, try DNS resolution
        dns_works = False
        if has_internet and not target.replace('.', '').isdigit():
            # Target is hostname, DNS already tested
            dns_works = True
        elif has_internet:
            # Test DNS with hostname
            dns_output = connection.send_command("ping www.google.com repeat 1")
            dns_works = "Success rate is" in dns_output and "0 percent" not in dns_output
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "target": target,
            "has_internet": has_internet,
            "success_rate": success_rate,
            "dns_working": dns_works,
            "ping_output": ping_output,
            "message": f"Internet {'accessible' if has_internet else 'NOT accessible'}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Connectivity test failed: {str(e)}"
        }


def traceroute(device_name, target):
    """
    Perform traceroute to show path to target.
    
    Args:
        device_name: Router name
        target: Target IP or hostname
    
    Returns:
        dict: Traceroute result
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        output = connection.send_command(f"traceroute {target}", delay_factor=2)
        
        # Parse hops
        hops = []
        for line in output.split('\n'):
            if line.strip() and line[0].isdigit():
                hops.append(line.strip())
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "target": target,
            "hop_count": len(hops),
            "hops": hops,
            "full_output": output
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Traceroute failed: {str(e)}"
        }


def ping_sweep(device_name, network, start_ip, end_ip):
    """
    Perform ping sweep to discover active hosts.
    
    Args:
        device_name: Router name
        network: Network address (e.g., "10.1.1")
        start_ip: Start host number (e.g., 1)
        end_ip: End host number (e.g., 254)
    
    Returns:
        dict: Ping sweep results
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        active_hosts = []
        inactive_hosts = []
        
        # Limit sweep to reasonable range
        if end_ip - start_ip > 50:
            end_ip = start_ip + 50
        
        for i in range(start_ip, end_ip + 1):
            target_ip = f"{network}.{i}"
            output = connection.send_command(f"ping {target_ip} repeat 2 timeout 1")
            
            if "!!" in output or "Success rate is 100" in output:
                active_hosts.append(target_ip)
            else:
                inactive_hosts.append(target_ip)
        
        connection.disconnect()
        
        return {
            "success": True,
            "device": device_name,
            "network_scanned": f"{network}.{start_ip}-{end_ip}",
            "active_count": len(active_hosts),
            "inactive_count": len(inactive_hosts),
            "active_hosts": active_hosts,
            "message": f"Found {len(active_hosts)} active hosts"
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Ping sweep failed: {str(e)}"
        }


def diagnose_connectivity(device_name, target_ip):
    """
    AI-powered connectivity troubleshooting.
    Performs comprehensive diagnostics and suggests fixes.
    
    Args:
        device_name: Router name
        target_ip: Target IP to diagnose
    
    Returns:
        dict: Diagnostic report with suggestions
    """
    from netmiko_connector import get_device_config
    from tools.get_interfaces import get_interfaces
    from tools.configure_advanced import show_routing_table
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        issues = []
        suggestions = []
        tests_passed = []
        
        # Test 1: Check interface status
        interfaces_result = get_interfaces(device_name)
        all_up = True
        if interfaces_result["success"]:
            for line in interfaces_result["output"].split('\n'):
                if 'up' in line.lower():
                    tests_passed.append("Interface check: UP")
                elif 'down' in line.lower():
                    all_up = False
                    issues.append(f"Interface down detected: {line.strip()}")
                    suggestions.append("Check cable connection and interface configuration")
        
        # Test 2: Ping test
        ping_output = connection.send_command(f"ping {target_ip} repeat 5")
        ping_success = "!!!" in ping_output
        
        if ping_success:
            tests_passed.append(f"Ping test: SUCCESS ({target_ip} is reachable)")
        else:
            issues.append(f"Ping test: FAILED (cannot reach {target_ip})")
            
            # Test 3: Check routing
            routing_result = show_routing_table(device_name)
            if routing_result["success"]:
                has_route = any(target_ip.rsplit('.', 1)[0] in route for route in routing_result["routes"])
                if not has_route:
                    issues.append("No route to destination network")
                    suggestions.append(f"Add static route or enable dynamic routing protocol")
                else:
                    tests_passed.append("Routing table: Route exists")
            
            # Test 4: Check NAT (if needed for internet)
            if target_ip in ["8.8.8.8", "1.1.1.1"] or not target_ip.startswith("10."):
                nat_output = connection.send_command("show ip nat statistics")
                if "Total active translations: 0" in nat_output or "% Invalid" in nat_output:
                    issues.append("NAT not configured (needed for internet access)")
                    suggestions.append("Configure NAT overload on outside interface")
                else:
                    tests_passed.append("NAT check: Configured")
        
        # Test 5: Check for interface errors
        int_stats = connection.send_command("show interfaces")
        if "error" in int_stats.lower():
            issues.append("Interface errors detected")
            suggestions.append("Check 'show interfaces' for CRC errors or collisions")
        else:
            tests_passed.append("Interface errors: None detected")
        
        connection.disconnect()
        
        diagnosis = "HEALTHY" if ping_success and len(issues) == 0 else "ISSUES DETECTED"
        
        return {
            "success": True,
            "device": device_name,
            "target": target_ip,
            "diagnosis": diagnosis,
            "connectivity": "OK" if ping_success else "FAILED",
            "tests_passed": tests_passed,
            "issues_found": issues,
            "suggestions": suggestions,
            "issue_count": len(issues),
            "ping_output": ping_output,
            "message": f"{diagnosis}: {len(issues)} issues found" if issues else "All checks passed!"
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Diagnostics failed: {str(e)}"
        }


def test_end_to_end_connectivity(source_device, destination_device):
    """
    Test full connectivity between two routers.
    
    Args:
        source_device: Source router name
        destination_device: Destination router name
    
    Returns:
        dict: End-to-end connectivity test
    """
    from netmiko_connector import get_device_config
    from tools.get_interfaces import get_interfaces
    
    try:
        # Get destination IP
        dest_interfaces = get_interfaces(destination_device)
        dest_ip = None
        
        for line in dest_interfaces["output"].split('\n'):
            if "10.1.1" in line:
                parts = line.split()
                for part in parts:
                    if "10.1.1" in part:
                        dest_ip = part
                        break
        
        if not dest_ip:
            return {
                "success": False,
                "error": "Could not determine destination IP"
            }
        
        # Test from source to destination
        source_config = get_device_config(source_device)
        connection = ConnectHandler(**source_config)
        
        forward_ping = connection.send_command(f"ping {dest_ip} repeat 5")
        forward_success = "!!!" in forward_ping
        
        connection.disconnect()
        
        # Test from destination back to source
        source_interfaces = get_interfaces(source_device)
        source_ip = None
        
        for line in source_interfaces["output"].split('\n'):
            if "10.1.1" in line:
                parts = line.split()
                for part in parts:
                    if "10.1.1" in part and part != dest_ip:
                        source_ip = part
                        break
        
        if source_ip:
            dest_config = get_device_config(destination_device)
            dest_connection = ConnectHandler(**dest_config)
            
            reverse_ping = dest_connection.send_command(f"ping {source_ip} repeat 5")
            reverse_success = "!!!" in reverse_ping
            
            dest_connection.disconnect()
        else:
            reverse_success = False
            reverse_ping = "Could not determine source IP"
        
        both_success = forward_success and reverse_success
        
        return {
            "success": True,
            "source_device": source_device,
            "destination_device": destination_device,
            "source_ip": source_ip,
            "destination_ip": dest_ip,
            "forward_test": "PASS" if forward_success else "FAIL",
            "reverse_test": "PASS" if reverse_success else "FAIL",
            "end_to_end": "PASS" if both_success else "FAIL",
            "forward_ping": forward_ping,
            "reverse_ping": reverse_ping,
            "message": "Full connectivity established!" if both_success else "Connectivity issues detected"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"End-to-end test failed: {str(e)}"
        }


if __name__ == "__main__":
    # Test troubleshooting tools
    print("=== Testing Troubleshooting Tools ===\n")
    
    print("1. Testing internet connectivity...")
    result = test_internet_connectivity("R1", "8.8.8.8")
    print(f"Result: {result.get('message')}")
    
    print("\n2. Testing diagnostics...")
    result = diagnose_connectivity("R1", "10.1.1.2")
    print(f"Diagnosis: {result.get('diagnosis')}")
    print(f"Issues: {result.get('issue_count')}")