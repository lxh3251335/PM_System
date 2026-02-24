# 冷库项目登记管理系统 - 数据模型

## 文档信息
- **文档版本**：V1.0
- **创建日期**：2026-01-27
- **文档编号**：PRD-V1.0-04
- **文档类型**：数据模型
- **上一文档**：PRD-V1.0-03-功能清单
- **下一文档**：PRD-V1.0-05-业务流程

---

## 数据库设计概览

### ER图概览

```
users (用户表)
    ├── projects (项目表)
    │   ├── cold_rooms (冷库表)
    │   │   ├── devices (设备表)
    │   │   │   └── device_relationships (设备关系表)
    │   ├── gateways (网关表)
    │   │   └── gateway_ports (网关端口表)
    │   └── project_flow_logs (项目流程日志表)
    │
device_brands (设备品牌表)
    └── device_models (设备型号表)

operation_logs (操作日志表)
```

---

## 表结构设计

### 表1：users（用户表）

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| user_id | INT | - | 否 | 自增 | 主键，用户ID |
| username | VARCHAR | 50 | 否 | - | 登录用户名，唯一索引 |
| password_hash | VARCHAR | 255 | 否 | - | 密码哈希值 |
| role | ENUM | - | 否 | - | 角色：super_admin, enterprise_admin |
| enterprise_name | VARCHAR | 100 | 是 | NULL | 企业名称（企业管理员必填） |
| contact_name | VARCHAR | 50 | 否 | - | 联系人姓名 |
| contact_phone | VARCHAR | 20 | 否 | - | 联系电话 |
| email | VARCHAR | 100 | 是 | NULL | 邮箱地址 |
| status | ENUM | - | 否 | active | 状态：active, disabled |
| need_change_password | TINYINT | 1 | 否 | 0 | 是否需要修改密码（首次登录） |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |
| last_login_at | DATETIME | - | 是 | NULL | 最后登录时间 |

**索引**：
- PRIMARY KEY (user_id)
- UNIQUE INDEX idx_username (username)
- INDEX idx_enterprise (enterprise_name)

---

### 表2：device_brands（设备品牌表）

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| brand_id | INT | - | 否 | 自增 | 主键，品牌ID |
| brand_name | VARCHAR | 100 | 否 | - | 品牌名称 |
| device_type | ENUM | - | 否 | - | 设备类型：air_cooler, temp_controller, power_meter, unit, freezer, gateway |
| description | TEXT | - | 是 | NULL | 品牌描述 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引**：
- PRIMARY KEY (brand_id)
- UNIQUE INDEX idx_brand_type (brand_name, device_type)

---

### 表3：device_models（设备型号表）

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| model_id | INT | - | 否 | 自增 | 主键，型号ID |
| brand_id | INT | - | 否 | - | 外键，品牌ID |
| model_name | VARCHAR | 100 | 否 | - | 型号名称 |
| device_type | ENUM | - | 否 | - | 设备类型（同brands） |
| comm_port_type | VARCHAR | 50 | 是 | NULL | 通讯端口类型（如RS485） |
| comm_protocol | VARCHAR | 50 | 是 | NULL | 通讯协议（如Modbus RTU） |
| gateway_port_count | INT | - | 是 | NULL | 网关端口数量（仅网关类型） |
| specs | TEXT | - | 是 | NULL | 规格参数（JSON格式） |
| description | TEXT | - | 是 | NULL | 型号描述 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**索引**：
- PRIMARY KEY (model_id)
- FOREIGN KEY (brand_id) REFERENCES device_brands(brand_id)
- INDEX idx_brand (brand_id)
- INDEX idx_device_type (device_type)

---

### 表4：projects（项目表）

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
| current_flow_step | ENUM | - | 否 | new_project | 当前流程节点（见流程枚举） |
| remark | TEXT | - | 是 | NULL | 备注 |
| created_by | INT | - | 否 | - | 创建人ID |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**流程枚举值**：
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

---

### 表5：cold_rooms（冷库表）

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
- refrigerant_amount = volume × coefficient（系数可配置）

**索引**：
- PRIMARY KEY (room_id)
- FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
- INDEX idx_project (project_id)

---

### 表6：devices（设备表）

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| device_id | INT | - | 否 | 自增 | 主键，设备ID |
| room_id | INT | - | 否 | - | 外键，冷库ID |
| device_code | VARCHAR | 50 | 否 | - | 设备编号（自动生成），唯一索引 |
| device_type | ENUM | - | 否 | - | 设备类型：air_cooler, temp_controller, power_meter, unit, freezer |
| brand_id | INT | - | 否 | - | 外键，品牌ID |
| model_id | INT | - | 否 | - | 外键，型号ID |
| quantity | INT | - | 否 | 1 | 数量 |
| factory_serial_no | VARCHAR | 100 | 是 | NULL | 出厂编号 |
| comm_port_type | VARCHAR | 50 | 是 | NULL | 通讯端口类型 |
| comm_protocol | VARCHAR | 50 | 是 | NULL | 通讯协议 |
| rs485_address | INT | - | 是 | NULL | 485地址 |
| gateway_port_id | INT | - | 是 | NULL | 绑定的网关端口ID |
| remark | TEXT | - | 是 | NULL | 备注 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**设备编号规则**：设备类型缩写-冷库ID-序号
- 冷风机：AC-001-001
- 温控器：TC-001-001
- 电表：PM-001-001
- 机组：UN-001-001
- 冷柜：FR-001-001

