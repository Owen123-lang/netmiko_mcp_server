# 🚀 Zero-Touch Configuration Guide

## Overview

This guide explains how to set up and use the **Zero-Touch Configuration** feature with 2 Cisco routers in GNS3. The system allows an LLM (Claude) to automatically configure network devices based on natural language requests.

---

## 🎯 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Claude Desktop (LLM)                   │
│              Natural Language Interface                 │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Netmiko MCP Server (Python)                │
│    - Interface Configuration Tools (POST)               │
│    - OSPF Configuration Tools (POST)                    │
│    - Validation Tools (GET)                             │
└────────────────────┬────────────────────────────────────┘
                     │ SSH (Netmiko)
                     ▼
┌─────────────────────────────────────────────────────────┐
│              GNS3 Topology (2 Routers)                  │
│                                                         │
│   ┌──────────┐              ┌──────────┐              │
│   │    R1    │◄────────────►│    R2    │              │
│   │ (NetAutoR1) │  OSPF     │ (NetAutoR2) │           │
│   └──────────┘   10.1.1.x   └──────────┘              │
│        │                                                │
│        │ Cloud Bridge                                   │
│        ▼                                                │
│   [Wi-Fi: 172.16.10.x]                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Network Topology

### **Router 1 (R1) - NetAutoR1**
- **Management IP:** `172.16.10.250` (via Wi-Fi Cloud)
- **Internal IP:** `10.1.1.1/24` (link to R2)
- **Interfaces:**
  - `FastEthernet0/0`: Cloud bridge to Wi-Fi (172.16.10.250)
  - `FastEthernet0/1`: Link to R2 (10.1.1.1)
- **OSPF:** Process 1, advertises default route

### **Router 2 (R2) - NetAutoR2**
- **Management IP:** `10.1.1.2/24` (reachable via R1)
- **Interfaces:**
  - `FastEthernet0/0`: Link to R1 (10.1.1.2)
- **OSPF:** Process 1, receives default route from R1

---

## 🛠️ GNS3 Setup Instructions

### **Step 1: Create GNS3 Project**

1. Open GNS3
2. Create new project: `NetAuto_ZeroTouch`
3. Import Cisco 7200 router (if not already done)

### **Step 2: Build Topology**

1. **Add Cloud Node:**
   - Drag Cloud to workspace
   - Configure: Enable Wi-Fi adapter (`172.16.10.x` network)

2. **Add Router 1 (R1):**
   - Drag Cisco 7200 router
   - Name: `R1`
   - Connect `FastEthernet0/0` to Cloud Wi-Fi adapter
   - Connect `FastEthernet0/1` to R2

3. **Add Router 2 (R2):**
   - Drag Cisco 7200 router
   - Name: `R2`
   - Connect `FastEthernet0/0` to R1's `FastEthernet0/1`

### **Step 3: Start Routers**

- Right-click R1 → Start
- Right-click R2 → Start
- Wait for both to boot (green icon)

### **Step 4: Manual Initial Configuration**

#### **R1 Console:**

```cisco
enable
configure terminal

hostname NetAutoR1

! Configure management interface (to Wi-Fi)
interface FastEthernet0/0
 description Link to Laptop WiFi
 ip address 172.16.10.250 255.255.255.0
 no shutdown
 exit

! Configure internal interface (to R2)
interface FastEthernet0/1
 description Link to R2
 ip address 10.1.1.1 255.255.255.0
 no shutdown
 exit

! Enable SSH
ip domain-name netauto.local
crypto key generate rsa modulus 1024
ip ssh version 2

! Create user
username admin privilege 15 secret admin123
enable secret admin123

! Configure VTY
line vty 0 4
 login local
 transport input ssh
 exit

! Configure DNS
ip domain-lookup
ip name-server 8.8.8.8

! Save
exit
write memory
```

#### **R2 Console:**

```cisco
enable
configure terminal

hostname NetAutoR2

! Configure interface (to R1)
interface FastEthernet0/0
 description Link to R1
 ip address 10.1.1.2 255.255.255.0
 no shutdown
 exit

! Enable SSH
ip domain-name netauto.local
crypto key generate rsa modulus 1024
ip ssh version 2

! Create user
username admin privilege 15 secret admin123
enable secret admin123

! Configure VTY
line vty 0 4
 login local
 transport input ssh
 exit

! Configure DNS
ip domain-lookup
ip name-server 8.8.8.8

! Save
exit
write memory
```

### **Step 5: Verify Connectivity**

From your laptop Command Prompt:

```cmd
# Test R1
ping 172.16.10.250
ssh admin@172.16.10.250

# Test R1 -> R2
ssh admin@172.16.10.250
ping 10.1.1.2
exit
```

---

## 🐍 Python Configuration

### **Update config.py**

The [`config.py`](config.py:1) is already configured for 2 routers:

