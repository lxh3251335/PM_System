"""
项目管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from urllib.parse import quote
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date, datetime, timezone
from ..database import get_db
from ..models.project import Project, ColdRoom, ProjectStatus, CustomerBusinessType
from ..models.device import Device, DeviceRelation
from ..models.gateway import Gateway, MailingRecord, FlowRecord
from ..models.user import User
from ..schemas import project as schemas
from ..auth_utils import get_current_user, require_admin, normalize_role, check_project_permission
from ..services.project_config_excel import (
    EXPORT_VERSION,
    apply_import,
    build_workbook_bytes,
    extract_workbook_preview,
)
from ..project_attachment_storage import attachment_path, remove_attachment_file

MAX_CONFIG_ATTACHMENT_BYTES = 15 * 1024 * 1024

router = APIRouter()


def generate_project_no(db: Session) -> str:
    """生成项目编号：PRJ + YYYYMMDD + 三位序号（当日递增）"""
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"PRJ{today}"
    latest = db.query(Project.project_no).filter(
        Project.project_no.like(f"{prefix}%")
    ).order_by(Project.project_no.desc()).first()

    next_seq = 1
    if latest and latest[0]:
        suffix = latest[0].replace(prefix, "")
        if suffix.isdigit():
            next_seq = int(suffix) + 1

    return f"{prefix}{next_seq:03d}"


def calculate_volume(area: float, height: float) -> float:
    """计算容积：面积 × 高度"""
    if area and height:
        return round(area * height, 2)
    return 0


def query_project_with_permission(
    db: Session,
    project_id: int,
    role: str,
    user: User
) -> Project:
    query = db.query(Project).filter(Project.id == project_id)
    if role != "admin":
        query = query.filter(Project.created_by == user.id)
    project = query.first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权限访问")
    return project


# ========== 项目 API ==========

@router.get("/", response_model=List[schemas.ProjectWithColdRooms])
async def get_projects(
    end_customer: Optional[str] = Query(None, description="最终用户筛选"),
    business_type: Optional[str] = Query(None, description="业务类型筛选"),
    status: Optional[ProjectStatus] = Query(None, description="状态筛选"),
    city: Optional[str] = Query(None, description="城市筛选"),
    company_name: Optional[str] = Query(None, description="企业名称筛选"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取项目列表
    支持多条件筛选（含企业名称）
    """
    role = normalize_role(current_user.role)
    query = db.query(Project)
    if role != "admin":
        query = query.filter(Project.created_by == current_user.id)
    
    if end_customer:
        query = query.filter(Project.end_customer == end_customer)
    if business_type:
        query = query.filter(Project.business_type == business_type)
    if status:
        query = query.filter(Project.status == status)
    if city:
        query = query.filter(Project.city == city)
    if company_name:
        creator_ids = [u.id for u in db.query(User.id).filter(User.company_name == company_name).all()]
        if creator_ids:
            query = query.filter(Project.created_by.in_(creator_ids))
    
    projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
    
    user_cache = {}
    result = []
    for p in projects:
        p_dict = schemas.Project.from_orm(p).model_dump()
        if p.created_by:
            if p.created_by not in user_cache:
                creator = db.query(User).filter(User.id == p.created_by).first()
                user_cache[p.created_by] = creator.company_name if creator else ""
            p_dict["creator_company"] = user_cache[p.created_by]
        result.append(p_dict)
    return result


