# -*- coding: utf-8 -*-
"""
PM_System 全量 API 冒烟测试（TestClient，无需先启动 uvicorn）。

包含：
  1) 子进程执行 scripts/smoke_pm_system.py（导出中文等）
  2) 认证、项目、设备、网关、标准库、用户等只读接口

用法（在 backend 目录下）:
  python scripts/full_system_test.py

退出码：0 全部通过，1 存在失败。
"""
from __future__ import annotations

import os
import subprocess
import sys
from typing import Any, List, Tuple

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)
os.chdir(BACKEND_ROOT)


def main() -> int:
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app, raise_server_exceptions=True)
    # redirect_slashes=False 时，各模块根列表须带尾部斜杠，如 /api/projects/
    def bearer(token: str | None) -> dict[str, str]:
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    results: List[Tuple[str, bool, str]] = []

    def chk(name: str, ok: bool, detail: str = "") -> None:
        results.append((name, ok, detail))

    def get(path: str, headers: dict | None = None, **kw: Any) -> Any:
        return client.get(path, headers=headers or {}, **kw)

    def post(path: str, **kw: Any) -> Any:
        return client.post(path, **kw)

    # ----- 0) 既有导出/中文冒烟 -----
    smoke_py = os.path.join(BACKEND_ROOT, "scripts", "smoke_pm_system.py")
    if os.path.isfile(smoke_py):
        p = subprocess.run(
            [sys.executable, smoke_py],
            cwd=BACKEND_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        chk(
            "smoke_pm_system.py",
            p.returncode == 0,
            (p.stdout or "") + (p.stderr or "")[:500],
        )
    else:
        chk("smoke_pm_system.py", False, "file missing")

    # ----- 1) 基础与文档 -----
    r = get("/health")
    chk("GET /health", r.status_code == 200 and r.json().get("status") == "ok", r.text[:200])

    r = get("/api")
    chk("GET /api", r.status_code == 200, r.text[:120])

    r = get("/openapi.json")
    chk("GET /openapi.json", r.status_code == 200, "len=%s" % len(r.text))

    r = get("/docs")
    chk("GET /docs (Swagger)", r.status_code == 200, "")

    r = get("/project-list.html")
    chk("GET /project-list.html (静态)", r.status_code == 200, "")

    # ----- 2) JWT 登录链路 -----
    r = post(
        "/api/auth/login",
        json={"username": "admin001", "password": "admin@2024!"},
    )
    chk("POST /api/auth/login (admin)", r.status_code == 200, r.text[:200])
    token: str | None = None
    if r.status_code == 200:
        body = r.json()
        token = body.get("access_token")
        chk("login 返回 access_token", bool(token), "")
    H_admin = bearer(token)
    if token:
        r = get("/api/auth/me", headers=H_admin)
        chk("GET /api/auth/me (Bearer)", r.status_code == 200, r.text[:200])

    # 兼容 Header 登录（须使用带尾部斜杠的路径，否则在 redirect_slashes=False 下会 404）
    r = get(
        "/api/users/",
        headers={
            "X-Username": "admin001",
            "X-User-Role": "admin",
            "Content-Type": "application/json",
        },
    )
    chk("GET /api/users/ (X-Username 兼容)", r.status_code == 200, r.text[:120])

    # ----- 3) 用户（管理员）-----
    r = get("/api/users/", headers=H_admin)
    chk(
        "GET /api/users/ (Bearer)",
        r.status_code == 200,
        "n=%s" % len(r.json() if r.status_code == 200 else []),
    )

    r = get("/api/users/companies", headers=H_admin)
    chk("GET /api/users/companies", r.status_code == 200, "")

    # ----- 4) 项目聚合 -----
    r = get("/api/projects/", headers=H_admin)
    chk("GET /api/projects/", r.status_code == 200, "")
    project_ids: list[int] = []
    if r.status_code == 200 and isinstance(r.json(), list):
        for p in r.json():
            if isinstance(p, dict) and p.get("id") is not None:
                project_ids.append(int(p["id"]))

    r = get("/api/projects/stats/summary", headers=H_admin)
    chk("GET /api/projects/stats/summary", r.status_code == 200, "")

    r = get("/api/projects/business-options", headers=H_admin)
    chk("GET /api/projects/business-options", r.status_code == 200, "")

    r = get("/api/projects/contacts", headers=H_admin)
    chk("GET /api/projects/contacts", r.status_code == 200, "")

    pid = project_ids[0] if project_ids else None
    if pid is not None:
        r = get(f"/api/projects/{pid}", headers=H_admin)
        chk("GET /api/projects/{id}", r.status_code == 200, "")

        r = get(f"/api/projects/{pid}/cold-rooms", headers=H_admin)
        chk("GET /api/projects/{id}/cold-rooms", r.status_code == 200, "")

        r = get("/api/devices/", headers=H_admin, params={"project_id": pid})
        chk("GET /api/devices (project_id)", r.status_code == 200, "")

        r = get(f"/api/devices/stats/{pid}", headers=H_admin)
        chk("GET /api/devices/stats/{project_id}", r.status_code == 200, "")

        r = get("/api/devices/relations", headers=H_admin, params={"project_id": pid})
        chk("GET /api/devices/relations", r.status_code == 200, "")

        r = get("/api/gateways/", headers=H_admin, params={"project_id": pid})
        chk("GET /api/gateways (project_id)", r.status_code == 200, "")

        r = get("/api/gateways/mailing", headers=H_admin, params={"project_id": pid})
        chk("GET /api/gateways/mailing", r.status_code == 200, "")

        r = get("/api/gateways/flows", headers=H_admin, params={"project_id": pid})
        chk("GET /api/gateways/flows", r.status_code == 200, "")

        r = get(f"/api/projects/{pid}/export-config-xlsx", headers=H_admin)
        chk(
            "GET export-config-xlsx",
            r.status_code == 200 and len(r.content) > 1000,
            "status=%s len=%s" % (r.status_code, len(r.content)),
        )

        r = get(f"/api/projects/{pid}/config-attachment/preview", headers=H_admin)
        chk(
            "GET config-attachment/preview (404或200均可)",
            r.status_code in (200, 404),
            str(r.status_code),
        )
    else:
        chk("跳过依赖 project_id 的接口", True, "数据库无项目")

    # ----- 5) 标准设备库 / 网关库 -----
    r = get("/api/equipment-library/categories", headers=H_admin)
    chk("GET /api/equipment-library/categories", r.status_code == 200, "")

    r = get("/api/equipment-library/brands", headers=H_admin)
    chk("GET /api/equipment-library/brands", r.status_code == 200, "")

    r = get("/api/equipment-library/models", headers=H_admin)
    chk("GET /api/equipment-library/models", r.status_code == 200, "")

    r = get("/api/gateway-library/models", headers=H_admin)
    chk("GET /api/gateway-library/models", r.status_code == 200, "")

    r = get("/api/gateway-library/inventory", headers=H_admin)
    chk("GET /api/gateway-library/inventory", r.status_code == 200, "")

    r = get("/api/gateway-library/inventory/available", headers=H_admin)
    chk("GET /api/gateway-library/inventory/available", r.status_code == 200, "")

    # ----- 6) 客户账号：应能访问项目列表（可能为空）-----
    rc = post(
        "/api/auth/login",
        json={"username": "customer001", "password": "customer@2024!"},
    )
    tok_c: str | None = rc.json().get("access_token") if rc.status_code == 200 else None
    chk("POST /api/auth/login (customer)", rc.status_code == 200, rc.text[:120])
    H_cust = bearer(tok_c)
    r = get("/api/projects/", headers=H_cust)
    chk(
        "GET /api/projects/ (customer)",
        r.status_code == 200 and isinstance(r.json(), list),
        "",
    )

    # ----- 汇总 -----
    failed = [x for x in results if not x[1]]
    ok_n = sum(1 for x in results if x[1])
    print("full_system_test: %d passed, %d failed (total %d)" % (ok_n, len(failed), len(results)))
    if failed:
        print("--- 失败项 ---")
        for name, _, detail in failed:
            print(" FAIL:", name, "|", detail[:300] if detail else "")
        return 1
    print("OK: full_system_test all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
