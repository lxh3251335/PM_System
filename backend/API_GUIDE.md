# API 使用指南 📖

## 📌 基本信息

- **Base URL**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs`
- **数据格式**: JSON

---

## 🔗 API 模块总览

| 模块 | 前缀 | 功能 | 状态 |
|------|------|------|------|
| 标准设备库 | `/api/equipment-library` | 品牌、型号管理 | ✅ |
| 项目管理 | `/api/projects` | 项目、冷库管理 | ✅ |
| 设备管理 | `/api/devices` | 设备登记、关系管理 | ✅ |
| 网关通讯 | `/api/gateways` | 网关、邮寄、流程管理 | ✅ |

---

## 1️⃣ 标准设备库 API

### 设备品牌管理

#### 获取品牌列表
```http
GET /api/equipment-library/brands?equipment_type=thermostat
```

#### 创建品牌
```http
POST /api/equipment-library/brands
Content-Type: application/json

{
  "name": "精创",
  "equipment_type": "thermostat",
  "description": "专业温控器品牌"
}
```

#### 更新品牌
```http
PUT /api/equipment-library/brands/{brand_id}
Content-Type: application/json

{
  "description": "更新后的描述"
}
```

#### 删除品牌
```http
DELETE /api/equipment-library/brands/{brand_id}
```

### 设备型号管理

#### 获取型号列表
```http
GET /api/equipment-library/models?brand_id=1&equipment_type=air_cooler
```

#### 创建型号
```http
POST /api/equipment-library/models
Content-Type: application/json

{
  "brand_id": 1,
  "model_name": "GL-CF-200",
  "equipment_type": "air_cooler",
  "defrost_method": "electric",
  "has_intelligent_defrost": "yes",
  "expansion_valve_type": "electronic",
  "comm_port_type": "RS485",
  "comm_protocol": "Modbus RTU"
}
```

#### 复制型号
```http
POST /api/equipment-library/models/{model_id}/copy?new_model_name=GL-CF-300
```

---

## 2️⃣ 项目管理 API

### 项目管理

#### 获取项目列表
```http
GET /api/projects?end_customer=盒马&business_type=前置仓
```

#### 创建项目
```http
POST /api/projects
Content-Type: application/json

{
  "name": "北京朝阳冷库项目",
  "end_customer": "盒马",
  "business_type": "前置仓",
  "city": "北京",
  "address": "北京市朝阳区xx路xx号",
  "mailing_address": "北京市朝阳区xx路xx号",
  "recipient_name": "张三",
  "recipient_phone": "13800138000",
  "expected_arrival_time": "2026-02-15",
  "remarks": "重要项目"
}
```

#### 获取项目详情
```http
GET /api/projects/{project_id}
```

#### 更新项目
```http
PUT /api/projects/{project_id}
Content-Type: application/json

{
  "status": "equipment_registration",
  "remarks": "设备登记中"
}
```

#### 复制项目
```http
POST /api/projects/{project_id}/copy
Content-Type: application/json

{
  "new_project_name": "北京朝阳冷库项目（二期）",
  "copy_cold_rooms": true,
  "copy_devices": false
}
```

#### 获取项目统计
```http
GET /api/projects/stats/summary
```

响应示例：
```json
{
  "total_projects": 10,
  "in_progress": 7,
  "due_today": 2,
  "overdue": 1,
  "completed": 3
}
```

### 冷库管理

#### 获取冷库列表
```http
GET /api/projects/{project_id}/cold-rooms
```

#### 创建冷库
```http
POST /api/projects/{project_id}/cold-rooms
Content-Type: application/json

{
  "name": "1号低温库",
  "room_type": "low_temp",
  "design_temp_min": -18,
  "design_temp_max": -15,
  "area": 500,
  "height": 6,
  "refrigerant_type": "R410A"
}
```

**自动计算容积**: `volume = area × height = 500 × 6 = 3000 m³`

#### 更新冷库
```http
PUT /api/projects/{project_id}/cold-rooms/{cold_room_id}
Content-Type: application/json

