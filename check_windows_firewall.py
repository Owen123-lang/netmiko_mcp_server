#!/usr/bin/env python3
"""
Check Windows Firewall and provide instructions to allow ICMP
"""

import subprocess
import sys

def run_command(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"

def check_firewall():
    """Check Windows Firewall status and rules"""
    
    print("=" * 60)
    print("🛡️  Windows Firewall Diagnostic")
    print("=" * 60)
    
    # Check if running as admin
    print("\n1️⃣  Checking admin privileges...")
    print("=" * 60)
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin:
            print("✅ Running as Administrator")
        else:
            print("⚠️  NOT running as Administrator")
            print("   Some commands will fail without admin rights")
    except:
        print("⚠️  Cannot determine admin status")
    
    # Check firewall status
    print("\n2️⃣  Checking Windows Firewall status...")
    print("=" * 60)
    output = run_command("netsh advfirewall show allprofiles state")
    print(output)
    
    if "State                                 ON" in output:
        print("⚠️  Windows Firewall is ENABLED")
        firewall_on = True
    else:
        print("✅ Windows Firewall is DISABLED")
        firewall_on = False
    
    # Check ICMP rules
    print("\n3️⃣  Checking ICMP (ping) rules...")
    print("=" * 60)
    output = run_command('netsh advfirewall firewall show rule name="File and Printer Sharing (Echo Request - ICMPv4-In)"')
    print(output)
    
    # Test ping again
    print("\n4️⃣  Testing ping to R2...")
    print("=" * 60)
    output = run_command("ping -n 2 10.1.1.2")
    print(output)
    
    if "TTL=" in output:
        print("\n✅ SUCCESS! R2 is now reachable!")
        return True
    else:
        print("\n❌ Still cannot reach R2")
    
    # Provide solutions
    print("\n" + "=" * 60)
    print("💡 SOLUTIONS")
    print("=" * 60)
    
    if firewall_on:
        print("\n🔧 OPTION 1: Temporarily disable firewall (for testing)")
        print("   Run PowerShell as Administrator:")
        print("   Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False")
        print("\n   To re-enable later:")
        print("   Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True")
        
        print("\n🔧 OPTION 2: Allow ICMP through firewall (permanent)")
        print("   Run PowerShell as Administrator:")
        print('   New-NetFirewallRule -DisplayName "Allow ICMPv4" -Protocol ICMPv4 -IcmpType 8 -Enabled True -Profile Any -Action Allow')
        
        print("\n🔧 OPTION 3: Enable built-in ICMP rule")
        print("   Run PowerShell as Administrator:")
        print('   Enable-NetFirewallRule -DisplayName "File and Printer Sharing (Echo Request - ICMPv4-In)"')
    
    print("\n🔧 OPTION 4: Check if R1 has access-list blocking traffic")
    print("   Run diagnostic script:")
    print("   python check_r1_access_lists.py")
    
    print("\n" + "=" * 60)
    print("📋 RECOMMENDED STEPS:")
    print("=" * 60)
    print("1. Open PowerShell as Administrator")
    print("2. Temporarily disable firewall:")
    print("   Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False")
    print("3. Test: ping 10.1.1.2")
    print("4. If it works, firewall was the issue")
    print("5. Re-enable and add ICMP rule")
    print("=" * 60)
    
    return False

if __name__ == "__main__":
    success = check_firewall()
    
    if success:
        print("\n🎉 PROBLEM SOLVED!")
        print("You can now proceed with MCP testing:")
        print("   python test_jumphost.py")
    else:
        print("\n⚠️  MANUAL ACTION REQUIRED")
        print("Follow the solutions above to fix firewall/routing")