```python
ROUTER1_DEVICE = {
    "host": "172.16.10.250",  # R1 via Wi-Fi
    ...
}

ROUTER2_DEVICE = {
    "host": "10.1.1.2",  # R2 via R1
    ...
}

DEVICES = {
    "R1": ROUTER1_DEVICE,
    "R2": ROUTER2_DEVICE,
}
```

---

## 🧪 Testing

### **Option 1: Python Test Script**

Run the automated test:

```bash
cd netmiko_mcp_server
python test_zero_touch.py
```

**What it does:**
1. ✅ Configures interfaces on R1 and R2
2. ✅ Configures OSPF on both routers
3. ✅ Tests connectivity between routers
4. ✅ Verifies OSPF adjacency
5. ✅ Runs comprehensive validation

### **Option 2: Manual Python Test**

```python
from tools.configure_interface import configure_interface
from tools.configure_ospf import configure_ospf
from tools.validate_config import validate_connectivity

# Configure R1 interface
result = configure_interface(
    device_name="R1",
    interface_name="FastEthernet0/1",
    ip_address="10.1.1.1",
    subnet_mask="255.255.255.0",
    description="Link to R2"
)
print(result)

# Configure OSPF on R1
result = configure_ospf(
    device_name="R1",
    process_id=1,
    networks=[{"network": "10.0.0.0", "wildcard": "0.255.255.255", "area": 0}],
    default_route=True
)
print(result)

# Test connectivity
result = validate_connectivity("R1", "10.1.1.2")
print(result)
```

---

## 💬 Using with Claude Desktop

### **Available Tools (17 Total)**

#### **Configuration Tools (POST - Write Operations):**

1. **`configure_interface`** - Set IP address on interface
   ```
   "Configure FastEthernet0/1 on R1 with IP 10.1.1.1/24"
   ```

2. **`configure_default_gateway`** - Set default route
   ```
   "Set default gateway on R2 to 10.1.1.1"
   ```

3. **`configure_dns`** - Configure DNS server
   ```
   "Configure DNS 8.8.8.8 on R1"
   ```

4. **`configure_ospf`** - Enable OSPF routing
   ```
   "Configure OSPF process 1 on R1, advertise network 10.0.0.0 with wildcard 0.255.255.255 in area 0"
   ```

5. **`verify_ospf_neighbors`** - Check OSPF neighbors
   ```
   "Show me OSPF neighbors on R1"
   ```

#### **Validation Tools (GET - Read Operations):**

6. **`validate_interface`** - Verify interface config
7. **`validate_connectivity`** - Test ping between devices
8. **`validate_ospf`** - Verify OSPF adjacencies
9. **`validate_routes`** - Check routing table
10. **`comprehensive_validation`** - Full device validation

#### **Original Tools (GET):**

11. `get_interfaces` - List all interfaces
12. `get_interface_detail` - Detailed interface info
13. `get_device_status` - Device version/status
14. `get_device_uptime` - Uptime information
15. `get_resource_usage` - CPU/memory usage
16. `get_running_config` - Show running config
17. `get_interface_config` - Interface configuration

### **Example Claude Conversations**

**Scenario 1: Configure OSPF from Scratch**

```
User: "I have 2 routers R1 and R2. R1 has interface Fa0/1 with IP 10.1.1.1 
       and R2 has Fa0/0 with IP 10.1.1.2. Please configure OSPF so they can 
       communicate."

Claude: [Uses tools]:
1. configure_ospf on R1 (process 1, network 10.0.0.0/8, area 0, default route)
2. configure_ospf on R2 (process 1, network 10.0.0.0/8, area 0)
3. validate_ospf on both routers
4. validate_connectivity (R1 -> R2 and R2 -> R1)

Result: "OSPF configured successfully. R1 and R2 are FULL neighbors. 
         Ping test shows 100% success rate."
```

**Scenario 2: Troubleshooting**

```
User: "Why can't R2 reach the internet?"

Claude: [Uses tools]:
1. get_interfaces on R2 (check interface status)
2. validate_routes on R2 (check for default route)
3. validate_ospf on R2 (verify OSPF neighbors)
4. validate_connectivity from R2 to R1

Analysis: "R2 is missing default route. R1 should advertise default route 
          via OSPF but it's not configured. Let me fix it..."

[Applies fix]:
- configure_ospf on R1 with default_route=True
- verify_ospf_neighbors on both routers
- validate_connectivity from R2 to external IP

Result: "Fixed! R1 now advertises default route. R2 learned it via OSPF."
```

---

## 🔧 Configuration Files

### **[`config.py`](config.py:1)** - Device credentials and network config

```python
DEVICES = {"R1": {...}, "R2": {...}}
NETWORK_CONFIG = {
    "R1": {interfaces, ospf, ...},
    "R2": {interfaces, ospf, ...}
}
```

### **[`mcp_server.py`](mcp_server.py:1)** - MCP server with 17 tools

Registers all configuration, validation, and monitoring tools.

### **Tool Files:**