{
  "area": 600,
  "height": 7
}
```

**容积自动重新计算**: `volume = 600 × 7 = 4200 m³`

---

## 3️⃣ 设备管理 API

### 设备登记

#### 获取设备列表
```http
GET /api/devices?project_id=1&device_type=air_cooler
```

#### 创建设备
```http
POST /api/devices?project_id=1
Content-Type: application/json

{
  "cold_room_id": 1,
  "device_type": "air_cooler",
  "brand": "格力",
  "model": "GL-CF-200",
  "defrost_method": "electric",
  "has_intelligent_defrost": "yes",
  "expansion_valve_type": "electronic",
  "factory_no": "GL20260127001",
  "comm_port_type": "RS485",
  "comm_protocol": "Modbus RTU"
}
```

**自动生成设备编号**: `AC-001-001`

#### 复制设备
```http
POST /api/devices/{device_id}/copy
Content-Type: application/json

{
  "count": 5,
  "copy_gateway_config": false
}
```

**批量创建5台相同配置的设备**: `AC-001-002` ~ `AC-001-006`

#### 批量创建设备
```http
POST /api/devices/batch?project_id=1
Content-Type: application/json

{
  "devices": [
    {
      "device_type": "thermostat",
      "brand": "精创",
      "model": "STC-200+",
      "comm_port_type": "RS485",
      "comm_protocol": "Modbus RTU"
    },
    {
      "device_type": "unit",
      "brand": "比泽尔",
      "model": "BZ-250",
      "factory_no": "BZ20260127001"
    }
  ]
}
```

#### 获取设备统计
```http
GET /api/devices/stats/{project_id}
```

响应示例：
```json
{
  "total_devices": 15,
  "air_coolers": 6,
  "thermostats": 2,
  "units": 2,
  "meters": 3,
  "freezers": 0,
  "defrost_controllers": 2
}
```

### 设备关系管理

#### 获取设备关系列表
```http
GET /api/devices/relations/?project_id=1
```

#### 创建设备关系
```http
POST /api/devices/relations/?project_id=1
Content-Type: application/json

{
  "from_device_id": 10,
  "to_device_id": 5,
  "relation_type": "thermostat_to_air_cooler",
  "description": "温控器TC-001-001控制冷风机AC-001-001"
}
```

**关系类型枚举**：
- `thermostat_to_air_cooler` - 温控器→冷风机
- `unit_to_air_cooler` - 机组→冷风机
- `unit_to_freezer` - 机组→冷柜
- `meter_to_unit` - 电表→机组
- `meter_to_air_cooler` - 电表→冷风机
- `defrost_to_air_cooler` - 融霜控制器→冷风机

#### 批量创建关系
```http
POST /api/devices/relations/batch?project_id=1
Content-Type: application/json

[
  {
    "from_device_id": 10,
    "to_device_id": 5,
    "relation_type": "thermostat_to_air_cooler"
  },
  {
    "from_device_id": 12,
    "to_device_id": 5,
    "relation_type": "unit_to_air_cooler"
  }
]
```

---

## 4️⃣ 网关和通讯配置 API

### 网关管理

#### 获取网关列表
```http
GET /api/gateways?project_id=1
```

#### 创建网关
```http
POST /api/gateways?project_id=1
Content-Type: application/json

{
  "brand": "华为",
  "model": "AR151",
  "total_ports": 8,
  "sim_card_no": "13800138000",
  "sim_operator": "中国移动",
  "sim_iccid": "89860000000000000001",
  "ip_address": "192.168.1.100",
  "mac_address": "00:11:22:33:44:55"
}
```

**自动生成网关编号**: `GW-001-001`

#### 更新网关
```http
PUT /api/gateways/{gateway_id}
Content-Type: application/json

{
  "rs485_address": "01"
}
```

### 邮寄记录管理

#### 获取邮寄记录列表
```http
GET /api/gateways/mailing/?project_id=1
```

#### 创建邮寄记录
```http
POST /api/gateways/mailing/?project_id=1
Content-Type: application/json

{
  "gateway_id": 1,
  "tracking_no": "SF1234567890",
  "courier_company": "顺丰速运",
  "mailing_date": "2026-01-27",
  "expected_arrival_date": "2026-01-29",
  "recipient_name": "张三",
  "recipient_phone": "13800138000",
  "recipient_address": "北京市朝阳区xx路xx号",
  "item_description": "网关设备1台"
}
```

#### 更新邮寄记录（记录实际到达）
```http
PUT /api/gateways/mailing/{record_id}
Content-Type: application/json

