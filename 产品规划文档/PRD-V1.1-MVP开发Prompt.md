# 冷库项目登记管理系统 - MVP开发Prompt

## 文档信息
- **文档版本**：V1.1 MVP
- **创建日期**：2026-01-27
- **文档类型**：开发指南（简化版）
- **预计工期**：15个工作日

---

## 一、MVP版本目标

### 核心目标
🎯 **快速替代Excel表格**，提供更便捷的信息登记、查询、进度查看功能

### MVP功能范围
✅ 项目管理（含复制功能、到货时间）  
✅ 冷库管理（自动计算容积）  
✅ 设备管理（5种类型，平级结构）  
✅ 网关管理（端口配置、485地址）  
✅ 流程管理（8个节点）  
✅ 导出功能（项目信息、设备清单）  

❌ 暂不包含：
- 用户管理（固定2用户）
- 标准设备库（手动输入）
- 设备关系配置（二期）
- 复杂报表统计（二期）

---

## 二、技术栈（保持不变）

### 前端
- Vue 3.3 + TypeScript + Vite
- Element Plus（UI组件库）
- Vue Router 4
- Pinia（状态管理）
- Axios
- xlsx（Excel导出）

### 后端
- FastAPI 0.100+
- SQLAlchemy 2.0
- MySQL 8.0
- PyJWT
- bcrypt
- openpyxl

---

## 三、项目结构（简化版）

### 后端结构

```
pm-system-backend/
├── app/
│   ├── main.py                 # FastAPI入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/                 # SQLAlchemy模型（8个表）
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── cold_room.py
│   │   ├── device.py
│   │   ├── gateway.py
│   │   ├── gateway_port.py
│   │   ├── project_flow_log.py
│   │   └── operation_log.py
│   ├── schemas/                # Pydantic模型
│   │   ├── auth.py
│   │   ├── project.py
│   │   ├── device.py
│   │   └── gateway.py
│   ├── crud/                   # 数据库操作
│   │   ├── project.py
│   │   ├── device.py
│   │   └── gateway.py
│   ├── api/                    # API路由
│   │   ├── deps.py             # 依赖项
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── devices.py
│   │   ├── gateways.py
│   │   └── exports.py
│   ├── services/               # 业务逻辑
│   │   ├── auth_service.py
│   │   ├── project_service.py  # 含复制逻辑
│   │   └── export_service.py
│   └── utils/                  # 工具函数
│       ├── security.py
│       └── code_generator.py
├── scripts/
│   └── init_db.py              # 数据库初始化
├── requirements.txt
└── .env
```

### 前端结构

```
pm-system-frontend/
├── src/
│   ├── views/                  # 页面（简化）
│   │   ├── Login.vue
│   │   ├── Home.vue
│   │   ├── projects/
│   │   │   ├── ProjectList.vue
│   │   │   ├── ProjectDetail.vue
│   │   │   └── ProjectForm.vue
│   │   ├── devices/
│   │   │   ├── DeviceList.vue
│   │   │   └── DeviceForm.vue
│   │   ├── gateways/
│   │   │   └── GatewayConfig.vue
│   │   └── flow/
│   │       └── FlowProgress.vue
│   ├── components/             # 公共组件
│   │   ├── DeviceTypeSelector.vue
│   │   └── FlowSteps.vue
│   ├── api/                    # API接口
│   │   ├── auth.ts
│   │   ├── project.ts
│   │   ├── device.ts
│   │   └── gateway.ts
│   ├── store/
│   │   └── user.ts
│   ├── router/
│   │   └── index.ts
│   ├── utils/
│   │   ├── request.ts
│   │   └── export.ts
│   └── types/
│       ├── project.ts
│       └── device.ts
├── package.json
└── vite.config.ts
```

---

## 四、后端开发Prompt（MVP版本）

### 4.1 数据库初始化

#### 创建数据库
```sql
CREATE DATABASE pm_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 初始化脚本（scripts/init_db.py）
```python
from app.database import engine, SessionLocal
from app.models import Base
from app.models.user import User
from app.utils.security import hash_password

# 创建所有表
Base.metadata.create_all(bind=engine)

