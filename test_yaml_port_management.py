"""
Quick Test Script for Settings Tab YAML Port Management
Tests the new YAML import/export functionality
"""

import sys
import os
import yaml

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'run_spark_gui'))

def test_yaml_port_structure():
    """Test if YAML files can be parsed correctly"""
    print("🧪 Testing YAML Port Structure...")
    
    # Test 1: Standard format
    yaml_content_standard = """
ports:
  spark_master_ui: 9090
  jupyter: 8888
"""
    try:
        data = yaml.safe_load(yaml_content_standard)
        ports = data.get('ports', {})
        assert 'spark_master_ui' in ports
        assert ports['spark_master_ui'] == 9090
        print("✅ Test 1 PASSED: Standard format")
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
    
    # Test 2: Flat format
    yaml_content_flat = """
spark_master_ui: 9090
jupyter: 8888
"""
    try:
        data = yaml.safe_load(yaml_content_flat)
        assert 'spark_master_ui' in data
        assert data['spark_master_ui'] == 9090
        print("✅ Test 2 PASSED: Flat format")
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
    
    # Test 3: Docker Compose format
    yaml_content_docker = """
services:
  spark-master:
    ports:
      - "9090:8080"
  jupyter:
    ports:
      - "8888:8888"
"""
    try:
        data = yaml.safe_load(yaml_content_docker)
        services = data.get('services', {})
        assert 'spark-master' in services
        assert 'ports' in services['spark-master']
        print("✅ Test 3 PASSED: Docker Compose format")
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")

def test_port_validation():
    """Test port number validation"""
    print("\n🧪 Testing Port Validation...")
    
    def validate_port(port_str):
        try:
            port = int(port_str)
            return 1024 <= port <= 65535
        except:
            return False
    
    # Valid ports
    assert validate_port("8080") == True
    assert validate_port("9090") == True
    assert validate_port("65535") == True
    assert validate_port("1024") == True
    print("✅ Valid port tests PASSED")
    
    # Invalid ports
    assert validate_port("80") == False
    assert validate_port("99999") == False
    assert validate_port("abc") == False
    assert validate_port("") == False
    print("✅ Invalid port tests PASSED")

def test_example_yaml_file():
    """Test if example YAML file exists and is valid"""
    print("\n🧪 Testing Example YAML File...")
    
    example_file = "example_port_config.yaml"
    
    if os.path.exists(example_file):
        try:
            with open(example_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                ports = data.get('ports', {})
                
                # Check default ports
                expected_ports = ['spark_master_ui', 'spark_worker_ui', 'hdfs_namenode_ui', 
                                 'hdfs_datanode_ui', 'history_server', 'jupyter']
                
                for port_name in expected_ports:
                    if port_name in ports:
                        print(f"  ✓ {port_name}: {ports[port_name]}")
                    else:
                        print(f"  ⚠ {port_name}: Not found")
                
                print("✅ Example YAML file is valid")
        except Exception as e:
            print(f"❌ Example YAML file is invalid: {e}")
    else:
        print(f"⚠️ Example YAML file not found: {example_file}")

def test_settings_tab_imports():
    """Test if settings_tab_v4.py has required imports"""
    print("\n🧪 Testing Settings Tab Imports...")
    
    try:
        settings_file = "run_spark_gui/settings_tab_v4.py"
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for yaml import
            if 'import yaml' in content:
                print("✅ yaml import found")
            else:
                print("❌ yaml import NOT found")
            
            # Check for new methods
            methods = [
                'def load_ports_from_yaml',
                'def save_ports_to_yaml',
                'def add_new_port',
                'def delete_port',
                'def _create_port_row'
            ]
            
            for method in methods:
                if method in content:
                    print(f"✅ {method} found")
                else:
                    print(f"❌ {method} NOT found")
                    
    except FileNotFoundError:
        print(f"❌ Settings file not found: {settings_file}")
    except Exception as e:
        print(f"❌ Error reading settings file: {e}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("YAML Port Management - Quick Test Suite")
    print("=" * 60)
    
    test_yaml_port_structure()
    test_port_validation()
    test_example_yaml_file()
    test_settings_tab_imports()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("1. Run the application: python run_spark_gui/main.py")
    print("2. Go to Settings tab")
    print("3. Test 'Load from YAML' with example_port_config.yaml")
    print("4. Test 'Add Port' functionality")
    print("5. Test 'Save to YAML' to export configuration")

if __name__ == "__main__":
    main()
