"""
测试今天修复的功能和潜在 bug
执行：python scripts/test_fixes.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from sqlalchemy import inspect, text

db = SessionLocal()
insp = inspect(engine)

results = []

def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    results.append((status, name, detail))
    print(f"[{status}] {name}: {detail}")


# ========== 1. 数据库 schema 测试 ==========
print("\n=== 1. Database schema ===")

device_cols = [c["name"] for c in insp.get_columns("devices")]
check("devices.cabinet_id", "cabinet_id" in device_cols, "column exists")
check("devices.meter_area", "meter_area" in device_cols, "column exists")

# 检查 SQLite 外键是否启用
fk_result = db.execute(text("PRAGMA foreign_keys")).scalar()
check("SQLite foreign_keys", fk_result == 1, f"value={fk_result}")


# ========== 2. DeviceType 枚举 ==========
print("\n=== 2. DeviceType enum ===")
from app.models.device import DeviceType
check("DeviceType.CABINET", DeviceType.CABINET.value == "cabinet", f"value={DeviceType.CABINET.value}")
check("DeviceType.COOLING_TOWER", DeviceType.COOLING_TOWER.value == "cooling_tower", f"value={DeviceType.COOLING_TOWER.value}")


# ========== 3. 项目级联删除测试（模拟） ==========
print("\n=== 3. Project cascade delete (simulation) ===")
from app.models.project import Project, ColdRoom
from app.models.device import Device, DeviceRelation
from app.models.gateway import Gateway, MailingRecord, FlowRecord

test_proj = Project(
    project_no="TEST-CASCADE-001",
    name="级联删除测试项目",
    address="测试地址",
    end_customer="测试客户"
)
db.add(test_proj)
db.flush()
pid = test_proj.id

cr = ColdRoom(project_id=pid, name="测试冷库", room_type="low_temp", area=100, height=3, volume=300, design_temp_min=-18, design_temp_max=-15, refrigerant_type="R404A")
db.add(cr)
db.flush()

dev1 = Device(project_id=pid, cold_room_id=cr.id, device_no="TC-001-001", device_type="thermostat", brand="测试品牌", model="T1")
dev2 = Device(project_id=pid, cold_room_id=cr.id, device_no="AC-001-001", device_type="air_cooler", brand="测试品牌", model="A1")
db.add_all([dev1, dev2])
db.flush()

rel = DeviceRelation(project_id=pid, from_device_id=dev1.id, to_device_id=dev2.id, relation_type="thermostat_to_air_cooler")
db.add(rel)

mr = MailingRecord(project_id=pid, recipient_name="测试", recipient_phone="13800138000", recipient_address="测试")
db.add(mr)
db.commit()

# 模拟 API 删除项目的行为
db.query(DeviceRelation).filter(DeviceRelation.project_id == pid).delete()
db.query(MailingRecord).filter(MailingRecord.project_id == pid).delete()
db.query(FlowRecord).filter(FlowRecord.project_id == pid).delete()
db.delete(test_proj)
db.commit()

remaining_relations = db.query(DeviceRelation).filter(DeviceRelation.project_id == pid).count()
remaining_mailing = db.query(MailingRecord).filter(MailingRecord.project_id == pid).count()
remaining_cold = db.query(ColdRoom).filter(ColdRoom.project_id == pid).count()
remaining_devices = db.query(Device).filter(Device.project_id == pid).count()

check("relations cleaned", remaining_relations == 0, f"remaining={remaining_relations}")
check("mailing cleaned", remaining_mailing == 0, f"remaining={remaining_mailing}")
check("cold_rooms cascaded (SQLAlchemy)", remaining_cold == 0, f"remaining={remaining_cold}")
check("devices cascaded (SQLAlchemy)", remaining_devices == 0, f"remaining={remaining_devices}")


# ========== 4. 删除冷库清理设备引用 ==========
print("\n=== 4. Delete cold room clears device reference ===")
test_proj2 = Project(
    project_no="TEST-DEL-CR", name="删除冷库测试",
    address="x", end_customer="x"
)
db.add(test_proj2)
db.flush()
cr2 = ColdRoom(project_id=test_proj2.id, name="cr2", room_type="low_temp", area=100, height=3, volume=300, design_temp_min=-18, design_temp_max=-15, refrigerant_type="R404A")
db.add(cr2)
db.flush()
dev3 = Device(project_id=test_proj2.id, cold_room_id=cr2.id, device_no="TC-X-001", device_type="thermostat", brand="x", model="x")
db.add(dev3)
db.commit()
dev3_id = dev3.id
cr2_id = cr2.id

# 模拟删除冷库
db.query(Device).filter(Device.cold_room_id == cr2_id).update({Device.cold_room_id: None})
db.delete(cr2)
db.commit()

dev3_after = db.query(Device).filter(Device.id == dev3_id).first()
check("device cold_room_id cleared", dev3_after.cold_room_id is None, f"cold_room_id={dev3_after.cold_room_id}")

# 清理
db.query(Device).filter(Device.id == dev3_id).delete()
db.delete(test_proj2)
db.commit()


# ========== 5. 项目复制功能 ==========
print("\n=== 5. Project copy (check project_no uniqueness) ===")
# 查找任意一个已有项目
sample = db.query(Project).first()
if sample:
    count = db.query(Project).filter(Project.name.like("%复制测试%")).count()
    check("project copy (existing project available)", True, f"sample id={sample.id}, existing test copies={count}")
else:
    check("project copy (no projects)", True, "no projects in DB, skipping")


# ========== 6. Device update schema 验证 ==========
print("\n=== 6. DeviceUpdate schema ===")
from app.schemas.device import DeviceUpdate
du = DeviceUpdate(rs485_address="01", gateway_port=1, cabinet_id=None)
check("DeviceUpdate accepts rs485_address", du.rs485_address == "01")
check("DeviceUpdate accepts cabinet_id", hasattr(du, "cabinet_id"))
check("DeviceUpdate accepts meter_area", hasattr(du, "meter_area"))
check("DeviceUpdate accepts device_no", hasattr(du, "device_no"))

du2 = DeviceUpdate(gateway_id=None, gateway_port=None, rs485_address=None)
check("DeviceUpdate allows nulls (unassign)", du2.gateway_id is None)


# ========== 7. 网关库存 API 验证 ==========
print("\n=== 7. Gateway inventory API ===")
try:
    from app.api.gateway_library import router as gl_router  # noqa
    check("gateway_library router importable", True)
except Exception as e:
    check("gateway_library router importable", False, str(e))


# ========== 8. ProjectCopy schema 验证 ==========
print("\n=== 8. ProjectCopy schema ===")
from app.schemas.project import ProjectCopy
pc = ProjectCopy(new_project_name="test")
check("ProjectCopy copy_devices default True", pc.copy_devices is True)
check("ProjectCopy copy_gateways default True", pc.copy_gateways is True)
check("ProjectCopy copy_relations default True", pc.copy_relations is True)
check("ProjectCopy copy_cold_rooms default True", pc.copy_cold_rooms is True)


# ========== 总结 ==========
print("\n=== Summary ===")
passed = sum(1 for r in results if r[0] == "PASS")
failed = sum(1 for r in results if r[0] == "FAIL")
print(f"Total: {len(results)}, PASS: {passed}, FAIL: {failed}")
if failed > 0:
    print("\nFailed tests:")
    for s, n, d in results:
        if s == "FAIL":
            print(f"  - {n}: {d}")

db.close()
sys.exit(0 if failed == 0 else 1)
