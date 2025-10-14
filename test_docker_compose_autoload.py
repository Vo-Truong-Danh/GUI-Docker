"""
Test Docker Compose Auto-Load Feature
Verify port parsing logic and auto-load functionality
"""

import os
import sys
import yaml

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'run_spark_gui'))

def test_docker_compose_parsing():
    """Test parsing docker-compose.yml"""
    print("=" * 60)
    print("🧪 Testing Docker Compose Port Parsing")
    print("=" * 60)
    
    # Read docker-compose.yml
    docker_compose_path = "docker-compose.yml"
    
    if not os.path.exists(docker_compose_path):
        print(f"❌ File not found: {docker_compose_path}")
        return False
    
    print(f"✅ Found docker-compose.yml\n")
    
    try:
        with open(docker_compose_path, 'r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
        
        print("📋 Services Found:")
        print("-" * 60)
        
        # Parse Docker Compose services
        ports = {}
        service_mapping = {
            'spark-master': 'spark_master_ui',
            'spark-worker': 'spark_worker_ui',
            'namenode': 'hdfs_namenode_ui',
            'datanode': 'hdfs_datanode_ui',
            'history-server': 'history_server',
            'jupyter': 'jupyter'
        }
        
        if 'services' in yaml_config:
            for service_name, service_config in yaml_config['services'].items():
                print(f"\n🔹 Service: {service_name}")
                
                if 'ports' in service_config:
                    port_list = service_config['ports']
                    print(f"   Ports configured: {len(port_list)}")
                    
                    for idx, port_mapping in enumerate(port_list):
                        if isinstance(port_mapping, str):
                            # Remove quotes and split
                            port_mapping = port_mapping.strip('"').strip("'")
                            parts = port_mapping.split(':')
                            
                            if len(parts) >= 2:
                                host_port = parts[0].strip()
                                container_port = parts[1].strip()
                                
                                print(f"   Port {idx+1}: \"{host_port}:{container_port}\"")
                                print(f"      → HOST port (correct): {host_port}")
                                print(f"      → Container port: {container_port}")
                                
                                # Store first port with mapped name
                                if idx == 0:
                                    if service_name in service_mapping:
                                        port_key = service_mapping[service_name]
                                        ports[port_key] = host_port
                                        print(f"      → Mapped to: {port_key} = {host_port} ✅")
                                else:
                                    # Additional ports
                                    port_key = f"{service_name}_port_{idx}"
                                    ports[port_key] = host_port
                                    print(f"      → Mapped to: {port_key} = {host_port} ✅")
                            elif len(parts) == 1:
                                # Single port (no mapping)
                                port = parts[0].strip()
                                print(f"   Port {idx+1}: {port}")
                                port_key = f"{service_name}_port"
                                ports[port_key] = port
                                print(f"      → Mapped to: {port_key} = {port} ✅")
                else:
                    print("   ⚠️  No ports configured")
        
        print("\n" + "=" * 60)
        print("📊 Final Port Mapping:")
        print("=" * 60)
        
        if ports:
            for key, value in ports.items():
                print(f"✅ {key:30s} → {value}")
            print(f"\n✅ Total ports loaded: {len(ports)}")
        else:
            print("❌ No ports found")
        
        # Verify expected ports
        print("\n" + "=" * 60)
        print("🔍 Verification:")
        print("=" * 60)
        
        expected_ports = {
            'spark_master_ui': '8081',  # NOT 8080!
            'hdfs_namenode_ui': '9870',
            'spark-master_port_1': '7077',
            'namenode_port_1': '8020'
        }
        
        all_passed = True
        for key, expected_value in expected_ports.items():
            if key in ports:
                actual_value = ports[key]
                if actual_value == expected_value:
                    print(f"✅ {key}: {actual_value} (expected {expected_value})")
                else:
                    print(f"❌ {key}: {actual_value} (expected {expected_value})")
                    all_passed = False
            else:
                print(f"⚠️  {key}: NOT FOUND (expected {expected_value})")
                all_passed = False
        
        print("\n" + "=" * 60)
        if all_passed:
            print("✅ All tests PASSED!")
        else:
            print("❌ Some tests FAILED!")
        print("=" * 60)
        
        return all_passed
        
    except yaml.YAMLError as e:
        print(f"❌ YAML Parse Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_port_parsing_logic():
    """Test individual port parsing cases"""
    print("\n" + "=" * 60)
    print("🧪 Testing Port Parsing Logic")
    print("=" * 60)
    
    test_cases = [
        ('"8081:8080"', '8081', 'Standard quoted format'),
        ("'8081:8080'", '8081', 'Single quoted format'),
        ('8081:8080', '8081', 'Unquoted format'),
        ('" 8081:8080 "', '8081', 'With extra spaces'),
        ('9870:9870', '9870', 'Same host and container'),
    ]
    
    all_passed = True
    for port_mapping, expected_host, description in test_cases:
        # Simulate parsing
        cleaned = port_mapping.strip('"').strip("'")
        parts = cleaned.split(':')
        if len(parts) >= 2:
            host_port = parts[0].strip()
            result = "✅ PASS" if host_port == expected_host else "❌ FAIL"
            print(f"{result} | {description:30s} | Input: {port_mapping:20s} | Output: {host_port} | Expected: {expected_host}")
            if host_port != expected_host:
                all_passed = False
        else:
            print(f"⚠️  SKIP | {description:30s} | Input: {port_mapping:20s} | Invalid format")
    
    return all_passed

def main():
    """Run all tests"""
    print("\n")
    print("🚀 Docker Compose Auto-Load Test Suite")
    print("=" * 60)
    
    # Test 1: Port parsing logic
    test1_passed = test_port_parsing_logic()
    
    # Test 2: Docker compose parsing
    test2_passed = test_docker_compose_parsing()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Port Parsing Logic: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Docker Compose Parse: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("\n✅ ✅ ✅ ALL TESTS PASSED! ✅ ✅ ✅")
        print("\n📝 Next Steps:")
        print("1. Run application: python run_spark_gui/main.py")
        print("2. Go to Settings tab")
        print("3. Click '🐳 Load from Docker Compose'")
        print("4. Verify ports: spark_master_ui=8081, hdfs_namenode_ui=9870")
        print("5. Click 'Save Settings'")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Please check the output above for details")
    
    print()

if __name__ == "__main__":
    main()
