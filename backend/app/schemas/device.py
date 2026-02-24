"""
设备管理 - Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.device import DeviceType, RelationType


# ========== 设备 ==========

class DeviceBase(BaseModel):
    """设备基础模型"""
    cold_room_id: Optional[int] = Field(None, description="冷库ID（冷风机必填）")
    device_type: DeviceType = Field(..., description="设备类型")
    brand: str = Field(..., description="品牌")
    model: str = Field(..., description="型号")
    
    # 冷风机特有
    defrost_method: Optional[str] = Field(None, description="融霜方式")
    has_intelligent_defrost: Optional[str] = Field(None, description="智能融霜")
    expansion_valve_type: Optional[str] = Field(None, description="膨胀阀方式")
    
    # 机组/冷风机特有
    factory_no: Optional[str] = Field(None, description="出厂编号")
    
    # 通讯参数
    comm_port_type: Optional[str] = Field(None, description="通讯端口类型")
    comm_protocol: Optional[str] = Field(None, description="通讯协议")
    
    # 网关配置
    gateway_id: Optional[int] = Field(None, description="网关ID")
    gateway_port: Optional[int] = Field(None, description="网关端口号")
    rs485_address: Optional[str] = Field(None, description="RS485地址")
    
    # 其他
    specifications: Optional[str] = Field(None, description="规格参数（JSON）")
    remarks: Optional[str] = Field(None, description="备注")


class DeviceCreate(DeviceBase):
    """创建设备"""
    pass


class DeviceUpdate(BaseModel):
    """更新设备"""
    cold_room_id: Optional[int] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    defrost_method: Optional[str] = None
    has_intelligent_defrost: Optional[str] = None
    expansion_valve_type: Optional[str] = None
    factory_no: Optional[str] = None
    comm_port_type: Optional[str] = None
    comm_protocol: Optional[str] = None
    gateway_id: Optional[int] = None
    gateway_port: Optional[int] = None
    rs485_address: Optional[str] = None
    specifications: Optional[str] = None
    remarks: Optional[str] = None


class Device(DeviceBase):
    """设备响应模型"""
    id: int
    project_id: int
    device_no: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DeviceCopy(BaseModel):
    """复制设备请求"""
    count: int = Field(1, ge=1, le=100, description="复制数量（1-100）")
    copy_gateway_config: bool = Field(False, description="是否复制网关配置")


# ========== 设备关系 ==========

class DeviceRelationBase(BaseModel):
    """设备关系基础模型"""
    from_device_id: int = Field(..., description="源设备ID")
    to_device_id: int = Field(..., description="目标设备ID")
    relation_type: RelationType = Field(..., description="关系类型")
    description: Optional[str] = Field(None, description="关系描述")


class DeviceRelationCreate(DeviceRelationBase):
    """创建设备关系"""
    pass


class DeviceRelation(DeviceRelationBase):
    """设备关系响应模型"""
    id: int
    project_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DeviceRelationWithDevices(DeviceRelation):
    """带设备信息的关系"""
    from_device: Device
    to_device: Device


# ========== 批量创建设备 ==========

class DeviceBatchCreate(BaseModel):
    """批量创建设备"""
    devices: List[DeviceCreate] = Field(..., description="设备列表")


# ========== 设备统计 ==========

class DeviceStats(BaseModel):
    """设备统计信息"""
    total_devices: int = Field(..., description="总设备数")
    air_coolers: int = Field(..., description="冷风机数量")
    thermostats: int = Field(..., description="温控器数量")
    units: int = Field(..., description="机组数量")
    meters: int = Field(..., description="电表数量")
    freezers: int = Field(..., description="冷柜数量")
    defrost_controllers: int = Field(..., description="融霜控制器数量")
