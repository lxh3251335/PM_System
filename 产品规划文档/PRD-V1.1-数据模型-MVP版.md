# 冷库项目登记管理系统 - 数据模型（MVP版本）

## 文档信息
- **文档版本**：V1.1 MVP
- **创建日期**：2026-01-27
- **文档类型**：数据模型（简化版）
- **变更说明**：根据实际需求简化，聚焦核心功能

---

## 数据库设计概览（简化版）

### ER图概览

```
users (用户表 - 仅2条固定记录)
    └── projects (项目表)
        ├── cold_rooms (冷库表)
        ├── devices (设备表 - 平级结构)
        ├── gateways (网关表)
        │   └── gateway_ports (网关端口表)
        └── project_flow_logs (项目流程日志表)

device_brands (标准设备品牌表 - 二期)
device_models (标准设备型号表 - 二期)
```

---

## 表结构设计

### 表1：users（用户表）- 简化版

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| user_id | INT | - | 否 | 自增 | 主键，用户ID |
| username | VARCHAR | 50 | 否 | - | 登录用户名，唯一索引 |
| password_hash | VARCHAR | 255 | 否 | - | 密码哈希值 |
| user_type | ENUM | - | 否 | - | 用户类型：user（用户方）, factory（厂家方） |
| display_name | VARCHAR | 50 | 否 | - | 显示名称 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| last_login_at | DATETIME | - | 是 | NULL | 最后登录时间 |

**索引**：
- PRIMARY KEY (user_id)
- UNIQUE INDEX idx_username (username)

**初始数据**：
```sql
INSERT INTO users (username, password_hash, user_type, display_name) VALUES
('user001', 'hashed_password', 'user', '用户方'),
('factory001', 'hashed_password', 'factory', '厂家方');
```

⚠️ **说明**：
- 一期只有2个固定用户，无需用户管理功能
- 简化了role、enterprise_name等字段
- 保留user_type用于操作日志区分

---

### 表2：projects（项目表）- 新增到货时间

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| project_id | INT | - | 否 | 自增 | 主键，项目ID |
| project_code | VARCHAR | 50 | 否 | - | 项目编号（自动生成），唯一索引 |
| project_name | VARCHAR | 200 | 否 | - | 项目名称（站名） |
| project_type | ENUM | - | 否 | - | 项目类型：new, renovation, expansion |
| city | VARCHAR | 100 | 否 | - | 城市 |
| project_address | VARCHAR | 255 | 否 | - | 项目地址 |
| mail_address | VARCHAR | 255 | 否 | - | 邮寄地址 |
| mail_contact | VARCHAR | 50 | 否 | - | 邮寄联系人 |
| mail_phone | VARCHAR | 20 | 否 | - | 邮寄联系电话 |
| **expected_delivery_date** | **DATE** | - | **否** | - | **货物期望到货时间** 🆕 |
| current_flow_step | ENUM | - | 否 | new_project | 当前流程节点 |
| remark | TEXT | - | 是 | NULL | 备注 |
| created_by | INT | - | 否 | - | 创建人ID |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**流程枚举值**（保持不变）：
- new_project：新项目
- device_registration：设备登记
- gateway_comm_assignment：网关及485通讯分配
- gateway_registration：网关登记
- gateway_shipping：网关邮寄
- comm_verification：通讯验证
- platform_online：平台上线
- completed：功能确认及完成

**索引**：
- PRIMARY KEY (project_id)
- UNIQUE INDEX idx_project_code (project_code)
- FOREIGN KEY (created_by) REFERENCES users(user_id)
- INDEX idx_created_by (created_by)
- INDEX idx_city (city)
- INDEX idx_flow_step (current_flow_step)
- **INDEX idx_delivery_date (expected_delivery_date)** 🆕

**项目编号规则**：PRJ + YYYYMMDD + 三位序号
- 例如：PRJ20260127001

---

### 表3：cold_rooms（冷库表）- 保持不变

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| room_id | INT | - | 否 | 自增 | 主键，冷库ID |
| project_id | INT | - | 否 | - | 外键，项目ID |
| room_name | VARCHAR | 100 | 否 | - | 冷库名称 |
| room_type | ENUM | - | 否 | - | 冷库类型：low_temp, cold_storage, medium_temp |
| design_temp_min | DECIMAL | 5,2 | 否 | - | 设计温度下限（℃） |
| design_temp_max | DECIMAL | 5,2 | 否 | - | 设计温度上限（℃） |
| area | DECIMAL | 10,2 | 否 | - | 面积（平方米） |
| height | DECIMAL | 10,2 | 否 | - | 高度（米） |
| volume | DECIMAL | 10,2 | 否 | - | 容积（立方米，自动计算） |
| refrigerant_amount | DECIMAL | 10,2 | 是 | NULL | 制冷剂量（kg，自动计算） |
| remark | TEXT | - | 是 | NULL | 备注 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**冷库类型对应温度**：
- low_temp：-18℃ ~ -15℃
- cold_storage：1℃ ~ 4℃
- medium_temp：8℃ ~ 10℃

