"""
项目管理 - Pydantic模型
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime, date
from ..models.project import ProjectStatus, ColdRoomType


# ========== 冷库 ==========

class ColdRoomBase(BaseModel):
    """冷库基础模型"""
    name: str = Field(..., description="冷库名称")
    room_type: ColdRoomType = Field(..., description="冷库类型")
    design_temp_min: Optional[float] = Field(None, description="设计温度下限（℃）")
    design_temp_max: Optional[float] = Field(None, description="设计温度上限（℃）")
    area: Optional[float] = Field(None, description="面积（㎡）")
    height: Optional[float] = Field(None, description="高度（m）")
    refrigerant_type: Optional[str] = Field(None, description="制冷剂类型")


class ColdRoomCreate(ColdRoomBase):
    """创建冷库"""
    pass


class ColdRoomUpdate(BaseModel):
    """更新冷库"""
    name: Optional[str] = None
    room_type: Optional[ColdRoomType] = None
    design_temp_min: Optional[float] = None
    design_temp_max: Optional[float] = None
    area: Optional[float] = None
    height: Optional[float] = None
    refrigerant_type: Optional[str] = None


class ColdRoom(ColdRoomBase):
    """冷库响应模型"""
    id: int
    project_id: int
    volume: Optional[float] = Field(None, description="容积（m³）")
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ========== 项目 ==========

class ProjectBase(BaseModel):
    """项目基础模型"""
    name: str = Field(..., description="项目名称")
    end_customer: Optional[str] = Field(None, description="最终用户")
    business_type: Optional[str] = Field(None, description="业务类型")
    city: Optional[str] = Field(None, description="城市")
    address: Optional[str] = Field(None, description="项目地址")
    mailing_address: Optional[str] = Field(None, description="邮寄地址")
    recipient_name: Optional[str] = Field(None, description="收件人姓名")
    recipient_phone: Optional[str] = Field(None, description="收件人电话")
    expected_arrival_time: Optional[date] = Field(None, description="期望到货时间")
    remarks: Optional[str] = Field(None, description="备注")


class ProjectCreate(ProjectBase):
    """创建项目"""
    pass


class ProjectUpdate(BaseModel):
    """更新项目"""
    name: Optional[str] = None
    end_customer: Optional[str] = None
    business_type: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    mailing_address: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    expected_arrival_time: Optional[date] = None
    status: Optional[ProjectStatus] = None
    remarks: Optional[str] = None


class Project(ProjectBase):
    """项目响应模型"""
    id: int
    project_no: str
    status: ProjectStatus
    created_by: Optional[int] = None
    creator_company: Optional[str] = Field(None, description="创建者企业名称")
    created_at: datetime
    updated_at: Optional[datetime] = None
    config_attachment_original_name: Optional[str] = Field(None, description="已上传配置 Excel 原始文件名")
    config_attachment_updated_at: Optional[datetime] = Field(None, description="配置附件上传时间")
    
    class Config:
        from_attributes = True


class ProjectWithColdRooms(Project):
    """带冷库信息的项目"""
    cold_rooms: List[ColdRoom] = []


class ProjectCopy(BaseModel):
    """复制项目请求（new_project_name 必填；其余字段若传入则覆盖源项目对应字段）"""
    new_project_name: str = Field(..., description="新项目名称")
    copy_cold_rooms: bool = Field(True, description="是否复制冷库")
    copy_devices: bool = Field(False, description="是否复制设备")

    @model_validator(mode="before")
    @classmethod
    def legacy_name_field(cls, data):
        """兼容旧前端只传 name 的请求体"""
        if isinstance(data, dict) and "new_project_name" not in data and data.get("name"):
            out = dict(data)
            out["new_project_name"] = out.pop("name", "")
            return out
        return data
    end_customer: Optional[str] = Field(None, description="最终用户（覆盖）")
    business_type: Optional[str] = Field(None, description="业务类型（覆盖）")
    city: Optional[str] = Field(None, description="城市（覆盖）")
    address: Optional[str] = Field(None, description="项目地址（覆盖）")
    mailing_address: Optional[str] = Field(None, description="邮寄地址（覆盖）")
    recipient_name: Optional[str] = Field(None, description="收件人（覆盖）")
    recipient_phone: Optional[str] = Field(None, description="收件电话（覆盖）")
    expected_arrival_time: Optional[date] = Field(None, description="期望到货时间（覆盖）")
    remarks: Optional[str] = Field(None, description="备注（覆盖）")


# ========== 收件信息 ==========

class ContactProfile(BaseModel):
    """历史收件信息"""
    recipient_name: str = Field(..., description="收件人姓名")
    recipient_phone: str = Field(..., description="收件人电话")
    mailing_address: str = Field(..., description="邮寄地址")


class CustomerBusinessTypeBase(BaseModel):
    """最终用户-业务类型基础模型"""
    end_customer: str = Field(..., description="最终用户")
    business_type: str = Field(..., description="业务类型")


class CustomerBusinessTypeCreate(CustomerBusinessTypeBase):
    """创建最终用户-业务类型"""
    pass


class CustomerBusinessTypeUpdate(BaseModel):
    """更新最终用户-业务类型"""
    end_customer: str = Field(..., description="最终用户")
    business_type: str = Field(..., description="业务类型")


class CustomerBusinessType(CustomerBusinessTypeBase):
    """最终用户-业务类型响应模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 项目统计 ==========

class ProjectStats(BaseModel):
    """项目统计信息"""
    total_projects: int = Field(..., description="总项目数")
    in_progress: int = Field(..., description="进行中")
    due_today: int = Field(..., description="今日到期")
    overdue: int = Field(..., description="已逾期")
    completed: int = Field(..., description="已完成")
