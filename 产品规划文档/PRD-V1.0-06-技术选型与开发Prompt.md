# 冷库项目登记管理系统 - 技术选型与开发Prompt

## 文档信息
- **文档版本**：V1.0
- **创建日期**：2026-01-27
- **文档编号**：PRD-V1.0-06
- **文档类型**：技术选型与开发Prompt
- **上一文档**：PRD-V1.0-05-业务流程
- **下一文档**：无（需求文档完结）

---

## 一、技术选型建议

### 1.1 技术栈架构

```
前端层：Vue 3 + Element Plus + TypeScript
         ↓
API层：FastAPI (Python) + Pydantic
         ↓
业务逻辑层：Python Services
         ↓
数据访问层：SQLAlchemy ORM
         ↓
数据存储层：MySQL 8.0
```

---

### 1.2 前端技术栈

#### 核心框架
- **Vue 3.3+**：渐进式框架，适合快速开发
- **TypeScript**：类型安全，提升代码质量
- **Vite**：快速的构建工具

#### UI组件库
- **Element Plus**：成熟的Vue 3组件库，组件丰富
  - Table：设备列表展示
  - Form：表单录入
  - Dialog：弹窗操作
  - Select：下拉选择
  - Tree：设备关系树（二期）
  - Steps：流程进度条

#### 状态管理
- **Pinia**：Vue 3官方推荐的状态管理库
  - 用户状态管理
  - 项目数据缓存

#### 路由管理
- **Vue Router 4**：官方路由库
  - 权限路由拦截
  - 动态路由加载

#### HTTP客户端
- **Axios**：成熟的HTTP库
  - 请求拦截器（添加Token）
  - 响应拦截器（统一错误处理）

#### 工具库
- **Day.js**：日期时间处理
- **xlsx**：Excel导出功能
- **jsPDF**：PDF导出功能（可选）
- **ECharts**：关系图可视化（二期）

---

### 1.3 后端技术栈

#### 核心框架
- **FastAPI 0.100+**：现代化Python Web框架
  - 自动生成API文档（Swagger）
  - 类型安全（Pydantic）
  - 高性能（异步支持）

#### ORM框架
- **SQLAlchemy 2.0+**：Python最成熟的ORM
  - 支持关系映射
  - 支持事务管理
  - 支持级联删除

#### 数据库
- **MySQL 8.0**：稳定可靠的关系型数据库
  - 支持外键约束
  - 支持事务
  - 云服务支持良好

#### 认证与安全
- **JWT（PyJWT）**：Token认证
- **bcrypt**：密码加密
- **python-multipart**：文件上传支持

#### 数据验证
- **Pydantic**：数据模型验证
  - 自动类型转换
  - 自动文档生成

#### 工具库
- **openpyxl**：Excel文件生成
- **python-dotenv**：环境变量管理
- **loguru**：日志记录

---

### 1.4 部署架构

#### 开发环境
- **前端**：Vite Dev Server（localhost:5173）
- **后端**：Uvicorn（localhost:8000）
- **数据库**：MySQL本地安装或Docker

#### 生产环境
- **云服务商**：阿里云或腾讯云
- **服务器**：ECS（2核4G起步）
- **前端部署**：Nginx静态托管
- **后端部署**：Gunicorn + Uvicorn Workers
- **数据库**：RDS MySQL
- **域名与SSL**：HTTPS证书配置

---

## 二、项目结构设计

### 2.1 前端项目结构

