"""项目配置 Excel 附件磁盘路径（文件名固定为 {id}.xlsx）"""
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
ATTACH_DIR = _BACKEND_ROOT / "data" / "project_config_attachments"


def attachment_path(project_id: int) -> Path:
    ATTACH_DIR.mkdir(parents=True, exist_ok=True)
    return ATTACH_DIR / f"{int(project_id)}.xlsx"


def remove_attachment_file(project_id: int) -> None:
    p = attachment_path(project_id)
    if p.is_file():
        p.unlink()
