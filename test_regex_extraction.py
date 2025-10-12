"""
Test script for container name extraction
Tests multiple regex patterns against real error messages
"""
import re

# Sample error messages from real logs
test_cases = [
    {
        'name': 'Test 1: Simple name format',
        'stderr': '''Error response from daemon: Conflict. The container name "/namenode" is already in use by container "c39838879bf5079aa1eaefd65a9924d31e458bddc5cd7ce0c94e3e753b7b7d4e".''',
        'expected': ['namenode']
    },
    {
        'name': 'Test 2: Multiple containers',
        'stderr': '''
Container namenode  Creating
Container spark-master  Creating
Container namenode  Error response from daemon: Conflict. The container name "/namenode" is already in use
Container spark-master  Error response from daemon: Conflict. The container name "/spark-master" is already in use
''',
        'expected': ['namenode', 'spark-master']
    },
    {
        'name': 'Test 3: Your actual error',
        'stderr': '''Network downloads_bigdata_network  Creating
Network downloads_bigdata_network  Created
Volume downloads_hadoop_datanode  Creating
Volume downloads_hadoop_datanode  Created
Volume downloads_hadoop_namenode  Creating
Volume downloads_hadoop_namenode  Created
Container namenode  Creating
Container spark-master  Creating
Container spark-master  Error response from daemon: Conflict. The container name "/spark-master" is already in use by container "ae7ed356083c85b0a794ebe8199baa2054ff0621def13de38deb7c52ebe44d79".
Error response from daemon: Conflict. The container name "/spark-master" is already in use''',
        'expected': ['namenode', 'spark-master']
    }
]

def extract_containers(stderr):
    """Extract container names using multiple patterns"""
    container_names = set()
    
    # Pattern 1: container name "/namenode"
    pattern1 = re.findall(r'container name "(/[^"]+)"', stderr)
    container_names.update(pattern1)
    
    # Pattern 2: Container namenode  Creating/Error
    pattern2 = re.findall(r'Container\s+(\S+)\s+(?:Creating|Error)', stderr)
    container_names.update(['/' + name for name in pattern2])
    
    # Pattern 3: Parse lines
    lines = stderr.split('\n')
    for line in lines:
        if 'Creating' in line or 'Error' in line:
            parts = line.strip().split()
            if len(parts) >= 2 and parts[0] == 'Container':
                container_names.add('/' + parts[1])
    
    # Clean names (remove leading /)
    return [name.lstrip('/') for name in container_names]

# Run tests
print("=" * 60)
print("CONTAINER NAME EXTRACTION TEST")
print("=" * 60)

for test in test_cases:
    print(f"\n{test['name']}")
    print("-" * 60)
    
    extracted = extract_containers(test['stderr'])
    expected = set(test['expected'])
    actual = set(extracted)
    
    print(f"Expected: {sorted(expected)}")
    print(f"Extracted: {sorted(actual)}")
    
    if expected == actual:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        missing = expected - actual
        extra = actual - expected
        if missing:
            print(f"  Missing: {missing}")
        if extra:
            print(f"  Extra: {extra}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