```
pm-system-frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/              # 静态资源
│   ├── components/          # 公共组件
│   │   ├── Breadcrumb.vue
│   │   ├── PageHeader.vue
│   │   └── DeviceSelector.vue
│   ├── views/               # 页面视图
│   │   ├── Login.vue
│   │   ├── Home.vue
│   │   ├── projects/
│   │   │   ├── ProjectList.vue
│   │   │   ├── ProjectDetail.vue
│   │   │   └── ProjectForm.vue
│   │   ├── coldrooms/
│   │   │   ├── ColdRoomDetail.vue
│   │   │   └── ColdRoomForm.vue
│   │   ├── devices/
│   │   │   ├── DeviceList.vue
│   │   │   └── DeviceForm.vue
│   │   ├── relationships/
│   │   │   └── RelationshipConfig.vue
│   │   ├── gateways/
│   │   │   ├── GatewayList.vue
│   │   │   └── PortConfig.vue
│   │   ├── admin/
│   │   │   ├── UserManagement.vue
│   │   │   ├── DeviceLibrary.vue
│   │   │   └── BrandModel.vue
│   │   └── flow/
│   │       └── FlowManagement.vue
│   ├── router/              # 路由配置
│   │   └── index.ts
│   ├── store/               # 状态管理
│   │   ├── user.ts
│   │   └── project.ts
│   ├── api/                 # API接口
│   │   ├── auth.ts
│   │   ├── project.ts
│   │   ├── device.ts
│   │   └── gateway.ts
│   ├── utils/               # 工具函数
│   │   ├── request.ts       # Axios封装
│   │   ├── auth.ts          # Token处理
│   │   └── export.ts        # 导出功能
│   ├── types/               # TypeScript类型定义
│   │   ├── user.ts
│   │   ├── project.ts
│   │   └── device.ts
│   ├── App.vue
│   └── main.ts
├── .env.development         # 开发环境配置
├── .env.production          # 生产环境配置
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

### 2.2 后端项目结构

```
pm-system-backend/
├── app/
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置文件
│   ├── database.py          # 数据库连接
│   ├── models/              # SQLAlchemy模型
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── cold_room.py
│   │   ├── device.py
│   │   ├── device_relationship.py
│   │   ├── gateway.py
│   │   └── operation_log.py
│   ├── schemas/             # Pydantic模型
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── device.py
│   │   └── gateway.py
│   ├── crud/                # 数据库操作
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── device.py
│   │   └── gateway.py
│   ├── api/                 # API路由
│   │   ├── deps.py          # 依赖项（认证等）
│   │   ├── auth.py          # 认证相关
│   │   ├── users.py
│   │   ├── projects.py
│   │   ├── cold_rooms.py
│   │   ├── devices.py
│   │   ├── relationships.py
│   │   ├── gateways.py
│   │   └── exports.py
│   ├── services/            # 业务逻辑
│   │   ├── auth_service.py
│   │   ├── project_service.py
│   │   ├── device_service.py
│   │   └── export_service.py
│   └── utils/               # 工具函数
│       ├── security.py      # 密码加密、Token生成
│       ├── code_generator.py # 编号生成器
│       └── excel_utils.py   # Excel处理
├── migrations/              # 数据库迁移（Alembic）
├── tests/                   # 测试文件
├── requirements.txt         # 依赖列表
├── .env                     # 环境变量
└── README.md
```

---

## 三、开发Prompt（开发指南）

### 3.1 前端开发Prompt

```markdown
# 冷库项目登记管理系统 - 前端开发Prompt

## 项目概述
开发一个基于 Vue 3 + TypeScript + Element Plus 的企业级管理系统，用于冷库项目和设备的登记管理。

## 技术栈
- Vue 3.3 + TypeScript + Vite
- Element Plus（UI组件库）
- Vue Router 4（路由）
- Pinia（状态管理）
- Axios（HTTP客户端）

## 开发任务清单

### P0 任务（核心功能）

#### 1. 用户认证模块
- [ ] 实现登录页面（Login.vue）
  - 用户名/密码输入表单
  - 表单验证（必填项）
  - 登录API调用
  - Token存储到localStorage
  - 登录成功跳转到首页
  - 登录失败提示错误信息

- [ ] 实现Token管理
  - Axios请求拦截器：自动添加Token到Header
  - Axios响应拦截器：Token失效自动跳转登录
  - 退出登录：清除Token

- [ ] 实现路由守卫
  - 未登录用户自动跳转到登录页
  - 根据角色控制页面访问权限

#### 2. 项目管理模块
- [ ] 项目列表页（ProjectList.vue）
  - 表格展示项目列表（项目编号、名称、城市、类型、状态、创建时间）
  - 搜索功能（按项目名称、城市）
  - 筛选功能（按类型、状态）
  - 新建项目按钮
  - 点击项目进入详情页
  - 分页功能