**索引**：
- PRIMARY KEY (device_id)
- UNIQUE INDEX idx_device_code (device_code)
- FOREIGN KEY (room_id) REFERENCES cold_rooms(room_id) ON DELETE CASCADE
- FOREIGN KEY (brand_id) REFERENCES device_brands(brand_id)
- FOREIGN KEY (model_id) REFERENCES device_models(model_id)
- INDEX idx_room (room_id)
- INDEX idx_device_type (device_type)

---

### 表7：device_relationships（设备关系表）

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| relationship_id | INT | - | 否 | 自增 | 主键，关系ID |
| room_id | INT | - | 否 | - | 外键，冷库ID |
| relationship_type | ENUM | - | 否 | - | 关系类型（见下方枚举） |
| source_device_id | INT | - | 否 | - | 源设备ID |
| target_device_id | INT | - | 否 | - | 目标设备ID |
| description | VARCHAR | 255 | 是 | NULL | 关系描述 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |

**关系类型枚举**：
- air_cooler_to_unit：冷风机-机组关系
- air_cooler_to_temp_controller：冷风机-温控器关系
- power_meter_to_device：电表-设备关系
- freezer_to_temp_controller：冷柜-温控器关系
- freezer_to_unit：冷柜-机组关系

**索引**：
- PRIMARY KEY (relationship_id)
- FOREIGN KEY (room_id) REFERENCES cold_rooms(room_id) ON DELETE CASCADE
- FOREIGN KEY (source_device_id) REFERENCES devices(device_id) ON DELETE CASCADE
- FOREIGN KEY (target_device_id) REFERENCES devices(device_id) ON DELETE CASCADE
- INDEX idx_room (room_id)
- INDEX idx_source (source_device_id)
- INDEX idx_target (target_device_id)
- INDEX idx_type (relationship_type)

---

### 表8：gateways（网关表）

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| gateway_id | INT | - | 否 | 自增 | 主键，网关ID |
| project_id | INT | - | 否 | - | 外键，项目ID |
| brand_id | INT | - | 否 | - | 外键，品牌ID |
| model_id | INT | - | 否 | - | 外键，型号ID |
| gateway_code | VARCHAR | 50 | 否 | - | 网关编号 |
| port_count | INT | - | 否 | - | 端口数量（来自型号） |
| remark | TEXT | - | 是 | NULL | 备注 |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 更新时间 |

**索引**：
- PRIMARY KEY (gateway_id)
- FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
- FOREIGN KEY (brand_id) REFERENCES device_brands(brand_id)
- FOREIGN KEY (model_id) REFERENCES device_models(model_id)
- INDEX idx_project (project_id)

---

### 表9：gateway_ports（网关端口表）

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

### 表10：project_flow_logs（项目流程日志表）

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

### 表11：operation_logs（操作日志表）

| 字段名 | 类型 | 长度 | 允许空 | 默认值 | 说明 |
|--------|------|------|--------|--------|------|
| log_id | BIGINT | - | 否 | 自增 | 主键，日志ID |
| user_id | INT | - | 否 | - | 操作用户ID |
| username | VARCHAR | 50 | 否 | - | 操作用户名 |
| action | ENUM | - | 否 | - | 操作类型：login, create, update, delete |
| module | VARCHAR | 50 | 否 | - | 模块名称 |
| target_id | INT | - | 是 | NULL | 操作对象ID |
| description | VARCHAR | 255 | 否 | - | 操作描述 |
| ip_address | VARCHAR | 50 | 是 | NULL | 操作IP |
| created_at | DATETIME | - | 否 | CURRENT_TIMESTAMP | 操作时间 |

**索引**：
- PRIMARY KEY (log_id)
- INDEX idx_user (user_id)
- INDEX idx_module (module)
- INDEX idx_created_at (created_at)

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
| gateway | 网关 | GW |

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

---

## 业务规则约束

### 1. 唯一性约束
- 用户名全局唯一
- 项目编号全局唯一
- 设备编号在项目范围内唯一
- 网关端口号在网关范围内唯一

### 2. 级联删除规则
- 删除项目 → 级联删除冷库、设备、网关、流程日志
- 删除冷库 → 级联删除设备、设备关系
- 删除网关 → 级联删除网关端口
- 删除设备 → 网关端口设备ID设为NULL，设备关系删除

### 3. 数据权限规则
- 系统管理员：查看所有数据
- 企业管理员：仅查看 created_by = 当前用户ID 的项目及其子数据

### 4. 自动计算字段
- 冷库容积 = 面积 × 高度
- 制冷剂量 = 容积 × 系数（默认系数：低温0.5，冷藏0.3，中温0.2）
- 设备编号 = 设备类型缩写-冷库ID-自增序号

---

## 下一步

请查看下一份文档：**PRD-V1.0-05-业务流程.md**

---

**文档结束**