# 创建固定用户
db = SessionLocal()
try:
    # 用户方
    user1 = User(
        username="user001",
        password_hash=hash_password("password123"),
        user_type="user",
        display_name="用户方"
    )
    # 厂家方
    user2 = User(
        username="factory001",
        password_hash=hash_password("password123"),
        user_type="factory",
        display_name="厂家方"
    )
    db.add_all([user1, user2])
    db.commit()
    print("✅ 数据库初始化成功！")
except Exception as e:
    print(f"❌ 错误：{e}")
    db.rollback()
finally:
    db.close()
```

---

### 4.2 核心功能实现

#### 功能1：项目复制（重点） 🆕

**后端实现**（services/project_service.py）：
```python
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.cold_room import ColdRoom
from app.models.device import Device
from datetime import datetime

def copy_project(db: Session, project_id: int, current_user_id: int) -> Project:
    """
    复制项目及其所有冷库和设备
    """
    # 1. 获取原项目
    original_project = db.query(Project).filter(Project.project_id == project_id).first()
    if not original_project:
        raise ValueError("项目不存在")
    
    # 2. 创建新项目（复制基础信息）
    new_project = Project(
        project_code=generate_project_code(db),  # 重新生成编号
        project_name=f"{original_project.project_name}（副本）",
        project_type=original_project.project_type,
        city=original_project.city,
        project_address=original_project.project_address,
        mail_address=original_project.mail_address,
        mail_contact=original_project.mail_contact,
        mail_phone=original_project.mail_phone,
        expected_delivery_date=original_project.expected_delivery_date,
        current_flow_step="new_project",  # 重置流程
        remark=original_project.remark,
        created_by=current_user_id
    )
    db.add(new_project)
    db.flush()  # 获取新项目ID
    
    # 3. 复制冷库
    original_rooms = db.query(ColdRoom).filter(ColdRoom.project_id == project_id).all()
    room_id_mapping = {}  # 旧ID -> 新ID映射
    
    for old_room in original_rooms:
        new_room = ColdRoom(
            project_id=new_project.project_id,
            room_name=old_room.room_name,
            room_type=old_room.room_type,
            design_temp_min=old_room.design_temp_min,
            design_temp_max=old_room.design_temp_max,
            area=old_room.area,
            height=old_room.height,
            volume=old_room.volume,
            refrigerant_amount=old_room.refrigerant_amount,
            remark=old_room.remark
        )
        db.add(new_room)
        db.flush()
        room_id_mapping[old_room.room_id] = new_room.room_id
    
    # 4. 复制设备
    original_devices = db.query(Device).filter(Device.project_id == project_id).all()
    device_counter = {}  # 每种设备类型的计数器
    
    for old_device in original_devices:
        # 重新生成设备编号
        device_type = old_device.device_type
        counter = device_counter.get(device_type, 0) + 1
        device_counter[device_type] = counter
        new_device_code = f"{get_device_prefix(device_type)}-{new_project.project_id:03d}-{counter:03d}"
        
        # 创建新设备
        new_device = Device(
            project_id=new_project.project_id,
            room_id=room_id_mapping.get(old_device.room_id),  # 使用新冷库ID
            device_code=new_device_code,
            device_type=old_device.device_type,
            brand_name=old_device.brand_name,
            model_name=old_device.model_name,
            quantity=old_device.quantity,
            factory_serial_no=None,  # 出厂编号不复制
            comm_port_type=old_device.comm_port_type,
            comm_protocol=old_device.comm_protocol,
            remark=old_device.remark
        )
        db.add(new_device)
    
    # 5. 提交事务
    db.commit()
    db.refresh(new_project)
    
    # 6. 记录操作日志
    log_operation(db, current_user_id, "copy", "project", new_project.project_id, 
                  f"复制项目：{original_project.project_name}")
    
    return new_project

def get_device_prefix(device_type: str) -> str:
    """获取设备类型前缀"""
    prefix_map = {
        "air_cooler": "AC",
        "temp_controller": "TC",
        "power_meter": "PM",
        "unit": "UN",
        "freezer": "FR"
    }
    return prefix_map.get(device_type, "DEV")
