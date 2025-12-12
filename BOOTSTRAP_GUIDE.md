# 🚀 Bootstrap Router Guide - True Zero-Touch Configuration

Panduan lengkap untuk **auto-configure router** yang belum memiliki SSH menggunakan **Bootstrap Tool**.

---

## 🎯 What is Bootstrap?

**Bootstrap** adalah fitur advanced yang memungkinkan sistem **mengkonfigurasi router baru** yang belum memiliki SSH access. Ini adalah **True Zero-Touch** karena:

1. **No Manual Console Access** - Tidak perlu login manual ke console
2. **Auto-Detection** - Sistem detect router mana yang perlu setup
3. **Multi-Hop SSH** - Menggunakan R1 sebagai jumphost untuk akses R2
4. **Self-Healing** - Sistem otomatis setup SSH jika belum ada

---

## 📊 How It Works

### Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. LLM (Claude) via MCP                                     │
│     ↓                                                        │
│  2. Python MCP Server                                        │
│     ↓                                                        │
│  3. Check R2 SSH Status ──→ SSH NOT AVAILABLE               │
│     ↓                                                        │
│  4. Bootstrap Tool Activated                                 │
│     ↓                                                        │
│  5. SSH to R1 (Jumphost) ✅                                  │
│     ↓                                                        │
│  6. Telnet from R1 → R2                                      │
│     ↓                                                        │
│  7. Configure SSH on R2:                                     │
│     - Set hostname                                           │
│     - Generate crypto keys                                   │
│     - Enable SSH v2                                          │
│     - Create user account                                    │
│     - Configure VTY lines                                    │
│     ↓                                                        │
│  8. Verify SSH Works ✅                                      │
│     ↓                                                        │
│  9. R2 Now Accessible! 🎉                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tools Available

### 1. `check_ssh_status`
**Purpose:** Diagnose if router has SSH enabled

**Usage:**
```python
from tools.bootstrap_router import check_router_ssh_status

result = check_router_ssh_status("R2")
print(result)
```

**Output Example:**
```json
{
  "success": false,
  "device": "R2",
  "error": "Cannot check SSH status: Failed to establish connection",
  "ssh_enabled": false,
  "message": "Device not accessible via SSH (may need bootstrapping)"
}
```

---

### 2. `bootstrap_router`
**Purpose:** Auto-configure SSH on target router

**Usage:**
```python
from tools.bootstrap_router import bootstrap_router_ssh

result = bootstrap_router_ssh(
    jumphost_device="R1",        # Router with SSH access
    target_ip="10.1.1.2",        # IP of router to bootstrap
    target_hostname="NetAutoR2", # Desired hostname
    username="admin",            # User to create
    password="admin123"          # Password
)
```

**Output Example (Success):**
```json
{
  "success": true,
  "message": "Successfully bootstrapped SSH on NetAutoR2 (10.1.1.2)",
  "jumphost": "R1",
  "target_ip": "10.1.1.2",
  "target_hostname": "NetAutoR2",
  "username": "admin",
  "ssh_verified": true,
  "test_output": "Cisco IOS Software, 7200 Software..."
}
```

---

## 🚀 Step-by-Step Demo

### Scenario: R2 Tidak Punya SSH Access

**Starting Condition:**
- R1: SSH ✅ (IP: 192.168.242.129)
- R2: Network reachable ✅ (IP: 10.1.1.2) but SSH ❌

---

### Method 1: Via Python Script (Standalone)

```bash
cd netmiko_mcp_server
python tools/bootstrap_router.py
```

**What Happens:**
```
=== Testing Bootstrap Router SSH ===

Checking R2 SSH status...
R2 SSH Status: {'success': False, 'ssh_enabled': False, ...}

R2 needs bootstrapping. Starting bootstrap process...

[1/5] Connecting to jumphost R1...
[2/5] Testing connectivity to 10.1.1.2...
✓ Target 10.1.1.2 is reachable
[3/5] Initiating telnet to 10.1.1.2...
[4/5] Configuring SSH on target router...
[5/5] Verifying SSH access to 10.1.1.2...

=== Bootstrap Result ===
Success: True
Message: Successfully bootstrapped SSH on NetAutoR2 (10.1.1.2)

✅ R2 is now accessible via SSH!
   You can now use: ssh admin@10.1.1.2
```

---

### Method 2: Via MCP Server (Interactive with Claude)

**Step 1:** Start MCP Server
```bash
cd netmiko_mcp_server
python mcp_server.py
```

**Step 2:** Open Claude Desktop (auto-connects via MCP)

**Step 3:** Use Natural Language

```
Prompt 1: "Check SSH status of R2"
→ Claude calls check_ssh_status("R2")
→ Result: SSH not available

Prompt 2: "Bootstrap R2 to enable SSH access"
→ Claude calls bootstrap_router(...)
→ System auto-configures R2
→ Result: R2 now has SSH! ✅
```

---

## 📝 Configuration Applied by Bootstrap

When you run bootstrap, this configuration is applied to R2:

```cisco
configure terminal

! Set hostname
hostname NetAutoR2

! Domain name (required for SSH)
ip domain-name netauto.local

! Generate RSA keys (2048 bits)
crypto key generate rsa
2048

! Enable SSH version 2
ip ssh version 2

! Create admin user
username admin privilege 15 secret admin123

! Configure VTY lines for SSH
line vty 0 4
 login local
 transport input ssh
 exec-timeout 0 0
exit

! Configure console
line con 0
 exec-timeout 0 0
 privilege level 15
exit

! Save configuration
end
write memory
```

---

## ✅ Verification Steps

### After Bootstrap, Verify R2 is Accessible

**Test 1: SSH from Host Machine**
```bash
ssh admin@10.1.1.2
# Password: admin123
```

**Test 2: Check via MCP Tools**
```
Prompt: "Get hostname from R2"
→ Result: "NetAutoR2" ✅

Prompt: "Show interfaces on R2"
→ Result: Interface list ✅

Prompt: "Get device status from R2"
→ Result: Version info ✅
```

---

## 🎓 Research Paper Value

Bootstrap Tool demonstrates advanced concepts:

### 1. **Multi-Hop SSH**
- System uses R1 as jumphost to reach R2
- Shows intelligent network traversal

### 2. **Self-Healing Network**
- Automatic detection of unconfigured devices
- Zero manual intervention required

### 3. **Context-Aware Bootstrap**
- System checks if SSH exists BEFORE attempting config
- Prevents redundant operations

### 4. **Hybrid RAG Application**
```
User: "Setup R2"
  ↓
LLM: Checks knowledge base → "Need SSH first"
  ↓
LLM: Calls check_ssh_status("R2")
  ↓
Context: "R2 SSH not available"
  ↓
LLM: Decision → Call bootstrap_router(...)
  ↓
Result: R2 configured! ✅
```

### 5. **Hallucination Prevention**
- Tool validates each step (ping, telnet, SSH verify)
- If verification fails, reports actual state
- No blind assumptions about device status

---

## 🔧 Troubleshooting

### Issue 1: Telnet Connection Failed
```
Error: Cannot telnet to target
```

**Solution:**
1. Check R2 is pingable from R1
2. Verify R2 console is accessible (not stuck at login)
3. Ensure no existing telnet sessions blocking

---

### Issue 2: SSH Verification Failed
```
Error: SSH configuration completed but verification failed
```

**Solution:**
- Configuration was applied successfully
- SSH service may need 10-30 seconds to start
- Wait a moment, then manually test: `ssh admin@10.1.1.2`

---

### Issue 3: Already Bootstrapped
```
Message: R2 already has SSH enabled
```

**Solution:**
- This is GOOD! R2 already accessible
- Skip bootstrap, use R2 directly

---

## 🎯 Use Cases

### Use Case 1: Initial Deployment
**Scenario:** Fresh router from factory  
**Solution:** Bootstrap auto-configures everything

### Use Case 2: Password Recovery
**Scenario:** Lost SSH password but have console  
**Solution:** Bootstrap recreates SSH access

### Use Case 3: Multi-Site Deployment
**Scenario:** 10 new routers need configuration  
**Solution:** Bootstrap all from single jumphost

### Use Case 4: Research Demo
**Scenario:** Show True Zero-Touch capability  
**Solution:** Live demo of auto-configuration

---

## 📊 Success Metrics

**Bootstrap is successful when:**
- ✅ R2 hostname changed to NetAutoR2
- ✅ SSH version 2 enabled
- ✅ Admin user created
- ✅ VTY lines configured
- ✅ SSH connection verified
- ✅ All MCP tools can access R2

**Verification Command:**
```bash
# From host machine
ssh admin@10.1.1.2
NetAutoR2# show ip ssh
SSH Enabled - version 2.0 ✅
```

---

## 🚀 Next Steps After Bootstrap

Once R2 is bootstrapped:

1. **Configure Interfaces:**
   ```
   "Configure FastEthernet0/1 on R2 with IP 10.1.2.1/24"
   ```

2. **Enable OSPF:**
   ```
   "Enable OSPF process 1 on R2 for network 10.0.0.0"
   ```

3. **Test Connectivity:**
   ```
   "Ping 10.1.1.1 from R2"
   ```

4. **Full Demo:**
   ```bash
   python test_simple_demo.py  # Now works with both R1 and R2!
   ```

---

## 📚 Technical Details

### Security Considerations
- Bootstrap uses telnet (unencrypted) for initial config
- SSH is configured immediately for secure future access
- Default credentials should be changed in production

### Network Requirements
- Jumphost must have IP connectivity to target
- Target router must accept telnet (default on Cisco)
- No ACLs blocking telnet/SSH

### Performance
- Bootstrap process: ~30-60 seconds
- SSH key generation: ~5-10 seconds
- Verification: ~3-5 seconds

---

## 🎉 Conclusion

Bootstrap Tool enables **True Zero-Touch Configuration**:
- No manual console access needed
- Automatic SSH setup
- Self-healing network capability
- Perfect for research demonstration

**Key Innovation:** System can configure devices that aren't even configured yet! 🚀

---

**Ready to bootstrap R2? Run:**
```bash
cd netmiko_mcp_server
python tools/bootstrap_router.py
```

Or via Claude:
```
"Bootstrap R2 router to enable SSH access"
```

**Let the automation begin! 🎯**