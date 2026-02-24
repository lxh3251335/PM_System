"""
网关、邮寄、流程管理 - Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# ========== 网关 ==========

class GatewayBase(BaseModel):
    """网关基础模型"""
    brand: str = Field(..., description="品牌")
    model: str = Field(..., description="型号")
    total_ports: int = Field(..., description="总端口数")
    serial_no: Optional[str] = Field(None, description="设备序列号/SN号")
    
    # 手机卡信息
    sim_card_no: Optional[str] = Field(None, description="手机卡号")
    sim_operator: Optional[str] = Field(None, description="运营商")
    sim_iccid: Optional[str] = Field(None, description="ICCID")
    
    # 网络信息
    ip_address: Optional[str] = Field(None, description="IP地址")
    mac_address: Optional[str] = Field(None, description="MAC地址")
    
    # 其他
    specifications: Optional[str] = Field(None, description="规格参数（JSON）")
    remarks: Optional[str] = Field(None, description="备注")


class GatewayCreate(GatewayBase):
    """创建网关"""
    pass


class GatewayUpdate(BaseModel):
    """更新网关"""
    brand: Optional[str] = None
    model: Optional[str] = None
    total_ports: Optional[int] = None
    serial_no: Optional[str] = None
    sim_card_no: Optional[str] = None
    sim_operator: Optional[str] = None
    sim_iccid: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    specifications: Optional[str] = None
    remarks: Optional[str] = None


class Gateway(GatewayBase):
    """网关响应模型"""
    id: int
    project_id: int
    gateway_no: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ========== 邮寄记录 ==========

class MailingRecordBase(BaseModel):
    """邮寄记录基础模型"""
    gateway_id: Optional[int] = Field(None, description="网关ID")
    tracking_no: Optional[str] = Field(None, description="快递单号")
    courier_company: Optional[str] = Field(None, description="快递公司")
    mailing_date: Optional[date] = Field(None, description="邮寄日期")
    expected_arrival_date: Optional[date] = Field(None, description="预计到达日期")
    actual_arrival_date: Optional[date] = Field(None, description="实际到达日期")
    
    recipient_name: Optional[str] = Field(None, description="收件人")
    recipient_phone: Optional[str] = Field(None, description="收件人电话")
    recipient_address: Optional[str] = Field(None, description="收件地址")
    
    item_description: Optional[str] = Field(None, description="邮寄物品描述")
    remarks: Optional[str] = Field(None, description="备注")


class MailingRecordCreate(MailingRecordBase):
    """创建邮寄记录"""
    pass


class MailingRecordUpdate(BaseModel):
    """更新邮寄记录"""
    tracking_no: Optional[str] = None
    courier_company: Optional[str] = None
    mailing_date: Optional[date] = None
    expected_arrival_date: Optional[date] = None
    actual_arrival_date: Optional[date] = None
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    recipient_address: Optional[str] = None
    item_description: Optional[str] = None
    remarks: Optional[str] = None


class MailingRecord(MailingRecordBase):
    """邮寄记录响应模型"""
    id: int
    project_id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MailingRecordWithGateway(MailingRecord):
    """带网关信息的邮寄记录"""
    gateway: Optional[Gateway] = None


# ========== 流程记录 ==========

class FlowRecordBase(BaseModel):
    """流程记录基础模型"""
    flow_step: str = Field(..., description="流程步骤")
    step_name: str = Field(..., description="步骤名称")
    status: str = Field(..., description="状态：pending, in_progress, completed")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    handler_id: Optional[int] = Field(None, description="处理人ID")
    remarks: Optional[str] = Field(None, description="备注")


class FlowRecordCreate(FlowRecordBase):
    """创建流程记录"""
    pass


class FlowRecordUpdate(BaseModel):
    """更新流程记录"""
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    handler_id: Optional[int] = None
    remarks: Optional[str] = None


class FlowRecord(FlowRecordBase):
    """流程记录响应模型"""
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
