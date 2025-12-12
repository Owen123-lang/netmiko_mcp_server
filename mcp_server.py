"""
MCP Server for Cisco Network Automation with Netmiko
Exposes network device tools to LLM clients via MCP protocol
"""

import asyncio
import logging
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server


from tools.get_interfaces import get_interfaces, get_interface_detail
from tools.get_device_status import get_device_status, get_device_uptime, get_memory_cpu_usage
from tools.get_running_config import get_running_config, get_interface_config, get_startup_config
from tools.configure_interface import configure_interface, configure_default_gateway, configure_dns
from tools.configure_ospf import configure_ospf, verify_ospf_neighbors, configure_ospf_interface
from tools.validate_config import (
    validate_interface_config, validate_connectivity,
    validate_ospf_adjacency, validate_routing_table, comprehensive_validation
)
from tools.configure_basic import (
    get_hostname, change_hostname, configure_interface_description,
    create_loopback, delete_loopback, set_banner, remove_banner
)
from tools.bootstrap_router import bootstrap_router_ssh, check_router_ssh_status
from advanced_tools_registry import get_advanced_tool_definitions
from advanced_tools_handlers import handle_advanced_tools


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("netmiko-mcp-server")


app = Server("netmiko-mcp-server")



@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools for the MCP client
    """
    return [
        Tool(
            name="get_interfaces",
            description="Get list of all network interfaces and their status from the Cisco device. Returns output of 'show ip interface brief' command.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_interface_detail",
            description="Get detailed information about a specific network interface including IP address, MTU, bandwidth, etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "interface_name": {
                        "type": "string",
                        "description": "Name of the interface (e.g., 'GigabitEthernet1', 'GigabitEthernet2')"
                    }
                },
                "required": ["interface_name"]
            }
        ),
        Tool(
            name="get_device_status",
            description="Get overall device status including IOS version, model, serial number, and uptime information.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_device_uptime",
            description="Get device uptime information showing how long the device has been running.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_resource_usage",
            description="Get CPU and memory usage information from the device.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_running_config",
            description="Get the running configuration from the device. Can optionally filter by keyword (e.g., 'interface', 'ip', 'router').",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_keyword": {
                        "type": "string",
                        "description": "Optional keyword to filter configuration (e.g., 'interface', 'ip', 'router')"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_interface_config",
            description="Get configuration for a specific interface from the running config.",
            inputSchema={
                "type": "object",
                "properties": {
                    "interface_name": {
                        "type": "string",
                        "description": "Name of the interface (e.g., 'GigabitEthernet1')"
                    }
                },
                "required": ["interface_name"]
            }
        ),
        Tool(
            name="get_startup_config",
            description="Get the startup configuration (saved configuration) from the device.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        # Configuration Tools (POST)
        Tool(
            name="configure_interface",
            description="Configure IP address on a router interface. This is a WRITE operation that changes device configuration.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "interface_name": {
                        "type": "string",
                        "description": "Interface name (e.g., 'FastEthernet0/0', 'FastEthernet0/1')"
                    },
                    "ip_address": {
                        "type": "string",
                        "description": "IP address to assign (e.g., '10.1.1.1')"
                    },
                    "subnet_mask": {
                        "type": "string",
                        "description": "Subnet mask (e.g., '255.255.255.0')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional interface description"
                    }
                },
                "required": ["device_name", "interface_name", "ip_address", "subnet_mask"]
            }
        ),
        Tool(
            name="configure_default_gateway",
            description="Configure default gateway (static route) on a router.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "gateway_ip": {
                        "type": "string",
                        "description": "Default gateway IP address"
                    }
                },
                "required": ["device_name", "gateway_ip"]
            }
        ),
        Tool(
            name="configure_dns",
            description="Configure DNS server on a router.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "dns_server": {
                        "type": "string",
                        "description": "DNS server IP address (default: 8.8.8.8)"
                    }
                },
                "required": ["device_name"]
            }
        ),
        Tool(
            name="configure_ospf",
            description="Configure OSPF routing protocol on a router. This enables dynamic routing between routers.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "process_id": {
                        "type": "integer",
                        "description": "OSPF process ID (typically 1)"
                    },
                    "networks": {
                        "type": "array",
                        "description": "List of networks to advertise in OSPF",
                        "items": {
                            "type": "object",
                            "properties": {
                                "network": {"type": "string"},
                                "wildcard": {"type": "string"},
                                "area": {"type": "integer"}
                            }
                        }
                    },
                    "default_route": {
                        "type": "boolean",
                        "description": "Whether to advertise default route (for R1 with internet access)"
                    }
                },
                "required": ["device_name", "process_id", "networks"]
            }
        ),
        Tool(
            name="verify_ospf_neighbors",
            description="Verify OSPF neighbor adjacencies and routing status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    }
                },
                "required": ["device_name"]
            }
        ),
        # Validation Tools (GET)
        Tool(
            name="validate_interface",
            description="Validate interface configuration and operational status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "interface_name": {
                        "type": "string",
                        "description": "Interface to validate"
                    },
                    "expected_ip": {
                        "type": "string",
                        "description": "Expected IP address (optional)"
                    }
                },
                "required": ["device_name", "interface_name"]
            }
        ),
        Tool(
            name="validate_connectivity",
            description="Test network connectivity using ping from a router to a target IP.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "target_ip": {
                        "type": "string",
                        "description": "Target IP address to ping"
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of ping packets (default: 5)"
                    }
                },
                "required": ["device_name", "target_ip"]
            }
        ),
        Tool(
            name="validate_ospf",
            description="Validate OSPF neighbor adjacencies and verify expected neighbors.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "expected_neighbors": {
                        "type": "array",
                        "description": "List of expected neighbor IP addresses (optional)",
                        "items": {"type": "string"}
                    }
                },
                "required": ["device_name"]
            }
        ),
        Tool(
            name="validate_routes",
            description="Validate routing table entries and verify expected routes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "expected_routes": {
                        "type": "array",
                        "description": "List of expected network prefixes (optional)",
                        "items": {"type": "string"}
                    }
                },
                "required": ["device_name"]
            }
        ),
        Tool(
            name="comprehensive_validation",
            description="Perform comprehensive validation of all device configurations and connectivity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    }
                },
                "required": ["device_name"]
            }
        ),
        # Basic Configuration Tools (Simple Demos)
        Tool(
            name="get_hostname",
            description="Get current hostname from device (Context-Aware - READ state)",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    }
                },
                "required": ["device_name"]
            }
        ),
        Tool(
            name="change_hostname",
            description="Change device hostname with safety check (POST - WRITE config)",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "new_hostname": {
                        "type": "string",
                        "description": "New hostname to set"
                    }
                },
                "required": ["device_name", "new_hostname"]
            }
        ),
        Tool(
            name="configure_interface_description",
            description="Add or change description on interface (POST with context check)",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "interface_name": {
                        "type": "string",
                        "description": "Interface name (e.g., 'FastEthernet0/1', 'Loopback0')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description text to set"
                    }
                },
                "required": ["device_name", "interface_name", "description"]
            }
        ),
        Tool(
            name="create_loopback",
            description="Create loopback interface with IP address (POST with duplicate prevention)",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "loopback_number": {
                        "type": "integer",
                        "description": "Loopback interface number (0-2147483647)"
                    },
                    "ip_address": {
                        "type": "string",
                        "description": "IP address for loopback (e.g., '1.1.1.1')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for loopback"
                    }
                },
                "required": ["device_name", "loopback_number", "ip_address"]
            }
        ),
        Tool(
            name="delete_loopback",
            description="Delete loopback interface (POST with existence check)",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "loopback_number": {
                        "type": "integer",
                        "description": "Loopback interface number to delete"
                    }
                },
                "required": ["device_name", "loopback_number"]
            }
        ),
        Tool(
            name="set_banner",
            description="Configure banner message on router (motd, login, or exec type)",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "banner_text": {
                        "type": "string",
                        "description": "Banner message text (multi-line supported)"
                    },
                    "banner_type": {
                        "type": "string",
                        "description": "Banner type: motd (message-of-the-day), login, or exec",
                        "enum": ["motd", "login", "exec"],
                        "default": "motd"
                    }
                },
                "required": ["device_name", "banner_text"]
            }
        ),
        Tool(
            name="remove_banner",
            description="Remove banner configuration from router",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    },
                    "banner_type": {
                        "type": "string",
                        "description": "Banner type to remove: motd, login, or exec",
                        "enum": ["motd", "login", "exec"],
                        "default": "motd"
                    }
                },
                "required": ["device_name"]
            }
        ),
        # Bootstrap Tools (Advanced Zero-Touch)
        Tool(
            name="check_ssh_status",
            description="Check if router has SSH enabled and accessible (Bootstrap diagnostic)",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_name": {
                        "type": "string",
                        "description": "Router name (R1 or R2)",
                        "enum": ["R1", "R2"]
                    }
                },
                "required": ["device_name"]
            }
        ),
        Tool(
            name="bootstrap_router",
            description="Auto-configure SSH on a router that doesn't have it yet (True Zero-Touch Bootstrap). Uses jumphost to telnet and configure target router.",
            inputSchema={
                "type": "object",
                "properties": {
                    "jumphost_device": {
                        "type": "string",
                        "description": "Router to use as jumphost (default: R1)",
                        "enum": ["R1", "R2"]
                    },
                    "target_ip": {
                        "type": "string",
                        "description": "IP address of target router to bootstrap"
                    },
                    "target_hostname": {
                        "type": "string",
                        "description": "Desired hostname for target router"
                    },
                    "username": {
                        "type": "string",
                        "description": "Username to create (default: admin)"
                    },
                    "password": {
                        "type": "string",
                        "description": "Password for user (default: admin123)"
                    }
                },
                "required": ["target_ip", "target_hostname"]
            }
        ),
        # Add advanced tools
        *get_advanced_tool_definitions(),
    ]



@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Execute the requested tool and return results
    """
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    try:
        
        if name == "get_interfaces":
            result = get_interfaces()
            
        elif name == "get_interface_detail":
            interface_name = arguments.get("interface_name")
            if not interface_name:
                result = {"success": False, "error": "interface_name is required"}
            else:
                result = get_interface_detail(interface_name)
                
        elif name == "get_device_status":
            result = get_device_status()
            
        elif name == "get_device_uptime":
            result = get_device_uptime()
            
        elif name == "get_resource_usage":
            result = get_memory_cpu_usage()
            
        elif name == "get_running_config":
            filter_keyword = arguments.get("filter_keyword")
            result = get_running_config(filter_keyword)
            
        elif name == "get_interface_config":
            interface_name = arguments.get("interface_name")
            if not interface_name:
                result = {"success": False, "error": "interface_name is required"}
            else:
                result = get_interface_config(interface_name)
                
        elif name == "get_startup_config":
            result = get_startup_config()
        
        # Configuration tools
        elif name == "configure_interface":
            device_name = arguments.get("device_name")
            interface_name = arguments.get("interface_name")
            ip_address = arguments.get("ip_address")
            subnet_mask = arguments.get("subnet_mask")
            description = arguments.get("description")
            
            if not all([device_name, interface_name, ip_address, subnet_mask]):
                result = {"success": False, "error": "Missing required parameters"}
            else:
                result = configure_interface(device_name, interface_name, ip_address, subnet_mask, description)
        
        elif name == "configure_default_gateway":
            device_name = arguments.get("device_name")
            gateway_ip = arguments.get("gateway_ip")
            
            if not all([device_name, gateway_ip]):
                result = {"success": False, "error": "Missing required parameters"}
            else:
                result = configure_default_gateway(device_name, gateway_ip)
        
        elif name == "configure_dns":
            device_name = arguments.get("device_name")
            dns_server = arguments.get("dns_server", "8.8.8.8")
            
            if not device_name:
                result = {"success": False, "error": "device_name is required"}
            else:
                result = configure_dns(device_name, dns_server)
        
        elif name == "configure_ospf":
            device_name = arguments.get("device_name")
            process_id = arguments.get("process_id")
            networks = arguments.get("networks")
            default_route = arguments.get("default_route", False)
            
            if not all([device_name, process_id, networks]):
                result = {"success": False, "error": "Missing required parameters"}
            else:
                result = configure_ospf(device_name, process_id, networks, default_route)
        
        elif name == "verify_ospf_neighbors":
            device_name = arguments.get("device_name")
            
            if not device_name:
                result = {"success": False, "error": "device_name is required"}
            else:
                result = verify_ospf_neighbors(device_name)
        
        # Validation tools
        elif name == "validate_interface":
            device_name = arguments.get("device_name")
            interface_name = arguments.get("interface_name")
            expected_ip = arguments.get("expected_ip")
            
            if not all([device_name, interface_name]):
                result = {"success": False, "error": "Missing required parameters"}
            else:
                result = validate_interface_config(device_name, interface_name, expected_ip)
        
        elif name == "validate_connectivity":
            device_name = arguments.get("device_name")
            target_ip = arguments.get("target_ip")
            count = arguments.get("count", 5)
            
            if not all([device_name, target_ip]):
                result = {"success": False, "error": "Missing required parameters"}
            else:
                result = validate_connectivity(device_name, target_ip, count)
        
        elif name == "validate_ospf":
            device_name = arguments.get("device_name")
            expected_neighbors = arguments.get("expected_neighbors")
            
            if not device_name:
                result = {"success": False, "error": "device_name is required"}
            else:
                result = validate_ospf_adjacency(device_name, expected_neighbors)
        
        elif name == "validate_routes":
            device_name = arguments.get("device_name")
            expected_routes = arguments.get("expected_routes")
            
            if not device_name:
                result = {"success": False, "error": "device_name is required"}
            else:
                result = validate_routing_table(device_name, expected_routes)
        
        elif name == "comprehensive_validation":
            device_name = arguments.get("device_name")
            
            if not device_name:
                result = {"success": False, "error": "device_name is required"}
            else:
                result = comprehensive_validation(device_name)
        
        # Basic configuration tools
        elif name == "get_hostname":
            device_name = arguments.get("device_name")
            
            if not device_name:
                result = {"success": False, "error": "device_name is required"}
            else:
                result = get_hostname(device_name)
        
        elif name == "change_hostname":
            device_name = arguments.get("device_name")
            new_hostname = arguments.get("new_hostname")
            
            if not all([device_name, new_hostname]):
                result = {"success": False, "error": "Missing required parameters"}
            else:
                result = change_hostname(device_name, new_hostname)
        
        elif name == "configure_interface_description":
            device_name = arguments.get("device_name")
            interface_name = arguments.get("interface_name")
            description = arguments.get("description")
            
            if not all([device_name, interface_name, description]):
                result = {"success": False, "error": "Missing required parameters"}
            else:
                result = configure_interface_description(device_name, interface_name, description)
        
        elif name == "create_loopback":
            device_name = arguments.get("device_name")
            loopback_number = arguments.get("loopback_number")
            ip_address = arguments.get("ip_address")
            description = arguments.get("description")
            
            if not all([device_name, loopback_number is not None, ip_address]):
                result = {"success": False, "error": "Missing required parameters"}
            else:
                result = create_loopback(device_name, loopback_number, ip_address, description)
        
        elif name == "delete_loopback":
            device_name = arguments.get("device_name")
            loopback_number = arguments.get("loopback_number")
            
            if not all([device_name, loopback_number is not None]):
                result = {"success": False, "error": "Missing required parameters"}
            else:
                result = delete_loopback(device_name, loopback_number)
        
        elif name == "set_banner":
            device_name = arguments.get("device_name")
            banner_text = arguments.get("banner_text")
            banner_type = arguments.get("banner_type", "motd")
            
            if not all([device_name, banner_text]):
                result = {"success": False, "error": "Missing required parameters"}
            else:
                result = set_banner(device_name, banner_text, banner_type)
        
        elif name == "remove_banner":
            device_name = arguments.get("device_name")
            banner_type = arguments.get("banner_type", "motd")
            
            if not device_name:
                result = {"success": False, "error": "device_name is required"}
            else:
                result = remove_banner(device_name, banner_type)
        
        # Bootstrap tools
        elif name == "check_ssh_status":
            device_name = arguments.get("device_name")
            
            if not device_name:
                result = {"success": False, "error": "device_name is required"}
            else:
                result = check_router_ssh_status(device_name)
        
        elif name == "bootstrap_router":
            jumphost_device = arguments.get("jumphost_device", "R1")
            target_ip = arguments.get("target_ip")
            target_hostname = arguments.get("target_hostname")
            username = arguments.get("username", "admin")
            password = arguments.get("password", "admin123")
            
            if not all([target_ip, target_hostname]):
                result = {"success": False, "error": "target_ip and target_hostname are required"}
            else:
                result = bootstrap_router_ssh(jumphost_device, target_ip, target_hostname, username, password)
            
        # Try advanced tools handler
        else:
            result = handle_advanced_tools(name, arguments)
            if result is None:
                result = {"success": False, "error": f"Unknown tool: {name}"}
        
        
        if result.get("success"):
            
            response_text = f"✅ {result.get('message', 'Success')}\n\n"
            
            if 'output' in result:
                response_text += f"Output:\n{result['output']}"
            elif 'config' in result:
                response_text += f"Configuration:\n{result['config']}"
            elif 'version_info' in result:
                response_text += f"Version Info:\n{result['version_info']}"
            else:
                
                for key, value in result.items():
                    if key not in ['success', 'message', 'command', 'commands']:
                        response_text += f"\n{key}: {value}"
                        
        else:
            response_text = f"❌ Error: {result.get('error', 'Unknown error')}"
        
        return [TextContent(type="text", text=response_text)]
        
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        error_text = f"❌ Exception occurred: {str(e)}"
        return [TextContent(type="text", text=error_text)]



async def main():
    """
    Main entry point for the MCP server
    """
    logger.info("Starting Netmiko MCP Server...")
    logger.info("Server is ready to accept connections from MCP clients")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())