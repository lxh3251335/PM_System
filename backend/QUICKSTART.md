# 快速开始指南 🚀

## 📋 前置要求

- Python 3.9 或更高版本
- MySQL 8.0 或更高版本
- pip 包管理器

---

## 🔧 安装步骤

### 1. 克隆项目

```bash
cd backend
```

### 2. 创建虚拟环境（推荐）

**Windows**:
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

#### 4.1 创建数据库

登录MySQL，创建数据库：

```sql
CREATE DATABASE pm_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 4.2 配置环境变量

复制 `env.example` 为 `.env`：

```bash
# Windows
copy env.example .env

# Linux/Mac
cp env.example .env
```

编辑 `.env` 文件，修改数据库连接信息：

```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/pm_system
SECRET_KEY=your-secret-key-change-this-in-production
```

### 5. 初始化数据库

运行初始化脚本，创建表和初始数据：

```bash
python init_data.py
```

输出示例：
```
========================================
初始化数据库...
========================================

1. 创建数据库表...
✅ 数据库表创建完成

2. 创建初始用户...
✅ 创建用户成功:
   - 用户名: user, 密码: user123 (用户方)
   - 用户名: factory, 密码: factory123 (厂家方)

3. 创建示例品牌数据...
✅ 创建 9 个品牌

4. 创建示例型号数据...
✅ 创建 5 个型号

========================================
✅ 数据库初始化完成！
========================================
```

### 6. 启动服务

#### 方式一：使用启动脚本（推荐）

**Windows**:
```bash
start.bat
```

**Linux/Mac**:
```bash
chmod +x start.sh
./start.sh
```

#### 方式二：直接启动

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 验证安装

打开浏览器访问：

- **根路径**: http://localhost:8000
- **健康检查**: http://localhost:8000/health
- **API文档**: http://localhost:8000/docs
- **ReDoc文档**: http://localhost:8000/redoc

---

## 🧪 测试API

### 方式一：使用Swagger UI（推荐）

1. 访问 http://localhost:8000/docs
2. 展开任意API端点
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute"
6. 查看响应结果

### 方式二：使用curl

#### 1. 获取品牌列表

```bash
curl -X GET "http://localhost:8000/api/equipment-library/brands"
```

#### 2. 创建品牌

```bash
curl -X POST "http://localhost:8000/api/equipment-library/brands" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "海尔",
    "equipment_type": "air_cooler",
    "description": "海尔冷风机"
  }'
```

#### 3. 获取型号列表

```bash
curl -X GET "http://localhost:8000/api/equipment-library/models?brand_id=1"
```

#### 4. 创建型号

```bash
curl -X POST "http://localhost:8000/api/equipment-library/models" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": 1,
    "model_name": "STC-300",
    "equipment_type": "thermostat",
    "comm_port_type": "RS485",
    "comm_protocol": "Modbus RTU"
  }'
```

#### 5. 复制型号

```bash
curl -X POST "http://localhost:8000/api/equipment-library/models/1/copy?new_model_name=STC-400"
```

### 方式三：使用Postman

1. 导入API集合（可从Swagger UI导出）
2. 设置 `base_url` 变量为 `http://localhost:8000`
3. 运行测试

---

## 📊 初始数据说明

### 用户账号

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| user | user123 | 用户方 | 创建项目、登记设备 |
| factory | factory123 | 厂家方 | 管理网关、邮寄 |

### 设备品牌

| 品牌名称 | 设备类型 | 说明 |
|---------|----------|------|
| 精创 | thermostat | 温控器品牌 |
| 小精灵 | thermostat | 温控器品牌 |
| 卡乐 | thermostat | 温控器品牌 |
| 格力 | air_cooler | 冷风机品牌 |
| 美的 | air_cooler | 冷风机品牌 |
| 比泽尔 | unit | 机组品牌 |
| 谷轮 | unit | 机组品牌 |
| 正泰 | meter | 电表品牌 |
| 德力西 | meter | 电表品牌 |

### 设备型号

| 品牌 | 型号 | 设备类型 | 特殊参数 |
|------|------|----------|----------|
| 精创 | STC-200+ | 温控器 | RS485, Modbus RTU |
| 小精灵 | XJL-8000 | 温控器 | RS485, Modbus RTU |
| 格力 | GL-CF-200 | 冷风机 | 电融霜, 智能融霜, 电子膨胀阀 |
| 美的 | MD-CF-150 | 冷风机 | 热气融霜, 无智能融霜, 热力膨胀阀 |
| 比泽尔 | BZ-250 | 机组 | RS485, Modbus RTU |