**计算规则**：
- volume = area × height
- refrigerant_amount = volume × coefficient
  - 低温库：系数0.5
  - 冷藏库：系数0.3
  - 中温库：系数0.2

**索引**：
- PRIMARY KEY (room_id)
- FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
- INDEX idx_project (project_id)

---

### 表4：devices（设备表）- 调整为平级结构

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| device_id | INT | - | 否 | 自增 | 主键，设备ID |
| project_id | INT | - | 否 | - | 外键，项目ID（平级关系） |
| room_id | INT | - | **是** | **NULL** | 外键，冷库ID（可选关联） 🔄 |
| device_code | VARCHAR | 50 | 否 | - | 设备编号（自动生成），唯一索引 |
| device_type | ENUM | - | 否 | - | 设备类型：air_cooler, temp_controller, power_meter, unit, freezer |
| brand_name | VARCHAR | 100 | 否 | - | 品牌名称（手动输入） 🔄 |
| model_name | VARCHAR | 100 | 否 | - | 型号名称（手动输入） 🔄 |
| quantity | INT | - | 否 | 1 | 数量 |
| factory_serial_no | VARCHAR | 100 | 是 | NULL | 出厂编号 |
| comm_port_type | VARCHAR | 50 | 是 | NULL | 通讯端口类型（如RS485） |
| comm_protocol | VARCHAR | 50 | 是 | NULL | 通讯协议（如Modbus RTU） |
| rs485_address | INT | - | 是 | NULL | 485地址 |
| gateway_port_id | INT | - | 是 | NULL | 绑定的网关端口ID |
| remark | TEXT | - | 是 | NULL | 备注 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**重要变更**：
- ✅ 增加 project_id（直接关联项目）
- ✅ room_id 改为可空（设备可以不关联冷库）
- ✅ 去掉 brand_id、model_id（不使用标准设备库）
- ✅ 新增 brand_name、model_name（直接输入文本）

**设备编号规则**：设备类型缩写-项目ID-序号
- 冷风机：AC-001-001
- 温控器：TC-001-001
- 电表：PM-001-001
- 机组：UN-001-001
- 冷柜：FR-001-001

**索引**：
- PRIMARY KEY (device_id)
- UNIQUE INDEX idx_device_code (device_code)
- FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
- FOREIGN KEY (room_id) REFERENCES cold_rooms(room_id) ON DELETE SET NULL
- INDEX idx_project (project_id)
- INDEX idx_room (room_id)
- INDEX idx_device_type (device_type)

---

### 表5：gateways（网关表）- 简化

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| gateway_id | INT | - | 否 | 自增 | 主键，网关ID |
| project_id | INT | - | 否 | - | 外键，项目ID |
| brand_name | VARCHAR | 100 | 否 | - | 品牌名称（手动输入） 🔄 |
| model_name | VARCHAR | 100 | 否 | - | 型号名称（手动输入） 🔄 |
| gateway_code | VARCHAR | 50 | 否 | - | 网关编号 |
| port_count | INT | - | 否 | - | 端口数量（手动输入） 🔄 |
| remark | TEXT | - | 是 | NULL | 备注 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**重要变更**：
- ✅ 去掉 brand_id、model_id
- ✅ 新增 brand_name、model_name（手动输入）
- ✅ port_count 改为手动输入（不自动获取）

**索引**：
- PRIMARY KEY (gateway_id)
- FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
- INDEX idx_project (project_id)

---

### 表6：gateway_ports（网关端口表）- 保持不变

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| port_id | INT | - | 否 | 自增 | 主键，端口ID |
| gateway_id | INT | - | 否 | - | 外键，网关ID |
| port_number | INT | - | 否 | - | 端口号（1, 2, 3...） |
| device_id | INT | - | 是 | NULL | 绑定的设备ID |
| rs485_address | INT | - | 是 | NULL | 分配的485地址 |
| status | ENUM | - | 否 | unassigned | 状态：unassigned, assigned |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**：
- PRIMARY KEY (port_id)
- FOREIGN KEY (gateway_id) REFERENCES gateways(gateway_id) ON DELETE CASCADE
- FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE SET NULL
- UNIQUE INDEX idx_gateway_port (gateway_id, port_number)
- INDEX idx_device (device_id)

---

### 表7：project_flow_logs（项目流程日志表）- 保持不变

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| log_id | INT | - | 否 | 自增 | 主键，日志ID |
| project_id | INT | - | 否 | - | 外键，项目ID |
| flow_step | ENUM | - | 否 | - | 流程节点（同projects表） |
| status | ENUM | - | 否 | - | 状态：started, completed |
| operated_by | INT | - | 否 | - | 操作人ID |
| operated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 操作时间 |
| remark | TEXT | - | 是 | NULL | 备注 |

