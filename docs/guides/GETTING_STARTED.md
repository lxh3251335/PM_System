# 项目启动指南

欢迎使用冷库项目登记管理系统！本指南将帮助您快速理解项目并开始开发。

---

## 📚 第一步：阅读文档（30分钟）

### 必读文档（按顺序阅读）

1. **[README.md](README.md)** - 5分钟  
   → 快速了解项目是什么、做什么、技术栈

2. **[产品规划文档/PRD-V1.0-01-产品概述.md](产品规划文档/PRD-V1.0-01-产品概述.md)** - 10分钟  
   → 理解产品定位、核心价值、使用场景

3. **[产品规划文档/PRD-V1.0-04-数据模型.md](产品规划文档/PRD-V1.0-04-数据模型.md)** - 15分钟  
   → 熟悉数据库设计，这是开发的基础

### 可选文档（开发时参考）

- **[产品规划文档/PRD-V1.0-02-用户角色与权限.md](产品规划文档/PRD-V1.0-02-用户角色与权限.md)**  
  → 实现权限控制时查阅

- **[产品规划文档/PRD-V1.0-03-功能清单.md](产品规划文档/PRD-V1.0-03-功能清单.md)**  
  → 开发具体功能时查阅

- **[产品规划文档/PRD-V1.0-05-业务流程.md](产品规划文档/PRD-V1.0-05-业务流程.md)**  
  → 实现业务逻辑时查阅

---

## 🛠️ 第二步：环境准备（30分钟）

按照 **[产品规划文档/QUICK_START.md](产品规划文档/QUICK_START.md)** 的指引：

### 2.1 检查环境

```bash
# 检查Node.js（需要16.0+）
node -v

# 检查Python（需要3.9+）
python --version

# 检查MySQL（需要8.0+）
mysql --version
```

### 2.2 创建数据库

```bash
mysql -u root -p
```

```sql
CREATE DATABASE pm_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

### 2.3 初始化后端

```bash
# 创建后端目录
mkdir pm-system-backend
cd pm-system-backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 或激活虚拟环境（macOS/Linux）
source venv/bin/activate

# 安装依赖
pip install fastapi uvicorn sqlalchemy pymysql python-jose[cryptography] passlib[bcrypt] python-multipart openpyxl python-dotenv pydantic-settings

# 保存依赖列表
pip freeze > requirements.txt
```

### 2.4 初始化前端

打开新终端：

```bash
# 创建前端项目
npm create vite@latest pm-system-frontend -- --template vue-ts

# 进入目录
cd pm-system-frontend

# 安装依赖
npm install

# 安装UI库
npm install element-plus axios pinia vue-router dayjs xlsx

# 启动测试
npm run dev
```

---

## 💻 第三步：开始开发（详细指引）

### 3.1 选择您的角色

#### 如果您是全栈开发
→ 建议先开发后端，再开发前端  
→ 参考：**[产品规划文档/PRD-V1.0-06-技术选型与开发Prompt.md](产品规划文档/PRD-V1.0-06-技术选型与开发Prompt.md)**

#### 如果您是后端开发
→ 直接查看文档中的"后端开发Prompt"部分  
→ 使用：**[产品规划文档/DEVELOPMENT_CHECKLIST.md](产品规划文档/DEVELOPMENT_CHECKLIST.md)** 跟踪进度

#### 如果您是前端开发
→ 直接查看文档中的"前端开发Prompt"部分  
→ 使用：**[产品规划文档/DEVELOPMENT_CHECKLIST.md](产品规划文档/DEVELOPMENT_CHECKLIST.md)** 跟踪进度

### 3.2 开发顺序建议

```
第1周：
  Day 1-2: 搭建基础框架（数据库、认证、登录）
  Day 3-5: 项目管理模块

第2周：
  Day 1-3: 冷库和设备管理
  Day 4-5: 设备关系配置

第3周：
  Day 1-3: 网关管理
  Day 4-5: 流程管理和导出

第4周：
  Day 1-2: 管理员功能
  Day 3-4: 测试和优化
  Day 5: 部署准备
```

### 3.3 每日开发流程

```
1. 早上：查看 DEVELOPMENT_CHECKLIST，确定今日任务
2. 开发：按照 Prompt 编码
3. 测试：使用浏览器或Postman测试
4. 提交：Git commit + push
5. 复盘：更新 CHECKLIST，记录问题
```

---

## 📋 第四步：跟踪进度

### 使用开发清单

打开 **[产品规划文档/DEVELOPMENT_CHECKLIST.md](产品规划文档/DEVELOPMENT_CHECKLIST.md)**

- [ ] 打印或导出为PDF
- [ ] 每完成一项打✓
- [ ] 每日回顾进度
- [ ] 遇到问题记录在清单中

### 使用Git管理

```bash
# 初始化Git
git init

# 添加远程仓库
git remote add origin <your-repo-url>

# 每日提交
git add .
git commit -m "feat: 完成XXX功能"
git push
```

---

## 🎯 第五步：里程碑验收

### M1：MVP版本（第10天）
- [ ] 可以登录系统
- [ ] 可以创建项目
- [ ] 可以创建冷库
- [ ] 可以添加设备

### M2：功能完整版（第18天）
- [ ] 所有功能开发完成
- [ ] 前后端联调成功
- [ ] 权限控制正常

### M3：测试版（第22天）
- [ ] 功能测试通过
- [ ] 无重大Bug
- [ ] 性能达标

### M4：生产版（第24天）
- [ ] 部署上线
- [ ] 用户培训完成
- [ ] 可交付使用

---

## 🔍 常见问题

### Q：文档太多，不知道从哪看起？
**A**：按顺序看：
1. README.md
2. PRD-V1.0-01-产品概述.md
3. PRD-V1.0-04-数据模型.md
4. QUICK_START.md
5. 开始编码

### Q：技术栈不熟悉怎么办？
**A**：
- FastAPI官网：https://fastapi.tiangolo.com/zh/
- Vue 3官网：https://cn.vuejs.org/
- 先跑通示例代码，再参考Prompt开发

### Q：遇到Bug无法解决？
**A**：
1. 查看官方文档
2. Stack Overflow搜索
3. GitHub Issues查找
4. 寻求团队支持

### Q：开发到一半需求变了？
**A**：
1. 评估变更影响
2. 更新PRD文档
3. 调整CHECKLIST
4. 重新评估工期

---

## 📞 获取帮助

### 技术文档
- FastAPI：https://fastapi.tiangolo.com/
- Vue 3：https://cn.vuejs.org/
- Element Plus：https://element-plus.org/zh-CN/
- SQLAlchemy：https://docs.sqlalchemy.org/

### 社区支持
- Stack Overflow
- GitHub Issues
- 掘金社区
- CSDN论坛

---

## ✨ 最后

**您现在已经具备了开始开发的所有条件！**

1. ✅ 完整的需求文档
2. ✅ 详细的开发指南
3. ✅ 清晰的任务清单
4. ✅ 环境搭建指引

**现在，开始您的编码之旅吧！🚀**

如有任何问题，随时查阅文档。祝开发顺利！

---

**快速导航**

- [返回README](README.md)
- [查看产品概述](产品规划文档/PRD-V1.0-01-产品概述.md)
- [快速开始](产品规划文档/QUICK_START.md)
- [开发清单](产品规划文档/DEVELOPMENT_CHECKLIST.md)
- [技术选型与开发Prompt](产品规划文档/PRD-V1.0-06-技术选型与开发Prompt.md)
- [项目总结](产品规划文档/SUMMARY.md)

---

**版本**：V1.0  
**日期**：2026-01-27  
**状态**：✅ 可开始开发