```

**API接口**（api/projects.py）：
```python
@router.post("/{project_id}/copy", response_model=ProjectResponse)
def copy_project_api(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """复制项目"""
    try:
        new_project = copy_project(db, project_id, current_user.user_id)
        return new_project
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"复制失败：{str(e)}")
```

---

#### 功能2：项目列表增强（到货时间） 🆕

**API接口**（api/projects.py）：
```python
from datetime import date, timedelta

@router.get("/", response_model=PageResponse[ProjectResponse])
def get_projects(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,  # 搜索关键词
    project_type: str = None,  # 项目类型筛选
    city: str = None,  # 城市筛选
    delivery_filter: str = None,  # 到货时间筛选：today/week/overdue
    sort_by: str = "created_at",  # 排序字段
    sort_order: str = "desc",  # 排序方向
    db: Session = Depends(get_db)
):
    """
    获取项目列表
    
    delivery_filter:
    - today: 今天到货
    - week: 本周到货
    - overdue: 逾期未到货（期望到货时间已过且流程未完成）
    """
    query = db.query(Project)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (Project.project_name.like(f"%{keyword}%")) |
            (Project.project_code.like(f"%{keyword}%"))
        )
    
    # 项目类型筛选
    if project_type:
        query = query.filter(Project.project_type == project_type)
    
    # 城市筛选
    if city:
        query = query.filter(Project.city == city)
    
    # 到货时间筛选
    if delivery_filter == "today":
        today = date.today()
        query = query.filter(Project.expected_delivery_date == today)
    elif delivery_filter == "week":
        today = date.today()
        week_end = today + timedelta(days=7)
        query = query.filter(
            Project.expected_delivery_date >= today,
            Project.expected_delivery_date <= week_end
        )
    elif delivery_filter == "overdue":
        today = date.today()
        query = query.filter(
            Project.expected_delivery_date < today,
            Project.current_flow_step != "completed"
        )
    
    # 排序
    if sort_by == "expected_delivery_date":
        order_field = Project.expected_delivery_date
    elif sort_by == "project_name":
        order_field = Project.project_name
    else:
        order_field = Project.created_at
    
    if sort_order == "asc":
        query = query.order_by(order_field.asc())
    else:
        query = query.order_by(order_field.desc())
    
    # 分页
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
```

---

### 4.3 简化的API清单

#### 认证相关
- `POST /auth/login` - 登录（2个固定用户）
- `POST /auth/logout` - 登出
- `GET /auth/me` - 获取当前用户信息

#### 项目管理
- `GET /projects` - 获取项目列表（含筛选、排序）
- `POST /projects` - 创建项目（含到货时间）
- `GET /projects/{id}` - 获取项目详情
- `PUT /projects/{id}` - 更新项目
- `DELETE /projects/{id}` - 删除项目
- `POST /projects/{id}/copy` - **复制项目** 🆕
- `PUT /projects/{id}/flow` - 推进流程

#### 冷库管理
- `GET /projects/{id}/cold-rooms` - 获取冷库列表
- `POST /projects/{id}/cold-rooms` - 创建冷库
- `PUT /cold-rooms/{id}` - 更新冷库
- `DELETE /cold-rooms/{id}` - 删除冷库

#### 设备管理
- `GET /projects/{id}/devices` - 获取设备列表
- `POST /projects/{id}/devices` - 创建设备
- `PUT /devices/{id}` - 更新设备
- `DELETE /devices/{id}` - 删除设备

#### 网关管理
- `GET /projects/{id}/gateways` - 获取网关列表
- `POST /projects/{id}/gateways` - 创建网关
- `GET /gateways/{id}/ports` - 获取端口列表
- `PUT /gateway-ports/{id}` - 更新端口配置

#### 导出功能
- `GET /projects/{id}/export/info` - 导出项目信息
- `GET /projects/{id}/export/devices` - 导出设备清单

**总计**：约25个接口（原60个）

---

## 五、前端开发Prompt（MVP版本）

### 5.1 UI/UX设计要求 🎨

#### 配色方案
```css
/* 主色调 */
--primary-color: #1890ff;
--success-color: #52c41a;
--warning-color: #faad14;
--danger-color: #f5222d;

