import requests
import json

BASE = "http://127.0.0.1:8000/api"
H = {"X-User-Role": "admin", "X-Username": "admin001"}

print("=== Projects ===")
r = requests.get(f"{BASE}/projects/", headers=H, timeout=5)
projects = r.json() if r.status_code == 200 else []
if isinstance(projects, list):
    for p in projects:
        pid = p.get("id")
        name = p.get("name")
        pno = p.get("project_no")
        print(f"  ID={pid} name={name} project_no={pno}")
else:
    print("  Response:", projects)

if isinstance(projects, list) and len(projects) > 0:
    pid = projects[0]["id"]

    print(f"\n=== Cold Rooms for project {pid} ===")
    r2 = requests.get(f"{BASE}/projects/{pid}/cold-rooms", headers=H, timeout=5)
    print(f"  Status: {r2.status_code}")
    if r2.status_code == 200:
        rooms = r2.json()
        print(f"  Found {len(rooms)} rooms")
        for rm in rooms:
            print(f"    id={rm.get('id')} name={rm.get('name')} type={rm.get('room_type')}")
    else:
        print(f"  Error: {r2.text}")

    print(f"\n=== Devices for project {pid} ===")
    r3 = requests.get(f"{BASE}/devices/", headers=H, params={"project_id": pid}, timeout=5)
    print(f"  Status: {r3.status_code}")
    if r3.status_code == 200:
        devs = r3.json()
        print(f"  Found {len(devs)} devices")
        for d in devs:
            print(f"    {d.get('device_no')} type={d.get('device_type')} brand={d.get('brand')}")
    else:
        print(f"  Error: {r3.text}")

    print(f"\n=== Device Stats for project {pid} ===")
    r4 = requests.get(f"{BASE}/devices/stats/{pid}", headers=H, timeout=5)
    print(f"  Status: {r4.status_code}")
    if r4.status_code == 200:
        print(f"  Stats: {json.dumps(r4.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"  Error: {r4.text}")
