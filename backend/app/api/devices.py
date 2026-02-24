"""
设备管理 API（含权限校验）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from ..database import get_db
from ..models.device import Device, DeviceRelation, DeviceType
from ..models.project import Project
from ..models.user import User
from ..schemas import device as schemas
from ..auth_utils import get_current_user, check_project_permission, normalize_role

router = APIRouter()


def generate_device_no(project_id: int, device_type: DeviceType, db: Session) -> str:
    """
    生成设备编号
    格式：类型前缀-项目ID-序号
    """
    prefix_map = {
        DeviceType.AIR_COOLER: "AC",
        DeviceType.THERMOSTAT: "TC",
        DeviceType.UNIT: "UN",
        DeviceType.METER: "PM",
        DeviceType.FREEZER: "FR",
        DeviceType.DEFROST_CONTROLLER: "DF",
    }
    
    prefix = prefix_map.get(device_type, "DEV")
    
    count = db.query(Device).filter(
        and_(
            Device.project_id == project_id,
            Device.device_type == device_type
        )
    ).count()
    
    sequence = str(count + 1).zfill(3)
    project_id_str = str(project_id).zfill(3)
    
    return f"{prefix}-{project_id_str}-{sequence}"


# ========== 设备 API ==========

@router.get("/", response_model=List[schemas.Device])
async def get_devices(
    project_id: int = Query(..., description="项目ID（必填）"),
    device_type: Optional[DeviceType] = Query(None, description="设备类型筛选"),
    cold_room_id: Optional[int] = Query(None, description="冷库ID筛选"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取设备列表（校验项目归属）"""
    check_project_permission(db, project_id, current_user)

    query = db.query(Device).filter(Device.project_id == project_id)
    
    if device_type:
        query = query.filter(Device.device_type == device_type)
    if cold_room_id:
        query = query.filter(Device.cold_room_id == cold_room_id)
    
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=schemas.Device, status_code=201)
async def create_device(
    project_id: int = Query(..., description="项目ID（必填）"),
    device: schemas.DeviceCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建设备（校验项目归属）"""
    check_project_permission(db, project_id, current_user)
    
    device_no = generate_device_no(project_id, device.device_type, db)
    
    db_device = Device(
        project_id=project_id,
        device_no=device_no,
        **device.model_dump()
    )
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


@router.post("/batch", response_model=List[schemas.Device], status_code=201)
async def batch_create_devices(
    project_id: int = Query(..., description="项目ID（必填）"),
    batch: schemas.DeviceBatchCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量创建设备（校验项目归属）"""
    check_project_permission(db, project_id, current_user)
    
    new_devices = []
    
    for device_data in batch.devices:
        device_no = generate_device_no(project_id, device_data.device_type, db)
        
        db_device = Device(
            project_id=project_id,
            device_no=device_no,
            **device_data.model_dump()
        )
        
        db.add(db_device)
        db.flush()
        new_devices.append(db_device)
    
    db.commit()
    
    for device in new_devices:
        db.refresh(device)
    
    return new_devices


@router.get("/stats/{project_id}", response_model=schemas.DeviceStats)
async def get_device_stats(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取项目的设备统计信息（校验项目归属）"""
    check_project_permission(db, project_id, current_user)
    
    total = db.query(Device).filter(Device.project_id == project_id).count()
    
    air_coolers = db.query(Device).filter(
        and_(Device.project_id == project_id, Device.device_type == DeviceType.AIR_COOLER)
    ).count()
    
    thermostats = db.query(Device).filter(
        and_(Device.project_id == project_id, Device.device_type == DeviceType.THERMOSTAT)
    ).count()
    
    units = db.query(Device).filter(
        and_(Device.project_id == project_id, Device.device_type == DeviceType.UNIT)
    ).count()
    
    meters = db.query(Device).filter(
        and_(Device.project_id == project_id, Device.device_type == DeviceType.METER)
    ).count()
    
    freezers = db.query(Device).filter(
        and_(Device.project_id == project_id, Device.device_type == DeviceType.FREEZER)
    ).count()
    
    defrost_controllers = db.query(Device).filter(
        and_(Device.project_id == project_id, Device.device_type == DeviceType.DEFROST_CONTROLLER)
    ).count()
    
    return schemas.DeviceStats(
        total_devices=total,
        air_coolers=air_coolers,
        thermostats=thermostats,
        units=units,
        meters=meters,
        freezers=freezers,
        defrost_controllers=defrost_controllers
    )


# ========== 设备关系 API ==========

@router.get("/relations", response_model=List[schemas.DeviceRelationWithDevices])
async def get_device_relations(
    project_id: int = Query(..., description="项目ID（必填）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取项目的设备关系列表（校验项目归属）"""
    check_project_permission(db, project_id, current_user)
    
    relations = db.query(DeviceRelation).filter(
        DeviceRelation.project_id == project_id
    ).all()
    return relations


@router.post("/relations", response_model=schemas.DeviceRelation, status_code=201)
async def create_device_relation(
    project_id: int = Query(..., description="项目ID（必填）"),
    relation: schemas.DeviceRelationCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建设备关系（校验项目归属）"""
    check_project_permission(db, project_id, current_user)

    from_device = db.query(Device).filter(Device.id == relation.from_device_id).first()
    to_device = db.query(Device).filter(Device.id == relation.to_device_id).first()
    
    if not from_device or not to_device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    if from_device.project_id != project_id or to_device.project_id != project_id:
        raise HTTPException(status_code=400, detail="设备不属于该项目")
    
    existing = db.query(DeviceRelation).filter(
        and_(
            DeviceRelation.from_device_id == relation.from_device_id,
            DeviceRelation.to_device_id == relation.to_device_id,
            DeviceRelation.relation_type == relation.relation_type
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该关系已存在")
    
    db_relation = DeviceRelation(
        project_id=project_id,
        **relation.model_dump()
    )
    
    db.add(db_relation)
    db.commit()
    db.refresh(db_relation)
    return db_relation


@router.delete("/relations/{relation_id}")
async def delete_device_relation(
    relation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除设备关系（校验项目归属）"""
    relation = db.query(DeviceRelation).filter(DeviceRelation.id == relation_id).first()
    if not relation:
        raise HTTPException(status_code=404, detail="关系不存在")
    check_project_permission(db, relation.project_id, current_user)
    
    db.delete(relation)
    db.commit()
    return {"message": "关系删除成功"}


@router.post("/relations/batch", response_model=List[schemas.DeviceRelation], status_code=201)
async def batch_create_relations(
    project_id: int = Query(..., description="项目ID（必填）"),
    relations: List[schemas.DeviceRelationCreate] = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量创建设备关系（校验项目归属）"""
    check_project_permission(db, project_id, current_user)

    new_relations = []
    
    for relation_data in relations:
        from_device = db.query(Device).filter(Device.id == relation_data.from_device_id).first()
        to_device = db.query(Device).filter(Device.id == relation_data.to_device_id).first()
        
        if not from_device or not to_device:
            continue
        
        if from_device.project_id != project_id or to_device.project_id != project_id:
            continue
        
        existing = db.query(DeviceRelation).filter(
            and_(
                DeviceRelation.from_device_id == relation_data.from_device_id,
                DeviceRelation.to_device_id == relation_data.to_device_id,
                DeviceRelation.relation_type == relation_data.relation_type
            )
        ).first()
        
        if existing:
            continue
        
        db_relation = DeviceRelation(
            project_id=project_id,
            **relation_data.model_dump()
        )
        
        db.add(db_relation)
        db.flush()
        new_relations.append(db_relation)
    
    db.commit()
    
    for relation in new_relations:
        db.refresh(relation)
    
    return new_relations


# ========== 单设备操作（参数化路由放最后，避免拦截固定路径） ==========

@router.get("/{device_id}", response_model=schemas.Device)
async def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取设备详情（校验项目归属）"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    check_project_permission(db, device.project_id, current_user)
    return device


@router.put("/{device_id}", response_model=schemas.Device)
async def update_device(
    device_id: int,
    device_update: schemas.DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新设备信息（校验项目归属）"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    check_project_permission(db, device.project_id, current_user)
    
    for key, value in device_update.model_dump(exclude_unset=True).items():
        setattr(device, key, value)
    
    db.commit()
    db.refresh(device)
    return device


@router.delete("/{device_id}")
async def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除设备（校验项目归属）"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    check_project_permission(db, device.project_id, current_user)
    
    db.delete(device)
    db.commit()
    return {"message": "设备删除成功"}


@router.post("/{device_id}/copy", response_model=List[schemas.Device], status_code=201)
async def copy_device(
    device_id: int,
    copy_request: schemas.DeviceCopy,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """复制设备（校验项目归属）"""
    original = db.query(Device).filter(Device.id == device_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="原设备不存在")
    check_project_permission(db, original.project_id, current_user)
    
    new_devices = []
    
    for i in range(copy_request.count):
        device_no = generate_device_no(original.project_id, original.device_type, db)
        
        new_device = Device(
            project_id=original.project_id,
            cold_room_id=original.cold_room_id,
            device_no=device_no,
            device_type=original.device_type,
            brand=original.brand,
            model=original.model,
            defrost_method=original.defrost_method,
            has_intelligent_defrost=original.has_intelligent_defrost,
            expansion_valve_type=original.expansion_valve_type,
            factory_no=None,
            comm_port_type=original.comm_port_type,
            comm_protocol=original.comm_protocol,
            specifications=original.specifications,
            remarks=f"复制自设备：{original.device_no}"
        )
        
        if copy_request.copy_gateway_config:
            new_device.gateway_id = original.gateway_id
            new_device.gateway_port = original.gateway_port
        
        db.add(new_device)
        db.flush()
        new_devices.append(new_device)
    
    db.commit()
    
    for device in new_devices:
        db.refresh(device)
    
    return new_devices
