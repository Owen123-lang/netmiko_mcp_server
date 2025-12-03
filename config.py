"""
Configuration file for Cisco DevNet Sandbox credentials
This uses the Catalyst 8000 Always-On Sandbox
"""

# DevNet Sandbox - Catalyst 8000 Always-On Device
# Unique credentials generated per user reservation
DEVNET_DEVICE = {
    "device_type": "cisco_ios",
    "host": "devnetsandboxiosxec8k.cisco.com",
    "port": 22,
    "username": "rowen.harahap",
    "password": "-8zG-lbr-06iXM3",  # Note: 06 is zero-six, not O-six
    "secret": "-8zG-lbr-06iXM3",  # Enable password (same as password)
    "timeout": 30,
    "session_log": "netmiko_session.log",  # Optional: log all commands
}

# Alternative: You can also use environment variables for security
# Uncomment below if you want to use .env file
"""
import os
from dotenv import load_dotenv

load_dotenv()

DEVNET_DEVICE = {
    "device_type": "cisco_ios",
    "host": os.getenv("CISCO_HOST", "sandbox-iosxe-latest-1.cisco.com"),
    "port": int(os.getenv("CISCO_PORT", "22")),
    "username": os.getenv("CISCO_USERNAME", "developer"),
    "password": os.getenv("CISCO_PASSWORD", "C1sco12345"),
    "secret": os.getenv("CISCO_SECRET", "C1sco12345"),
    "timeout": 30,
}
"""