{
  "actual_arrival_date": "2026-01-28",
  "remarks": "已签收"
}
```

### 流程管理

#### 获取流程记录列表
```http
GET /api/gateways/flows/?project_id=1
```

#### 初始化项目流程
```http
POST /api/gateways/flows/init?project_id=1
```

**自动创建8个流程节点**：
1. 新项目 (completed)
2. 设备登记 (pending)
3. 网关及485通讯分配 (pending)
4. 网关登记 (pending)
5. 网关邮寄 (pending)
6. 通讯验证 (pending)
7. 平台上线 (pending)
8. 功能确认及完成 (pending)

#### 完成流程节点
```http
POST /api/gateways/flows/{record_id}/complete?remarks=设备登记完成
```

**自动记录完成时间**

#### 更新流程记录
```http
PUT /api/gateways/flows/{record_id}
Content-Type: application/json

{
  "status": "in_progress",
  "started_at": "2026-01-27T10:00:00",
  "handler_id": 1
}
```

---

## 📋 完整业务流程示例

### 流程1: 创建新项目

```bash
# 1. 创建项目
POST /api/projects
{
  "name": "北京朝阳冷库项目",
  "end_customer": "盒马",
  "business_type": "前置仓",
  "city": "北京",
  "expected_arrival_time": "2026-02-15"
}
# 返回 project_id: 1

# 2. 初始化流程
POST /api/gateways/flows/init?project_id=1

# 3. 创建冷库
POST /api/projects/1/cold-rooms
{
  "name": "1号低温库",
  "room_type": "low_temp",
  "design_temp_min": -18,
  "design_temp_max": -15,
  "area": 500,
  "height": 6,
  "refrigerant_type": "R410A"
}
# 返回 cold_room_id: 1, volume: 3000
```

### 流程2: 设备登记

```bash
# 1. 创建第一台冷风机
POST /api/devices?project_id=1
{
  "cold_room_id": 1,
  "device_type": "air_cooler",
  "brand": "格力",
  "model": "GL-CF-200",
  "defrost_method": "electric",
  "has_intelligent_defrost": "yes",
  "expansion_valve_type": "electronic"
}
# 返回 device_id: 5, device_no: "AC-001-001"

# 2. 复制创建5台相同配置的冷风机
POST /api/devices/5/copy
{
  "count": 5,
  "copy_gateway_config": false
}
# 返回 5台设备: AC-001-002 ~ AC-001-006

# 3. 创建温控器
POST /api/devices?project_id=1
{
  "device_type": "thermostat",
  "brand": "精创",
  "model": "STC-200+",
  "comm_port_type": "RS485",
  "comm_protocol": "Modbus RTU"
}
# 返回 device_id: 11, device_no: "TC-001-001"

# 4. 创建机组
POST /api/devices?project_id=1
{
  "device_type": "unit",
  "brand": "比泽尔",
  "model": "BZ-250",
  "factory_no": "BZ20260127001"
}
# 返回 device_id: 12, device_no: "UN-001-001"
```

### 流程3: 建立设备关系

```bash
# 1. 温控器→冷风机
POST /api/devices/relations/?project_id=1
{
  "from_device_id": 11,
  "to_device_id": 5,
  "relation_type": "thermostat_to_air_cooler",
  "description": "温控器控制冷风机"
}

# 2. 机组→冷风机（批量）
POST /api/devices/relations/batch?project_id=1
[
  {"from_device_id": 12, "to_device_id": 5, "relation_type": "unit_to_air_cooler"},
  {"from_device_id": 12, "to_device_id": 6, "relation_type": "unit_to_air_cooler"},
  {"from_device_id": 12, "to_device_id": 7, "relation_type": "unit_to_air_cooler"}
]
```

### 流程4: 网关配置

```bash
# 1. 创建网关
POST /api/gateways?project_id=1
{
  "brand": "华为",
  "model": "AR151",
  "total_ports": 8,
  "sim_card_no": "13800138000"
}
# 返回 gateway_id: 1, gateway_no: "GW-001-001"

