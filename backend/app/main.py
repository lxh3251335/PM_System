"""
FastAPI 主应用
修复CORS重定向问题
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from .config import settings
from .database import engine, Base, SessionLocal
from . import models  # noqa: F401  # 确保模型在 create_all 前全部注册到 metadata
from .models.user import User
from .password_utils import hash_password_bcrypt, needs_rehash
import os


def _migrate_add_columns() -> None:
    """增量迁移：为已有表添加新列（SQLite 不支持 create_all 自动加列）"""
    from sqlalchemy import text, inspect
    db = SessionLocal()
    try:
        insp = inspect(engine)
        migrations = [
            ("gateways", "serial_no", "VARCHAR(100)"),
        ]
        for table, col, col_type in migrations:
            if table in insp.get_table_names():
                existing = [c["name"] for c in insp.get_columns(table)]
                if col not in existing:
                    db.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                    db.commit()
    finally:
        db.close()


def ensure_default_users() -> None:
    """初始化默认账号（不存在时创建）；同时将旧 SHA256 密码迁移到 bcrypt"""
    db = SessionLocal()
    try:
        defaults = [
            {"username": "admin001", "password": "admin@2024!", "role": "admin", "company_name": "系统管理"},
            {"username": "customer001", "password": "customer@2024!", "role": "customer", "company_name": "演示客户"},
        ]
        for item in defaults:
            user = db.query(User).filter(User.username == item["username"]).first()
            if not user:
                db.add(
                    User(
                        username=item["username"],
                        password_hash=hash_password_bcrypt(item["password"]),
                        role=item["role"],
                        company_name=item.get("company_name", ""),
                        is_active=True,
                    )
                )
            else:
                if needs_rehash(user.password_hash):
                    user.password_hash = hash_password_bcrypt(item["password"])
                if not user.company_name and item.get("company_name"):
                    user.company_name = item["company_name"]
        db.commit()
    finally:
        db.close()


# ensure_default_users()

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="冷库项目登记管理系统 - 后端API",
    redirect_slashes=False,  # 禁用自动重定向，避免CORS预检失败
    docs_url=None,  # 禁用默认的 /docs 路由，使用自定义的
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # 隐藏 Models
    }
)

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    Base.metadata.create_all(bind=engine)
    _migrate_add_columns()
    ensure_default_users()

# 挂载静态文件目录（用于自定义 Swagger CSS）
# static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
# if os.path.exists(static_dir):
#     app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用冷库项目登记管理系统API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义 Swagger UI 文档页面，注入自定义 CSS"""
    # 自定义 CSS 样式
    custom_css = """
    <style>
        /* 标题样式增强 */
        .info .title {
            font-size: 38px !important;  /* 从默认 36px 增加到 38px */
            font-weight: 600 !important;
        }
        
        /* HTTP 方法标签样式增强 */
        .opblock-summary-method {
            font-size: 16px !important;  /* 字体大小从 14px 增加到 16px */
            font-weight: 700 !important;
            min-width: 90px !important;  /* 宽度从 80px 增加到 90px */
            padding: 8px 15px !important;  /* 增加内边距，让按钮更大 */
            line-height: 1.4 !important;
        }
        
        /* 整个摘要区域也稍微增大 */
        .opblock-summary {
            padding: 8px !important;
        }
        
        /* GET 方法更醒目 */
        .opblock-get .opblock-summary-method {
            font-size: 17px !important;
        }
        
        /* POST 方法更醒目 */
        .opblock-post .opblock-summary-method {
            font-size: 17px !important;
        }
        
        /* PUT 方法更醒目 */
        .opblock-put .opblock-summary-method {
            font-size: 17px !important;
        }
        
        /* DELETE 方法更醒目 */
        .opblock-delete .opblock-summary-method {
            font-size: 17px !important;
        }
    </style>
    """
    
    # 获取默认的 Swagger UI HTML
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - 接口文档",
    )
    
    # 将 HTML 转换为字符串并注入自定义 CSS
    html_content = html.body.decode('utf-8')
    html_content = html_content.replace('</head>', custom_css + '</head>')
    
    return HTMLResponse(content=html_content)


# 导入路由
from .api import equipment_library, projects, devices, gateways, users, auth, gateway_library
app.include_router(equipment_library.router, prefix="/api/equipment-library", tags=["标准设备库"])
app.include_router(gateway_library.router, prefix="/api/gateway-library", tags=["网关型号库与库存"])
app.include_router(projects.router, prefix="/api/projects", tags=["项目管理"])
app.include_router(devices.router, prefix="/api/devices", tags=["设备管理"])
app.include_router(gateways.router, prefix="/api/gateways", tags=["网关和通讯配置"])
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])

# 挂载前端静态文件（放在路由注册之后，作为 fallback）
demo_dir = os.path.join(os.path.dirname(__file__), "..", "..", "demo")
if os.path.exists(demo_dir):
    app.mount("/", StaticFiles(directory=demo_dir, html=True), name="demo")
