"""
网关型号库 + 库存管理 API
管理员维护网关型号和库存，项目分配时从库存选择
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import List, Optional
from ..database import get_db
from ..models.gateway_library import GatewayModel, GatewayInventory, GatewayStatus
from ..models.user import User
from ..schemas import gateway_library as schemas
from ..auth_utils import get_current_user, require_admin

router = APIRouter()


# ========== 网关型号 ==========

@router.get("/models", response_model=List[schemas.GatewayModelWithStats])
async def get_gateway_models(
    brand: str = Query(None, description="按品牌筛选"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取网关型号列表（附带库存统计）"""
    q = db.query(GatewayModel)
    if brand:
        q = q.filter(GatewayModel.brand.ilike(f"%{brand}%"))
    models = q.offset(skip).limit(limit).all()

    result = []
    for m in models:
        total = db.query(sql_func.count(GatewayInventory.id)).filter(
            GatewayInventory.gateway_model_id == m.id
        ).scalar() or 0
        in_stock = db.query(sql_func.count(GatewayInventory.id)).filter(
            GatewayInventory.gateway_model_id == m.id,
            GatewayInventory.status == GatewayStatus.IN_STOCK.value
        ).scalar() or 0
        allocated = db.query(sql_func.count(GatewayInventory.id)).filter(
            GatewayInventory.gateway_model_id == m.id,
            GatewayInventory.status == GatewayStatus.ALLOCATED.value
        ).scalar() or 0

        item = schemas.GatewayModelWithStats.from_orm(m)
        item.total_count = total
        item.in_stock_count = in_stock
        item.allocated_count = allocated
        result.append(item)
    return result


@router.post("/models", response_model=schemas.GatewayModelOut, status_code=201)
async def create_gateway_model(
    data: schemas.GatewayModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员新建网关型号"""
    require_admin(current_user)
    exists = db.query(GatewayModel).filter(
        GatewayModel.brand == data.brand,
        GatewayModel.model_name == data.model_name
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="该品牌下型号已存在")

    obj = GatewayModel(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/models/{model_id}", response_model=schemas.GatewayModelOut)
async def update_gateway_model(
    model_id: int,
    data: schemas.GatewayModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新网关型号"""
    require_admin(current_user)
    obj = db.query(GatewayModel).filter(GatewayModel.id == model_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="型号不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/models/{model_id}")
async def delete_gateway_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除网关型号（级联删除库存）"""
    require_admin(current_user)
    obj = db.query(GatewayModel).filter(GatewayModel.id == model_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="型号不存在")
    allocated = db.query(GatewayInventory).filter(
        GatewayInventory.gateway_model_id == model_id,
        GatewayInventory.status != GatewayStatus.IN_STOCK.value
    ).count()
    if allocated > 0:
        raise HTTPException(status_code=400, detail=f"该型号下有 {allocated} 台已分配/发货的网关，无法删除")
    db.delete(obj)
    db.commit()
    return {"message": "删除成功"}


# ========== 网关库存 ==========

@router.get("/inventory", response_model=List[schemas.GatewayInventoryWithModel])
async def get_inventory(
    gateway_model_id: int = Query(None, description="按型号筛选"),
    status: str = Query(None, description="按状态筛选"),
    project_id: int = Query(None, description="按项目筛选"),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db)
):
    """获取网关库存列表"""
    q = db.query(GatewayInventory)
    if gateway_model_id:
        q = q.filter(GatewayInventory.gateway_model_id == gateway_model_id)
    if status:
        q = q.filter(GatewayInventory.status == status)
    if project_id:
        q = q.filter(GatewayInventory.project_id == project_id)
    return q.order_by(GatewayInventory.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/inventory/available", response_model=List[schemas.GatewayInventoryWithModel])
async def get_available_inventory(
    gateway_model_id: int = Query(None, description="按型号筛选"),
    db: Session = Depends(get_db)
):
    """获取可分配的库存（仅 in_stock 状态）"""
    q = db.query(GatewayInventory).filter(GatewayInventory.status == GatewayStatus.IN_STOCK.value)
    if gateway_model_id:
        q = q.filter(GatewayInventory.gateway_model_id == gateway_model_id)
    return q.order_by(GatewayInventory.created_at.desc()).all()


@router.post("/inventory", response_model=schemas.GatewayInventoryOut, status_code=201)
async def create_inventory(
    data: schemas.GatewayInventoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员录入网关库存"""
    require_admin(current_user)
    gw_model = db.query(GatewayModel).filter(GatewayModel.id == data.gateway_model_id).first()
    if not gw_model:
        raise HTTPException(status_code=404, detail="网关型号不存在")
    if db.query(GatewayInventory).filter(GatewayInventory.serial_no == data.serial_no).first():
        raise HTTPException(status_code=400, detail="序列号已存在")

    obj = GatewayInventory(**data.model_dump(), status=GatewayStatus.IN_STOCK.value)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/inventory/{item_id}", response_model=schemas.GatewayInventoryOut)
async def update_inventory(
    item_id: int,
    data: schemas.GatewayInventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新库存信息"""
    require_admin(current_user)
    obj = db.query(GatewayInventory).filter(GatewayInventory.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/inventory/{item_id}")
async def delete_inventory(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除库存（仅在库状态可删）"""
    require_admin(current_user)
    obj = db.query(GatewayInventory).filter(GatewayInventory.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    if obj.status != GatewayStatus.IN_STOCK.value:
        raise HTTPException(status_code=400, detail="已分配的网关不能直接删除，请先取消分配")
    db.delete(obj)
    db.commit()
    return {"message": "删除成功"}


@router.post("/inventory/{item_id}/allocate")
async def allocate_to_project(
    item_id: int,
    project_id: int = Query(..., description="目标项目ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """将库存网关分配给项目"""
    require_admin(current_user)
    obj = db.query(GatewayInventory).filter(GatewayInventory.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    if obj.status != GatewayStatus.IN_STOCK.value:
        raise HTTPException(status_code=400, detail=f"当前状态为 {obj.status}，无法分配")
    obj.project_id = project_id
    obj.status = GatewayStatus.ALLOCATED.value
    db.commit()
    db.refresh(obj)
    return {"message": "分配成功", "inventory_id": obj.id, "project_id": project_id}


@router.post("/inventory/{item_id}/release")
async def release_from_project(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消分配，归还库存"""
    require_admin(current_user)
    obj = db.query(GatewayInventory).filter(GatewayInventory.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    if obj.status not in (GatewayStatus.ALLOCATED.value,):
        raise HTTPException(status_code=400, detail=f"当前状态为 {obj.status}，无法释放")
    obj.project_id = None
    obj.status = GatewayStatus.IN_STOCK.value
    db.commit()
    return {"message": "已释放回库存"}
