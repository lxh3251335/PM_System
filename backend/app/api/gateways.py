"""
网关、邮寄、流程管理 API（含权限校验）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..models.gateway import Gateway, MailingRecord, FlowRecord
from ..models.project import Project
from ..models.user import User
from ..schemas import gateway as schemas
from ..auth_utils import get_current_user, require_admin, check_project_permission, normalize_role

router = APIRouter()


def generate_gateway_no(project_id: int, db: Session) -> str:
    count = db.query(Gateway).filter(Gateway.project_id == project_id).count()
    sequence = str(count + 1).zfill(3)
    project_id_str = str(project_id).zfill(3)
    return f"GW-{project_id_str}-{sequence}"


# ========== 邮寄记录 API（创建/改/删限管理员，查询校验项目归属） ==========
# 固定路径路由必须在 /{gateway_id} 之前注册，避免被参数化路由拦截

@router.get("/mailing", response_model=List[schemas.MailingRecordWithGateway])
async def get_mailing_records(
    project_id: int = Query(..., description="项目ID（必填）"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取项目的邮寄记录列表（客户可查看自己项目的发货状态）"""
    check_project_permission(db, project_id, current_user)
    records = db.query(MailingRecord).filter(
        MailingRecord.project_id == project_id
    ).offset(skip).limit(limit).all()
    return records


