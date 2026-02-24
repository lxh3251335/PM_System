import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def check_system():
    print("-" * 30)
    print("Checking System Health...")
    
    headers = {}
    
    # 1. Login
    try:
        login_data = {
            "username": "admin001",
            "password": "password123"
        }
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if resp.status_code != 200:
            print(f"Login Failed: {resp.status_code} {resp.text}")
            return
            
        result = resp.json()
        token = result.get("access_token")
        username = result.get("username")
        role = result.get("role")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Username": username,
            "X-User-Role": role
        }
        print(f"Login Success. Token obtained. User: {username}, Role: {role}")

        # 1.5 Get Users (Admin only)
        resp = requests.get(f"{BASE_URL}/users/", headers=headers)
        if resp.status_code == 200:
            users = resp.json()
            print("Users:")
            for u in users:
                print(f"  - ID: {u['id']}, Username: {u['username']}, Role: {u['role']}")
        else:
            print(f"Get Users Failed: {resp.status_code}")

    except Exception as e:
        print(f"Connection Error: {e}")
        return

    # 2. Get Projects
    try:
        resp = requests.get(f"{BASE_URL}/projects/", headers=headers)
        if resp.status_code != 200:
            print(f"Get Projects Failed: {resp.status_code} {resp.text}")
            return
            
        projects = resp.json()
        print(f"Projects found: {len(projects)}")
        
        if not projects:
            print("No projects available to test cold rooms.")
            return
            
        project = projects[0]
        pid = project['id']
        print(f"Testing Project ID: {pid} ({project.get('name', 'No Name')}) - Created By: {project.get('created_by')}")
        
        # 3. Get Cold Rooms
        resp = requests.get(f"{BASE_URL}/projects/{pid}/cold-rooms", headers=headers)
        if resp.status_code != 200:
            print(f"Get Cold Rooms Failed: {resp.status_code} {resp.text}")
        else:
            rooms = resp.json()
            print(f"Cold Rooms found: {len(rooms)}")
            for r in rooms:
                print(f"  - ID: {r['id']}, Name: {r['name']}")
                
        # 4. Get Devices
        resp = requests.get(f"{BASE_URL}/devices/?project_id={pid}", headers=headers)
        if resp.status_code != 200:
            print(f"Get Devices Failed: {resp.status_code} {resp.text}")
        else:
            devices = resp.json()
            print(f"Devices found: {len(devices)}")

        # 5. Get Categories (for relations page)
        resp = requests.get(f"{BASE_URL}/equipment-library/categories", headers=headers)
        if resp.status_code != 200:
            print(f"Get Categories Failed: {resp.status_code} {resp.text}")
        else:
            cats = resp.json()
            print(f"Categories found: {len(cats)}")

    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    check_system()
