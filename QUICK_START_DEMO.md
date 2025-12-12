# ⚡ Quick Start - Run Demo in 3 Minutes

Panduan singkat untuk langsung menjalankan demo Zero-Touch Configuration.

---

## 🎯 Prerequisites Check (30 seconds)

```bash
# 1. Check GNS3 VM running
# 2. Check R1 router started (192.168.242.129)
# 3. Ping test
ping 192.168.242.129

# 4. SSH test (optional)
ssh admin@192.168.242.129
# Password: admin123
```

---

## 🚀 Run Demo (1 minute)

### Option A: Standalone Test Script

```bash
cd netmiko_mcp_server
python test_simple_demo.py
```

**Expected Result:**
```
======================================================================
  SIMPLE DEMO: Context-Aware Zero-Touch Configuration
======================================================================

✅ PASS  Test 1: Read Current Hostname
✅ PASS  Test 2: Change Hostname
✅ PASS  Test 3: Add Interface Description
✅ PASS  Test 4: Create Loopback
✅ PASS  Test 5: Prevent Duplicate Loopback
✅ PASS  Test 6: Verify All Changes

Results: 6/6 tests passed (100%)

🎉 ALL TESTS PASSED! 🎉
```

---

### Option B: Interactive with Claude Desktop

```bash
# Terminal 1: Start MCP Server
cd netmiko_mcp_server
python mcp_server.py

# Terminal 2: Open Claude Desktop
# It will auto-connect via MCP
```

**Try these prompts in Claude:**

```
1. "Check the hostname of R1"
2. "Change R1's hostname to TestRouter"
3. "Add description 'Demo Port' to FastEthernet0/1 on R1"
4. "Create loopback 10 with IP 10.10.10.10 on R1"
```

---

## 📊 What You'll See

### Test 1: GET (Context-Aware)
```
✓ Current hostname: Router
💡 System reads state FIRST
```

### Test 2: POST (Apply Config)
```
✓ Before: Router
✓ After: DemoRouter1
💡 Configuration verified
```

### Test 3: POST with Verify
```
✓ Interface: FastEthernet0/1
✓ Description: ** DEMO: Zero-Touch Configured **
💡 Before/After validated
```

### Test 4: POST with Safety
```
✓ Loopback0 created
✓ IP: 1.1.1.1
💡 Safety check passed
```

### Test 5: Safety Prevention
```
✓ Duplicate PREVENTED
✓ Safety mechanism working
💡 Conflict detection active
```

### Test 6: Final Validation
```
✓ All changes verified
✓ Configuration persisted
💡 Zero-Touch complete
```

---

## 🔧 Quick Troubleshooting

### Connection Failed?
```bash
# Check GNS3 VM
# Restart R1 router in GNS3
# Verify IP: show ip interface brief
```

### Loopback Already Exists?
```bash
# This is NORMAL if running demo twice
# Test 5 will still PASS (safety works!)
# To reset:
Router(config)# no interface Loopback0
```

### Authentication Error?
```bash
# Check config.py has:
# username: "admin"
# password: "admin123"
```

---

## 📈 Success Criteria

✅ **6/6 tests passed** = Demo SUCCESS  
✅ **Safety mechanism triggered** = Protection working  
✅ **Verification successful** = Zero-Touch proven  

---

## 📚 Full Documentation

- **Detailed Guide:** [`SIMPLE_DEMO_GUIDE.md`](SIMPLE_DEMO_GUIDE.md)
- **Zero-Touch Setup:** [`ZERO_TOUCH_SETUP.md`](ZERO_TOUCH_SETUP.md)
- **Main README:** [`README.md`](README.md)

---

**Ready? Run the demo now! 🚀**

```bash
cd netmiko_mcp_server && python test_simple_demo.py