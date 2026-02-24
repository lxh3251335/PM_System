# SQLite版本 - 5分钟快速启动 🚀

## 🎯 优势

### 为什么选择SQLite开发？
- ✅ **零配置**：无需安装MySQL，Python自带SQLite
- ✅ **一键启动**：3条命令就能运行
- ✅ **轻量级**：一个文件就是整个数据库
- ✅ **完美开发**：快速迭代，边测边改
- ✅ **无缝切换**：部署时一行配置切换到MySQL/PostgreSQL

---

## 🚀 5分钟启动步骤

### Step 1: 安装依赖（2分钟）

```powershell
cd D:\projects\PM_System\backend

# 安装Python依赖
pip install -r requirements.txt
```

### Step 2: 配置环境（30秒）

```powershell
# 复制配置文件
copy env.example .env
```

**就这样！不需要改任何东西！**
配置文件已经默认使用SQLite了。

### Step 3: 初始化数据库（1分钟）

```powershell
python init_data.py
```

**预期输出：**
```
开始初始化数据库...
数据库连接成功！
正在创建表结构...
表结构创建成功！
正在初始化用户数据...
创建用户: user (用户)
创建用户: factory (厂家)
正在初始化设备库数据...
创建品牌: 比泽尔 (机组)
... 更多初始化信息 ...
数据初始化完成！

✓ SQLite数据库文件已创建：pm_system.db
```

### Step 4: 启动后端（30秒）

```powershell
# Windows
start.bat

# 或手动启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: 验证运行（30秒）

浏览器打开：
- **API文档**: http://localhost:8000/docs ✅
- **健康检查**: http://localhost:8000/ ✅
- **品牌列表**: http://localhost:8000/api/equipment/brands ✅

---

## ✅ 完成！

**就这么简单！现在您可以：**
1. ✅ 开始测试所有API接口
2. ✅ 前端页面可以调用真实API
3. ✅ 数据真实保存到数据库文件
4. ✅ 边开发边测试，随时重启

**数据库文件位置：**
```
D:\projects\PM_System\backend\pm_system.db
```

---

## 🔄 后期切换到MySQL/PostgreSQL

### 切换非常简单！

#### 方式一：修改 .env 文件
```ini
# 注释掉SQLite
# DATABASE_URL=sqlite:///./pm_system.db

# 启用MySQL
DATABASE_URL=mysql+pymysql://pm_user:pm_password123@localhost:3306/pm_system

# 或启用PostgreSQL
# DATABASE_URL=postgresql://pm_user:pm_password123@localhost:5432/pm_system
```

#### 方式二：使用环境变量
```powershell
# Windows
set DATABASE_URL=mysql+pymysql://pm_user:pm_password123@localhost:3306/pm_system

# Linux/Mac
export DATABASE_URL=mysql+pymysql://pm_user:pm_password123@localhost:5432/pm_system
```

然后：
```powershell
# 重新初始化数据库（新数据库）
python init_data.py

# 重启后端服务
start.bat
```

**代码完全不需要修改！** SQLAlchemy会自动适配不同的数据库。

---

## 📊 数据库对比

### 开发阶段（推荐SQLite）
| 特性 | SQLite | MySQL/PostgreSQL |
|------|--------|------------------|
| 安装配置 | ✅ 无需安装 | ❌ 需要安装配置 |
| 启动时间 | ✅ 秒级 | ⚠️ 需要启动服务 |
| 数据迁移 | ✅ 复制文件即可 | ⚠️ 导出导入 |
| 学习成本 | ✅ 零成本 | ⚠️ 需要学习SQL管理 |
| 适用场景 | ✅ 单人开发测试 | ⚠️ 开发有点重 |

### 生产阶段（推荐MySQL/PostgreSQL）
| 特性 | SQLite | MySQL/PostgreSQL |
|------|--------|------------------|
| 并发性能 | ⚠️ 写入有限制 | ✅ 高并发 |
| 数据量 | ⚠️ <100GB | ✅ TB级别 |
| 多用户 | ⚠️ 有限制 | ✅ 完美支持 |
| 备份恢复 | ✅ 复制文件 | ✅ 专业工具 |
| 适用场景 | ⚠️ 小型应用 | ✅ 企业级应用 |

---

## 🔧 SQLite数据库管理

### 查看数据库
```powershell
# 安装SQLite命令行工具（可选）
# 下载：https://www.sqlite.org/download.html

# 或使用Python
python -c "import sqlite3; conn = sqlite3.connect('pm_system.db'); print(conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall())"
```

### 使用图形化工具（推荐）
- **DB Browser for SQLite**: https://sqlitebrowser.org/
  - 免费、开源
  - 可视化查看和编辑数据
  - 支持SQL查询

### 使用VS Code插件
- 安装"SQLite Viewer"插件
- 直接在VS Code中查看`.db`文件

---

## 🎨 开发建议

### 开发阶段
```
SQLite本地开发
    ↓
快速迭代功能
    ↓
测试所有接口
    ↓
优化业务逻辑
```

### 测试阶段
```
SQLite功能测试
    ↓
MySQL/PostgreSQL性能测试
    ↓
压力测试
    ↓
优化查询性能
```

### 部署阶段
```
切换到MySQL/PostgreSQL
    ↓
数据迁移
    ↓
生产环境部署
    ↓
监控和维护
```

---

## 🐛 常见问题

### Q1: SQLite文件在哪里？
**答：** `D:\projects\PM_System\backend\pm_system.db`

### Q2: 如何重置数据库？
**答：** 删除`pm_system.db`文件，重新运行`python init_data.py`

### Q3: 数据会丢失吗？
**答：** 不会！数据保存在`.db`文件中，只要文件在，数据就在。

### Q4: 可以备份数据吗？
**答：** 可以！直接复制`pm_system.db`文件即可备份。

### Q5: SQLite有什么限制？
**答：** 
- 单文件大小建议<100GB
- 并发写入有限制（但读取无限制）
- 不支持某些高级SQL特性
- **但对于开发和测试，完全够用！**

### Q6: 切换到MySQL会丢数据吗？
**答：** 
- 切换数据库后是新的空数据库
- 可以导出SQLite数据，导入到MySQL
- 或者在MySQL中重新初始化测试数据

---

## 💡 性能提示

### SQLite性能优化
```python
# 在config.py中已配置
connect_args={
    "check_same_thread": False,  # 允许多线程
    "timeout": 30  # 超时设置
}
```

### 批量操作优化
```python
# 使用事务
with db.begin():
    db.add_all([device1, device2, device3])
    db.commit()
```

---

## 📞 下一步

SQLite后端启动成功后：

1. ✅ **验证API**: 访问 http://localhost:8000/docs
2. ✅ **测试接口**: 在Swagger UI中测试各个API
3. ✅ **前端对接**: 开始迁移前端页面调用API
4. ✅ **完整测试**: 走通所有业务流程

---

## 🎉 总结

**SQLite方案的优势：**
- 🚀 5分钟快速启动
- 💻 零配置，零依赖
- 🔄 随时切换到MySQL/PostgreSQL
- 📦 完美的开发体验
- ✅ 专业的架构设计

**现在就开始吧！只需要3条命令：**
```powershell
cd D:\projects\PM_System\backend
pip install -r requirements.txt
python init_data.py
start.bat
```

**就这么简单！** 🎊
