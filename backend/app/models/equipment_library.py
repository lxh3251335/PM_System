"""
标准设备库模型 - 用户自己维护的品牌、型号等标准数据
重构：支持动态设备类型和JSON模板
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class EquipmentCategory(Base):
    """
    设备类型表 (Level 1)
    管理员维护，如：冷风机、温控器、电表
    """
    __tablename__ = "equipment_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True, comment="类型名称，如：冷风机")
    code = Column(String(50), nullable=False, unique=True, index=True, comment="类型编码，如：air_cooler")
    description = Column(Text, comment="描述")
    
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    brands = relationship("EquipmentBrand", back_populates="category", cascade="all, delete-orphan")


class EquipmentBrand(Base):
    """
    设备品牌表 (Level 2)
    关联到设备类型，并定义该品牌特有的属性模板
    """
    __tablename__ = "equipment_brands"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("equipment_categories.id"), nullable=False, comment="所属设备类型")
    name = Column(String(100), nullable=False, index=True, comment="品牌名称")
    
    # 核心字段：属性模板
    # 格式示例：[{"key": "port", "label": "通讯口", "type": "text"}, {"key": "baud", "label": "波特率", "type": "select", "options": ["9600", "115200"]}]
    spec_template = Column(JSON, comment="属性模板定义(JSON)")
    
    description = Column(Text, comment="品牌描述")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    category = relationship("EquipmentCategory", back_populates="brands")
    models = relationship("EquipmentModel", back_populates="brand", cascade="all, delete-orphan")


class EquipmentModel(Base):
    """
    设备型号表 (Level 3)
    具体型号数据，specifications 存储的值必须符合 Brand 的 spec_template
    """
    __tablename__ = "equipment_models"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("equipment_brands.id"), nullable=False, comment="所属品牌")
    model_name = Column(String(100), nullable=False, index=True, comment="型号名称")
    
    # 核心字段：具体属性值
    # 格式示例：{"port": "RS485", "baud": "9600"}
    specifications = Column(JSON, comment="规格参数值(JSON)")
    
    description = Column(Text, comment="型号说明")
    
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    brand = relationship("EquipmentBrand", back_populates="models")
