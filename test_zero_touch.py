"""
Test Script for Zero-Touch Configuration
Tests 2-router topology with OSPF routing
"""

import sys
from config import DEVICES, NETWORK_CONFIG
from tools.configure_interface import configure_interface, configure_default_gateway, configure_dns
from tools.configure_ospf import configure_ospf, verify_ospf_neighbors
from tools.validate_config import (
    validate_interface_config, validate_connectivity, 
    validate_ospf_adjacency, comprehensive_validation
)


def print_separator(title=""):
    """Print a separator line with optional title"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"{'='*60}\n")


def test_router_configuration(router_name):
    """Configure a router based on NETWORK_CONFIG"""
    print_separator(f"Configuring {router_name}")
    
    config = NETWORK_CONFIG[router_name]
    
    # Configure interfaces
    for interface_name, interface_config in config["interfaces"].items():
        print(f"📡 Configuring {interface_name}...")
        result = configure_interface(
            device_name=router_name,
            interface_name=interface_name,
            ip_address=interface_config["ip_address"],
            subnet_mask=interface_config["subnet_mask"],
            description=interface_config["description"]
        )
        
        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"   IP: {result['ip_address']}/{result['subnet_mask']}")
        else:
            print(f"❌ Failed: {result['error']}")
            return False
    
    # Configure DNS (for R1 only)
    if router_name == "R1":
        print(f"\n🌐 Configuring DNS...")
        result = configure_dns(router_name, "8.8.8.8")
        if result["success"]:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Failed: {result['error']}")
    
    # Configure OSPF
    print(f"\n🔄 Configuring OSPF...")
    ospf_config = config["ospf"]
    default_route = ospf_config.get("default_information") == "originate"
    
    result = configure_ospf(
        device_name=router_name,
        process_id=ospf_config["process_id"],
        networks=ospf_config["networks"],
        default_route=default_route
    )
    
    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"   Process ID: {result['process_id']}")
        print(f"   Networks: {result['networks']}")
    else:
        print(f"❌ Failed: {result['error']}")
        return False
    
    return True


def test_connectivity():
    """Test connectivity between routers"""
    print_separator("Testing Connectivity")
    
    # Test R1 -> R2
    print("📡 Testing R1 -> R2 (10.1.1.2)...")
    result = validate_connectivity("R1", "10.1.1.2", count=5)
    if result["success"]:
        if result["connectivity_ok"]:
            print(f"✅ Connectivity OK - Success rate: {result['success_rate']}%")
        else:
            print(f"⚠️  Partial connectivity - Success rate: {result['success_rate']}%")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test R2 -> R1
    print("\n📡 Testing R2 -> R1 (10.1.1.1)...")
    result = validate_connectivity("R2", "10.1.1.1", count=5)
    if result["success"]:
        if result["connectivity_ok"]:
            print(f"✅ Connectivity OK - Success rate: {result['success_rate']}%")
        else:
            print(f"⚠️  Partial connectivity - Success rate: {result['success_rate']}%")
    else:
        print(f"❌ Failed: {result['error']}")


def test_ospf_adjacency():
    """Test OSPF neighbor adjacencies"""
    print_separator("Testing OSPF Adjacency")
    
    # Check R1 OSPF neighbors
    print("🔄 Checking R1 OSPF neighbors...")
    result = verify_ospf_neighbors("R1")
    if result["success"]:
        print(f"✅ OSPF verification completed")
        print(f"\nNeighbors:\n{result['neighbors']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Check R2 OSPF neighbors
    print("\n🔄 Checking R2 OSPF neighbors...")
    result = verify_ospf_neighbors("R2")
    if result["success"]:
        print(f"✅ OSPF verification completed")
        print(f"\nNeighbors:\n{result['neighbors']}")
    else:
        print(f"❌ Failed: {result['error']}")


def test_comprehensive_validation():
    """Run comprehensive validation on both routers"""
    print_separator("Comprehensive Validation")
    
    for router_name in ["R1", "R2"]:
        print(f"\n🔍 Validating {router_name}...")
        result = comprehensive_validation(router_name)
        
        if result["success"]:
            validation = result["validation_results"]
            print(f"\n{'─'*40}")
            print(f"Device: {validation['device']}")
            print(f"Overall Status: {validation['overall_status']}")
            print(f"Checks: {validation['total_checks']} total, {validation['failed_checks']} failed")
            print(f"{'─'*40}")
            
            for check in validation["checks"]:
                status_icon = "✅" if check["status"] == "PASS" else ("⚠️" if check["status"] == "WARNING" else "❌")
                print(f"{status_icon} {check['name']}: {check['details']}")
        else:
            print(f"❌ Failed: {result['error']}")


def main():
    """Main test function"""
    print_separator("ZERO-TOUCH CONFIGURATION TEST")
    print("Testing 2-Router Topology with OSPF")
    print(f"Devices: {list(DEVICES.keys())}")
    
    # Step 1: Configure R1
    success_r1 = test_router_configuration("R1")
    if not success_r1:
        print("\n❌ R1 configuration failed. Stopping tests.")
        sys.exit(1)
    
    # Step 2: Configure R2
    success_r2 = test_router_configuration("R2")
    if not success_r2:
        print("\n❌ R2 configuration failed. Stopping tests.")
        sys.exit(1)
    
    # Step 3: Test connectivity
    test_connectivity()
    
    # Step 4: Test OSPF adjacency
    test_ospf_adjacency()
    
    # Step 5: Comprehensive validation
    test_comprehensive_validation()
    
    # Final summary
    print_separator("TEST SUMMARY")
    print("✅ All configuration steps completed!")
    print("\n📋 Next Steps:")
    print("   1. Verify OSPF neighbors are in FULL state")
    print("   2. Check routing tables on both routers")
    print("   3. Test end-to-end connectivity")
    print("   4. Test with Claude Desktop via MCP Server")
    
    print_separator()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)