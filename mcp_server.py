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

# Import our custom tools
from tools.get_interfaces import get_interfaces, get_interface_detail
from tools.get_device_status import get_device_status, get_device_uptime, get_memory_cpu_usage
from tools.get_running_config import get_running_config, get_interface_config, get_startup_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("netmiko-mcp-server")

# Create MCP server instance
app = Server("netmiko-mcp-server")


# Define available tools
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
    ]


# Handle tool execution
@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Execute the requested tool and return results
    """
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    try:
        # Route to appropriate tool based on name
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
            
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}
        
        # Format the response
        if result.get("success"):
            # Format successful response
            response_text = f"✅ {result.get('message', 'Success')}\n\n"
            
            if 'output' in result:
                response_text += f"Output:\n{result['output']}"
            elif 'config' in result:
                response_text += f"Configuration:\n{result['config']}"
            elif 'version_info' in result:
                response_text += f"Version Info:\n{result['version_info']}"
            else:
                # Include all relevant fields
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


# Main entry point
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