"""
项目管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date, datetime
from ..database import get_db
from ..models.project import Project, ColdRoom, ProjectStatus, CustomerBusinessType
from ..models.device import Device
from ..models.user import User
from ..schemas import project as schemas
from ..auth_utils import get_current_user, require_admin, normalize_role, check_project_permission

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


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除项目（级联删除关联数据）"""
    role = normalize_role(current_user.role)
    project = query_project_with_permission(db, project_id, role, current_user)
    
    db.delete(project)
    db.commit()
    return {"message": "项目删除成功"}


@router.post("/{project_id}/copy", response_model=schemas.Project, status_code=201)
async def copy_project(
    project_id: int,
    copy_request: schemas.ProjectCopy,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    复制项目
    支持复制冷库和设备
    """
    role = normalize_role(current_user.role)
    original = query_project_with_permission(db, project_id, role, current_user)
    
    new_project = Project(
        project_no=generate_project_no(db),
        name=copy_request.new_project_name,
        end_customer=original.end_customer,
        business_type=original.business_type,
        city=original.city,
        address=original.address,
        mailing_address=original.mailing_address,
        recipient_name=original.recipient_name,
        recipient_phone=original.recipient_phone,
        expected_arrival_time=original.expected_arrival_time,
        status=ProjectStatus.NEW,
        created_by=current_user.id,
        remarks=f"复制自项目：{original.project_no}"
    )
    
    db.add(new_project)
    db.flush()  # 获取new_project.id
    
    # 复制冷库
    if copy_request.copy_cold_rooms:
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
                refrigerant_type=old_room.refrigerant_type
            )
            db.add(new_room)
    
    # 复制设备（如果需要）
    if copy_request.copy_devices:
        # TODO: 实现设备复制逻辑
        pass
    
    db.commit()
    db.refresh(new_project)
    return new_project



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
    
    db.delete(cold_room)
    db.commit()
    return {"message": "冷库删除成功"}
