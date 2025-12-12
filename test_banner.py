#!/usr/bin/env python3
"""
Test script for banner configuration tools
Tests both set_banner and remove_banner functions
"""

from tools.configure_basic import set_banner, remove_banner, get_hostname

def test_banner_operations():
    """Test banner configuration on R1 and R2"""
    
    print("="*70)
    print("BANNER CONFIGURATION TEST")
    print("="*70)
    
    # Test 1: Get current hostname to verify connectivity
    print("\n[TEST 1] Verify R1 Connectivity")
    print("-" * 70)
    result = get_hostname("R1")
    if result["success"]:
        print(f"✅ R1 is accessible. Current hostname: {result['current_hostname']}")
    else:
        print(f"❌ Cannot access R1: {result['error']}")
        return
    
    # Test 2: Set MOTD banner on R1
    print("\n[TEST 2] Set MOTD Banner on R1")
    print("-" * 70)
    banner_text = """
*********************************************
*  UNAUTHORIZED ACCESS IS PROHIBITED!      *
*  This is R1 - Core Router                *
*  Contact: admin@network.local            *
*********************************************
"""
    result = set_banner("R1", banner_text.strip(), "motd")
    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"Commands sent: {result['commands_sent']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 3: Set login banner on R1
    print("\n[TEST 3] Set Login Banner on R1")
    print("-" * 70)
    login_banner = "Welcome to R1! Please login with your credentials."
    result = set_banner("R1", login_banner, "login")
    if result["success"]:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 4: Verify R2 connectivity
    print("\n[TEST 4] Verify R2 Connectivity")
    print("-" * 70)
    result = get_hostname("R2")
    if result["success"]:
        print(f"✅ R2 is accessible. Current hostname: {result['current_hostname']}")
    else:
        print(f"❌ Cannot access R2: {result['error']}")
        print("Skipping R2 tests...")
        return
    
    # Test 5: Set MOTD banner on R2
    print("\n[TEST 5] Set MOTD Banner on R2")
    print("-" * 70)
    r2_banner = """
==========================================
   R2 - Distribution Router
   Access Restricted to Authorized Users
==========================================
"""
    result = set_banner("R2", r2_banner.strip(), "motd")
    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"Commands sent: {result['commands_sent']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 6: Remove login banner from R1
    print("\n[TEST 6] Remove Login Banner from R1")
    print("-" * 70)
    result = remove_banner("R1", "login")
    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"Command sent: {result['command_sent']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 7: Try to set banner with special characters
    print("\n[TEST 7] Set Banner with Special Characters on R1")
    print("-" * 70)
    special_banner = "Router R1 | Status: Active | Build: 2024-01"
    result = set_banner("R1", special_banner, "exec")
    if result["success"]:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    print("\n" + "="*70)
    print("BANNER CONFIGURATION TEST COMPLETED")
    print("="*70)
    print("\nNext steps:")
    print("1. SSH to R1 and verify the banners are displayed")
    print("2. SSH to R2 and verify the banner is displayed")
    print("3. Check 'show running-config | include banner' on both routers")

if __name__ == "__main__":
    try:
        test_banner_operations()
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()