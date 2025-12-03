"""
Netmiko connector module for SSH connections to Cisco devices
Handles connection management and command execution
"""

from netmiko import ConnectHandler
from typing import Dict, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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