- [ ] 项目创建/编辑表单（ProjectForm.vue）
  - 项目类型下拉选择
  - 城市选择（支持搜索）
  - 项目名称、地址输入
  - 邮寄信息输入
  - 表单验证
  - 保存按钮

- [ ] 项目详情页（ProjectDetail.vue）
  - Tab页：基础信息、冷库列表、网关管理、流程管理
  - 编辑项目按钮
  - 删除项目按钮（二次确认）
  - 导出按钮

#### 3. 冷库管理模块
- [ ] 冷库详情页（ColdRoomDetail.vue）
  - 冷库基础信息展示
  - Tab页：冷风机、温控器、电表、机组、冷柜、设备关系
  - 各设备列表表格
  - 添加设备按钮
  - 编辑/删除设备按钮

- [ ] 冷库创建/编辑表单（ColdRoomForm.vue）
  - 冷库名称、类型选择
  - 面积、高度输入（数字框）
  - 自动计算容积和制冷剂（实时显示）
  - 备注输入
  - 保存按钮

#### 4. 设备管理模块
- [ ] 设备表单（DeviceForm.vue）
  - 品牌下拉选择（从标准设备库获取）
  - 型号下拉选择（联动品牌）
  - 数量输入
  - 出厂编号输入
  - 通讯信息自动填充（从型号）
  - 备注输入
  - 保存按钮
  - 复制功能按钮

- [ ] 设备关系配置（RelationshipConfig.vue）
  - 关系类型选择
  - 源设备下拉选择
  - 目标设备下拉选择
  - 关系列表表格展示
  - 删除关系按钮

#### 5. 网关管理模块
- [ ] 网关列表（GatewayList.vue）
  - 网关信息展示
  - 添加网关按钮
  - 进入端口配置

- [ ] 端口配置页（PortConfig.vue）
  - 端口列表表格（端口号、状态、绑定设备、485地址）
  - 设备下拉选择（仅通讯设备）
  - 485地址输入或自动分配按钮
  - 保存配置按钮
  - 导出配置清单按钮

#### 6. 管理员功能（仅系统管理员）
- [ ] 用户管理（UserManagement.vue）
  - 用户列表表格
  - 创建用户按钮
  - 编辑/删除/启用/禁用用户

- [ ] 标准设备库（DeviceLibrary.vue）
  - 品牌管理（增删改查）
  - 型号管理（增删改查）
  - 按设备类型分类展示

#### 7. 流程管理模块
- [ ] 流程进度展示（FlowManagement.vue）
  - 使用Element Plus的Steps组件
  - 显示当前节点
  - 推进按钮
  - 流程历史记录

#### 8. 导出功能
- [ ] 实现Excel导出（utils/export.ts）
  - 使用xlsx库
  - 导出项目信息
  - 导出设备清单
  - 导出设备关系表
  - 导出网关配置表

### P1 任务（增强功能）
- [ ] 修改密码功能
- [ ] 操作日志查看
- [ ] 表格排序功能
- [ ] 全局Loading状态
- [ ] 错误提示优化

### P2 任务（优化功能）
- [ ] 设备关系图可视化（ECharts）
- [ ] 批量导入设备
- [ ] 数据缓存优化
- [ ] 响应式布局优化

## 开发规范

### 命名规范
- 组件文件：PascalCase（如ProjectList.vue）
- 工具文件：camelCase（如auth.ts）
- CSS类名：kebab-case（如.project-list）

### TypeScript规范
- 所有API接口需定义类型
- 组件Props需定义类型
- 避免使用any类型

### 代码注释
- 复杂逻辑需添加注释
- 公共函数需添加JSDoc注释

### 提交规范
- feat: 新功能
- fix: 修复Bug
- refactor: 重构
- docs: 文档更新

## API接口设计

### 认证相关
- POST /api/auth/login - 登录
- POST /api/auth/logout - 登出
- POST /api/auth/change-password - 修改密码

### 用户管理
- GET /api/users - 获取用户列表
- POST /api/users - 创建用户
- PUT /api/users/{user_id} - 更新用户
- DELETE /api/users/{user_id} - 删除用户

