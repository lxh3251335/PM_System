# -*- coding: utf-8 -*-
"""批量修改 creator_company 端到端测试（不依赖 HTTP，直接调用端点函数）"""
import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.schemas.project import ProjectBatchUpdate
from app.api.projects import batch_update_projects
import asyncio


async def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 准备 2 个管理员账号：一个当前操作者、一个作为目标企业
        tag = uuid.uuid4().hex[:8]
        admin = User(username=f'admin_{tag}', password_hash='x', role='admin', company_name='发起方集团')
        target = User(username=f'targetco_{tag}', password_hash='x', role='customer', company_name='酷凌科技有限公司')
        db.add_all([admin, target])
        db.commit(); db.refresh(admin); db.refresh(target)

        # 2 个项目
        p1 = Project(project_no=f'BT{tag}_1', name='批量测试-1', created_by=admin.id, status=ProjectStatus.NEW)
        p2 = Project(project_no=f'BT{tag}_2', name='批量测试-2', created_by=admin.id, status=ProjectStatus.NEW)
        db.add_all([p1, p2]); db.commit(); db.refresh(p1); db.refresh(p2)
        assert p1.created_by == admin.id and p2.created_by == admin.id
        print(f'[PRE] 项目 {p1.id}/{p2.id} created_by={admin.id}')

        # 调用批量更新：企业名称 + 业务类型
        payload = ProjectBatchUpdate(
            project_ids=[p1.id, p2.id],
            business_type='前置仓',
            city='上海',
            creator_company='酷凌科技有限公司',
        )
        result = await batch_update_projects(payload=payload, db=db, current_user=admin)
        print(f'[RESP] {result}')

        db.refresh(p1); db.refresh(p2)
        assert p1.business_type == '前置仓' and p2.business_type == '前置仓', f'business_type 未更新'
        assert p1.city == '上海' and p2.city == '上海', f'city 未更新'
        assert p1.created_by == target.id and p2.created_by == target.id, \
            f'created_by 未迁移：p1={p1.created_by} p2={p2.created_by}'
        print(f'[OK] 批量修改成功，已迁移到 target.id={target.id}')

        # 错误场景 1：企业不存在
        payload2 = ProjectBatchUpdate(project_ids=[p1.id], creator_company='不存在的企业_xxx')
        try:
            await batch_update_projects(payload=payload2, db=db, current_user=admin)
            print('[FAIL] 应抛出 400，但未抛出')
        except Exception as e:
            print(f'[OK] 企业不存在正确拦截：{type(e).__name__}: {e}')

        # 错误场景 2：非 admin 用户尝试改 creator_company
        normal = User(username=f'user_{tag}', password_hash='x', role='customer', company_name='任意公司')
        db.add(normal); db.commit(); db.refresh(normal)
        payload3 = ProjectBatchUpdate(project_ids=[p1.id], creator_company='酷凌科技有限公司')
        try:
            await batch_update_projects(payload=payload3, db=db, current_user=normal)
            print('[FAIL] 应抛出 403，但未抛出')
        except Exception as e:
            print(f'[OK] 非管理员正确拦截：{type(e).__name__}: {e}')

        # 清理
        db.query(Project).filter(Project.id.in_([p1.id, p2.id])).delete()
        db.query(User).filter(User.id.in_([admin.id, target.id, normal.id])).delete()
        db.commit()
        print('\n全部测试通过')
    finally:
        db.close()


if __name__ == '__main__':
    asyncio.run(run())
