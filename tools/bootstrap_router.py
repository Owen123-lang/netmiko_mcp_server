"""
Bootstrap Router Tool - True Zero-Touch Configuration
Auto-configures a new router that doesn't have SSH enabled yet.

Strategy:
1. SSH to R1 (jumphost)
2. Telnet from R1 to target router (R2)
3. Configure SSH on target router
4. Verify SSH access works
5. Close telnet and exit

This demonstrates:
- Bootstrap automation (configuring unconfigured devices)
- Multi-hop access (R1 as jumphost)
- Self-healing network capability
"""

from netmiko import ConnectHandler
import time
import re


def bootstrap_router_ssh(jumphost_device="R1", target_ip="10.1.1.2", 
                        target_hostname="NetAutoR2", 
                        username="admin", password="admin123",
                        domain_name="netauto.local"):
    """
    Bootstrap SSH configuration on a router that doesn't have it yet.
    
    Args:
        jumphost_device: Device to use as jumphost (default: R1)
        target_ip: IP address of target router
        target_hostname: Desired hostname for target router
        username: Username to create on target router
        password: Password for the user
        domain_name: Domain name for crypto key generation
    
    Returns:
        dict: Status of bootstrap operation
    """
    from netmiko_connector import get_device_config
    
    try:
        # Step 1: Connect to jumphost (R1)
        print(f"[1/5] Connecting to jumphost {jumphost_device}...")
        jumphost_config = get_device_config(jumphost_device)
        connection = ConnectHandler(**jumphost_config)
        
        # Step 2: Check if target is reachable
        print(f"[2/5] Testing connectivity to {target_ip}...")
        ping_output = connection.send_command(f"ping {target_ip} repeat 3")
        
        if "Success rate is 0" in ping_output or "!!!" not in ping_output:
            return {
                "success": False,
                "error": f"Target {target_ip} is not reachable from {jumphost_device}",
                "ping_output": ping_output
            }
        
        print(f"✓ Target {target_ip} is reachable")
        
        # Step 3: Telnet to target router
        print(f"[3/5] Initiating telnet to {target_ip}...")
        
        # Send telnet command
        connection.write_channel(f"telnet {target_ip}\n")
        time.sleep(2)
        
        # Wait for router prompt or login
        output = connection.read_channel()
        
        # Check if we need to press Enter to get started
        if "Press RETURN to get started" in output or "to get started" in output:
            connection.write_channel("\n")
            time.sleep(1)
            output += connection.read_channel()
        
        # If already at router prompt (no login), we can proceed
        # Router prompt looks like: Router> or Router#
        
        print(f"[4/5] Configuring SSH on target router...")
        
        # Enter privileged mode
        connection.write_channel("enable\n")
        time.sleep(1)
        output += connection.read_channel()
        
        # Enter configuration mode
        connection.write_channel("configure terminal\n")
        time.sleep(1)
        output += connection.read_channel()
        
        # Configure hostname
        connection.write_channel(f"hostname {target_hostname}\n")
        time.sleep(1)
        
        # Configure domain name (required for SSH)
        connection.write_channel(f"ip domain-name {domain_name}\n")
        time.sleep(1)
        
        # Generate RSA keys
        connection.write_channel("crypto key generate rsa\n")
        time.sleep(2)
        output += connection.read_channel()
        
        # Input modulus size (2048)
        if "How many bits in the modulus" in output:
            connection.write_channel("2048\n")
            time.sleep(5)  # Key generation takes time
            output += connection.read_channel()
        
        # Enable SSH version 2
        connection.write_channel("ip ssh version 2\n")
        time.sleep(1)
        
        # Create user account
        connection.write_channel(f"username {username} privilege 15 secret {password}\n")
        time.sleep(1)
        
        # Configure VTY lines
        connection.write_channel("line vty 0 4\n")
        time.sleep(1)
        connection.write_channel("login local\n")
        time.sleep(1)
        connection.write_channel("transport input ssh\n")
        time.sleep(1)
        connection.write_channel("exec-timeout 0 0\n")
        time.sleep(1)
        connection.write_channel("exit\n")
        time.sleep(1)
        
        # Configure console line
        connection.write_channel("line con 0\n")
        time.sleep(1)
        connection.write_channel("exec-timeout 0 0\n")
        time.sleep(1)
        connection.write_channel("privilege level 15\n")
        time.sleep(1)
        connection.write_channel("exit\n")
        time.sleep(1)
        
        # Exit configuration mode
        connection.write_channel("end\n")
        time.sleep(1)
        
        # Save configuration
        connection.write_channel("write memory\n")
        time.sleep(2)
        output += connection.read_channel()
        
        # Exit telnet
        connection.write_channel("exit\n")
        time.sleep(2)
        
        print(f"[5/5] Verifying SSH access to {target_ip}...")
        
        # Step 4: Verify SSH works
        time.sleep(3)  # Wait for SSH service to start
        
        try:
            # Try to SSH directly to target
            target_config = {
                "device_type": "cisco_ios",
                "host": target_ip,
                "username": username,
                "password": password,
                "secret": password,
                "timeout": 20,
            }
            
            test_connection = ConnectHandler(**target_config)
            test_output = test_connection.send_command("show version | include IOS")
            test_connection.disconnect()
            
            connection.disconnect()
            
            return {
                "success": True,
                "message": f"Successfully bootstrapped SSH on {target_hostname} ({target_ip})",
                "jumphost": jumphost_device,
                "target_ip": target_ip,
                "target_hostname": target_hostname,
                "username": username,
                "ssh_verified": True,
                "test_output": test_output,
                "bootstrap_output": output
            }
            
        except Exception as ssh_error:
            connection.disconnect()
            return {
                "success": False,
                "error": f"SSH configuration completed but verification failed: {str(ssh_error)}",
                "message": "Configuration was applied but SSH may need more time to start",
                "target_ip": target_ip,
                "suggestion": f"Try manually: ssh {username}@{target_ip}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Bootstrap failed: {str(e)}",
            "jumphost": jumphost_device,
            "target_ip": target_ip
        }