### 项目管理
- GET /api/projects - 获取项目列表
- POST /api/projects - 创建项目
- GET /api/projects/{project_id} - 获取项目详情
- PUT /api/projects/{project_id} - 更新项目
- DELETE /api/projects/{project_id} - 删除项目

### 冷库管理
- GET /api/projects/{project_id}/cold-rooms - 获取冷库列表
- POST /api/projects/{project_id}/cold-rooms - 创建冷库
- GET /api/cold-rooms/{room_id} - 获取冷库详情
- PUT /api/cold-rooms/{room_id} - 更新冷库
- DELETE /api/cold-rooms/{room_id} - 删除冷库

### 设备管理
- GET /api/cold-rooms/{room_id}/devices - 获取设备列表
- POST /api/cold-rooms/{room_id}/devices - 创建设备
- PUT /api/devices/{device_id} - 更新设备
- DELETE /api/devices/{device_id} - 删除设备

### 设备关系
- GET /api/cold-rooms/{room_id}/relationships - 获取关系列表
- POST /api/cold-rooms/{room_id}/relationships - 创建关系
- DELETE /api/relationships/{relationship_id} - 删除关系

### 网关管理
- GET /api/projects/{project_id}/gateways - 获取网关列表
- POST /api/projects/{project_id}/gateways - 创建网关
- GET /api/gateways/{gateway_id}/ports - 获取端口列表
- PUT /api/gateway-ports/{port_id} - 更新端口配置

### 标准设备库
- GET /api/device-brands - 获取品牌列表
- POST /api/device-brands - 创建品牌
- GET /api/device-models?brand_id={brand_id} - 获取型号列表
- POST /api/device-models - 创建型号

### 导出功能
- GET /api/projects/{project_id}/export/info - 导出项目信息
- GET /api/projects/{project_id}/export/devices - 导出设备清单
- GET /api/projects/{project_id}/export/relationships - 导出关系表
- GET /api/projects/{project_id}/export/gateway-config - 导出网关配置

## 响应数据格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "错误信息",
  "data": null
}
```

### 分页响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

## 开始开发

### 1. 初始化项目
```bash
npm create vite@latest pm-system-frontend -- --template vue-ts
cd pm-system-frontend
npm install
npm install element-plus axios pinia vue-router dayjs xlsx
npm install -D @types/node
```

### 2. 配置环境变量
创建 .env.development：
```
VITE_API_BASE_URL=http://localhost:8000/api
```

### 3. 配置Axios
在 src/utils/request.ts 中封装Axios，添加拦截器。

### 4. 开发顺序
建议按照以下顺序开发：
1. 登录页面和认证功能
2. 首页布局和路由配置
3. 项目管理（列表、创建、详情）
4. 冷库和设备管理
5. 设备关系配置
6. 网关管理
7. 管理员功能
8. 导出功能

### 5. 测试
每完成一个模块，使用浏览器测试功能是否正常。

## 注意事项
- 所有API请求需处理错误情况
- 表单提交前需验证数据
- 删除操作需二次确认
- 敏感操作需记录日志
- 注意数据权限控制（企业管理员只能看自己的项目）
```

---

### 3.2 后端开发Prompt

