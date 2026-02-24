"""
标准设备库 - Pydantic模型
重构：支持三级动态结构
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ========== 设备类型 (Category) ==========

class EquipmentCategoryBase(BaseModel):
    name: str = Field(..., description="类型名称")
    code: str = Field(..., description="类型编码")
    description: Optional[str] = None

class EquipmentCategoryCreate(EquipmentCategoryBase):
    pass

class EquipmentCategoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

class EquipmentCategory(EquipmentCategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========== 设备品牌 (Brand) ==========

class EquipmentBrandBase(BaseModel):
    category_id: int = Field(..., description="所属类型ID")
    name: str = Field(..., description="品牌名称")
    spec_template: Optional[List[Dict[str, Any]]] = Field(None, description="属性模板(JSON list)")
    description: Optional[str] = None

class EquipmentBrandCreate(EquipmentBrandBase):
    pass

class EquipmentBrandUpdate(BaseModel):
    name: Optional[str] = None
    spec_template: Optional[List[Dict[str, Any]]] = None
    description: Optional[str] = None

class EquipmentBrand(EquipmentBrandBase):
    id: int
    created_at: datetime
    category: Optional[EquipmentCategory] = None
    
    class Config:
        from_attributes = True


# ========== 设备型号 (Model) ==========

class EquipmentModelBase(BaseModel):
    brand_id: int = Field(..., description="品牌ID")
    model_name: str = Field(..., description="型号名称")
    specifications: Optional[Dict[str, Any]] = Field(None, description="规格参数值(JSON dict)")
    description: Optional[str] = None

class EquipmentModelCreate(EquipmentModelBase):
    pass

class EquipmentModelUpdate(BaseModel):
    model_name: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    description: Optional[str] = None

class EquipmentModel(EquipmentModelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EquipmentModelWithBrand(EquipmentModel):
    brand: EquipmentBrand
