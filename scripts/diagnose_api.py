import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def check_api():
    print(f"Checking API at {BASE_URL}...")
    
    # 1. Check Health/Root (if exists) or simple endpoint
    try:
        # Try to login first to get a token (simulating user)
        # Using a test user if possible, or just checking public endpoints if any
        # Assuming we need to verify Project ID 1 as per user's context
        project_id = 1
        
        # Test Headers
        headers = {
            "X-User-Role": "admin",
            "X-Username": "diagnostic_script"
        }

        # 2. Check Project Detail
        print(f"\n[GET] /projects/{project_id}")
        try:
            resp = requests.get(f"{BASE_URL}/projects/{project_id}", headers=headers, timeout=5)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("Success. Project Name:", resp.json().get("name"))
            else:
                print("Failed:", resp.text)
        except Exception as e:
            print(f"Request Error: {e}")

        # 3. Check Cold Rooms
        print(f"\n[GET] /projects/{project_id}/cold-rooms")
        try:
            resp = requests.get(f"{BASE_URL}/projects/{project_id}/cold-rooms", headers=headers, timeout=5)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"Success. Found {len(data)} cold rooms.")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print("Failed:", resp.text)
        except Exception as e:
            print(f"Request Error: {e}")

        # 4. Check Device Stats
        print(f"\n[GET] /devices/stats/{project_id}")
        try:
            resp = requests.get(f"{BASE_URL}/devices/stats/{project_id}", headers=headers, timeout=5)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("Success. Stats:", json.dumps(resp.json(), indent=2, ensure_ascii=False))
            else:
                print("Failed:", resp.text)
        except Exception as e:
            print(f"Request Error: {e}")

    except Exception as main_e:
        print(f"Critical Error: {main_e}")

if __name__ == "__main__":
    check_api()
