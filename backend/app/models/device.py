"""
设备模型 - 实际项目中的设备
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class DeviceType(str, enum.Enum):
    """设备类型"""
    AIR_COOLER = "air_cooler"  # 冷风机
    THERMOSTAT = "thermostat"  # 温控器
    UNIT = "unit"  # 机组
    METER = "meter"  # 电表
    FREEZER = "freezer"  # 冷柜
    DEFROST_CONTROLLER = "defrost_controller"  # 智能融霜控制器


class Device(Base):
    """设备表 - 项目中的实际设备"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True, comment="项目ID")
    cold_room_id = Column(Integer, ForeignKey("cold_rooms.id"), nullable=True, index=True, comment="冷库ID（冷风机必填）")
    
    # 设备基本信息
    device_no = Column(String(50), nullable=False, index=True, comment="设备编号：AC-001-001, TC-001-001等")
    device_type = Column(SQLEnum(DeviceType), nullable=False, index=True, comment="设备类型")
    
    # 从标准库选择或手动输入
    brand = Column(String(100), nullable=False, comment="品牌")
    model = Column(String(100), nullable=False, comment="型号")
    
    # 冷风机特有
    defrost_method = Column(String(50), comment="融霜方式")
    has_intelligent_defrost = Column(String(10), comment="智能融霜：yes=是, no=否")
    expansion_valve_type = Column(String(50), comment="膨胀阀方式")
    
    # 机组/冷风机特有
    factory_no = Column(String(100), comment="出厂编号")
    
    # 通讯参数
    comm_port_type = Column(String(50), comment="通讯端口类型")
    comm_protocol = Column(String(50), comment="通讯协议")
    
    # 网关配置
    gateway_id = Column(Integer, ForeignKey("gateways.id"), comment="关联网关ID")
    gateway_port = Column(Integer, comment="网关端口号")
    rs485_address = Column(String(10), comment="RS485地址")
    
    # 其他参数
    specifications = Column(Text, comment="规格参数（JSON格式）")
    remarks = Column(Text, comment="备注")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    project = relationship("Project", back_populates="devices")
    cold_room = relationship("ColdRoom", back_populates="devices")
    gateway = relationship("Gateway", back_populates="devices")
    
    # 设备关系
    related_from = relationship("DeviceRelation", foreign_keys="DeviceRelation.from_device_id", back_populates="from_device")
    related_to = relationship("DeviceRelation", foreign_keys="DeviceRelation.to_device_id", back_populates="to_device")


class RelationType(str, enum.Enum):
    """设备关系类型"""
    THERMOSTAT_TO_AIR_COOLER = "thermostat_to_air_cooler"  # 温控器→冷风机
    UNIT_TO_AIR_COOLER = "unit_to_air_cooler"  # 机组→冷风机
    UNIT_TO_FREEZER = "unit_to_freezer"  # 机组→冷柜
    METER_TO_UNIT = "meter_to_unit"  # 电表→机组
    METER_TO_AIR_COOLER = "meter_to_air_cooler"  # 电表→冷风机
    DEFROST_TO_AIR_COOLER = "defrost_to_air_cooler"  # 融霜控制器→冷风机


class DeviceRelation(Base):
    """设备关系表"""
    __tablename__ = "device_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True, comment="项目ID")
    from_device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True, comment="源设备ID")
    to_device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True, comment="目标设备ID")
    relation_type = Column(SQLEnum(RelationType), nullable=False, comment="关系类型")
    description = Column(String(200), comment="关系描述")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关系
    from_device = relationship("Device", foreign_keys=[from_device_id], back_populates="related_from")
    to_device = relationship("Device", foreign_keys=[to_device_id], back_populates="related_to")
