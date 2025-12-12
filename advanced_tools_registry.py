"""
Advanced Tools Registry for MCP Server
Contains tool definitions for advanced features:
- Static routing and NAT
- Backup/restore
- Monitoring and troubleshooting
"""

from mcp.types import Tool


def get_advanced_tool_definitions():
    """Return list of advanced tool definitions for MCP server"""
    return [
        # ========== ROUTING TOOLS ==========
        Tool(
            name="configure_static_route",
            description="Configure static route on router. Alternative to OSPF for simple 2-router setups.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "destination_network": {
                        "type": "string",
                        "description": "Destination network (e.g., '0.0.0.0' for default route)"
                    },
                    "subnet_mask": {
                        "type": "string",
                        "description": "Subnet mask (e.g., '0.0.0.0' for default route)"
                    },
                    "next_hop_ip": {
                        "type": "string",
                        "description": "Next hop IP address"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional route description"
                    }
                },
                "required": ["device_name", "destination_network", "subnet_mask", "next_hop_ip"]
            }
        ),
        Tool(
            name="show_routing_table",
            description="Show IP routing table with optional protocol filter.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "protocol": {
                        "type": "string",
                        "description": "Optional protocol filter (static, ospf, connected)",
                        "enum": ["static", "ospf", "connected", "rip", "bgp"]
                    }
                },
                "required": ["device_name"]
            }
        ),
        
        # ========== NAT TOOLS ==========
        Tool(
            name="configure_nat_overload",
            description="Configure NAT overload (PAT) for internet sharing. Allows R2 to access internet via R1.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (typically R1)",
                        "enum": ["R1", "R2"]
                    },
                    "outside_interface": {
                        "type": "string",
                        "description": "Interface connected to internet (e.g., 'FastEthernet0/0')"
                    },
                    "inside_network": {
                        "type": "string",
                        "description": "Internal network to NAT (e.g., '10.1.1.0')"
                    },
                    "inside_mask": {
                        "type": "string",
                        "description": "Wildcard mask (e.g., '0.0.0.255')"
                    }
                },
                "required": ["device_name", "outside_interface", "inside_network", "inside_mask"]
            }
        ),
        Tool(
            name="show_nat_translations",
            description="Show NAT translation table and statistics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name",
                        "enum": ["R1", "R2"]
                    }
                },
                "required": ["device_name"]
            }
        ),
        
        # ========== BACKUP & RESTORE TOOLS ==========
        Tool(
            name="backup_config",
            description="Backup device configuration to local file with timestamp.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name",
                        "enum": ["R1", "R2"]
                    },
                    "backup_dir": {
                        "type": "string",
                        "description": "Backup directory (default: backups)"
                    }
                },
                "required": ["device_name"]
            }
        ),
        Tool(
            name="compare_configs",
            description="Compare running config vs startup config. Detects unsaved changes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name",
                        "enum": ["R1", "R2"]
                    }
                },
                "required": ["device_name"]
            }
        ),
        Tool(
            name="save_config",
            description="Save running config to startup config (write memory).",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name",
                        "enum": ["R1", "R2"]
                    }
                },
                "required": ["device_name"]
            }
        ),
        
        # ========== MONITORING TOOLS ==========
        Tool(
            name="get_interface_stats",
            description="Get interface traffic statistics (packets, errors, utilization).",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name",
                        "enum": ["R1", "R2"]
                    },
                    "interface_name": {
                        "type": "string",
                        "description": "Optional specific interface"
                    }
                },
                "required": ["device_name"]
            }
        ),
        Tool(
            name="get_logs",
            description="Get recent syslog messages with categorization (errors, warnings, info).",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name",
                        "enum": ["R1", "R2"]
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of log lines to retrieve (default: 50)"
                    }
                },
                "required": ["device_name"]
            }
        ),
        
        # ========== TROUBLESHOOTING TOOLS ==========
        Tool(
            name="test_internet_connectivity",
            description="Test internet connectivity from router (ping + DNS test).",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name",
                        "enum": ["R1", "R2"]
                    },
                    "target": {
                        "type": "string",
                        "description": "Target IP or hostname (default: 8.8.8.8)"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of ping packets (default: 5)"
                    }
                },
                "required": ["device_name"]
            }
        ),
        Tool(
            name="traceroute",
            description="Perform traceroute to show path to target.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name",
                        "enum": ["R1", "R2"]
                    },
                    "target": {
                        "type": "string",
                        "description": "Target IP or hostname"
                    }
                },
                "required": ["device_name", "target"]
            }
        ),
        Tool(
            name="ping_sweep",
            description="Perform ping sweep to discover active hosts on network.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name",
                        "enum": ["R1", "R2"]
                    },
                    "network": {
                        "type": "string",
                        "description": "Network address (e.g., '10.1.1')"
                    },
                    "start_ip": {
                        "type": "integer",
                        "description": "Start host number (e.g., 1)"
                    },
                    "end_ip": {
                        "type": "integer",
                        "description": "End host number (e.g., 254, max 50 range)"
                    }
                },
                "required": ["device_name", "network", "start_ip", "end_ip"]
            }
        ),
        Tool(
            name="diagnose_connectivity",
            description="AI-powered connectivity troubleshooting. Performs comprehensive diagnostics and suggests fixes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name",
                        "enum": ["R1", "R2"]
                    },
                    "target_ip": {
                        "type": "string",
                        "description": "Target IP to diagnose"
                    }
                },
                "required": ["device_name", "target_ip"]
            }
        ),
        Tool(
            name="test_end_to_end_connectivity",
            description="Test full connectivity between two routers (bidirectional ping test).",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_device": {
                        "type": "string",
                        "description": "Source router name",
                        "enum": ["R1", "R2"]
                    },
                    "destination_device": {
                        "type": "string",
                        "description": "Destination router name",
                        "enum": ["R1", "R2"]
                    }
                },
                "required": ["source_device", "destination_device"]
            }
        ),
    ]