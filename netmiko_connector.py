"""
Netmiko connector module for SSH connections to Cisco devices
Handles connection management and command execution with SSH Jumphost support
"""

from netmiko import ConnectHandler
from typing import Dict, Optional
import logging
from paramiko import SSHClient, AutoAddPolicy

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global jumphost connection cache
_jumphost_connections = {}


class CiscoDeviceConnector:
    """
    Wrapper class for Netmiko connections to Cisco devices
    Provides clean interface for connecting and executing commands
    """
    
    def __init__(self, device_config: Dict[str, str]):
        """
        Initialize the connector with device configuration
        
        Args:
            device_config: Dictionary containing device connection parameters
        """
        self.device_config = device_config
        self.connection = None
        
    def connect(self) -> bool:
        """
        Establish SSH connection to the device
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to {self.device_config['host']}...")
            self.connection = ConnectHandler(**self.device_config)
            logger.info("Connection established successfully")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Safely disconnect from the device"""
        if self.connection:
            self.connection.disconnect()
            logger.info("Disconnected from device")
            self.connection = None
    
    def execute_command(self, command: str) -> Optional[str]:
        """
        Execute a single command on the device
        
        Args:
            command: CLI command to execute
            
        Returns:
            str: Command output or None if failed
        """
        if not self.connection:
            logger.error("Not connected to device. Call connect() first.")
            return None
            
        try:
            logger.info(f"Executing command: {command}")
            output = self.connection.send_command(command)
            return output
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return None
    
    def execute_config_commands(self, commands: list) -> Optional[str]:
        """
        Execute configuration commands on the device
        
        Args:
            commands: List of configuration commands
            
        Returns:
            str: Command output or None if failed
        """
        if not self.connection:
            logger.error("Not connected to device. Call connect() first.")
            return None
            
        try:
            logger.info(f"Executing config commands: {commands}")
            output = self.connection.send_config_set(commands)
            return output
        except Exception as e:
            logger.error(f"Config command execution failed: {str(e)}")
            return None
    
    def get_device_info(self) -> Dict[str, str]:
        """
        Get basic device information
        
        Returns:
            dict: Device information including hostname, version, etc.
        """
        if not self.connection:
            return {"error": "Not connected"}
        
        try:
            hostname = self.execute_command("show running-config | include hostname")
            version = self.execute_command("show version | include Version")
            
            return {
                "hostname": hostname.strip() if hostname else "Unknown",
                "version": version.strip() if version else "Unknown",
                "connected": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    def __enter__(self):
        """Context manager entry"""
        success = self.connect()
        if not success:
            raise Exception("Failed to establish connection to device")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Convenience function for quick commands
def execute_single_command(device_config: Dict[str, str], command: str) -> Optional[str]:
    """
    Execute a single command without manual connection management
    
    Args:
        device_config: Device configuration dictionary
        command: Command to execute
        
    Returns:
        str: Command output or None if failed
    """
    with CiscoDeviceConnector(device_config) as connector:
        return connector.execute_command(command)


def get_device_config(device_name: str) -> Dict[str, any]:
    """
    Get device configuration with automatic jumphost support for R2.
    
    R2 is in internal network (10.1.1.0/24) and requires R1 as jumphost.
    
    Args:
        device_name: Router name (R1 or R2)
    
    Returns:
        dict: Device configuration with jumphost channel if needed
    """
    from config import DEVICES
    
    if device_name not in DEVICES:
        raise ValueError(f"Unknown device: {device_name}")
    
    device_config = DEVICES[device_name].copy()
    
    # R2 requires jumphost via R1
    if device_name == "R2":
        logger.info("R2 detected - configuring SSH jumphost via R1")
        
        jumphost = DEVICES["R1"]
        jumphost_key = f"{jumphost['host']}:{jumphost.get('port', 22)}"
        
        # Reuse existing jumphost connection if available
        if jumphost_key not in _jumphost_connections or not _jumphost_connections[jumphost_key]:
            logger.info(f"Creating new jumphost connection to R1 ({jumphost['host']})")
            
            jump_client = SSHClient()
            jump_client.set_missing_host_key_policy(AutoAddPolicy())
            
            try:
                jump_client.connect(
                    hostname=jumphost["host"],
                    username=jumphost["username"],
                    password=jumphost["password"],
                    port=jumphost.get("port", 22),
                    timeout=jumphost.get("timeout", 30),
                    allow_agent=False,
                    look_for_keys=False
                )
                
                _jumphost_connections[jumphost_key] = jump_client
                logger.info("✅ Jumphost connection established")
                
            except Exception as e:
                logger.error(f"❌ Failed to connect to jumphost R1: {str(e)}")
                raise Exception(f"Cannot establish jumphost to R1: {str(e)}")
        
        else:
            logger.info("♻️  Reusing existing jumphost connection")
        
        jump_client = _jumphost_connections[jumphost_key]
        
        try:
            # Get transport from jumphost
            jump_transport = jump_client.get_transport()
            
            if not jump_transport or not jump_transport.is_active():
                logger.warning("Jumphost transport inactive, reconnecting...")
                jump_client.close()
                del _jumphost_connections[jumphost_key]
                return get_device_config(device_name)  # Retry
            
            # Try modern SSH port forwarding first (for newer devices)
            dest_addr = (device_config["host"], device_config.get("port", 22))
            local_addr = ('127.0.0.1', 0)
            
            logger.info(f"Attempting SSH channel: R1 → R2 ({dest_addr[0]}:{dest_addr[1]})")
            
            try:
                # Try direct-tcpip (modern SSH servers)
                jump_channel = jump_transport.open_channel(
                    "direct-tcpip",
                    dest_addr,
                    local_addr
                )
                logger.info("✅ SSH channel established via direct-tcpip")
                
            except Exception as channel_error:
                logger.warning(f"direct-tcpip failed (old IOS?): {str(channel_error)}")
                logger.info("Falling back to session-based forwarding...")
                
                # Fallback: Use exec channel with SSH command
                # This works with older Cisco IOS that don't support port forwarding
                jump_channel = jump_transport.open_session()
                
                # Execute SSH to R2 from R1
                ssh_command = f"ssh -l {device_config['username']} {device_config['host']}"
                jump_channel.exec_command(ssh_command)
                
                # Wait for password prompt
                import time
                time.sleep(2)
                
                # Send password
                jump_channel.send(device_config['password'] + '\n')
                time.sleep(2)
                
                logger.info("✅ SSH session established via exec channel")
            
            # Configure Netmiko to use the channel
            device_config['sock'] = jump_channel
            
            # Store internal metadata (won't be passed to Netmiko)
            # Store in global dict instead of device_config to avoid passing to Netmiko
            device_config['__metadata__'] = {
                'jumphost_client': jump_client,
                'using_jumphost': True,
                'jumphost_key': jumphost_key
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to establish connection to R2: {str(e)}")
            # Clean up failed jumphost connection
            if jumphost_key in _jumphost_connections:
                _jumphost_connections[jumphost_key].close()
                del _jumphost_connections[jumphost_key]
            raise Exception(f"Cannot establish connection to R2: {str(e)}")
    
    else:
        logger.info(f"Direct connection to {device_name}")
    
    return device_config


def cleanup_jumphost_connections():
    """
    Clean up all cached jumphost connections.
    Call this when shutting down MCP server or before creating new connections.
    """
    global _jumphost_connections
    
    for key, client in list(_jumphost_connections.items()):
        try:
            if client:
                client.close()
                logger.info(f"Closed jumphost connection: {key}")
        except Exception as e:
            logger.warning(f"Error closing jumphost {key}: {str(e)}")
    
    _jumphost_connections.clear()
    logger.info("All jumphost connections cleaned up")


def get_connection(device_name: str):
    """
    Get a Netmiko connection to a device with automatic cleanup and reconnection.
    
    This is the recommended way to get connections as it handles:
    - Automatic jumphost setup for R2
    - Connection cleanup for old IOS devices with channel limits
    - Proper error handling and reconnection
    
    Args:
        device_name: Router name (R1 or R2)
    
    Returns:
        ConnectHandler: Netmiko connection object
    
    Example:
        connection = get_connection("R2")
        output = connection.send_command("show version")
        connection.disconnect()
    """
    # For R2, cleanup old connections to avoid "Resource shortage" on old IOS
    if device_name == "R2":
        logger.info("Cleaning up old R2 connections before creating new one...")
        cleanup_jumphost_connections()
    
    # Get device config with jumphost setup if needed
    config = get_device_config(device_name)
    
    # Remove internal metadata before passing to Netmiko
    metadata = config.pop('__metadata__', None)
    
    # Remove ALL parameters starting with underscore (internal use only)
    # These are flags from config.py that shouldn't go to Netmiko
    clean_config = {k: v for k, v in config.items() if not k.startswith('_')}
    
    try:
        # Create Netmiko connection with cleaned config
        connection = ConnectHandler(**clean_config)
        
        # Store metadata back for future cleanup
        if metadata:
            connection._jumphost_metadata = metadata
        
        return connection
        
    except Exception as e:
        logger.error(f"Failed to create connection to {device_name}: {str(e)}")
        # Cleanup on failure
        if device_name == "R2":
            cleanup_jumphost_connections()
        raise