"""
Configuration file for GNS3 Multi-Router Setup
Supports Zero-Touch Configuration with 2 routers (R1 and R2)
"""

# Router 1 Configuration (Connected to Cloud/Wi-Fi)
ROUTER1_DEVICE = {
    "device_type": "cisco_ios",
    "host": "172.16.10.200",  # R1 IP on Wi-Fi network
    "port": 22,
    "username": "admin",
    "password": "admin123",
    "secret": "admin123",
    "timeout": 30,
}

# Router 2 Configuration (Internal network)
ROUTER2_DEVICE = {
    "device_type": "cisco_ios",
    "host": "10.1.1.2",  # R2 IP on internal network (reachable via R1)
    "port": 22,
    "username": "admin",
    "password": "admin123",
    "secret": "admin123",
    "timeout": 30,
}

# Multi-device configuration for easy iteration
DEVICES = {
    "R1": ROUTER1_DEVICE,
    "R2": ROUTER2_DEVICE,
}

# Default device (for backward compatibility with existing tools)
DEVNET_DEVICE = ROUTER1_DEVICE

# Network Configuration for Zero-Touch Setup
NETWORK_CONFIG = {
    "R1": {
        "hostname": "NetAutoR1",
        "interfaces": {
            "FastEthernet0/0": {
                "description": "Link to Cloud (Wi-Fi)",
                "ip_address": "172.16.10.250",
                "subnet_mask": "255.255.255.0",
            },
            "FastEthernet0/1": {
                "description": "Link to R2",
                "ip_address": "10.1.1.1",
                "subnet_mask": "255.255.255.0",
            },
        },
        "ospf": {
            "process_id": 1,
            "networks": [
                {"network": "10.0.0.0", "wildcard": "0.255.255.255", "area": 0},
            ],
            "default_information": "originate",
        },
    },
    "R2": {
        "hostname": "NetAutoR2",
        "interfaces": {
            "FastEthernet0/0": {
                "description": "Link to R1",
                "ip_address": "10.1.1.2",
                "subnet_mask": "255.255.255.0",
            },
        },
        "ospf": {
            "process_id": 1,
            "networks": [
                {"network": "10.0.0.0", "wildcard": "0.255.255.255", "area": 0},
            ],
        },
    },
}