/* 辅助色 */
--bg-color: #f0f2f5;
--card-bg: #ffffff;
--border-color: #d9d9d9;
--text-primary: #262626;
--text-secondary: #8c8c8c;
```

#### 布局结构
```vue
<!-- 整体布局 -->
<el-container>
  <!-- 顶部导航 -->
  <el-header>
    <div class="logo">冷库项目管理系统</div>
    <div class="user-info">
      <span>{{ userInfo.display_name }}</span>
      <el-button @click="logout">退出</el-button>
    </div>
  </el-header>
  
  <el-container>
    <!-- 侧边菜单 -->
    <el-aside width="200px">
      <el-menu :default-active="currentRoute">
        <el-menu-item index="/projects">
          <el-icon><Document /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</el-container>
```

---

### 5.2 核心页面实现

#### 页面1：项目列表（含复制按钮、到货时间筛选） 🆕

```vue
<template>
  <div class="project-list">
    <!-- 顶部操作区 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input v-model="searchForm.keyword" placeholder="搜索项目名称或编号" clearable />
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.city" placeholder="选择城市" clearable>
            <el-option label="全部" value="" />
            <el-option label="北京" value="北京" />
            <el-option label="上海" value="上海" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchForm.deliveryFilter" placeholder="到货时间" clearable>
            <el-option label="全部" value="" />
            <el-option label="今天到货" value="today" />
            <el-option label="本周到货" value="week" />
            <el-option label="逾期未到" value="overdue" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-col>
        <el-col :span="4" style="text-align: right">
          <el-button type="primary" @click="handleCreate">新建项目</el-button>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 表格区 -->
    <el-card class="table-card">
      <el-table :data="projectList" stripe border>
        <el-table-column prop="project_code" label="项目编号" width="150" />
        <el-table-column prop="project_name" label="项目名称" width="200" />
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column prop="project_type" label="项目类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.project_type === 'new'">新建</el-tag>
            <el-tag v-else-if="row.project_type === 'renovation'" type="warning">改造</el-tag>
            <el-tag v-else type="info">扩建</el-tag>
          </template>
        </el-table-column>
        
        <!-- 到货时间列（新增，高亮显示） -->
        <el-table-column prop="expected_delivery_date" label="期望到货时间" width="140" sortable>
          <template #default="{ row }">
            <span :class="getDeliveryDateClass(row.expected_delivery_date)">
              {{ formatDate(row.expected_delivery_date) }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="current_flow_step" label="当前流程" width="120">
          <template #default="{ row }">
            {{ getFlowStepName(row.current_flow_step) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="160" />
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <!-- 复制按钮（新增） -->
            <el-button size="small" type="success" @click="handleCopy(row)">复制</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadProjects"
        @size-change="loadProjects"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProjects, copyProject, deleteProject } from '@/api/project'

const router = useRouter()

// 搜索表单
const searchForm = ref({
  keyword: '',
  city: '',
  deliveryFilter: ''  // 到货时间筛选
})

// 项目列表
const projectList = ref([])

// 分页
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await getProjects({
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      ...searchForm.value
    })
    projectList.value = res.data.items
    pagination.value.total = res.data.total
  } catch (error) {
    ElMessage.error('加载项目列表失败')
  }
}

// 复制项目
const handleCopy = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确认复制项目【${row.project_name}】？将复制项目信息、冷库和设备。`,
      '复制项目',
      { confirmButtonText: '确认', cancelButtonText: '取消' }
    )
    
    const res = await copyProject(row.project_id)
    ElMessage.success('项目复制成功！')
    router.push(`/projects/${res.data.project_id}/edit`)  // 跳转到编辑页
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('复制失败：' + error.message)
    }
  }
}

// 到货日期样式
const getDeliveryDateClass = (dateStr: string) => {
  const deliveryDate = new Date(dateStr)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  if (deliveryDate < today) {
    return 'text-danger'  // 已逾期，红色
  } else if (deliveryDate.getTime() === today.getTime()) {
    return 'text-warning'  // 今天到货，橙色
  }
  return 'text-normal'  // 正常，黑色
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return dateStr // 或使用 dayjs 格式化
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.text-danger {
  color: #f5222d;
  font-weight: bold;
}
.text-warning {
  color: #faad14;
  font-weight: bold;
}
.text-normal {
  color: #262626;
}
</style>
```

