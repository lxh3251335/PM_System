import requests
import json

BASE = "http://127.0.0.1:8000/api"
H = {
    "X-User-Role": "admin",
    "X-Username": "admin001",
    "Content-Type": "application/json"
}

print("=== Test 1: Get Cold Rooms for project 1 ===")
r = requests.get(f"{BASE}/projects/1/cold-rooms", headers=H, timeout=5)
print(f"  Status: {r.status_code}")
print(f"  Body: {r.text[:500]}")

print("\n=== Test 2: Get Devices for project 1 ===")
r2 = requests.get(f"{BASE}/devices/", headers=H, params={"project_id": 1}, timeout=5)
print(f"  Status: {r2.status_code}")
print(f"  Body: {r2.text[:500]}")

print("\n=== Test 3: Create a test device for project 1 ===")
payload = {
    "device_type": "thermostat",
    "brand": "TestBrand",
    "model": "TestModel",
    "cold_room_id": 1
}
r3 = requests.post(f"{BASE}/devices/?project_id=1", headers=H, json=payload, timeout=5)
print(f"  Status: {r3.status_code}")
print(f"  Body: {r3.text[:500]}")

print("\n=== Test 4: Device Stats for project 1 ===")
r4 = requests.get(f"{BASE}/devices/stats/1", headers=H, timeout=5)
print(f"  Status: {r4.status_code}")
print(f"  Body: {r4.text[:500]}")

print("\n=== Test 5: Customer login test ===")
r5 = requests.get(f"{BASE}/projects/1/cold-rooms", headers={
    "X-User-Role": "customer",
    "X-Username": "customer001",
    "Content-Type": "application/json"
}, timeout=5)
print(f"  Customer cold rooms status: {r5.status_code}")
print(f"  Body: {r5.text[:500]}")