def check_router_ssh_status(device_name):
    """
    Check if a router has SSH enabled and accessible.
    
    Args:
        device_name: Name of the device (R1, R2, etc.)
    
    Returns:
        dict: SSH status information
    """
    from netmiko_connector import get_device_config
    
    try:
        device_config = get_device_config(device_name)
        connection = ConnectHandler(**device_config)
        
        # Get SSH status
        ssh_output = connection.send_command("show ip ssh")
        
        # Get crypto key status
        crypto_output = connection.send_command("show crypto key mypubkey rsa")
        
        connection.disconnect()
        
        # Parse outputs
        ssh_enabled = "SSH Enabled" in ssh_output
        ssh_version = None
        if "version" in ssh_output.lower():
            version_match = re.search(r'version\s+(\d+\.\d+)', ssh_output, re.IGNORECASE)
            if version_match:
                ssh_version = version_match.group(1)
        
        has_keys = "Key pair" in crypto_output or "Key name:" in crypto_output
        
        return {
            "success": True,
            "device": device_name,
            "ssh_enabled": ssh_enabled,
            "ssh_version": ssh_version,
            "has_crypto_keys": has_keys,
            "ssh_output": ssh_output,
            "crypto_output": crypto_output
        }
        
    except Exception as e:
        return {
            "success": False,
            "device": device_name,
            "error": f"Cannot check SSH status: {str(e)}",
            "ssh_enabled": False,
            "message": "Device not accessible via SSH (may need bootstrapping)"
        }


if __name__ == "__main__":
    # Test bootstrap
    print("=== Testing Bootstrap Router SSH ===\n")
    
    # First check R2 status
    print("Checking R2 SSH status...")
    status = check_router_ssh_status("R2")
    print(f"R2 SSH Status: {status}")
    
    if not status["success"]:
        print("\nR2 needs bootstrapping. Starting bootstrap process...")
        result = bootstrap_router_ssh(
            jumphost_device="R1",
            target_ip="10.1.1.2",
            target_hostname="NetAutoR2",
            username="admin",
            password="admin123"
        )
        
        print("\n=== Bootstrap Result ===")
        print(f"Success: {result['success']}")
        print(f"Message: {result.get('message', result.get('error'))}")
        
        if result["success"]:
            print("\n✅ R2 is now accessible via SSH!")
            print(f"   You can now use: ssh admin@10.1.1.2")