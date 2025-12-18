#!/usr/bin/env python3
"""
Simple CLI Chat: Ollama + MCP Tools
Network automation assistant with local LLM
"""

import requests
import json
import sys
import re
from tools.get_interfaces import get_interfaces
from tools.get_device_status import get_device_status
from tools.configure_interface import configure_interface
from tools.validate_config import validate_connectivity

class OllamaMCPChat:
    def __init__(self, model="qwen3:14b"):
        self.model = model
        self.ollama_url = "http://localhost:11434"
        
        # Network topology context for AI
        self.network_context = """You are a network automation assistant for a GNS3 lab with this topology:

NETWORK TOPOLOGY:
- R1 (NetAutoR1): IP 192.168.242.129
  * FastEthernet0/0: Management (to Cloud/Wi-Fi)
  * FastEthernet0/1: 10.1.1.1/24 - Link to R2
  * FastEthernet1/0: 192.168.10.1/24 - LAN for PC1

- R2 (NetAutoR2): IP 10.1.1.2
  * FastEthernet0/0: 10.1.1.2/24 - Link to R1
  * FastEthernet0/1: 192.168.20.1/24 - LAN for PC2

- PC1: 192.168.10.10 (gateway: R1 f1/0)
- PC2: 192.168.20.10 (gateway: R2 f0/1)

AVAILABLE TOOLS:
You can call these Python functions to interact with the routers:
1. get_interfaces(device) - Get all interfaces from R1 or R2
2. get_device_status(device) - Get device info, version, uptime
3. validate_connectivity(device, target_ip) - Test ping from router
4. configure_interface(device, interface, ip, mask, desc) - Configure interface

When user asks about the network, suggest which tool to use or I will execute it automatically.
"""
        
        print("=" * 70)
        print("🤖 Ollama + MCP Network Assistant")
        print("=" * 70)
        print(f"Model: {self.model}")
        print("Network: R1 (192.168.242.129) ↔ R2 (10.1.1.2)")
        print("MCP Tools: ✅ Ready")
        print("=" * 70)
        print("\nCommands:")
        print("  - Ask anything about the network")
        print("  - Type 'tools' to see available tools")
        print("  - Type 'topology' to see network diagram")
        print("  - Type 'exit' to quit")
        print("=" * 70)
    
    def chat(self, user_message):
        """Send message to Ollama"""
        full_prompt = f"{self.network_context}\n\nUser: {user_message}\n\nAssistant:"
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                },
                timeout=120
            )
            
            if response.status_code == 200:
                ai_response = response.json()["response"]
                
                # Check if we should execute tools
                tool_result = self.auto_execute_tools(user_message)
                
                if tool_result:
                    # AI sees the actual tool result
                    return self.chat_with_tool_result(user_message, tool_result, ai_response)
                
                return ai_response
            else:
                return f"❌ Ollama error: {response.status_code}"
                
        except requests.Timeout:
            return "❌ Request timeout. Model might be too slow or not loaded."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def auto_execute_tools(self, user_message):
        """Automatically detect and execute tools based on user query"""
        msg_lower = user_message.lower()
        
        # Detect get_interfaces
        if any(word in msg_lower for word in ["interface", "show ip int", "list interface"]):
            device = "R2" if "r2" in msg_lower else "R1"
            print(f"\n🔧 Auto-executing: get_interfaces('{device}')")
            result = get_interfaces(device)
            if result["success"]:
                return {"tool": "get_interfaces", "device": device, "output": result["output"]}
        
        # Detect device status
        if any(word in msg_lower for word in ["status", "version", "uptime", "device info"]):
            device = "R2" if "r2" in msg_lower else "R1"
            print(f"\n🔧 Auto-executing: get_device_status('{device}')")
            result = get_device_status(device)
            if result["success"]:
                return {"tool": "get_device_status", "device": device, "output": str(result)}
        
        # Detect ping/connectivity
        if any(word in msg_lower for word in ["ping", "reach", "connectivity", "can connect"]):
            device = "R1"
            target = "10.1.1.2"  # Default R1 ping R2
            
            # Try to extract IP
            ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', user_message)
            if ip_match:
                target = ip_match.group(0)
            
            if "r2" in msg_lower and "r1" not in msg_lower:
                device = "R2"
                target = "10.1.1.1"
            
            print(f"\n🔧 Auto-executing: validate_connectivity('{device}', '{target}')")
            result = validate_connectivity(device, target)
            return {"tool": "validate_connectivity", "device": device, "target": target, "output": str(result)}
        
        return None
    
    def chat_with_tool_result(self, question, tool_result, initial_response):
        """Send tool results back to AI for analysis"""
        result_prompt = f"""{self.network_context}

User asked: {question}

I executed: {tool_result['tool']}({tool_result.get('device', '')})
Real output from network:
{tool_result['output']}

Analyze this output and answer the user's question with specific details from the real data.
"""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": result_prompt,
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"\n✅ Tool executed successfully!\n\n{tool_result['output']}"
                
        except:
            return f"\n✅ Tool executed successfully!\n\n{tool_result['output']}"
    
    def interactive(self):
        """Main interactive chat loop"""
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "exit":
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == "tools":
                    print("\n🔧 Available MCP Tools:")
                    print("  • get_interfaces(device) - Show all interfaces")
                    print("  • get_device_status(device) - Device info & uptime")
                    print("  • validate_connectivity(device, ip) - Test ping")
                    print("  • configure_interface(device, intf, ip, mask) - Configure IP")
                    continue
                
                if user_input.lower() == "topology":
                    print("\n🌐 Network Topology:")
                    print("  Internet/Cloud")
                    print("       |")
                    print("    [R1:f0/0]  192.168.242.129")
                    print("       |")
                    print("    [R1:f0/1] ←→ [R2:f0/0]  (10.1.1.0/24)")
                    print("       |              |")
                    print("    [R1:f1/0]     [R2:f0/1]")
                    print("       |              |")
                    print("      PC1            PC2")
                    print("  (192.168.10.10) (192.168.20.10)")
                    continue
                
                print("\n🤖 AI:", end=" ", flush=True)
                response = self.chat(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

def main():
    """Entry point"""
    
    # Check Ollama is running
    print("🔍 Checking Ollama...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama not responding!")
            print("\nStart Ollama first:")
            print("  ollama serve")
            sys.exit(1)
    except:
        print("❌ Cannot connect to Ollama!")
        print("\nMake sure Ollama is running:")
        print("  ollama serve")
        print("\nOr check if model is downloaded:")
        print("  ollama pull qwen3:14b")
        sys.exit(1)
    
    print("✅ Ollama is running\n")
    
    # Start chat
    chat = OllamaMCPChat(model="qwen3:14b")
    chat.interactive()

if __name__ == "__main__":
    main()