```markdown
# 冷库项目登记管理系统 - 后端开发Prompt

## 项目概述
开发一个基于 FastAPI + SQLAlchemy + MySQL 的RESTful API服务，为冷库项目登记管理系统提供后端支持。

## 技术栈
- FastAPI 0.100+
- SQLAlchemy 2.0+
- MySQL 8.0
- PyJWT（JWT认证）
- bcrypt（密码加密）
- openpyxl（Excel生成）

## 开发任务清单

### P0 任务（核心功能）

#### 1. 项目初始化
- [ ] 创建项目结构
- [ ] 配置requirements.txt
- [ ] 配置.env环境变量（数据库连接、JWT密钥等）
- [ ] 配置database.py（SQLAlchemy数据库连接）
- [ ] 配置main.py（FastAPI应用入口、CORS配置）

#### 2. 数据库模型（models/）
- [ ] User模型（用户表）
- [ ] DeviceBrand模型（设备品牌表）
- [ ] DeviceModel模型（设备型号表）
- [ ] Project模型（项目表）
- [ ] ColdRoom模型（冷库表）
- [ ] Device模型（设备表）
- [ ] DeviceRelationship模型（设备关系表）
- [ ] Gateway模型（网关表）
- [ ] GatewayPort模型（网关端口表）
- [ ] ProjectFlowLog模型（项目流程日志表）
- [ ] OperationLog模型（操作日志表）

#### 3. Pydantic模式（schemas/）
- [ ] UserCreate, UserUpdate, UserResponse
- [ ] ProjectCreate, ProjectUpdate, ProjectResponse
- [ ] ColdRoomCreate, ColdRoomUpdate, ColdRoomResponse
- [ ] DeviceCreate, DeviceUpdate, DeviceResponse
- [ ] RelationshipCreate, RelationshipResponse
- [ ] GatewayCreate, GatewayResponse
- [ ] PortConfigUpdate, PortConfigResponse

#### 4. CRUD操作（crud/）
- [ ] user.py - 用户CRUD
- [ ] project.py - 项目CRUD（含权限过滤）
- [ ] cold_room.py - 冷库CRUD
- [ ] device.py - 设备CRUD（含编号自动生成）
- [ ] device_relationship.py - 关系CRUD
- [ ] gateway.py - 网关CRUD（含端口自动创建）

#### 5. 业务逻辑（services/）
- [ ] auth_service.py
  - 用户登录验证
  - Token生成和验证
  - 密码加密和校验
  - 登录失败次数记录

- [ ] project_service.py
  - 项目编号生成（PRJ + YYYYMMDD + 序号）
  - 项目流程推进
  - 项目权限检查

- [ ] device_service.py
  - 设备编号生成（设备类型-冷库ID-序号）
  - 冷库容积和制冷剂计算
  - 设备关系验证（如一个冷风机只能对应一个机组）

- [ ] export_service.py
  - 生成项目信息Excel
  - 生成设备清单Excel
  - 生成设备关系表Excel
  - 生成网关配置表Excel

#### 6. API路由（api/）
- [ ] auth.py
  - POST /auth/login - 登录
  - POST /auth/logout - 登出
  - POST /auth/change-password - 修改密码

- [ ] users.py（仅系统管理员）
  - GET /users - 获取用户列表
  - POST /users - 创建用户
  - PUT /users/{user_id} - 更新用户
  - DELETE /users/{user_id} - 删除用户

- [ ] projects.py
  - GET /projects - 获取项目列表（含权限过滤）
  - POST /projects - 创建项目
  - GET /projects/{project_id} - 获取项目详情
  - PUT /projects/{project_id} - 更新项目
  - DELETE /projects/{project_id} - 删除项目
  - PUT /projects/{project_id}/flow - 推进流程

- [ ] cold_rooms.py
  - GET /projects/{project_id}/cold-rooms - 获取冷库列表
  - POST /projects/{project_id}/cold-rooms - 创建冷库
  - GET /cold-rooms/{room_id} - 获取冷库详情
  - PUT /cold-rooms/{room_id} - 更新冷库
  - DELETE /cold-rooms/{room_id} - 删除冷库

- [ ] devices.py
  - GET /cold-rooms/{room_id}/devices - 获取设备列表
  - POST /cold-rooms/{room_id}/devices - 创建设备
  - PUT /devices/{device_id} - 更新设备
  - DELETE /devices/{device_id} - 删除设备

- [ ] relationships.py
  - GET /cold-rooms/{room_id}/relationships - 获取关系列表
  - POST /cold-rooms/{room_id}/relationships - 创建关系
  - DELETE /relationships/{relationship_id} - 删除关系

- [ ] gateways.py
  - GET /projects/{project_id}/gateways - 获取网关列表
  - POST /projects/{project_id}/gateways - 创建网关
  - GET /gateways/{gateway_id}/ports - 获取端口列表
  - PUT /gateway-ports/{port_id} - 更新端口配置

- [ ] device_library.py（仅系统管理员）
  - GET /device-brands - 获取品牌列表
  - POST /device-brands - 创建品牌
  - PUT /device-brands/{brand_id} - 更新品牌
  - DELETE /device-brands/{brand_id} - 删除品牌
  - GET /device-models - 获取型号列表
  - POST /device-models - 创建型号
  - PUT /device-models/{model_id} - 更新型号
  - DELETE /device-models/{model_id} - 删除型号

- [ ] exports.py
  - GET /projects/{project_id}/export/info - 导出项目信息
  - GET /projects/{project_id}/export/devices - 导出设备清单
  - GET /projects/{project_id}/export/relationships - 导出关系表
  - GET /projects/{project_id}/export/gateway-config - 导出网关配置

#### 7. 工具函数（utils/）
- [ ] security.py
  - hash_password() - 密码加密
  - verify_password() - 密码验证
  - create_access_token() - 生成JWT Token
  - verify_token() - 验证JWT Token

- [ ] code_generator.py
  - generate_project_code() - 生成项目编号
  - generate_device_code() - 生成设备编号

- [ ] excel_utils.py
  - create_excel() - 创建Excel文件
  - add_sheet() - 添加Sheet
  - write_data() - 写入数据

#### 8. 依赖项（api/deps.py）
- [ ] get_db() - 数据库Session依赖
- [ ] get_current_user() - 获取当前登录用户
- [ ] require_admin() - 要求管理员权限
- [ ] check_project_permission() - 检查项目权限

### P1 任务（增强功能）
- [ ] 操作日志记录中间件
- [ ] 请求日志记录
- [ ] 数据库连接池配置
- [ ] API限流
- [ ] 数据库迁移脚本（Alembic）

### P2 任务（优化功能）
- [ ] 单元测试
- [ ] 性能优化（查询优化、索引优化）
- [ ] 缓存机制（Redis）
- [ ] 异步任务队列（Celery）

## 开发规范

### 代码规范
- 遵循PEP 8规范
- 函数需添加类型提示
- 复杂逻辑需添加注释
- 使用docstring描述函数功能

### 错误处理
- 使用HTTPException抛出HTTP错误
- 统一错误响应格式
- 记录错误日志

### 数据库操作
- 使用事务处理复杂操作
- 使用ORM查询，避免原生SQL（防止注入）
- 查询需添加索引
- 级联删除需谨慎处理

### 安全规范
- 密码必须加密存储
- JWT Token使用强密钥
- 敏感操作需二次验证
- 所有API需权限控制

## 数据库初始化

### 1. 创建数据库
```sql
CREATE DATABASE pm_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 创建表（使用SQLAlchemy自动创建）
```python
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)
```

