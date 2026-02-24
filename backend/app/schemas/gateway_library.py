"""
网关型号库 + 库存管理 - Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========== 网关型号 ==========

class GatewayModelBase(BaseModel):
    brand: str = Field(..., description="品牌")
    model_name: str = Field(..., description="型号名称")
    serial_port_count: int = Field(0, description="串口数量")
    ethernet_port_count: int = Field(0, description="网口数量")
    supported_protocols: Optional[List[str]] = Field(None, description="支持的通讯协议")
    specifications: Optional[Dict[str, Any]] = Field(None, description="其他规格参数")
    description: Optional[str] = None

class GatewayModelCreate(GatewayModelBase):
    pass

class GatewayModelUpdate(BaseModel):
    brand: Optional[str] = None
    model_name: Optional[str] = None
    serial_port_count: Optional[int] = None
    ethernet_port_count: Optional[int] = None
    supported_protocols: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

class GatewayModelOut(GatewayModelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GatewayModelWithStats(GatewayModelOut):
    """附带库存统计"""
    total_count: int = 0
    in_stock_count: int = 0
    allocated_count: int = 0


# ========== 网关库存 ==========

class GatewayInventoryBase(BaseModel):
    gateway_model_id: int = Field(..., description="网关型号ID")
    serial_no: str = Field(..., description="设备序列号")
    sim_card_no: Optional[str] = None
    sim_operator: Optional[str] = None
    sim_iccid: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    remarks: Optional[str] = None

class GatewayInventoryCreate(GatewayInventoryBase):
    pass

class GatewayInventoryUpdate(BaseModel):
    serial_no: Optional[str] = None
    sim_card_no: Optional[str] = None
    sim_operator: Optional[str] = None
    sim_iccid: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    status: Optional[str] = None
    project_id: Optional[int] = None
    remarks: Optional[str] = None

class GatewayInventoryOut(GatewayInventoryBase):
    id: int
    status: str
    project_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GatewayInventoryWithModel(GatewayInventoryOut):
    """附带型号信息"""
    gateway_model: Optional[GatewayModelOut] = None
