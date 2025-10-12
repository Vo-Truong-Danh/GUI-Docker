"""
Simple test to verify ThreadPoolExecutor works correctly
"""

from concurrent.futures import ThreadPoolExecutor
import time
import threading

def test_function(name, delay):
    """Test function to run in thread"""
    print(f"[{threading.current_thread().name}] Starting {name}...")
    time.sleep(delay)
    print(f"[{threading.current_thread().name}] Finished {name} after {delay}s")
    return f"{name} completed"

def main():
    print("="*60)
    print("ThreadPoolExecutor Test")
    print("="*60)
    
    # Create thread pool
    print("\n1. Creating ThreadPoolExecutor with max_workers=3...")
    thread_pool = ThreadPoolExecutor(max_workers=3)
    print("   ✓ Thread pool created")
    
    # Submit tasks
    print("\n2. Submitting tasks...")
    future1 = thread_pool.submit(test_function, "Task 1", 2)
    print(f"   ✓ Task 1 submitted. Future: {future1}")
    
    future2 = thread_pool.submit(test_function, "Task 2", 1)
    print(f"   ✓ Task 2 submitted. Future: {future2}")
    
    future3 = thread_pool.submit(test_function, "Task 3", 3)
    print(f"   ✓ Task 3 submitted. Future: {future3}")
    
    # Wait for results
    print("\n3. Waiting for tasks to complete...")
    result1 = future1.result()
    print(f"   ✓ Task 1 result: {result1}")
    
    result2 = future2.result()
    print(f"   ✓ Task 2 result: {result2}")
    
    result3 = future3.result()
    print(f"   ✓ Task 3 result: {result3}")
    
    print("\n4. All tasks completed!")
    print("="*60)
    print("✅ ThreadPoolExecutor is working correctly!")
    print("="*60)
    
    # Shutdown
    thread_pool.shutdown(wait=True)
    print("\n✓ Thread pool shutdown complete")

if __name__ == '__main__':
    main()