**索引**：
- PRIMARY KEY (log_id)
- FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
- FOREIGN KEY (operated_by) REFERENCES users(user_id)
- INDEX idx_project (project_id)
- INDEX idx_flow_step (flow_step)

---

### 表8：operation_logs（操作日志表）- 简化

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| log_id | BIGINT | - | 否 | 自增 | 主键，日志ID |
| user_id | INT | - | 否 | - | 操作用户ID |
| user_type | ENUM | - | 否 | - | 用户类型：user, factory |
| action | ENUM | - | 否 | - | 操作类型：login, create, update, delete, copy |
| module | VARCHAR | 50 | 否 | - | 模块名称（project, device, gateway等） |
| target_id | INT | - | 是 | NULL | 操作对象ID |
| description | VARCHAR | 255 | 否 | - | 操作描述 |
| ip_address | VARCHAR | 50 | 是 | NULL | 操作IP |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 操作时间 |

**重要变更**：
- ✅ 增加 user_type 字段（记录是用户方还是厂家方操作）
- ✅ action 增加 copy 类型（项目复制）

**索引**：
- PRIMARY KEY (log_id)
- INDEX idx_user (user_id)
- INDEX idx_module (module)
- INDEX idx_created_at (created_at)

---

## 删除的表（二期再建）

以下表在MVP版本中不创建：

### ❌ device_brands（设备品牌表）
**原因**：一期不使用标准设备库，品牌型号直接输入文本

### ❌ device_models（设备型号表）
**原因**：同上

### ❌ device_relationships（设备关系表）
**原因**：一期设备为平级结构，不建立关系

---

## 数据字典

### 设备类型枚举（device_type）
| 值 | 中文名称 | 缩写 |
|----|----------|------|
| air_cooler | 冷风机 | AC |
| temp_controller | 温控器 | TC |
| power_meter | 电表 | PM |
| unit | 机组 | UN |
| freezer | 冷柜 | FR |

### 项目类型枚举（project_type）
| 值 | 中文名称 |
|----|----------|
| new | 新建项目 |
| renovation | 改造项目 |
| expansion | 扩建项目 |

### 冷库类型枚举（room_type）
| 值 | 中文名称 | 温度范围 |
|----|----------|----------|
| low_temp | 低温库 | -18℃ ~ -15℃ |
| cold_storage | 冷藏库 | 1℃ ~ 4℃ |
| medium_temp | 中温库 | 8℃ ~ 10℃ |

### 用户类型枚举（user_type）
| 值 | 中文名称 |
|----|----------|
| user | 用户方 |
| factory | 厂家方 |

---

## 业务规则约束

### 1. 唯一性约束
- 用户名全局唯一（仅2个）
- 项目编号全局唯一
- 设备编号全局唯一
- 网关端口号在网关范围内唯一

### 2. 级联删除规则
- 删除项目 → 级联删除冷库、设备、网关、流程日志
- 删除冷库 → 设备的room_id设为NULL（设备不删除）
- 删除网关 → 级联删除网关端口
- 删除设备 → 网关端口的device_id设为NULL

### 3. 自动计算字段
- 冷库容积 = 面积 × 高度
- 制冷剂量 = 容积 × 系数（低温0.5，冷藏0.3，中温0.2）
- 设备编号 = 设备类型缩写-项目ID-自增序号
- 项目编号 = PRJ + YYYYMMDD + 序号

### 4. 项目复制规则
- 复制范围：项目信息、冷库、设备（不含网关）
- 不复制：项目编号、流程状态、创建时间
- 新项目名称自动添加"（副本）"后缀
- 设备编号重新生成

---

## 数据库初始化SQL

### 创建数据库
```sql
CREATE DATABASE pm_system 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE pm_system;
```

### 初始化固定用户
```sql
-- 注意：实际部署时需要使用bcrypt加密密码
INSERT INTO users (username, password_hash, user_type, display_name) VALUES
('user001', '$2b$12$...', 'user', '用户方'),
('factory001', '$2b$12$...', 'factory', '厂家方');
```

---

## 与V1.0的主要差异

| 项目 | V1.0 | V1.1 MVP | 变更原因 |
|------|------|----------|----------|
| 表数量 | 11张 | 8张 | 简化功能 |
| users表 | 复杂字段 | 简化字段 | 固定用户 |
| projects表 | 无到货时间 | 有到货时间 | 新增需求 |
| devices表 | 外键brand/model | 文本字段brand/model | 不用标准库 |
| devices表 | room_id必填 | room_id可空 | 平级结构 |
| 设备品牌表 | 有 | 无 | 二期再建 |
| 设备型号表 | 有 | 无 | 二期再建 |
| 设备关系表 | 有 | 无 | 二期再建 |

---

## 下一步

请查看：
- **PRD-V1.1-MVP开发Prompt.md** - MVP版本开发指南
- **PRD-V1.1-需求变更说明.md** - 详细变更说明

---

**文档版本**：V1.1 MVP  
**最后更新**：2026-01-27  
**状态**：✅ 适用于MVP版本开发  

---

**文档结束**