---

## 🎯 常见操作示例

### 1. 管理设备品牌

```python
# 使用Python requests库

import requests

BASE_URL = "http://localhost:8000/api/equipment-library"

# 创建品牌
brand_data = {
    "name": "海尔",
    "equipment_type": "air_cooler",
    "description": "海尔冷风机"
}
response = requests.post(f"{BASE_URL}/brands", json=brand_data)
print(response.json())

# 获取品牌列表
response = requests.get(f"{BASE_URL}/brands?equipment_type=thermostat")
print(response.json())

# 更新品牌
brand_update = {"description": "海尔专业冷风机"}
response = requests.put(f"{BASE_URL}/brands/10", json=brand_update)
print(response.json())

# 删除品牌
response = requests.delete(f"{BASE_URL}/brands/10")
print(response.json())
```

### 2. 管理设备型号

```python
# 创建型号
model_data = {
    "brand_id": 1,
    "model_name": "STC-500",
    "equipment_type": "thermostat",
    "comm_port_type": "RS485",
    "comm_protocol": "Modbus RTU",
    "description": "高级温控器"
}
response = requests.post(f"{BASE_URL}/models", json=model_data)
model_id = response.json()["id"]

# 复制型号
response = requests.post(f"{BASE_URL}/models/{model_id}/copy?new_model_name=STC-600")
print(response.json())

# 获取型号列表（带品牌信息）
response = requests.get(f"{BASE_URL}/models?brand_id=1")
for model in response.json():
    print(f"{model['brand']['name']} - {model['model_name']}")
```

### 3. 按设备类型筛选

```python
# 获取所有温控器品牌
response = requests.get(f"{BASE_URL}/brands?equipment_type=thermostat")
thermostat_brands = response.json()

# 获取所有冷风机品牌
response = requests.get(f"{BASE_URL}/brands?equipment_type=air_cooler")
air_cooler_brands = response.json()

# 获取格力品牌下的所有型号
brand_id = 4  # 格力
response = requests.get(f"{BASE_URL}/models?brand_id={brand_id}")
models = response.json()
```

---

## 🐛 故障排除

### 问题1: 数据库连接失败

**错误信息**:
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server on 'localhost'")
```

**解决方案**:
1. 确认MySQL服务已启动
2. 检查 `.env` 文件中的数据库连接信息
3. 确认数据库用户有访问权限

### 问题2: 端口被占用

**错误信息**:
```
OSError: [WinError 10048] 通常每个套接字地址(协议/网络地址/端口)只允许使用一次。
```

**解决方案**:
1. 更改端口号：`uvicorn app.main:app --reload --port 8001`
2. 或关闭占用8000端口的进程

### 问题3: 模块导入错误

**错误信息**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案**:
1. 确认虚拟环境已激活
2. 重新安装依赖：`pip install -r requirements.txt`

### 问题4: 表已存在

**错误信息**:
```
sqlalchemy.exc.ProgrammingError: (pymysql.err.ProgrammingError) (1050, "Table 'users' already exists")
```

**解决方案**:
这是正常的，表已经存在。如果需要重建数据库：
```sql
DROP DATABASE pm_system;
CREATE DATABASE pm_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
然后重新运行 `python init_data.py`

---

## 📚 下一步

完成快速开始后，您可以：

1. **阅读架构文档**: `ARCHITECTURE.md`
2. **查看API文档**: http://localhost:8000/docs
3. **查看完整README**: `README.md`
4. **开发其他API模块**: 参考 `equipment_library.py` 的实现

---

## 💡 提示

### 开发模式特性

- 自动重载：修改代码后自动重启服务
- 详细日志：显示SQL查询和请求日志
- 调试模式：显示详细错误信息

### 生产环境建议

1. 修改 `SECRET_KEY` 为强密码
2. 设置 `DEBUG=False`
3. 使用环境变量管理敏感信息
4. 配置CORS为特定域名
5. 使用Gunicorn启动多个Worker

---

**祝您使用愉快！** 🎉

如有问题，请查看：
- API文档: http://localhost:8000/docs
- 架构文档: ARCHITECTURE.md
- README: README.md