### 3. 初始化超级管理员
```python
from app.utils.security import hash_password
from app.models.user import User

admin = User(
    username="admin",
    password_hash=hash_password("admin123"),
    role="super_admin",
    contact_name="系统管理员",
    contact_phone="13800138000",
    status="active"
)
db.add(admin)
db.commit()
```

### 4. 初始化设备类型和标准品牌（可选）
根据实际需求预置设备品牌和型号数据。

## API响应格式

### 统一响应结构
```python
from pydantic import BaseModel
from typing import Any, Optional

class Response(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

def success_response(data: Any = None, message: str = "success"):
    return Response(code=200, message=message, data=data)

def error_response(code: int, message: str):
    return Response(code=code, message=message, data=None)
```

### 分页响应
```python
from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')

class PageResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
```

## 认证流程

### JWT Token结构
```python
{
    "user_id": 1,
    "username": "admin",
    "role": "super_admin",
    "exp": 1706345678  # 过期时间戳
}
```

### 权限验证流程
1. 从请求Header中提取Token
2. 验证Token有效性
3. 解析Token获取用户信息
4. 检查用户权限（角色、数据权限）
5. 执行业务逻辑

## 开始开发

### 1. 初始化项目
```bash
mkdir pm-system-backend
cd pm-system-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pymysql python-jose[cryptography] passlib[bcrypt] python-multipart openpyxl python-dotenv
pip freeze > requirements.txt
```

### 2. 创建.env文件
```
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/pm_system
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24
```

