"""
测试项目列表的"解析预览"功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.project import Project
from app.services.project_config_excel import extract_workbook_preview
from app.project_attachment_storage import attachment_path

db = SessionLocal()

# 查找带附件的项目
projects_with_att = db.query(Project).filter(Project.config_attachment_updated_at.isnot(None)).all()

print(f"\n带有配置附件的项目数: {len(projects_with_att)}")
for p in projects_with_att:
    print(f"  - id={p.id}, name={p.name}, file={p.config_attachment_original_name}")

if not projects_with_att:
    print("\n没有找到带附件的项目，无法测试预览功能")
    print("\n解析预览功能的测试只能通过实际上传 Excel 附件后测试。")
    print("但可以先验证函数是否可导入并能处理空内容：")
    try:
        result = extract_workbook_preview(b"invalid data")
        print(f"  预览函数调用成功（预期失败）: {result}")
    except Exception as e:
        print(f"  预览函数对无效输入返回错误（正常）: {type(e).__name__}: {e}")
    sys.exit(0)

print("\n逐一测试带附件项目的预览功能：")
for p in projects_with_att:
    path = attachment_path(p.id)
    if not path.is_file():
        print(f"  [FAIL] 项目 {p.id}: DB 有记录但文件不存在 at {path}")
        continue
    try:
        raw = path.read_bytes()
        result = extract_workbook_preview(raw)
        summary = result.get("summary", {})
        sheets = result.get("sheet_names", [])
        print(f"  [PASS] 项目 {p.id} ({p.name}):")
        print(f"         工作表: {sheets}")
        print(f"         冷库={summary.get('cold_room_count',0)}, 设备={summary.get('device_count',0)}, 关系={summary.get('relation_count',0)}")
    except Exception as e:
        print(f"  [FAIL] 项目 {p.id}: {type(e).__name__}: {e}")

db.close()
