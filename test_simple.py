# Simple Test - Working with old commit
import requests

def test_simple():
    base_url = "http://localhost:8001"
    
    print("=== Simple Test for Old Commit ===")
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"1. Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"1. Health Check Failed: {e}")
    
    # Test 2: Admin Users
    try:
        response = requests.get(f"{base_url}/admin/users", timeout=10)
        print(f"2. Users API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Users found: {len(data.get('users', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"2. Users API Failed: {e}")
    
    # Test 3: Admin Panel
    try:
        response = requests.get(f"{base_url}/admin", timeout=10)
        print(f"3. Admin Panel: {response.status_code}")
        if response.status_code == 200:
            print("   Admin panel accessible")
        else:
            print(f"   Error: Status {response.status_code}")
    except Exception as e:
        print(f"3. Admin Panel Failed: {e}")
    
    print("\nTest URLs:")
    print(f"- Admin Panel: http://localhost:8001/admin")
    print(f"- API Docs: http://localhost:8001/docs")
    print(f"- Health: http://localhost:8001/health")

if __name__ == "__main__":
    test_simple()
