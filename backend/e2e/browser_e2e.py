# -*- coding: utf-8 -*-
"""
PM_System 浏览器端 E2E（Playwright + Chromium）。

覆盖：首页入口、管理员/客户登录、项目列表交互、侧边栏主要页面跳转；
若库中有项目则尝试「进入」打开项目详情。

安装（在 backend 目录）:
  pip install -r e2e/requirements.txt
  playwright install chromium

运行（会自动在本机 8000 启动 uvicorn；需保证 8000 未被占用）:
  python e2e/browser_e2e.py

说明：demo 的 config.js 在非 8000 端口打开页面时会强制把 API 指到 :8000，
若 E2E 把后端起在其它端口会导致浏览器跨域登录失败，故默认与生产一致使用 8000。

已手动启动 uvicorn 于 8000 时:
  python e2e/browser_e2e.py --no-serve

其它端口的后端 + 静态页分离部署时，请自行保证前端 API_BASE_URL 与页面同源或 CORS 正确后再 --no-serve。

调试（有界面）:
  python e2e/browser_e2e.py --headed
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 与 demo/config.js 中非 8000 端口时的 API 重写逻辑对齐：页面与 API 同用 8000 避免 CORS
DEFAULT_PORT = 8000


def _wait_health(base_url: str, timeout_sec: float = 90.0) -> None:
    url = base_url.rstrip("/") + "/health"
    deadline = time.monotonic() + timeout_sec
    last_err: str | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                if resp.status == 200:
                    return
        except (urllib.error.URLError, OSError) as e:
            last_err = str(e)
        time.sleep(0.4)
    raise RuntimeError("health check timeout: %s last=%s" % (url, last_err))


def _start_uvicorn(port: int) -> subprocess.Popen:
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=BACKEND_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def _stop_process(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()


def _accept_dialogs(page) -> None:
    page.on("dialog", lambda d: d.accept())


def _login(page, base: str, role: str) -> None:
    """role: 'admin' | 'customer'"""
    page.goto(base.rstrip("/") + "/login.html", wait_until="domcontentloaded")
    page.wait_for_timeout(300)
    page.locator('.user-type-btn[data-type="%s"]' % role).click()
    page.fill("#username", "admin001" if role == "admin" else "customer001")
    page.fill("#password", "admin@2024!" if role == "admin" else "customer@2024!")
    page.get_by_role("button", name="立即登录").click()
    # 不用默认 load：部分页面外链资源慢会拖死 wait_for_url
    page.wait_for_url("**/project-list.html", timeout=45000, wait_until="domcontentloaded")


def _assert_title_contains(page, needle: str, step: str) -> None:
    title = page.title()
    if needle not in title:
        raise AssertionError("%s: title 应包含 %r，实际: %r" % (step, needle, title))


def _wait_after_logout(page, base: str, timeout_sec: float = 45.0) -> None:
    """nav.js 将顶栏改为 doLogout()，清除 token 后跳转 login.html（与静态 HTML 的 index 不同）。"""
    page.locator("header.top-bar button.btn-logout").click()
    origin = base.rstrip("/")
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        u = page.url
        if "login.html" in u or "index.html" in u or u.rstrip("/") == origin:
            return
        time.sleep(0.2)
    raise AssertionError("等待退出后页面超时，当前 URL: " + page.url)


def _click_nav_by_href(page, href: str) -> None:
    """侧栏链接用 href 定位，避免中文在部分环境下 has_text 异常。"""
    page.locator('aside.sidebar a.nav-item[href="%s"]' % href).first.click()
    page.wait_for_load_state("domcontentloaded")


def run_flows(page, base: str) -> None:
    _accept_dialogs(page)

    # --- 首页 -> 登录 ---
    page.goto(base.rstrip("/") + "/index.html", wait_until="domcontentloaded")
    page.get_by_role("link", name="立即体验").first.click()
    page.wait_for_url("**/login.html", wait_until="domcontentloaded")
    _assert_title_contains(page, "登录", "首页跳转登录")

    # --- 管理员 ---
    _login(page, base, "admin")
    _assert_title_contains(page, "项目列表", "管理员登录后")

    page.get_by_role("button", name="搜索").click()
    page.wait_for_timeout(400)

    # project-list 等页会加载 nav.js，侧边栏由脚本按角色重绘（与静态 HTML 不完全一致）
    nav_pages = [
        ("shipping-register.html", "发货登记"),
        ("equipment-config.html", "设备配置管理"),
        ("business-options.html", "业务类型配置"),
        ("gateway-inventory.html", "网关库存"),
        ("user-management.html", "用户管理"),
    ]
    for href, title_needle in nav_pages:
        _click_nav_by_href(page, href)
        _assert_title_contains(page, title_needle, "侧栏 " + href)
    _click_nav_by_href(page, "project-list.html")
    _assert_title_contains(page, "项目列表", "返回项目列表")

    # 未挂在当前侧栏的页面：直接打开（仍可能被 requireAuth 允许）
    for rel, title_needle in (
        ("device-management.html", "设备管理"),
        ("gateway-config.html", "网关配置"),
    ):
        page.goto(base.rstrip("/") + "/" + rel, wait_until="domcontentloaded")
        _assert_title_contains(page, title_needle, "直达 " + rel)
    page.goto(base.rstrip("/") + "/project-list.html", wait_until="domcontentloaded")

    page.get_by_role("button", name="+ 新建项目").click()
    page.wait_for_url("**/project-create.html", wait_until="domcontentloaded")
    _assert_title_contains(page, "新建项目", "新建项目按钮")
    # 新建项目页无 app 侧栏，直接回列表
    page.goto(base.rstrip("/") + "/project-list.html", wait_until="domcontentloaded")

    enter = page.locator("button.btn-primary:has-text('进入')")
    if enter.count() > 0:
        enter.first.click()
        page.wait_for_url("**/project-detail.html*", wait_until="domcontentloaded")
        _assert_title_contains(page, "项目详情", "进入项目详情")
        _click_nav_by_href(page, "project-list.html")
        _assert_title_contains(page, "项目列表", "从详情返回列表")

    th = page.locator("th.sortable-th").first
    if th.is_visible():
        th.click()
        page.wait_for_timeout(300)

    # --- 客户：隐藏管理员菜单 ---
    page.evaluate("localStorage.clear()")
    page.goto(base.rstrip("/") + "/login.html", wait_until="domcontentloaded")
    _login(page, base, "customer")
    if page.locator("#navUserManagement").is_visible():
        raise AssertionError("客户账号应隐藏用户管理入口")
    if page.locator("#navBusinessOptions").is_visible():
        raise AssertionError("客户账号应隐藏业务类型配置入口")

    _wait_after_logout(page, base)


def main() -> int:
    parser = argparse.ArgumentParser(description="PM_System Playwright E2E")
    parser.add_argument(
        "--no-serve",
        action="store_true",
        help="不启动 uvicorn，使用环境变量 E2E_BASE_URL（默认 http://127.0.0.1:8000）",
    )
    parser.add_argument("--headed", action="store_true", help="有头模式，便于本地调试")
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="自动起服务时的端口（默认 8000，与静态 demo 的 API 配置一致）",
    )
    args = parser.parse_args()

    if args.no_serve:
        base = os.environ.get("E2E_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
        proc = None
    else:
        base = "http://127.0.0.1:%d" % args.port
        proc = _start_uvicorn(args.port)
        try:
            _wait_health(base)
        except Exception:
            err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
            _stop_process(proc)
            print("启动后端失败或 health 超时。", err[:800], file=sys.stderr)
            return 1

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("请先安装: pip install -r e2e/requirements.txt && playwright install chromium", file=sys.stderr)
        _stop_process(proc)
        return 1

    exit_code = 0
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not args.headed)
            context = browser.new_context(locale="zh-CN", viewport={"width": 1280, "height": 800})
            page = context.new_page()
            try:
                run_flows(page, base)
                print("OK: browser_e2e passed")
            except Exception as ex:
                print("FAIL:", ex, file=sys.stderr)
                exit_code = 1
            finally:
                browser.close()
    finally:
        _stop_process(proc)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