---

#### 页面2：项目表单（含到货时间、复制来源提示）

```vue
<template>
  <el-card>
    <template #header>
      <span>{{ isEdit ? '编辑项目' : '新建项目' }}</span>
      <span v-if="isCopied" class="copy-badge">(从【{{ copiedFromName }}】复制)</span>
    </template>
    
    <el-form :model="form" :rules="rules" ref="formRef" label-width="140px">
      <el-form-item label="项目名称" prop="project_name">
        <el-input v-model="form.project_name" placeholder="请输入项目名称" />
      </el-form-item>
      
      <el-form-item label="项目类型" prop="project_type">
        <el-radio-group v-model="form.project_type">
          <el-radio label="new">新建项目</el-radio>
          <el-radio label="renovation">改造项目</el-radio>
          <el-radio label="expansion">扩建项目</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="城市" prop="city">
        <el-select v-model="form.city" filterable placeholder="请选择城市">
          <el-option label="北京" value="北京" />
          <el-option label="上海" value="上海" />
          <el-option label="广州" value="广州" />
          <!-- 更多城市 -->
        </el-select>
      </el-form-item>
      
      <!-- 到货时间（新增，必填） -->
      <el-form-item label="货物期望到货时间" prop="expected_delivery_date">
        <el-date-picker
          v-model="form.expected_delivery_date"
          type="date"
          placeholder="选择日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
        <span class="form-tip">用于进度查看和提醒</span>
      </el-form-item>
      
      <el-form-item label="项目地址" prop="project_address">
        <el-input v-model="form.project_address" placeholder="请输入项目地址" />
      </el-form-item>
      
      <el-form-item label="邮寄地址" prop="mail_address">
        <el-input v-model="form.mail_address" placeholder="请输入邮寄地址" />
      </el-form-item>
      
      <el-form-item label="邮寄联系人" prop="mail_contact">
        <el-input v-model="form.mail_contact" placeholder="请输入联系人姓名" />
      </el-form-item>
      
      <el-form-item label="邮寄联系电话" prop="mail_phone">
        <el-input v-model="form.mail_phone" placeholder="请输入联系电话" />
      </el-form-item>
      
      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" rows="3" />
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
        <el-button @click="handleCancel">取消</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createProject, updateProject, getProjectDetail } from '@/api/project'

const route = useRoute()
const router = useRouter()

const isEdit = ref(false)
const isCopied = ref(false)
const copiedFromName = ref('')

const form = ref({
  project_name: '',
  project_type: 'new',
  city: '',
  project_address: '',
  mail_address: '',
  mail_contact: '',
  mail_phone: '',
  expected_delivery_date: '',
  remark: ''
})

const rules = {
  project_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  project_type: [{ required: true, message: '请选择项目类型', trigger: 'change' }],
  city: [{ required: true, message: '请选择城市', trigger: 'change' }],
  expected_delivery_date: [{ required: true, message: '请选择到货时间', trigger: 'change' }]
}

onMounted(async () => {
  const projectId = route.params.id
  if (projectId) {
    isEdit.value = true
    const res = await getProjectDetail(projectId as string)
    form.value = res.data
    
    // 检查是否是复制的项目（名称包含"（副本）"）
    if (form.value.project_name.includes('（副本）')) {
      isCopied.value = true
      copiedFromName.value = form.value.project_name.replace('（副本）', '')
    }
  }
})

const handleSubmit = async () => {
  // 提交逻辑
}
</script>

<style scoped>
.copy-badge {
  margin-left: 10px;
  color: #52c41a;
  font-size: 14px;
}
.form-tip {
  margin-left: 10px;
  color: #8c8c8c;
  font-size: 12px;
}
</style>
```

---

