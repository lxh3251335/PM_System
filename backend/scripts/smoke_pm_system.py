# -*- coding: utf-8 -*-
"""
PM_System 后端冒烟测试（无需手动启动 uvicorn，使用 Starlette TestClient）。

用法（在 backend 目录下）:
  python scripts/smoke_pm_system.py

失败时进程退出码为 1，并打印第一条失败断言。
"""
from __future__ import annotations

import io
import os
import sys

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)
os.chdir(BACKEND_ROOT)


def main() -> int:
    from fastapi.testclient import TestClient
    from openpyxl import load_workbook

    from app.database import SessionLocal
    from app.main import app
    from app.models.project import Project
    from app.services.project_config_excel import (
        EXPORT_VERSION,
        build_workbook_bytes,
        _dt_label,
    )

    fails: list[str] = []
    n_ok = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal n_ok
        if cond:
            n_ok += 1
        else:
            fails.append(f"{name}: {detail}")

    client = TestClient(app)

    r = client.get("/health")
    check("GET /health", r.status_code == 200 and r.json().get("status") == "ok", r.text)

    r = client.get("/api")
    check("GET /api", r.status_code == 200, r.text)

    db = SessionLocal()
    try:
        first = db.query(Project.id).order_by(Project.id).first()
        if not first:
            fails.append("数据库中无任何项目，跳过导出相关断言")
        else:
            pid = int(first[0])
            data, safe = build_workbook_bytes(db, pid)
            check("build_workbook_bytes 非空", len(data) > 2000, "长度过小")
            check("build_workbook safe_name", bool(safe), safe)

            wb = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
            try:
                a2 = wb["项目"]["A2"].value
                s_a2 = str(a2 or "")
                check(
                    "项目表A2为中文说明列(非project_id)",
                    "project_id" not in s_a2.replace(" ", "").lower(),
                    repr(s_a2)[:80],
                )
                check("项目表A2含项目字样", "项目" in s_a2, repr(s_a2)[:80])

                b1_cold = str(wb["冷库"]["B1"].value or "")
                check("冷库表B1表头无room_type英文后缀", "room_type" not in b1_cold.lower(), b1_cold)
                check("冷库表B1为冷库类型", b1_cold == "冷库类型", b1_cold)

                b1_dev = str(wb["设备"]["B1"].value or "")
                check("设备表B1无device_type英文后缀", "device_type" not in b1_dev.lower(), b1_dev)
                check("设备表B1为设备类型", b1_dev == "设备类型", b1_dev)

                b2_dev = str(wb["设备"]["B2"].value or "")
                check(
                    "设备第2行类型列为中文或空(非thermostat英文)",
                    b2_dev == "" or b2_dev not in ("thermostat", "unit", "meter", "air_cooler"),
                    b2_dev,
                )

                meta = wb["导出信息"]["B1"].value
                check("导出信息B1版本号", int(meta) == int(EXPORT_VERSION), str(meta))
            finally:
                wb.close()

            auth = {"X-Username": "admin001"}
            rx = client.get(f"/api/projects/{pid}/export-config-xlsx", headers=auth)
            check("HTTP 导出 200", rx.status_code == 200, rx.text[:200])
            if rx.status_code == 200:
                check("响应头导出版本", rx.headers.get("x-pm-export-version") == str(EXPORT_VERSION), str(rx.headers))
                dispo = rx.headers.get("content-disposition") or ""
                check("Content-Disposition 含 _config_v", "_config_v" in dispo, dispo[:120])
    finally:
        db.close()

    check("_dt_label(AIR_COOLER) 中文", "冷" in _dt_label("AIR_COOLER"), _dt_label("AIR_COOLER"))

    if fails:
        print("FAILED (%d):" % len(fails))
        for f in fails:
            print(" -", f)
        return 1
    print("OK: smoke_pm_system passed (%d checks)" % n_ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