@router.post("/mailing", response_model=schemas.MailingRecord, status_code=201)
async def create_mailing_record(
    project_id: int = Query(..., description="项目ID（必填）"),
    record: schemas.MailingRecordCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建邮寄记录（仅管理员）"""
    require_admin(current_user)
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    if record.gateway_id:
        gateway = db.query(Gateway).filter(Gateway.id == record.gateway_id).first()
        if not gateway:
            raise HTTPException(status_code=404, detail="网关不存在")
    
    db_record = MailingRecord(
        project_id=project_id,
        created_by=current_user.id,
        **record.model_dump()
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/mailing/{record_id}", response_model=schemas.MailingRecordWithGateway)
async def get_mailing_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取邮寄记录详情（校验项目归属）"""
    record = db.query(MailingRecord).filter(MailingRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="邮寄记录不存在")
    check_project_permission(db, record.project_id, current_user)
    return record


@router.put("/mailing/{record_id}", response_model=schemas.MailingRecord)
async def update_mailing_record(
    record_id: int,
    record_update: schemas.MailingRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新邮寄记录（仅管理员）"""
    require_admin(current_user)
    record = db.query(MailingRecord).filter(MailingRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="邮寄记录不存在")
    
    for key, value in record_update.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    
    db.commit()
    db.refresh(record)
    return record


@router.delete("/mailing/{record_id}")
async def delete_mailing_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除邮寄记录（仅管理员）"""
    require_admin(current_user)
    record = db.query(MailingRecord).filter(MailingRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="邮寄记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "邮寄记录删除成功"}


# ========== 流程记录 API ==========

@router.get("/flows", response_model=List[schemas.FlowRecord])
async def get_flow_records(
    project_id: int = Query(..., description="项目ID（必填）"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取项目的流程记录列表（校验项目归属）"""
    check_project_permission(db, project_id, current_user)
    records = db.query(FlowRecord).filter(
        FlowRecord.project_id == project_id
    ).order_by(FlowRecord.created_at).offset(skip).limit(limit).all()
    return records


@router.post("/flows", response_model=schemas.FlowRecord, status_code=201)
async def create_flow_record(
    project_id: int = Query(..., description="项目ID（必填）"),
    record: schemas.FlowRecordCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建流程记录（校验项目归属）"""
    check_project_permission(db, project_id, current_user)
    
    db_record = FlowRecord(
        project_id=project_id,
        handler_id=current_user.id,
        **record.model_dump()
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.put("/flows/{record_id}", response_model=schemas.FlowRecord)
async def update_flow_record(
    record_id: int,
    record_update: schemas.FlowRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新流程记录（校验项目归属）"""
    record = db.query(FlowRecord).filter(FlowRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="流程记录不存在")
    check_project_permission(db, record.project_id, current_user)
    
    for key, value in record_update.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    
    db.commit()
    db.refresh(record)
    return record


@router.post("/flows/init", response_model=List[schemas.FlowRecord], status_code=201)
async def init_project_flows(
    project_id: int = Query(..., description="项目ID（必填）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """初始化项目流程（校验项目归属）"""
    check_project_permission(db, project_id, current_user)
    
    existing = db.query(FlowRecord).filter(FlowRecord.project_id == project_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="项目流程已初始化")
    
    flow_steps = [
        # 阶段一：客户操作
        {"flow_step": "new", "step_name": "新项目", "status": "completed"},
        {"flow_step": "cold_room", "step_name": "创建冷库", "status": "pending"},
        {"flow_step": "equipment_registration", "step_name": "设备登记", "status": "pending"},
        {"flow_step": "device_relations", "step_name": "设备关系绑定", "status": "pending"},
        {"flow_step": "submit_review", "step_name": "提交审核", "status": "pending"},
        # 阶段二：管理员操作
        {"flow_step": "gateway_config", "step_name": "网关配置", "status": "pending"},
        {"flow_step": "comm_setup", "step_name": "通讯设置", "status": "pending"},
        {"flow_step": "shipping", "step_name": "发货登记", "status": "pending"},
        {"flow_step": "completion", "step_name": "完成", "status": "pending"},
    ]
    
    new_records = []
    
    for step_data in flow_steps:
        record = FlowRecord(
            project_id=project_id,
            handler_id=current_user.id,
            **step_data
        )
        db.add(record)
        db.flush()
        new_records.append(record)
    
    db.commit()
    
    for record in new_records:
        db.refresh(record)
    
    return new_records


@router.post("/flows/{record_id}/complete", response_model=schemas.FlowRecord)
async def complete_flow_step(
    record_id: int,
    remarks: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    完成流程节点（校验项目归属 + 角色校验）
    客户可推进：创建冷库、设备登记、设备关系绑定、提交审核
    管理员可推进：网关配置、通讯设置、发货登记、完成
    """
    record = db.query(FlowRecord).filter(FlowRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="流程记录不存在")
    check_project_permission(db, record.project_id, current_user)
    
    if record.status == "completed":
        raise HTTPException(status_code=400, detail="该流程节点已完成")
    
    role = normalize_role(current_user.role)
    customer_steps = {"new", "cold_room", "equipment_registration", "device_relations", "submit_review"}
    admin_steps = {"gateway_config", "comm_setup", "shipping", "completion"}
    
    if role != "admin" and record.flow_step not in customer_steps:
        raise HTTPException(status_code=403, detail="您无权推进此流程节点")
    if role == "admin" and record.flow_step in customer_steps:
        pass  # 管理员可推进所有步骤
    
    record.status = "completed"
    record.completed_at = datetime.now()
    record.handler_id = current_user.id
    if remarks:
        record.remarks = remarks
    
    db.commit()
    db.refresh(record)
    return record


# ========== 网关 CRUD（参数化路由 /{gateway_id} 放最后，避免拦截 /mailing、/flows 等固定路径） ==========

@router.get("/", response_model=List[schemas.Gateway])
async def get_gateways(
    project_id: int = Query(..., description="项目ID（必填）"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取项目的网关列表（校验项目归属）"""
    check_project_permission(db, project_id, current_user)
    gateways = db.query(Gateway).filter(
        Gateway.project_id == project_id
    ).offset(skip).limit(limit).all()
    return gateways


@router.post("/", response_model=schemas.Gateway, status_code=201)
async def create_gateway(
    project_id: int = Query(..., description="项目ID（必填）"),
    gateway: schemas.GatewayCreate = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建网关（仅管理员）"""
    require_admin(current_user)
    check_project_permission(db, project_id, current_user)
    
    gateway_no = generate_gateway_no(project_id, db)
    
    db_gateway = Gateway(
        project_id=project_id,
        gateway_no=gateway_no,
        **gateway.model_dump()
    )
    
    db.add(db_gateway)
    db.commit()
    db.refresh(db_gateway)
    return db_gateway


@router.get("/{gateway_id}", response_model=schemas.Gateway)
async def get_gateway(
    gateway_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取网关详情（校验项目归属）"""
    gateway = db.query(Gateway).filter(Gateway.id == gateway_id).first()
    if not gateway:
        raise HTTPException(status_code=404, detail="网关不存在")
    check_project_permission(db, gateway.project_id, current_user)
    return gateway


@router.put("/{gateway_id}", response_model=schemas.Gateway)
async def update_gateway(
    gateway_id: int,
    gateway_update: schemas.GatewayUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新网关信息（仅管理员）"""
    require_admin(current_user)
    gateway = db.query(Gateway).filter(Gateway.id == gateway_id).first()
    if not gateway:
        raise HTTPException(status_code=404, detail="网关不存在")
    check_project_permission(db, gateway.project_id, current_user)
    
    for key, value in gateway_update.model_dump(exclude_unset=True).items():
        setattr(gateway, key, value)
    
    db.commit()
    db.refresh(gateway)
    return gateway


@router.delete("/{gateway_id}")
async def delete_gateway(
    gateway_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除网关（仅管理员）"""
    require_admin(current_user)
    gateway = db.query(Gateway).filter(Gateway.id == gateway_id).first()
    if not gateway:
        raise HTTPException(status_code=404, detail="网关不存在")
    check_project_permission(db, gateway.project_id, current_user)
    
    db.delete(gateway)
    db.commit()
    return {"message": "网关删除成功"}
