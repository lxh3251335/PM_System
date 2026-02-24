# 后端架构设计文档

## 📐 整体架构

```
┌─────────────────────────────────────────────────┐
│           Frontend (Vue 3 / Demo)              │
│              HTTP Requests (REST)               │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│            FastAPI Application                  │
│  ┌──────────────────────────────────────────┐  │
│  │         API Routes (Endpoints)            │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │ • /api/equipment-library  ✅       │  │  │
│  │  │ • /api/projects           🚧       │  │  │
│  │  │ • /api/devices            🚧       │  │  │
│  │  │ • /api/gateways           🚧       │  │  │
│  │  │ • /api/auth               🚧       │  │  │
│  │  └────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │          Business Logic                   │  │
│  │  • Pydantic Schemas (Validation)         │  │
│  │  • Service Layer (Business Rules)        │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │       Data Access Layer (ORM)            │  │
│  │  • SQLAlchemy Models                     │  │
│  │  • Database Session Management           │  │
│  └──────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│              MySQL Database                     │
│  • users                                        │
│  • equipment_brands / equipment_models          │
│  • projects / cold_rooms                        │
│  • devices / device_relations                   │
│  • gateways / mailing_records / flow_records    │
└─────────────────────────────────────────────────┘
```

---

## 🗂️ 目录结构说明

### `/app` - 应用核心目录

```
app/
├── main.py              # FastAPI主应用，注册路由和中间件
├── config.py            # 配置管理（数据库URL、JWT密钥等）
├── database.py          # 数据库连接和会话管理
│
├── models/              # 数据库模型（SQLAlchemy ORM）
│   ├── __init__.py
│   ├── user.py                 # 用户模型
│   ├── equipment_library.py    # 标准设备库模型
│   ├── project.py              # 项目和冷库模型
│   ├── device.py               # 设备和设备关系模型
│   └── gateway.py              # 网关、邮寄、流程模型
│
├── schemas/             # Pydantic模型（数据验证和序列化）
│   ├── __init__.py
│   ├── equipment_library.py    # 设备库Schema
│   ├── project.py              # 项目Schema（待创建）
│   ├── device.py               # 设备Schema（待创建）
│   └── gateway.py              # 网关Schema（待创建）
│
└── api/                 # API路由
    ├── __init__.py
    ├── equipment_library.py    # 标准设备库API ✅
    ├── projects.py             # 项目管理API 🚧
    ├── devices.py              # 设备管理API 🚧
    ├── gateways.py             # 网关管理API 🚧
    └── auth.py                 # 认证API 🚧
```

---

## 💾 数据库模型设计

### 1. 用户模块

```python
# User - 用户表
- id: 主键
- username: 用户名（唯一）
- password_hash: 密码哈希
- role: 角色（user=用户方, factory=厂家方）
- is_active: 是否激活
- created_at: 创建时间
```

### 2. 标准设备库模块 ✅

```python
# EquipmentBrand - 设备品牌表
- id: 主键
- name: 品牌名称
- equipment_type: 设备类型（air_cooler, thermostat, unit等）
- description: 品牌描述
- created_by: 创建人ID

# EquipmentModel - 设备型号表
- id: 主键
- brand_id: 品牌ID（外键）
- model_name: 型号名称
- equipment_type: 设备类型
# 冷风机特有
- defrost_method: 融霜方式
- has_intelligent_defrost: 智能融霜（yes/no）
- expansion_valve_type: 膨胀阀方式
# 通用通讯参数
- comm_port_type: 通讯端口类型
- comm_protocol: 通讯协议
- specifications: 规格参数（JSON）
```

**核心特点**：
- 用户可自己维护品牌和型号库
- 支持不同设备类型独立管理
- 支持型号复制功能
- 融霜方式、膨胀阀等参数预设

### 3. 项目模块

