# 冷库项目登记管理系统 - 后端API

基于 **FastAPI + SQLAlchemy + MySQL** 的后端服务

---

## 📁 项目结构

```
backend/
├── app/
│   ├── api/                      # API路由
│   │   ├── equipment_library.py  # 标准设备库API
│   │   ├── projects.py           # 项目管理API（待创建）
│   │   ├── devices.py            # 设备管理API（待创建）
│   │   ├── gateways.py           # 网关管理API（待创建）
│   │   └── __init__.py
│   ├── models/                   # 数据库模型
│   │   ├── user.py               # 用户模型
│   │   ├── equipment_library.py  # 标准设备库模型
│   │   ├── project.py            # 项目和冷库模型
│   │   ├── device.py             # 设备和设备关系模型
│   │   ├── gateway.py            # 网关、邮寄、流程模型
│   │   └── __init__.py
│   ├── schemas/                  # Pydantic模型
│   │   ├── equipment_library.py
│   │   └── __init__.py
│   ├── config.py                 # 配置文件
│   ├── database.py               # 数据库连接
│   └── main.py                   # 主应用
├── requirements.txt              # Python依赖
├── env.example                   # 环境变量示例
└── README.md                     # 本文件
```

---

## 🎯 核心功能模块

### 1️⃣ **标准设备库管理** ✅ 已完成
- **设备品牌管理**：用户自己维护品牌库（精创、小精灵、卡乐等）
- **设备型号管理**：维护型号及参数（融霜方式、膨胀阀等）
- **支持复制**：快速创建相似配置的型号
- **设备类型**：冷风机、温控器、机组、电表、冷柜、融霜控制器

### 2️⃣ **项目管理** 🚧 待实现
- 项目CRUD
- 项目复制功能
- 冷库管理（自动计算容积）
- 期望到货时间管理
- 流程状态管理

### 3️⃣ **设备登记** 🚧 待实现
- 设备CRUD
- 设备复制功能
- 从标准库选择或手动输入
- 自动生成设备编号
- 关联冷库、网关

### 4️⃣ **设备关系管理** 🚧 待实现
- 温控器 ↔ 冷风机
- 机组 ↔ 冷风机/冷柜
- 电表 ↔ 机组/冷风机
- 融霜控制器 ↔ 冷风机

### 5️⃣ **网关和通讯配置** 🚧 待实现
- 网关管理
- 手机卡信息
- 端口分配
- RS485地址配置

### 6️⃣ **邮寄管理** 🚧 待实现
- 邮寄记录
- 快递跟踪
- 到货确认

### 7️⃣ **流程管理** 🚧 待实现
- 8个流程节点
- 流程推进
- 流程记录

---

## 🚀 快速开始

### 1. 环境要求
- Python 3.9+
- MySQL 8.0+

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置数据库

创建 `.env` 文件（参考 `env.example`）：

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/pm_system
SECRET_KEY=your-secret-key-here
```

### 4. 创建数据库

```sql
CREATE DATABASE pm_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. 访问API文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📊 数据库设计

### 核心表

1. **users** - 用户表
2. **equipment_brands** - 设备品牌表
3. **equipment_models** - 设备型号表
4. **projects** - 项目表
5. **cold_rooms** - 冷库表
6. **devices** - 设备表
7. **device_relations** - 设备关系表
8. **gateways** - 网关表
9. **mailing_records** - 邮寄记录表
10. **flow_records** - 流程记录表

### 设备编号规则

- 冷风机：**AC**-项目ID-序号 (AC-001-001)
- 温控器：**TC**-项目ID-序号 (TC-001-001)
- 机组：**UN**-项目ID-序号 (UN-001-001)
- 电表：**PM**-项目ID-序号 (PM-001-001)
- 冷柜：**FR**-项目ID-序号 (FR-001-001)
- 融霜控制器：**DF**-项目ID-序号 (DF-001-001)

---

## 🔌 API接口示例

### 标准设备库API

#### 1. 创建品牌

```http
POST /api/equipment-library/brands
Content-Type: application/json

{
  "name": "精创",
  "equipment_type": "thermostat",
  "description": "专业温控器品牌"
}
```

#### 2. 创建型号

```http
POST /api/equipment-library/models
Content-Type: application/json

{
  "brand_id": 1,
  "model_name": "STC-200+",
  "equipment_type": "air_cooler",
  "defrost_method": "electric",
  "has_intelligent_defrost": "yes",
  "expansion_valve_type": "electronic",
  "comm_port_type": "RS485",
  "comm_protocol": "Modbus RTU"
}
```

#### 3. 复制型号

```http
POST /api/equipment-library/models/1/copy?new_model_name=STC-300
```

#### 4. 获取品牌列表

```http
GET /api/equipment-library/brands?equipment_type=thermostat
```

#### 5. 获取型号列表

```http
GET /api/equipment-library/models?brand_id=1&equipment_type=air_cooler
```

---

## 🎨 设备类型枚举

```python
# 设备类型
AIR_COOLER = "air_cooler"           # 冷风机
THERMOSTAT = "thermostat"           # 温控器
UNIT = "unit"                       # 机组
METER = "meter"                     # 电表
FREEZER = "freezer"                 # 冷柜
DEFROST_CONTROLLER = "defrost_controller"  # 融霜控制器

# 冷库类型
LOW_TEMP = "low_temp"               # 低温库
REFRIGERATED = "refrigerated"       # 冷藏库
MEDIUM_TEMP = "medium_temp"         # 中温库

# 关系类型
THERMOSTAT_TO_AIR_COOLER           # 温控器→冷风机
UNIT_TO_AIR_COOLER                  # 机组→冷风机
UNIT_TO_FREEZER                     # 机组→冷柜
METER_TO_UNIT                       # 电表→机组
METER_TO_AIR_COOLER                 # 电表→冷风机
DEFROST_TO_AIR_COOLER              # 融霜控制器→冷风机
```

---

## 🔥 核心特性

### ✅ 用户自定义标准库
- 用户可以自己维护品牌库和型号库
- 不同设备类型独立管理
- 支持添加、编辑、删除、复制

### ✅ 设备复制功能
- 型号复制：快速创建相似配置的型号
- 设备复制（待实现）：快速添加相同配置的设备
- 项目复制（待实现）：复制整个项目及设备

### ✅ 灵活的设备参数
- 冷风机：融霜方式、智能融霜、膨胀阀
- 所有设备：通讯端口、通讯协议
- 支持JSON格式的扩展参数

### ✅ 完整的关系管理
- 设备之间的关联关系
- 设备与网关的关联
- 设备与冷库的关联

---

## 📝 TODO列表

- [ ] 实现项目管理API
- [ ] 实现设备登记API（支持复制）
- [ ] 实现设备关系管理API
- [ ] 实现网关和通讯配置API
- [ ] 实现邮寄管理API
- [ ] 实现流程管理API
- [ ] 实现用户认证和授权
- [ ] 添加数据验证和错误处理
- [ ] 添加单元测试
- [ ] 添加API文档和注释

---

## 🛠️ 技术栈

- **FastAPI**: 现代、快速的Web框架
- **SQLAlchemy**: ORM框架
- **Pydantic**: 数据验证
- **MySQL**: 关系数据库
- **Uvicorn**: ASGI服务器

---

## 📞 后续开发

如需继续开发其他API模块，请参考 `equipment_library.py` 的实现方式：

1. 在 `app/schemas/` 创建Pydantic模型
2. 在 `app/api/` 创建路由
3. 在 `app/main.py` 注册路由
4. 测试API功能

---

**状态**: 🚧 核心架构已搭建，标准设备库API已完成，其他模块待开发
