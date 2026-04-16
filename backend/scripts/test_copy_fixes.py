"""
测试项目复制是否正确传递 cabinet_id、meter_area；并验证网关/设备编号唯一性
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.project import Project, ColdRoom
from app.models.device import Device, DeviceType
from app.models.gateway import Gateway
from app.api.projects import (
    _next_device_no,
    _DEVICE_TYPE_PREFIX_MAP,
)

db = SessionLocal()

results = []
def check(name, ok, detail=""):
    results.append((ok, name, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


# === 1. _next_device_no 单元测试 ===
print("\n=== 1. _next_device_no ===")
seq = {}
nos = [
    _next_device_no(9, DeviceType.THERMOSTAT, seq),
    _next_device_no(9, DeviceType.THERMOSTAT, seq),
    _next_device_no(9, DeviceType.AIR_COOLER, seq),
    _next_device_no(9, DeviceType.THERMOSTAT, seq),
    _next_device_no(9, DeviceType.CABINET, seq),
]
check("独立计数器", nos == ["TC-009-001", "TC-009-002", "AC-009-001", "TC-009-003", "CB-009-001"], str(nos))
check("前缀映射全", set(_DEVICE_TYPE_PREFIX_MAP.keys()) >= {
    "air_cooler","thermostat","unit","meter","freezer","defrost_controller","cabinet","cooling_tower"
}, "all types covered")


# === 2. 构造带 cabinet_id / meter_area 的源项目，调用 copy_project 逻辑 ===
print("\n=== 2. Project copy with cabinet_id / meter_area ===")
import uuid
src = Project(project_no="COPY-SRC-" + uuid.uuid4().hex[:8].upper(), name="复制源项目-cabinet", address="x", end_customer="x")
db.add(src); db.flush()

cr = ColdRoom(project_id=src.id, name="CR1", room_type="low_temp",
              design_temp_min=-20, design_temp_max=-15, area=100, height=3, volume=300, refrigerant_type="R404A")
db.add(cr); db.flush()

suffix = uuid.uuid4().hex[:8].upper()
cabinet = Device(project_id=src.id, cold_room_id=cr.id, device_no=f"CB-{suffix}-001",
                 device_type=DeviceType.CABINET, brand="盒马", model="柜体X")
db.add(cabinet); db.flush()

meter = Device(project_id=src.id, cold_room_id=cr.id, device_no=f"PM-{suffix}-001",
               device_type=DeviceType.METER, brand="安科瑞", model="DTSU666",
               cabinet_id=cabinet.id, meter_area="cold_chain")
thermo = Device(project_id=src.id, cold_room_id=cr.id, device_no=f"TC-{suffix}-001",
                device_type=DeviceType.THERMOSTAT, brand="精创", model="ETC",
                cabinet_id=cabinet.id)
db.add_all([meter, thermo]); db.commit()

src_project_id = src.id
src_cabinet_id = cabinet.id
src_meter_id = meter.id
src_thermo_id = thermo.id

# 直接调用 copy_project 的同步逻辑：用 TestClient 调 API
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User

admin = db.query(User).filter(User.role == "admin").first()
assert admin, "need admin user"

# 伪造鉴权：通过 override dependency
from app.database import get_db
from app.auth_utils import get_current_user

def _override_db():
    try:
        yield db
    finally:
        pass

def _override_user():
    return admin

app.dependency_overrides[get_db] = _override_db
app.dependency_overrides[get_current_user] = _override_user

client = TestClient(app)
resp = client.post(
    f"/api/projects/{src_project_id}/copy",
    json={"new_project_name": "复制目标-cabinet测试"}
)
check("copy API 返回 201", resp.status_code == 201, f"status={resp.status_code} body={resp.text[:200]}")

if resp.status_code == 201:
    new_pid = resp.json()["id"]
    # 验证复制过来的设备是否带 cabinet_id / meter_area
    new_devices = db.query(Device).filter(Device.project_id == new_pid).order_by(Device.id).all()
    by_no_prefix = {}
    for d in new_devices:
        prefix = d.device_no.split("-")[0]
        by_no_prefix[prefix] = d
    new_cabinet = by_no_prefix.get("CB")
    new_meter = by_no_prefix.get("PM")
    new_thermo = by_no_prefix.get("TC")

    check("新项目包含 CB 设备", new_cabinet is not None, f"no={new_cabinet.device_no if new_cabinet else None}")
    check("新项目包含 PM 设备", new_meter is not None, f"no={new_meter.device_no if new_meter else None}")
    check("新项目包含 TC 设备", new_thermo is not None, f"no={new_thermo.device_no if new_thermo else None}")

    if new_meter and new_cabinet:
        check("电表 meter_area 已复制", new_meter.meter_area == "cold_chain", f"value={new_meter.meter_area}")
        check("电表 cabinet_id 指向新柜子", new_meter.cabinet_id == new_cabinet.id, f"cabinet_id={new_meter.cabinet_id}, expected={new_cabinet.id}")

    if new_thermo and new_cabinet:
        check("温控器 cabinet_id 指向新柜子", new_thermo.cabinet_id == new_cabinet.id, f"cabinet_id={new_thermo.cabinet_id}")

    # 清理
    for d in new_devices: db.delete(d)
    new_project = db.query(Project).filter(Project.id == new_pid).first()
    if new_project: db.delete(new_project)

# 清理源项目
db.delete(meter); db.delete(thermo); db.delete(cabinet); db.delete(cr); db.delete(src)
db.commit()

print("\n=== Summary ===")
passed = sum(1 for r in results if r[0])
failed = sum(1 for r in results if not r[0])
print(f"Total: {len(results)}, PASS: {passed}, FAIL: {failed}")
db.close()
sys.exit(0 if failed == 0 else 1)
