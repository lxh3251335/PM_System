# 快速开始指南

## 面向开发人员：如何使用本文档开始开发

### 一、文档阅读顺序

作为开发人员，建议按照以下顺序阅读文档：

```
开发人员路径：
1. README.md（5分钟）→ 了解项目全貌
2. PRD-V1.0-01-产品概述.md（10分钟）→ 理解产品定位
3. PRD-V1.0-04-数据模型.md（30分钟）→ 熟悉数据结构
4. PRD-V1.0-06-技术选型与开发Prompt.md（60分钟）→ 开始编码
5. PRD-V1.0-03-功能清单.md（参考）→ 开发时查阅
6. PRD-V1.0-05-业务流程.md（参考)→ 实现业务逻辑时查阅
```

---

## 二、立即开始开发（30分钟快速启动）

### Step 1：环境准备（5分钟）

#### 检查环境
```bash
# 检查Node.js版本（要求16.0+）
node -v

# 检查Python版本（要求3.9+）
python --version

# 检查MySQL版本（要求8.0+）
mysql --version
```

#### 安装缺失的环境
- Node.js：https://nodejs.org/
- Python：https://www.python.org/
- MySQL：https://dev.mysql.com/downloads/mysql/

---

### Step 2：创建数据库（2分钟）

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE pm_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 退出
exit;
```

---

### Step 3：初始化后端（10分钟）

```bash
# 1. 创建后端项目目录
mkdir pm-system-backend
cd pm-system-backend

# 2. 创建虚拟环境
python -m venv venv

# Windows激活
venv\Scripts\activate

# macOS/Linux激活
source venv/bin/activate

# 3. 安装依赖
pip install fastapi uvicorn sqlalchemy pymysql python-jose[cryptography] passlib[bcrypt] python-multipart openpyxl python-dotenv pydantic-settings

# 4. 保存依赖列表
pip freeze > requirements.txt

# 5. 创建基础结构
mkdir app
mkdir app/models
mkdir app/schemas
mkdir app/crud
mkdir app/api
mkdir app/services
mkdir app/utils

# 6. 创建.env文件
echo "DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/pm_system" > .env
echo "JWT_SECRET_KEY=your-secret-key-change-in-production" >> .env
echo "JWT_ALGORITHM=HS256" >> .env
echo "JWT_EXPIRE_HOURS=24" >> .env

# 7. 创建main.py
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="冷库项目登记管理系统API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to PM System API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
EOF

# 8. 启动后端测试
uvicorn app.main:app --reload
```

访问 http://localhost:8000 查看是否成功
访问 http://localhost:8000/docs 查看API文档

---

### Step 4：初始化前端（10分钟）

打开新终端：

```bash
# 1. 创建前端项目
npm create vite@latest pm-system-frontend -- --template vue-ts

# 2. 进入项目目录
cd pm-system-frontend

# 3. 安装依赖
npm install

# 4. 安装UI库和工具库
npm install element-plus axios pinia vue-router dayjs xlsx

# 5. 安装开发依赖
npm install -D @types/node

# 6. 创建环境变量文件
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env.development