```python
# Project - 项目表
- id: 主键
- project_no: 项目编号（唯一，自动生成）
- name: 项目名称
- end_customer: 最终用户
- business_type: 业务类型
- city: 城市
- address: 项目地址
- mailing_address: 邮寄地址
- recipient_name/phone: 收件人信息
- expected_arrival_time: 期望到货时间
- status: 项目流程状态（枚举）
- remarks: 备注
- created_by: 创建人ID

# ColdRoom - 冷库表
- id: 主键
- project_id: 项目ID（外键）
- name: 冷库名称
- room_type: 冷库类型（low_temp, refrigerated, medium_temp）
- design_temp_min/max: 设计温度范围
- area: 面积（㎡）
- height: 高度（m）
- volume: 容积（m³，自动计算 = area * height）
- refrigerant_type: 制冷剂类型（R410A, R404A等）
```

**核心特点**：
- 项目编号自动生成（PRJ20260127001）
- 冷库容积自动计算
- 8个流程状态管理
- 期望到货时间追踪

### 4. 设备模块

```python
# Device - 设备表
- id: 主键
- project_id: 项目ID（外键）
- cold_room_id: 冷库ID（外键，冷风机必填）
- device_no: 设备编号（AC-001-001等）
- device_type: 设备类型（枚举）
- brand: 品牌
- model: 型号
# 冷风机特有
- defrost_method: 融霜方式
- has_intelligent_defrost: 智能融霜
- expansion_valve_type: 膨胀阀方式
# 机组/冷风机特有
- factory_no: 出厂编号
# 通讯参数
- comm_port_type: 通讯端口类型
- comm_protocol: 通讯协议
# 网关配置
- gateway_id: 网关ID（外键）
- gateway_port: 网关端口号
- rs485_address: RS485地址
- specifications: 规格参数（JSON）
- remarks: 备注

# DeviceRelation - 设备关系表
- id: 主键
- project_id: 项目ID
- from_device_id: 源设备ID
- to_device_id: 目标设备ID
- relation_type: 关系类型（枚举）
- description: 关系描述
```

**设备类型枚举**：
- `air_cooler`: 冷风机
- `thermostat`: 温控器
- `unit`: 机组
- `meter`: 电表
- `freezer`: 冷柜
- `defrost_controller`: 智能融霜控制器

**关系类型枚举**：
- `thermostat_to_air_cooler`: 温控器→冷风机
- `unit_to_air_cooler`: 机组→冷风机
- `unit_to_freezer`: 机组→冷柜
- `meter_to_unit`: 电表→机组
- `meter_to_air_cooler`: 电表→冷风机
- `defrost_to_air_cooler`: 融霜控制器→冷风机

### 5. 网关和通讯模块

```python
# Gateway - 网关表
- id: 主键
- project_id: 项目ID
- gateway_no: 网关编号
- brand: 品牌
- model: 型号
- total_ports: 总端口数
# 手机卡信息
- sim_card_no: 手机卡号
- sim_operator: 运营商
- sim_iccid: ICCID
# 网络信息
- ip_address: IP地址
- mac_address: MAC地址
- specifications: 规格参数（JSON）

# MailingRecord - 邮寄记录表
- id: 主键
- project_id: 项目ID
- gateway_id: 网关ID
- tracking_no: 快递单号
- courier_company: 快递公司
- mailing_date: 邮寄日期
- expected_arrival_date: 预计到达日期
- actual_arrival_date: 实际到达日期
- recipient_name/phone/address: 收件信息
- item_description: 邮寄物品描述

# FlowRecord - 流程记录表
- id: 主键
- project_id: 项目ID
- flow_step: 流程步骤
- step_name: 步骤名称
- status: 状态（pending, in_progress, completed）
- started_at: 开始时间
- completed_at: 完成时间
- handler_id: 处理人ID
- remarks: 备注
```

---

## 🔌 API设计规范

### RESTful API风格

```
GET    /api/resource         # 获取资源列表
GET    /api/resource/:id     # 获取单个资源
POST   /api/resource         # 创建资源
PUT    /api/resource/:id     # 更新资源
DELETE /api/resource/:id     # 删除资源
POST   /api/resource/:id/copy  # 复制资源
```

### 响应格式

成功响应：
```json
{
  "id": 1,
  "name": "...",
  "created_at": "2026-01-27T10:00:00Z"
}
```

