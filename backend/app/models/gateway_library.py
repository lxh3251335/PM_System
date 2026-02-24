"""
网关型号库 + 网关库存模型
管理员维护标准网关型号及库存，项目分配时从库存中选择
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class GatewayStatus(str, enum.Enum):
    """网关库存状态"""
    IN_STOCK = "in_stock"           # 在库
    ALLOCATED = "allocated"         # 已分配项目（未发货）
    SHIPPED = "shipped"             # 已发货
    INSTALLED = "installed"         # 已安装
    RETURNED = "returned"           # 已退回


class GatewayModel(Base):
    """
    网关型号表
    管理员维护不同品牌、型号的网关规格（串口数、网口数等）
    """
    __tablename__ = "gateway_models"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(100), nullable=False, index=True, comment="品牌，如：研华、有人")
    model_name = Column(String(100), nullable=False, index=True, comment="型号，如：EKI-1528")
    
    serial_port_count = Column(Integer, nullable=False, default=0, comment="串口(COM/RS485)数量")
    ethernet_port_count = Column(Integer, nullable=False, default=0, comment="网口数量")
    
    supported_protocols = Column(JSON, comment="支持的通讯协议列表，如：['Modbus-RTU','Modbus-TCP']")
    specifications = Column(JSON, comment="其他规格参数(JSON)，如：{\"供电\":\"DC12V\",\"工作温度\":\"-40~85℃\"}")
    description = Column(Text, comment="型号说明")
    
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    inventory_items = relationship("GatewayInventory", back_populates="gateway_model", cascade="all, delete-orphan")


class GatewayInventory(Base):
    """
    网关库存表
    每条记录代表一台实体网关设备，管理员预录入后可分配给项目
    """
    __tablename__ = "gateway_inventory"

    id = Column(Integer, primary_key=True, index=True)
    gateway_model_id = Column(Integer, ForeignKey("gateway_models.id"), nullable=False, index=True, comment="网关型号ID")
    
    serial_no = Column(String(100), unique=True, index=True, nullable=False, comment="设备序列号/出厂编号")
    
    sim_card_no = Column(String(50), comment="手机卡号")
    sim_operator = Column(String(50), comment="运营商")
    sim_iccid = Column(String(50), comment="ICCID")
    
    ip_address = Column(String(50), comment="IP地址")
    mac_address = Column(String(50), comment="MAC地址")
    
    status = Column(String(20), nullable=False, default=GatewayStatus.IN_STOCK.value, index=True, comment="状态")
    
    project_id = Column(Integer, ForeignKey("projects.id"), comment="分配的项目ID（NULL=未分配）")
    
    remarks = Column(Text, comment="备注")
    created_by = Column(Integer, ForeignKey("users.id"), comment="录入人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    gateway_model = relationship("GatewayModel", back_populates="inventory_items")