# 7. 启动前端测试
npm run dev
```

访问 http://localhost:5173 查看是否成功

---

### Step 5：验证环境（3分钟）

#### 后端验证
- 访问 http://localhost:8000 应该看到 {"message": "Welcome to PM System API"}
- 访问 http://localhost:8000/docs 应该看到Swagger文档

#### 前端验证
- 访问 http://localhost:5173 应该看到Vite默认页面

✅ 恭喜！环境搭建完成，可以开始开发了！

---

## 三、开发路线图（按顺序执行）

### 第1阶段：搭建基础框架（建议第1天完成）

#### 后端任务
- [ ] 创建database.py（数据库连接）
- [ ] 创建所有Model（11个表）
- [ ] 创建基础Schema（User、Project）
- [ ] 实现JWT认证（utils/security.py）
- [ ] 实现登录API（api/auth.py）

#### 前端任务
- [ ] 配置路由（router/index.ts）
- [ ] 封装Axios（utils/request.ts）
- [ ] 创建登录页面（views/Login.vue）
- [ ] 创建首页布局（views/Home.vue）
- [ ] 实现Token管理（store/user.ts）

**验收标准**：可以登录系统并跳转到首页

---

### 第2阶段：项目管理模块（建议第2-3天完成）

#### 后端任务
- [ ] 实现Project CRUD（crud/project.py）
- [ ] 实现项目API（api/projects.py）
- [ ] 实现权限过滤（企业管理员只能看自己的项目）
- [ ] 实现项目编号自动生成

#### 前端任务
- [ ] 创建项目列表页（views/projects/ProjectList.vue）
- [ ] 创建项目表单（views/projects/ProjectForm.vue）
- [ ] 创建项目详情页（views/projects/ProjectDetail.vue）
- [ ] 实现项目API调用（api/project.ts）

**验收标准**：可以创建、查看、编辑、删除项目

---

### 第3阶段：冷库和设备管理（建议第4-6天完成）

#### 后端任务
- [ ] 实现ColdRoom CRUD（crud/cold_room.py）
- [ ] 实现Device CRUD（crud/device.py）
- [ ] 实现容积和制冷剂自动计算
- [ ] 实现设备编号自动生成
- [ ] 实现冷库和设备API

#### 前端任务
- [ ] 创建冷库表单（views/coldrooms/ColdRoomForm.vue）
- [ ] 创建冷库详情页（views/coldrooms/ColdRoomDetail.vue）
- [ ] 创建设备表单（views/devices/DeviceForm.vue）
- [ ] 实现设备列表（支持5种设备类型）
- [ ] 实现复制设备功能

**验收标准**：可以创建冷库、添加各类设备、自动计算容积

---

### 第4阶段：设备关系配置（建议第7-8天完成）

#### 后端任务
- [ ] 实现DeviceRelationship CRUD
- [ ] 实现关系验证（如一个冷风机只能对应一个机组）
- [ ] 实现关系查询API

#### 前端任务
- [ ] 创建关系配置页（views/relationships/RelationshipConfig.vue）
- [ ] 实现关系表格展示
- [ ] 实现关系添加/删除功能

**验收标准**：可以建立设备关系并查看关系表

---

### 第5阶段：网关管理（建议第9-10天完成）

#### 后端任务
- [ ] 实现Gateway和GatewayPort CRUD
- [ ] 实现端口自动创建（根据网关型号）
- [ ] 实现485地址分配和冲突检测
- [ ] 实现网关配置API

#### 前端任务
- [ ] 创建网关列表（views/gateways/GatewayList.vue）
- [ ] 创建端口配置页（views/gateways/PortConfig.vue）
- [ ] 实现端口绑定设备功能
- [ ] 实现485地址自动分配

**验收标准**：可以添加网关、配置端口、分配485地址

---

### 第6阶段：流程管理和导出（建议第11-12天完成）

#### 后端任务
- [ ] 实现项目流程推进API
- [ ] 实现流程日志记录
- [ ] 实现Excel导出功能（4种报表）
- [ ] 实现导出API

#### 前端任务
- [ ] 创建流程管理页（views/flow/FlowManagement.vue）
- [ ] 实现流程进度条展示
- [ ] 实现流程推进功能
- [ ] 实现报表导出功能

**验收标准**：可以推进流程、导出各类报表

---

### 第7阶段：管理员功能（建议第13-14天完成）

#### 后端任务
- [ ] 实现用户管理API
- [ ] 实现设备品牌和型号管理API
- [ ] 实现权限控制（仅系统管理员）

#### 前端任务
- [ ] 创建用户管理页（views/admin/UserManagement.vue）
- [ ] 创建设备库管理页（views/admin/DeviceLibrary.vue）
- [ ] 实现品牌型号管理

**验收标准**：系统管理员可以创建用户、维护设备库

---

### 第8阶段：测试和优化（建议第15-16天完成）

- [ ] 功能测试（所有功能走一遍）
- [ ] 权限测试（不同角色）
- [ ] 性能测试（大数据量）
- [ ] UI优化（交互体验）
- [ ] Bug修复
- [ ] 部署准备

**验收标准**：系统稳定运行，无重大Bug

---

## 四、开发技巧和注意事项

### 后端开发技巧

#### 1. 数据库模型关系
```python
# 使用relationship建立关联
class Project(Base):
    __tablename__ = "projects"
    # ...
    cold_rooms = relationship("ColdRoom", back_populates="project", cascade="all, delete-orphan")