@router.post("/", response_model=schemas.Project, status_code=201)
async def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新项目
    自动生成项目编号
    """
    project_no = generate_project_no(db)

    db_project = Project(
        project_no=project_no,
        created_by=current_user.id,
        **project.model_dump()
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/business-options", response_model=List[schemas.CustomerBusinessType])
async def get_business_options(
    end_customer: Optional[str] = Query(None, description="最终用户筛选"),
    db: Session = Depends(get_db)
):
    """获取最终用户-业务类型配置（客户侧用于选择）"""
    query = db.query(CustomerBusinessType)
    if end_customer:
        query = query.filter(CustomerBusinessType.end_customer == end_customer)

    return query.order_by(
        CustomerBusinessType.end_customer.asc(),
        CustomerBusinessType.business_type.asc()
    ).all()


@router.post("/business-options", response_model=schemas.CustomerBusinessType, status_code=201)
async def create_business_option(
    option: schemas.CustomerBusinessTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """新增最终用户-业务类型配置（仅管理员）"""
    require_admin(current_user)

    end_customer = option.end_customer.strip()
    business_type = option.business_type.strip()
    if not end_customer or not business_type:
        raise HTTPException(status_code=400, detail="最终用户和业务类型不能为空")

    exists = db.query(CustomerBusinessType).filter(
        CustomerBusinessType.end_customer == end_customer,
        CustomerBusinessType.business_type == business_type
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="该最终用户与业务类型已存在")

    db_item = CustomerBusinessType(
        end_customer=end_customer,
        business_type=business_type
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/business-options/{option_id}", response_model=schemas.CustomerBusinessType)
async def update_business_option(
    option_id: int,
    option: schemas.CustomerBusinessTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新最终用户-业务类型配置（仅管理员）"""
    require_admin(current_user)

    db_item = db.query(CustomerBusinessType).filter(CustomerBusinessType.id == option_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="配置不存在")

    end_customer = option.end_customer.strip()
    business_type = option.business_type.strip()
    if not end_customer or not business_type:
        raise HTTPException(status_code=400, detail="最终用户和业务类型不能为空")

    exists = db.query(CustomerBusinessType).filter(
        CustomerBusinessType.end_customer == end_customer,
        CustomerBusinessType.business_type == business_type,
        CustomerBusinessType.id != option_id
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="该最终用户与业务类型已存在")

    db_item.end_customer = end_customer
    db_item.business_type = business_type
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/business-options/{option_id}")
async def delete_business_option(
    option_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除最终用户-业务类型配置（仅管理员）"""
    require_admin(current_user)

    db_item = db.query(CustomerBusinessType).filter(CustomerBusinessType.id == option_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="配置不存在")

    db.delete(db_item)
    db.commit()
    return {"message": "配置删除成功"}


@router.post("/business-options/batch", response_model=List[schemas.CustomerBusinessType], status_code=201)
async def batch_create_business_options(
    items: List[schemas.CustomerBusinessTypeCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量创建最终用户-业务类型配置（跳过已存在的）"""
    require_admin(current_user)
    created = []
    for item in items:
        end_customer = item.end_customer.strip()
        business_type = item.business_type.strip()
        if not end_customer or not business_type:
            continue
        exists = db.query(CustomerBusinessType).filter(
            CustomerBusinessType.end_customer == end_customer,
            CustomerBusinessType.business_type == business_type
        ).first()
        if exists:
            continue
        db_item = CustomerBusinessType(end_customer=end_customer, business_type=business_type)
        db.add(db_item)
        db.flush()
        created.append(db_item)
    db.commit()
    for c in created:
        db.refresh(c)
    return created


@router.get("/contacts", response_model=List[schemas.ContactProfile])
async def get_contact_profiles(
    end_customer: Optional[str] = Query(None, description="按最终用户筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取历史收件信息（用于创建项目时快速选择）
    按创建时间倒序去重，保留同一收件人下最新的一条记录
    """
    role = normalize_role(current_user.role)

    query = db.query(Project).filter(
        Project.recipient_name.isnot(None),
        Project.recipient_phone.isnot(None),
        Project.mailing_address.isnot(None)
    )
    if role != "admin":
        query = query.filter(Project.created_by == current_user.id)
    if end_customer:
        query = query.filter(Project.end_customer == end_customer)

    projects = query.order_by(Project.created_at.desc()).all()

    contact_map = {}
    for item in projects:
        key = (item.recipient_name or "").strip()
        if not key:
            continue
        if key not in contact_map:
            contact_map[key] = schemas.ContactProfile(
                recipient_name=(item.recipient_name or "").strip(),
                recipient_phone=(item.recipient_phone or "").strip(),
                mailing_address=(item.mailing_address or "").strip()
            )

    return list(contact_map.values())


@router.get("/stats/summary", response_model=schemas.ProjectStats)
async def get_project_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目统计信息"""
    today = date.today()
    role = normalize_role(current_user.role)

    base_query = db.query(Project)
    if role != "admin":
        base_query = base_query.filter(Project.created_by == current_user.id)

    total = base_query.count()
    in_progress = base_query.filter(Project.status != ProjectStatus.COMPLETED).count()
    due_today = base_query.filter(
        and_(
            Project.expected_arrival_time == today,
            Project.status != ProjectStatus.COMPLETED
        )
    ).count()
    overdue = base_query.filter(
        and_(
            Project.expected_arrival_time < today,
            Project.status != ProjectStatus.COMPLETED
        )
    ).count()
    completed = base_query.filter(Project.status == ProjectStatus.COMPLETED).count()

    return schemas.ProjectStats(
        total_projects=total,
        in_progress=in_progress,
        due_today=due_today,
        overdue=overdue,
        completed=completed
    )


@router.get("/{project_id}", response_model=schemas.ProjectWithColdRooms)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目详情（含冷库列表）"""
    role = normalize_role(current_user.role)
    query = db.query(Project).options(joinedload(Project.cold_rooms)).filter(Project.id == project_id)
    if role != "admin":
        query = query.filter(Project.created_by == current_user.id)
    project = query.first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在或无权限访问")
    return project


@router.put("/{project_id}", response_model=schemas.Project)
async def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新项目信息"""
    role = normalize_role(current_user.role)
    project = query_project_with_permission(db, project_id, role, current_user)
    
    for key, value in project_update.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return project


@router.patch("/batch-update")
async def batch_update_projects(
    payload: schemas.ProjectBatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """批量更新指定字段（end_customer / business_type / city / creator_company）。

    仅更新调用者有权限的项目；不存在或越权的项目会跳过并在返回体中列出。
    creator_company 会被转换成 created_by：查找该企业下第一个用户作为目标创建人，
    并且这一操作仅允许 admin 调用（普通用户不能迁移项目归属）。
    """
    role = normalize_role(current_user.role)
    update_fields = payload.model_dump(exclude_unset=True)
    update_fields.pop("project_ids", None)
    if not update_fields:
        raise HTTPException(status_code=400, detail="至少需要指定一个要更新的字段")

    # 处理 creator_company -> created_by 的转换（仅 admin 允许）
    target_created_by: Optional[int] = None
    if "creator_company" in update_fields:
        company_name = (update_fields.pop("creator_company") or "").strip()
        if not company_name:
            raise HTTPException(status_code=400, detail="企业名称不能为空")
        if role != "admin":
            raise HTTPException(status_code=403, detail="仅管理员可批量修改企业名称")
        target_user = (
            db.query(User)
            .filter(User.company_name == company_name)
            .order_by(User.id.asc())
            .first()
        )
        if not target_user:
            raise HTTPException(
                status_code=400,
                detail=f"未找到归属于企业「{company_name}」的用户，请先在用户管理中创建该企业下的账号",
            )
        target_created_by = target_user.id

    updated_ids: list[int] = []
    skipped: list[dict] = []

    projects = db.query(Project).filter(Project.id.in_(payload.project_ids)).all()
    found_ids = {p.id for p in projects}
    for pid in payload.project_ids:
        if pid not in found_ids:
            skipped.append({"id": pid, "reason": "项目不存在"})

    for project in projects:
        # 权限：非 admin 只能改自己创建的项目
        if role != "admin" and project.created_by != current_user.id:
            skipped.append({"id": project.id, "reason": "无权限"})
            continue
        for key, value in update_fields.items():
            setattr(project, key, value)
        if target_created_by is not None:
            project.created_by = target_created_by
        updated_ids.append(project.id)

    if updated_ids:
        db.commit()

    applied_fields = list(update_fields.keys())
    if target_created_by is not None:
        applied_fields.append("creator_company")
    return {
        "updated_count": len(updated_ids),
        "updated_ids": updated_ids,
        "skipped": skipped,
        "fields": applied_fields,
    }


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除项目（级联删除关联数据）"""
    role = normalize_role(current_user.role)
    project = query_project_with_permission(db, project_id, role, current_user)

    db.query(DeviceRelation).filter(DeviceRelation.project_id == project_id).delete()
    db.query(MailingRecord).filter(MailingRecord.project_id == project_id).delete()
    db.query(FlowRecord).filter(FlowRecord.project_id == project_id).delete()

    remove_attachment_file(project_id)
    db.delete(project)
    db.commit()
    return {"message": "项目删除成功"}


_DEVICE_TYPE_PREFIX_MAP = {
    "air_cooler": "AC",
    "thermostat": "TC",
    "unit": "UN",
    "meter": "PM",
    "freezer": "FR",
    "defrost_controller": "DF",
    "cabinet": "CB",
    "cooling_tower": "CT",
}


def _device_type_value(device_type) -> str:
    return getattr(device_type, "value", device_type) or ""


def _generate_device_no_for_copy(project_id: int, device_type, db: Session) -> str:
    """复制项目时生成设备编号（单次查询，保留用于非批量场景）"""
    dt_val = _device_type_value(device_type)
    prefix = _DEVICE_TYPE_PREFIX_MAP.get(dt_val, "DEV")
    count = db.query(Device).filter(
        and_(Device.project_id == project_id, Device.device_type == device_type)
    ).count()
    return f"{prefix}-{str(project_id).zfill(3)}-{str(count + 1).zfill(3)}"


def _next_device_no(project_id: int, device_type, seq_map: dict) -> str:
    """基于内存序列 map 生成下一个编号，避免 O(N²) 查询。seq_map 以 device_type.value 为 key。"""
    dt_val = _device_type_value(device_type)
    prefix = _DEVICE_TYPE_PREFIX_MAP.get(dt_val, "DEV")
    seq_map[dt_val] = seq_map.get(dt_val, 0) + 1
    return f"{prefix}-{str(project_id).zfill(3)}-{str(seq_map[dt_val]).zfill(3)}"


def _generate_gateway_no_for_copy(project_id: int, db: Session) -> str:
    """复制项目时生成网关编号（与 gateways.py 中逻辑一致）"""
    count = db.query(Gateway).filter(Gateway.project_id == project_id).count()
    return f"GW-{str(project_id).zfill(3)}-{str(count + 1).zfill(3)}"


@router.post("/{project_id}/copy", response_model=schemas.Project, status_code=201)
async def copy_project(
    project_id: int,
    copy_request: schemas.ProjectCopy,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    完整复制项目
    支持复制：冷库、设备、网关、设备关系（含通讯配置）
    """
    role = normalize_role(current_user.role)
    original = query_project_with_permission(db, project_id, role, current_user)

    req_data = copy_request.model_dump(exclude_unset=True)
    new_name = req_data.pop("new_project_name")
    copy_cold_rooms = req_data.pop("copy_cold_rooms", True)
    copy_devices = req_data.pop("copy_devices", True)
    copy_gateways = req_data.pop("copy_gateways", True)
    copy_relations = req_data.pop("copy_relations", True)

    merge_keys = (
        "end_customer",
        "business_type",
        "city",
        "address",
        "mailing_address",
        "recipient_name",
        "recipient_phone",
        "expected_arrival_time",
        "remarks",
    )
    merge_values = {
        "end_customer": original.end_customer,
        "business_type": original.business_type,
        "city": original.city,
        "address": original.address,
        "mailing_address": original.mailing_address,
        "recipient_name": original.recipient_name,
        "recipient_phone": original.recipient_phone,
        "expected_arrival_time": original.expected_arrival_time,
        "remarks": f"复制自项目：{original.project_no}",
    }
    for key in merge_keys:
        if key in req_data:
            merge_values[key] = req_data[key]

    new_project = Project(
        project_no=generate_project_no(db),
        name=new_name,
        status=ProjectStatus.NEW,
        created_by=current_user.id,
        **merge_values,
    )

    db.add(new_project)
    db.flush()

    # ── 1. 复制冷库，记录 old_id -> new_id 映射 ──
    cold_room_id_map: dict[int, int] = {}
    if copy_cold_rooms:
        original_cold_rooms = db.query(ColdRoom).filter(ColdRoom.project_id == project_id).all()
        for old_room in original_cold_rooms:
            new_room = ColdRoom(
                project_id=new_project.id,
                name=old_room.name,
                room_type=old_room.room_type,
                design_temp_min=old_room.design_temp_min,
                design_temp_max=old_room.design_temp_max,
                area=old_room.area,
                height=old_room.height,
                volume=old_room.volume,
                refrigerant_type=old_room.refrigerant_type,
            )
            db.add(new_room)
            db.flush()
            cold_room_id_map[old_room.id] = new_room.id

    # ── 2. 复制网关，记录 old_id -> new_id 映射 ──
    gateway_id_map: dict[int, int] = {}
    gateway_seq = 0
    if copy_gateways:
        original_gateways = db.query(Gateway).filter(Gateway.project_id == project_id).all()
        for old_gw in original_gateways:
            gateway_seq += 1
            new_gw = Gateway(
                project_id=new_project.id,
                gateway_no=f"GW-{str(new_project.id).zfill(3)}-{str(gateway_seq).zfill(3)}",
                brand=old_gw.brand,
                model=old_gw.model,
                total_ports=old_gw.total_ports,
                serial_no=None,
                sim_card_no=old_gw.sim_card_no,
                sim_operator=old_gw.sim_operator,
                sim_iccid=old_gw.sim_iccid,
                ip_address=old_gw.ip_address,
                mac_address=old_gw.mac_address,
                specifications=old_gw.specifications,
                remarks=old_gw.remarks,
            )
            db.add(new_gw)
            db.flush()
            gateway_id_map[old_gw.id] = new_gw.id

    # ── 3. 复制设备，记录 old_id -> new_id 映射 ──
    # 注意：cabinet_id 指向另一台设备（电控柜），需要先复制所有设备再回填
    device_id_map: dict[int, int] = {}
    old_cabinet_by_new_id: dict[int, int] = {}
    device_no_seq: dict[str, int] = {}
    if copy_devices:
        original_devices = db.query(Device).filter(Device.project_id == project_id).all()
        for old_dev in original_devices:
            new_cold_room_id = cold_room_id_map.get(old_dev.cold_room_id) if old_dev.cold_room_id else None
            new_gateway_id = gateway_id_map.get(old_dev.gateway_id) if old_dev.gateway_id else None

            new_dev = Device(
                project_id=new_project.id,
                cold_room_id=new_cold_room_id,
                device_no=_next_device_no(new_project.id, old_dev.device_type, device_no_seq),
                device_type=old_dev.device_type,
                brand=old_dev.brand,
                model=old_dev.model,
                defrost_method=old_dev.defrost_method,
                has_intelligent_defrost=old_dev.has_intelligent_defrost,
                expansion_valve_type=old_dev.expansion_valve_type,
                factory_no=old_dev.factory_no,
                comm_port_type=old_dev.comm_port_type,
                comm_protocol=old_dev.comm_protocol,
                gateway_id=new_gateway_id,
                gateway_port=old_dev.gateway_port,
                rs485_address=old_dev.rs485_address,
                # 新增字段（与 device 模型保持一致）
                meter_area=old_dev.meter_area,
                # cabinet_id 延后回填，避免指向旧项目的柜子
                cabinet_id=None,
                specifications=old_dev.specifications,
                remarks=old_dev.remarks,
            )
            db.add(new_dev)
            db.flush()
            device_id_map[old_dev.id] = new_dev.id
            if old_dev.cabinet_id:
                old_cabinet_by_new_id[new_dev.id] = old_dev.cabinet_id

        # 第二遍：根据 device_id_map 回填 cabinet_id（指向本项目内的新柜子）
        for new_dev_id, old_cabinet_id in old_cabinet_by_new_id.items():
            new_cabinet_id = device_id_map.get(old_cabinet_id)
            if new_cabinet_id:
                db.query(Device).filter(Device.id == new_dev_id).update(
                    {Device.cabinet_id: new_cabinet_id}
                )

    # ── 4. 复制设备关系 ──
    if copy_relations and copy_devices:
        original_relations = db.query(DeviceRelation).filter(
            DeviceRelation.project_id == project_id
        ).all()
        for old_rel in original_relations:
            new_from = device_id_map.get(old_rel.from_device_id)
            new_to = device_id_map.get(old_rel.to_device_id)
            if new_from and new_to:
                new_rel = DeviceRelation(
                    project_id=new_project.id,
                    from_device_id=new_from,
                    to_device_id=new_to,
                    relation_type=old_rel.relation_type,
                    description=old_rel.description,
                )
                db.add(new_rel)

    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("/{project_id}/export-config-xlsx")
async def export_project_config_xlsx(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """导出项目全量配置（Excel 多工作表）"""
    role = normalize_role(current_user.role)
    query_project_with_permission(db, project_id, role, current_user)
    try:
        data, safe_name = build_workbook_bytes(db, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    fname = f"{safe_name}_config_v{EXPORT_VERSION}.xlsx"
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quote(fname)}",
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "X-PM-Export-Version": str(EXPORT_VERSION),
    }
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.post("/{project_id}/config-attachment")
async def upload_project_config_attachment(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传项目配置 Excel 附件（仅存文件，不自动写入业务表；可再下载）"""
    role = normalize_role(current_user.role)
    project = query_project_with_permission(db, project_id, role, current_user)
    fn = (file.filename or "").lower()
    if not fn.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="请上传 .xlsx 文件")
    raw = await file.read()
    if len(raw) > MAX_CONFIG_ATTACHMENT_BYTES:
        raise HTTPException(status_code=400, detail="文件过大（上限 15MB）")
    dest = attachment_path(project_id)
    dest.write_bytes(raw)
    project.config_attachment_original_name = file.filename or "config.xlsx"
    project.config_attachment_updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(project)
    return {
        "message": "配置 Excel 已保存，可随时下载",
        "config_attachment_original_name": project.config_attachment_original_name,
        "config_attachment_updated_at": project.config_attachment_updated_at.isoformat()
        if project.config_attachment_updated_at
        else None,
    }


@router.get("/{project_id}/config-attachment/preview")
async def preview_project_config_attachment(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """解析已上传的配置 Excel，返回项目/冷库/设备/关系的结构化 JSON（不写库）"""
    role = normalize_role(current_user.role)
    query_project_with_permission(db, project_id, role, current_user)
    path = attachment_path(project_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="尚未上传配置附件")
    raw = path.read_bytes()
    try:
        return extract_workbook_preview(raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/config-attachment")
async def download_project_config_attachment(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """下载已上传的项目配置 Excel 附件"""
    role = normalize_role(current_user.role)
    project = query_project_with_permission(db, project_id, role, current_user)
    path = attachment_path(project_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="尚未上传配置附件")
    data = path.read_bytes()
    oname = project.config_attachment_original_name or f"{project.project_no}_config.xlsx"
    headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(oname)}"}
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.delete("/{project_id}/config-attachment")
async def delete_project_config_attachment(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除已上传的配置附件"""
    role = normalize_role(current_user.role)
    project = query_project_with_permission(db, project_id, role, current_user)
    remove_attachment_file(project_id)
    project.config_attachment_original_name = None
    project.config_attachment_updated_at = None
    db.commit()
    return {"message": "配置附件已删除"}


@router.post("/{project_id}/import-config-xlsx")
async def import_project_config_xlsx(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """从 Excel 导入/合并项目配置（须与导出模板一致，「项目」表中 project_id 须匹配）"""
    role = normalize_role(current_user.role)
    query_project_with_permission(db, project_id, role, current_user)
    fn = (file.filename or "").lower()
    if not fn.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="请上传 .xlsx 格式（与导出模板一致）")
    raw = await file.read()
    if len(raw) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件过大（上限 15MB）")
    try:
        stats = apply_import(db, project_id, raw)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        db.rollback()
        raise
    db.commit()
    msg = (
        f"导入完成：冷库 {stats['cold_rooms']} 条，设备 {stats['devices']} 条，"
        f"关系 {stats['relations']} 条"
    )
    return {"message": msg, **stats}


# ========== 冷库 API ==========

@router.get("/{project_id}/cold-rooms", response_model=List[schemas.ColdRoom])
async def get_cold_rooms(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取项目的冷库列表"""
    role = normalize_role(current_user.role)
    query_project_with_permission(db, project_id, role, current_user)
    
    cold_rooms = db.query(ColdRoom).filter(ColdRoom.project_id == project_id).all()
    return cold_rooms


@router.post("/{project_id}/cold-rooms", response_model=schemas.ColdRoom, status_code=201)
async def create_cold_room(
    project_id: int,
    cold_room: schemas.ColdRoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建冷库
    自动计算容积：面积 × 高度
    """
    role = normalize_role(current_user.role)
    query_project_with_permission(db, project_id, role, current_user)
    
    volume = calculate_volume(cold_room.area, cold_room.height)
    
    db_cold_room = ColdRoom(
        project_id=project_id,
        volume=volume,
        **cold_room.model_dump()
    )
    
    db.add(db_cold_room)
    db.commit()
    db.refresh(db_cold_room)
    return db_cold_room


@router.get("/{project_id}/cold-rooms/{cold_room_id}", response_model=schemas.ColdRoom)
async def get_cold_room(
    project_id: int,
    cold_room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取冷库详情"""
    role = normalize_role(current_user.role)
    query_project_with_permission(db, project_id, role, current_user)

    cold_room = db.query(ColdRoom).filter(
        and_(
            ColdRoom.id == cold_room_id,
            ColdRoom.project_id == project_id
        )
    ).first()
    
    if not cold_room:
        raise HTTPException(status_code=404, detail="冷库不存在")
    return cold_room


@router.put("/{project_id}/cold-rooms/{cold_room_id}", response_model=schemas.ColdRoom)
async def update_cold_room(
    project_id: int,
    cold_room_id: int,
    cold_room_update: schemas.ColdRoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新冷库信息，自动重新计算容积"""
    role = normalize_role(current_user.role)
    query_project_with_permission(db, project_id, role, current_user)

    cold_room = db.query(ColdRoom).filter(
        and_(
            ColdRoom.id == cold_room_id,
            ColdRoom.project_id == project_id
        )
    ).first()
    
    if not cold_room:
        raise HTTPException(status_code=404, detail="冷库不存在")
    
    for key, value in cold_room_update.model_dump(exclude_unset=True).items():
        setattr(cold_room, key, value)
    
    # 重新计算容积
    if cold_room.area and cold_room.height:
        cold_room.volume = calculate_volume(cold_room.area, cold_room.height)
    
    db.commit()
    db.refresh(cold_room)
    return cold_room


@router.delete("/{project_id}/cold-rooms/{cold_room_id}")
async def delete_cold_room(
    project_id: int,
    cold_room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除冷库"""
    role = normalize_role(current_user.role)
    query_project_with_permission(db, project_id, role, current_user)

    cold_room = db.query(ColdRoom).filter(
        and_(
            ColdRoom.id == cold_room_id,
            ColdRoom.project_id == project_id
        )
    ).first()
    
    if not cold_room:
        raise HTTPException(status_code=404, detail="冷库不存在")

    db.query(Device).filter(Device.cold_room_id == cold_room_id).update(
        {Device.cold_room_id: None}
    )
    db.delete(cold_room)
    db.commit()
    return {"message": "冷库删除成功"}
