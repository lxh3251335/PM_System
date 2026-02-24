"""
项目和冷库模型
"""
from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class ProjectStatus(str, enum.Enum):
    """项目流程状态（两阶段模型）"""
    # 阶段一：客户操作
    NEW = "new"                                        # 新项目
    EQUIPMENT_REGISTRATION = "equipment_registration"  # 设备登记中
    SUBMITTED = "submitted"                            # 已提交，等待管理员配置
    # 阶段二：管理员操作
    CONFIGURING = "configuring"                        # 管理员配置中（网关/通讯/发货）
    COMPLETED = "completed"                            # 已完成


class Project(Base):
    """项目表"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_no = Column(String(50), unique=True, index=True, nullable=False, comment="项目编号")
    name = Column(String(200), nullable=False, index=True, comment="项目名称")
    
    # 客户信息
    end_customer = Column(String(100), index=True, comment="最终用户")
    business_type = Column(String(100), comment="业务类型")
    city = Column(String(50), index=True, comment="城市")
    address = Column(Text, comment="项目地址")
    
    # 邮寄信息
    mailing_address = Column(Text, comment="邮寄地址")
    recipient_name = Column(String(100), comment="收件人姓名")
    recipient_phone = Column(String(20), comment="收件人电话")
    
    # 时间管理
    expected_arrival_time = Column(Date, index=True, comment="期望到货时间")
    
    # 流程状态
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.NEW, index=True, comment="项目流程状态")
    
    # 备注
    remarks = Column(Text, comment="备注")
    
    # 审计字段
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True, comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    cold_rooms = relationship("ColdRoom", back_populates="project", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="project", cascade="all, delete-orphan")
    gateways = relationship("Gateway", back_populates="project", cascade="all, delete-orphan")
    flow_records = relationship("FlowRecord", back_populates="project", cascade="all, delete-orphan")


class CustomerBusinessType(Base):
    """最终用户-业务类型配置（由管理员维护）"""
    __tablename__ = "customer_business_types"

    id = Column(Integer, primary_key=True, index=True)
    end_customer = Column(String(100), nullable=False, index=True, comment="最终用户")
    business_type = Column(String(100), nullable=False, comment="业务类型")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")


class ColdRoomType(str, enum.Enum):
    """冷库类型"""
    LOW_TEMP = "low_temp"  # 低温库
    REFRIGERATED = "refrigerated"  # 冷藏库
    MEDIUM_TEMP = "medium_temp"  # 中温库


class ColdRoom(Base):
    """冷库表"""
    __tablename__ = "cold_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True, comment="项目ID")
    name = Column(String(100), nullable=False, comment="冷库名称")
    room_type = Column(SQLEnum(ColdRoomType), nullable=False, comment="冷库类型")
    
    # 设计参数
    design_temp_min = Column(Float, comment="设计温度下限（℃）")
    design_temp_max = Column(Float, comment="设计温度上限（℃）")
    area = Column(Float, comment="面积（㎡）")
    height = Column(Float, comment="高度（m）")
    volume = Column(Float, comment="容积（m³），自动计算")
    refrigerant_type = Column(String(50), comment="制冷剂类型：R410A, R404A等")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    project = relationship("Project", back_populates="cold_rooms")
    devices = relationship("Device", back_populates="cold_room")