### 3. 创建main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="冷库项目登记管理系统API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to PM System API"}
```

### 4. 开发顺序
建议按照以下顺序开发：
1. 数据库连接和模型定义
2. 用户认证和JWT实现
3. 项目CRUD
4. 冷库和设备CRUD
5. 设备关系管理
6. 网关管理
7. 导出功能
8. 管理员功能

### 5. 测试
```bash
uvicorn app.main:app --reload
```
访问 http://localhost:8000/docs 查看API文档。

## 注意事项
- 所有数据库操作需处理异常
- 敏感信息（密码、密钥）不得硬编码
- API需添加权限验证
- 复杂查询需优化性能
- 记录操作日志
- 数据权限控制（企业管理员只能访问自己的项目）
```

---

## 四、部署指南

### 4.1 开发环境部署

#### 前端
```bash
cd pm-system-frontend
npm install
npm run dev
```
访问：http://localhost:5173

#### 后端
```bash
cd pm-system-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
访问：http://localhost:8000
API文档：http://localhost:8000/docs

#### 数据库
```bash
# 使用Docker快速启动MySQL
docker run -d \
  --name pm-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=pm_system \
  mysql:8.0
```

---

### 4.2 生产环境部署

#### 服务器要求
- CPU：2核以上
- 内存：4GB以上
- 硬盘：40GB以上
- 操作系统：Ubuntu 20.04 / CentOS 7+

#### 前端部署
```bash
# 1. 构建前端
cd pm-system-frontend
npm run build

# 2. 配置Nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /var/www/pm-system-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 3. 启动Nginx
sudo systemctl start nginx
```

#### 后端部署
```bash
# 1. 安装依赖
cd pm-system-backend
pip install -r requirements.txt
pip install gunicorn

# 2. 使用Gunicorn启动
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --daemon

# 3. 配置系统服务（可选）
sudo vim /etc/systemd/system/pm-system.service
```

#### SSL证书配置
使用Let's Encrypt免费证书：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 五、验收标准

### 5.1 功能验收
- [ ] 用户可以正常登录和退出
- [ ] 系统管理员可以创建企业管理员账号
- [ ] 企业管理员只能查看自己的项目
- [ ] 可以创建项目并填写完整信息
- [ ] 可以创建冷库并自动计算容积和制冷剂
- [ ] 可以添加各类设备并自动生成编号
- [ ] 可以建立设备关系并展示关系表
- [ ] 可以添加网关并配置端口
- [ ] 可以更新项目流程状态
- [ ] 可以导出各类报表（Excel）

### 5.2 非功能验收
- [ ] 页面加载时间<3秒
- [ ] API响应时间<500ms
- [ ] 支持50+并发用户
- [ ] 数据库每日自动备份
- [ ] HTTPS加密传输
- [ ] 操作日志完整记录

---

## 六、风险与应对

### 风险1：技术选型不熟悉
- **应对**：提供详细的开发文档和示例代码，团队成员提前学习

### 风险2：开发周期紧张
- **应对**：采用MVP迭代开发，先完成P0功能，后续逐步完善

### 风险3：数据安全问题
- **应对**：严格权限控制，定期备份，使用HTTPS

### 风险4：用户需求变更
- **应对**：采用敏捷开发，预留扩展接口，快速响应变更

---

## 七、下一步行动

### 立即行动项
1. **搭建开发环境**：安装Node.js、Python、MySQL
2. **初始化项目**：创建前后端项目结构
3. **创建数据库**：执行数据库初始化脚本
4. **开发P0功能**：按照Prompt开发核心功能

### 预计时间表
- **第1周**：环境搭建 + 认证模块 + 项目管理
- **第2周**：冷库管理 + 设备管理
- **第3周**：设备关系 + 网关管理
- **第4周**：流程管理 + 导出功能 + 测试部署

---

## 八、总结

本文档提供了完整的技术选型建议和开发Prompt，涵盖：
- ✅ 前后端技术栈选择
- ✅ 项目结构设计
- ✅ 详细的开发任务清单
- ✅ API接口设计
- ✅ 数据库设计
- ✅ 部署指南
- ✅ 验收标准

开发团队可以直接使用本文档作为开发指南，按照Prompt逐步实现系统功能。

---

**文档结束 - 需求文档已全部完成**