# 2. 为设备分配网关端口
PUT /api/devices/11
{
  "gateway_id": 1,
  "gateway_port": 1,
  "rs485_address": "01"
}

PUT /api/devices/12
{
  "gateway_id": 1,
  "gateway_port": 2,
  "rs485_address": "02"
}
```

### 流程5: 邮寄管理

```bash
# 1. 创建邮寄记录
POST /api/gateways/mailing/?project_id=1
{
  "gateway_id": 1,
  "tracking_no": "SF1234567890",
  "courier_company": "顺丰速运",
  "mailing_date": "2026-01-27",
  "expected_arrival_date": "2026-01-29",
  "recipient_name": "张三",
  "recipient_phone": "13800138000"
}

# 2. 到货后更新
PUT /api/gateways/mailing/1
{
  "actual_arrival_date": "2026-01-28",
  "remarks": "已签收"
}
```

### 流程6: 推进流程

```bash
# 1. 完成"设备登记"节点
POST /api/gateways/flows/2/complete?remarks=所有设备登记完成

# 2. 完成"网关配置"节点
POST /api/gateways/flows/3/complete?remarks=网关及485地址分配完成

# 3. 完成"网关邮寄"节点
POST /api/gateways/flows/5/complete?remarks=网关已寄出并签收

# 4. 完成整个项目
PUT /api/projects/1
{
  "status": "completed"
}

POST /api/gateways/flows/8/complete?remarks=项目验收完成
```

---

## 🎯 设备类型和编号规则

| 设备类型 | 枚举值 | 编号前缀 | 编号示例 |
|---------|--------|----------|----------|
| 冷风机 | `air_cooler` | AC | AC-001-001 |
| 温控器 | `thermostat` | TC | TC-001-001 |
| 机组 | `unit` | UN | UN-001-001 |
| 电表 | `meter` | PM | PM-001-001 |
| 冷柜 | `freezer` | FR | FR-001-001 |
| 融霜控制器 | `defrost_controller` | DF | DF-001-001 |

**编号规则**: `{前缀}-{项目ID(3位)}-{序号(3位)}`

---

## 📊 常用查询组合

### 查询1: 项目概览
```bash
# 获取项目基本信息
GET /api/projects/1

# 获取项目统计
GET /api/projects/stats/summary

# 获取设备统计
GET /api/devices/stats/1

# 获取流程进度
GET /api/gateways/flows/?project_id=1
```

### 查询2: 设备清单
```bash
# 所有冷风机
GET /api/devices?project_id=1&device_type=air_cooler

# 所有温控器
GET /api/devices?project_id=1&device_type=thermostat

# 某个冷库的所有设备
GET /api/devices?project_id=1&cold_room_id=1
```

### 查询3: 设备关系图
```bash
# 获取所有设备关系
GET /api/devices/relations/?project_id=1

# 获取所有设备详情
GET /api/devices?project_id=1&limit=1000
```

---

## 🔥 高级功能

### 功能1: 项目复制
复制历史项目快速创建新项目
```http
POST /api/projects/{old_project_id}/copy
{
  "new_project_name": "新项目名称",
  "copy_cold_rooms": true,
  "copy_devices": false
}
```

### 功能2: 设备批量复制
一次创建多台相同配置的设备
```http
POST /api/devices/{device_id}/copy
{
  "count": 10
}
```

### 功能3: 型号复制
快速创建相似型号
```http
POST /api/equipment-library/models/{model_id}/copy?new_model_name=新型号
```

---

## ⚠️ 注意事项

1. **设备编号自动生成**: 创建设备时无需提供`device_no`，系统自动生成
2. **容积自动计算**: 创建/更新冷库时，容积自动计算（area × height）
3. **项目ID必填**: 大部分API需要指定`project_id`参数
4. **关系验证**: 创建设备关系时会验证设备是否属于同一项目
5. **流程初始化**: 每个项目只能初始化一次流程
6. **删除级联**: 删除项目会级联删除所有关联数据（冷库、设备、网关等）

---

**祝您使用愉快！** 🚀

如需更多帮助，请访问：
- Swagger文档: http://localhost:8000/docs
- 架构文档: `ARCHITECTURE.md`
- 快速开始: `QUICKSTART.md`