列表响应：
```json
[
  { "id": 1, "name": "..." },
  { "id": 2, "name": "..." }
]
```

错误响应：
```json
{
  "detail": "错误信息"
}
```

---

## 🎯 核心功能实现

### ✅ 1. 标准设备库管理（已完成）

**功能点**：
- ✅ 品牌CRUD
- ✅ 型号CRUD
- ✅ 型号复制功能
- ✅ 按设备类型筛选
- ✅ 按品牌筛选

**API端点**：
```
GET    /api/equipment-library/brands
POST   /api/equipment-library/brands
GET    /api/equipment-library/brands/:id
PUT    /api/equipment-library/brands/:id
DELETE /api/equipment-library/brands/:id

GET    /api/equipment-library/models
POST   /api/equipment-library/models
GET    /api/equipment-library/models/:id
PUT    /api/equipment-library/models/:id
DELETE /api/equipment-library/models/:id
POST   /api/equipment-library/models/:id/copy
```

### 🚧 2. 项目管理（待开发）

**功能点**：
- 项目CRUD
- 项目复制功能
- 冷库管理（自动计算容积）
- 期望到货时间管理
- 项目流程状态管理

### 🚧 3. 设备登记（待开发）

**功能点**：
- 设备CRUD
- 设备复制功能
- 从标准库选择
- 自动生成设备编号
- 关联冷库和网关

### 🚧 4. 设备关系管理（待开发）

**功能点**：
- 创建设备关系
- 查询设备关系
- 删除设备关系
- 关系可视化数据

### 🚧 5. 网关和通讯配置（待开发）

**功能点**：
- 网关管理
- 手机卡管理
- 端口分配
- RS485地址配置

### 🚧 6. 邮寄管理（待开发）

**功能点**：
- 邮寄记录管理
- 快递跟踪
- 到货确认

### 🚧 7. 流程管理（待开发）

**功能点**：
- 流程节点管理
- 流程推进
- 流程记录查询

---

## 🔐 认证和授权（待开发）

### JWT认证流程

```
1. 用户登录 → POST /api/auth/login
2. 返回JWT Token
3. 后续请求携带Token：Authorization: Bearer <token>
4. 中间件验证Token
5. 解析用户信息
```

### 角色权限

- **user（用户方）**：
  - 创建项目
  - 登记设备
  - 查看流程进度
  
- **factory（厂家方）**：
  - 查看所有项目
  - 配置网关
  - 管理邮寄
  - 更新流程状态

---

## 🧪 测试策略

### 单元测试

```python
# 测试数据库模型
def test_create_brand():
    brand = EquipmentBrand(name="精创", equipment_type="thermostat")
    assert brand.name == "精创"

# 测试API端点
def test_get_brands(client):
    response = client.get("/api/equipment-library/brands")
    assert response.status_code == 200
```

### 集成测试

- 测试完整的API流程
- 测试数据库事务
- 测试设备复制功能
- 测试项目复制功能

---

## 📦 部署建议

### 开发环境

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境

```bash
# 使用Gunicorn + Uvicorn Workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker部署

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔧 配置管理

### 环境变量

```env
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
CORS_ORIGINS=["http://localhost:3000"]
```

### 配置加载

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    # ...
    
    class Config:
        env_file = ".env"
```

---

## 📈 性能优化

### 数据库优化

- 合理创建索引
- 使用连接池
- 懒加载关联数据
- 批量操作

### API优化

- 分页查询
- 响应缓存
- 异步处理
- 压缩响应

---

## 🎯 下一步开发计划

1. ✅ **标准设备库API** - 已完成
2. 🚧 **项目管理API** - 进行中
3. 🚧 **设备登记API** - 待开发
4. 🚧 **设备关系API** - 待开发
5. 🚧 **网关配置API** - 待开发
6. 🚧 **邮寄管理API** - 待开发
7. 🚧 **流程管理API** - 待开发
8. 🚧 **认证授权** - 待开发
9. 🚧 **单元测试** - 待开发
10. 🚧 **部署文档** - 待开发

---

**当前状态**: ✅ 核心架构已搭建，标准设备库API已完成并可测试