### 5.3 简化的前端页面清单

#### 核心页面（必须实现）
1. **Login.vue** - 登录页
2. **Home.vue** - 首页布局
3. **ProjectList.vue** - 项目列表（含复制、到货筛选）
4. **ProjectForm.vue** - 项目表单（含到货时间）
5. **ProjectDetail.vue** - 项目详情（Tab页）
6. **DeviceList.vue** - 设备列表
7. **DeviceForm.vue** - 设备表单
8. **GatewayConfig.vue** - 网关配置
9. **FlowProgress.vue** - 流程进度

**总计**：9个核心页面（原30个）

---

## 六、15天开发计划

### 第1周（Day 1-5）

#### Day 1：环境搭建
- [ ] 创建前后端项目
- [ ] 配置数据库连接
- [ ] 创建8张数据表
- [ ] 初始化2个固定用户
- [ ] 实现登录功能

#### Day 2：项目管理基础
- [ ] 项目CRUD API
- [ ] 项目列表页面
- [ ] 项目表单页面（含到货时间）

#### Day 3：项目复制功能
- [ ] 实现项目复制后端逻辑
- [ ] 项目列表增加复制按钮
- [ ] 测试复制功能

#### Day 4：冷库管理
- [ ] 冷库CRUD API
- [ ] 冷库列表和表单
- [ ] 自动计算容积

#### Day 5：设备管理基础
- [ ] 设备CRUD API
- [ ] 设备列表页面
- [ ] 设备表单页面

### 第2周（Day 6-10）

#### Day 6：设备管理完善
- [ ] 5种设备类型支持
- [ ] 设备编号自动生成
- [ ] 设备复制功能

#### Day 7：网关管理
- [ ] 网关CRUD API
- [ ] 网关配置页面
- [ ] 端口分配和485地址

#### Day 8：流程管理
- [ ] 流程更新API
- [ ] 流程进度展示（Steps组件）
- [ ] 流程日志记录

#### Day 9：导出功能
- [ ] 项目信息导出
- [ ] 设备清单导出
- [ ] Excel格式优化

#### Day 10：UI优化
- [ ] 按UI/UX标准调整样式
- [ ] 响应式布局调整
- [ ] 交互优化（Loading、Message）

### 第3周（Day 11-15）

#### Day 11-12：功能测试
- [ ] 完整业务流程测试
- [ ] 项目复制功能测试
- [ ] 到货时间筛选测试
- [ ] Bug修复

#### Day 13：性能优化
- [ ] SQL查询优化
- [ ] 前端加载优化
- [ ] 表格分页优化

#### Day 14：部署准备
- [ ] 配置生产环境
- [ ] 数据库迁移脚本
- [ ] 打包前后端

#### Day 15：上线培训
- [ ] 部署到服务器
- [ ] 用户培训和演示
- [ ] 收集初步反馈

---

## 七、MVP验收标准

### 功能验收
- [ ] 2个用户可以正常登录
- [ ] 可以创建项目并填写到货时间
- [ ] 可以复制历史项目（含冷库和设备）
- [ ] 项目列表可以按到货时间筛选和排序
- [ ] 可以创建冷库并自动计算容积
- [ ] 可以添加5种类型的设备
- [ ] 可以配置网关和端口
- [ ] 可以推进项目流程
- [ ] 可以导出项目信息和设备清单

### UI验收
- [ ] 界面简洁美观，符合UI/UX要求
- [ ] 操作流畅，无明显卡顿
- [ ] 表单验证友好
- [ ] 到货时间有颜色提示（逾期红色）

### 性能验收
- [ ] 页面加载 < 3秒
- [ ] 项目复制 < 5秒
- [ ] 支持20+项目数据

---

## 八、下一步

1. ✅ 确认需求变更
2. ✅ 开始环境搭建
3. ✅ 按15天计划开发
4. ✅ 每日测试和提交
5. ✅ 15天后上线使用

---

**文档版本**：V1.1 MVP  
**最后更新**：2026-01-27  
**状态**：✅ 可开始开发  
**预计完成**：15个工作日

---

**祝开发顺利！🚀**