- [`tools/configure_interface.py`](tools/configure_interface.py:1) - Interface config
- [`tools/configure_ospf.py`](tools/configure_ospf.py:1) - OSPF config
- [`tools/validate_config.py`](tools/validate_config.py:1) - Validation functions

---

## ⚠️ Important Notes

### **R2 Connectivity via R1**

Since R2 is not directly connected to your laptop Wi-Fi, you access it through R1:

1. **Direct SSH to R1:** `ssh admin@172.16.10.250`
2. **From R1, SSH to R2:** `ssh admin@10.1.1.2`

Python tools handle this automatically using the configured host IPs.

### **OSPF Neighbor Requirements**

For OSPF to work:
- ✅ Interfaces must be UP/UP
- ✅ IP addresses must be in same subnet (10.1.1.x/24)
- ✅ OSPF process ID can be different (usually both use 1)
- ✅ Area must match (both in area 0)
- ✅ No authentication mismatch

Wait 30-40 seconds after OSPF configuration for neighbors to reach FULL state.

### **Connectivity Suicide Prevention**

The system prevents accidental lockout:
- ✅ Never shutdown management interface (Fa0/0 on R1)
- ✅ Always verify configuration before applying
- ✅ Validation tools check current state before changes

---

## 🎓 Zero-Touch Configuration Workflow

### **Phase 1: Intent Analysis**
Claude receives natural language request (e.g., "Configure OSPF")

### **Phase 2: Context Awareness (MCP Tools)**
- Check current device status [`get_device_status`](tools/get_device_status.py:1)
- Check existing configuration [`get_running_config`](tools/get_running_config.py:1)
- Validate interface status [`validate_interface`](tools/validate_config.py:1)

### **Phase 3: Conflict Resolution**
- Compare desired vs. current state
- Detect IP conflicts
- Check for connectivity suicide scenarios

### **Phase 4: Configuration Generation**
- Generate Cisco IOS commands
- Apply via Netmiko [`configure_interface`](tools/configure_interface.py:1) / [`configure_ospf`](tools/configure_ospf.py:1)

### **Phase 5: Validation**
- Verify configuration applied [`validate_interface`](tools/validate_config.py:1)
- Test connectivity [`validate_connectivity`](tools/validate_config.py:1)
- Validate OSPF [`validate_ospf`](tools/validate_config.py:1)

---

## 📊 Success Criteria

✅ **Configuration Applied:**
- Interfaces configured with correct IPs
- OSPF enabled and running
- No syntax errors

✅ **Connectivity Established:**
- Ping R1 ↔ R2: 100% success
- SSH access maintained to both routers

✅ **OSPF Adjacency:**
- Neighbors in FULL state
- Routes exchanged
- Default route propagated (R1 → R2)

✅ **Validation Passed:**
- All interfaces UP/UP
- Routing table populated
- Comprehensive validation: PASS

---

## 🐛 Troubleshooting

### **Issue: OSPF Neighbors Not Forming**

**Symptoms:** `show ip ospf neighbor` is empty

**Fixes:**
1. Check interface status: `show ip interface brief`
2. Verify OSPF configuration: `show ip ospf`
3. Check network statements: `show run | section ospf`
4. Verify subnet masks match on both sides
5. Clear OSPF process: `clear ip ospf process`

### **Issue: Cannot SSH to R2**

**Symptoms:** `ssh admin@10.1.1.2` times out

**Fixes:**
1. Verify R1 can ping R2: `ping 10.1.1.2` from R1
2. Check R2 VTY configuration: `show run | section line vty`
3. Verify SSH enabled: `show ip ssh` on R2
4. Test from laptop via R1 as jump host

### **Issue: Python Script Fails**

**Symptoms:** Connection timeout or authentication error

**Fixes:**
1. Verify router IPs in [`config.py`](config.py:1)
2. Test manual SSH: `ssh admin@172.16.10.250`
3. Check username/password correct
4. Verify SSH enabled on router
5. Check firewall not blocking port 22

---

## 📚 Additional Resources

- **Cisco IOS OSPF Configuration:** [cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/7039-1.html](https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/7039-1.html)
- **Netmiko Documentation:** [github.com/ktbyers/netmiko](https://github.com/ktbyers/netmiko)
- **MCP Protocol:** [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **GNS3 Cloud Bridging:** [docs.gns3.com](https://docs.gns3.com/docs/using-gns3/advanced/connect-gns3-to-the-internet)

---

## 🎉 Congratulations!

You now have a fully functional **Zero-Touch Configuration** system capable of:
- ✅ Configuring network devices via natural language
- ✅ Automatically setting up OSPF routing
- ✅ Validating configurations before and after changes
- ✅ Preventing connectivity suicide
- ✅ Providing intelligent troubleshooting assistance

**Next Steps:**
1. Test with Claude Desktop
2. Experiment with more complex topologies
3. Add NAT configuration for R1 internet access
4. Implement more advanced features (ACLs, VLANs, etc.)