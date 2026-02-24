"""
网关和通讯配置模型
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class Gateway(Base):
    """网关表"""
    __tablename__ = "gateways"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True, comment="项目ID")
    
    # 网关信息
    gateway_no = Column(String(50), unique=True, index=True, nullable=False, comment="网关编号")
    brand = Column(String(100), nullable=False, comment="品牌")
    model = Column(String(100), nullable=False, comment="型号")
    total_ports = Column(Integer, nullable=False, comment="总端口数")
    serial_no = Column(String(100), comment="设备序列号/SN号")
    
    # 手机卡信息
    sim_card_no = Column(String(50), comment="手机卡号")
    sim_operator = Column(String(50), comment="运营商")
    sim_iccid = Column(String(50), comment="ICCID")
    
    # 网络信息
    ip_address = Column(String(50), comment="IP地址")
    mac_address = Column(String(50), comment="MAC地址")
    
    # 其他参数
    specifications = Column(Text, comment="规格参数（JSON格式）")
    remarks = Column(Text, comment="备注")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    project = relationship("Project", back_populates="gateways")
    devices = relationship("Device", back_populates="gateway")
    mailing_records = relationship("MailingRecord", back_populates="gateway")


class MailingRecord(Base):
    """邮寄记录表"""
    __tablename__ = "mailing_records"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True, comment="项目ID")
    gateway_id = Column(Integer, ForeignKey("gateways.id"), comment="网关ID")
    
    # 邮寄信息
    tracking_no = Column(String(100), index=True, comment="快递单号")
    courier_company = Column(String(100), comment="快递公司")
    mailing_date = Column(Date, comment="邮寄日期")
    expected_arrival_date = Column(Date, comment="预计到达日期")
    actual_arrival_date = Column(Date, comment="实际到达日期")
    
    # 收件信息
    recipient_name = Column(String(100), comment="收件人")
    recipient_phone = Column(String(20), comment="收件人电话")
    recipient_address = Column(Text, comment="收件地址")
    
    # 邮寄内容
    item_description = Column(Text, comment="邮寄物品描述")
    remarks = Column(Text, comment="备注")
    
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    gateway = relationship("Gateway", back_populates="mailing_records")


class FlowRecord(Base):
    """流程记录表"""
    __tablename__ = "flow_records"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True, comment="项目ID")
    
    # 流程信息
    flow_step = Column(String(50), nullable=False, index=True, comment="流程步骤")
    step_name = Column(String(100), nullable=False, comment="步骤名称")
    status = Column(String(20), nullable=False, comment="状态：pending=待处理, in_progress=进行中, completed=已完成")
    
    # 时间信息
    started_at = Column(DateTime(timezone=True), comment="开始时间")
    completed_at = Column(DateTime(timezone=True), comment="完成时间")
    
    # 处理信息
    handler_id = Column(Integer, ForeignKey("users.id"), comment="处理人ID")
    remarks = Column(Text, comment="备注")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    project = relationship("Project", back_populates="flow_records")
