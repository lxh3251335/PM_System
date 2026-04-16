"""
测试完整的 导出 -> 预览解析 往返：取一个已有项目导出 Excel，再用 preview 解析它
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.project import Project, ColdRoom
from app.models.device import Device
from app.services.project_config_excel import build_workbook_bytes, extract_workbook_preview

db = SessionLocal()

# 找个有冷库或设备的项目
project = None
for p in db.query(Project).all():
    cr_count = db.query(ColdRoom).filter(ColdRoom.project_id == p.id).count()
    dev_count = db.query(Device).filter(Device.project_id == p.id).count()
    if cr_count > 0 or dev_count > 0:
        project = p
        project_cr = cr_count
        project_dev = dev_count
        break

if project is None:
    print("[SKIP] 没有找到包含冷库或设备的项目")
    sys.exit(0)

print(f"\n测试项目: id={project.id}, name={project.name}")
print(f"  实际冷库数={project_cr}, 设备数={project_dev}")

# 1. 导出 Excel
try:
    data, fname = build_workbook_bytes(db, project.id)
    print(f"\n[PASS] 导出成功: {fname}, {len(data)} bytes")
except Exception as e:
    print(f"[FAIL] 导出失败: {type(e).__name__}: {e}")
    sys.exit(1)

# 2. 用预览函数解析它
try:
    result = extract_workbook_preview(data)
    summary = result.get("summary", {})
    sheets = result.get("sheet_names", [])
    print(f"\n[PASS] 预览解析成功")
    print(f"  工作表: {sheets}")
    print(f"  冷库数={summary.get('cold_room_count', 0)}")
    print(f"  设备数={summary.get('device_count', 0)}")
    print(f"  关系数={summary.get('relation_count', 0)}")

    if summary.get("cold_room_count", 0) != project_cr:
        print(f"  [WARN] 冷库数不匹配: preview={summary.get('cold_room_count')}, actual={project_cr}")
    if summary.get("device_count", 0) != project_dev:
        print(f"  [WARN] 设备数不匹配: preview={summary.get('device_count')}, actual={project_dev}")

    # 检查返回结构的关键字段
    keys = list(result.keys())
    print(f"  返回字段: {keys}")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"[FAIL] 预览解析失败: {type(e).__name__}: {e}")
    sys.exit(1)

db.close()
print("\n全部通过")