```

#### 2. 权限过滤示例
```python
def get_projects(db: Session, current_user: User):
    query = db.query(Project)
    if current_user.role == "enterprise_admin":
        query = query.filter(Project.created_by == current_user.user_id)
    return query.all()
```

#### 3. 自动生成编号
```python
def generate_project_code(db: Session):
    today = datetime.now().strftime("%Y%m%d")
    count = db.query(Project).filter(
        Project.project_code.like(f"PRJ{today}%")
    ).count()
    return f"PRJ{today}{count+1:03d}"
```

---

### 前端开发技巧

#### 1. Axios请求拦截器
```typescript
// src/utils/request.ts
import axios from 'axios'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

// 请求拦截器：添加Token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Token失效，跳转登录
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default request
```

#### 2. 路由守卫
```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: () => import('@/views/Login.vue') },
    {
      path: '/',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: true },
      children: [
        // ...子路由
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

#### 3. Element Plus表单验证
```vue
<template>
  <el-form :model="form" :rules="rules" ref="formRef">
    <el-form-item label="项目名称" prop="projectName">
      <el-input v-model="form.projectName" />
    </el-form-item>
    <el-button @click="submitForm">提交</el-button>
  </el-form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FormInstance } from 'element-plus'

const formRef = ref<FormInstance>()
const form = ref({
  projectName: ''
})

const rules = {
  projectName: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ]
}

const submitForm = () => {
  formRef.value?.validate((valid) => {
    if (valid) {
      // 提交表单
    }
  })
}
</script>
```

---

## 五、常见问题解答

### Q1：数据库连接失败？
**A**：检查.env文件中的DATABASE_URL是否正确，确保MySQL服务已启动。

### Q2：CORS错误？
**A**：确保后端main.py中CORS配置的allow_origins包含前端地址。

### Q3：Token验证失败？
**A**：检查JWT_SECRET_KEY是否配置正确，确保前后端使用相同的密钥。

### Q4：前端路由404？
**A**：检查Nginx配置，确保配置了try_files $uri $uri/ /index.html。

### Q5：Excel导出中文乱码？
**A**：使用openpyxl库，确保文件编码为UTF-8。

---

## 六、获取帮助

### 开发文档
- FastAPI文档：https://fastapi.tiangolo.com/
- Vue 3文档：https://cn.vuejs.org/
- Element Plus文档：https://element-plus.org/zh-CN/
- SQLAlchemy文档：https://docs.sqlalchemy.org/

### 社区支持
- FastAPI GitHub：https://github.com/tiangolo/fastapi
- Vue GitHub：https://github.com/vuejs/core
- Stack Overflow：搜索相关技术问题

---

## 七、下一步

✅ 完成环境搭建后，建议：

1. **仔细阅读 PRD-V1.0-04-数据模型.md**，理解所有表结构
2. **参考 PRD-V1.0-06-技术选型与开发Prompt.md**，开始编码
3. **按照上述开发路线图逐步实现功能**
4. **遇到业务逻辑问题时参考 PRD-V1.0-05-业务流程.md**

祝开发顺利！🚀

---

**文档版本**：V1.0  
**最后更新**：2026-01-27
