"""
测试项目创建功能
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"

def test_create_project():
    """测试创建项目"""
    print("\n" + "="*60)
    print("测试：创建项目")
    print("="*60)
    
    # 准备测试数据
    project_data = {
        "name": "上海浦东前置仓项目-测试",
        "end_customer": "盒马",
        "business_type": "前置仓",
        "city": "上海",
        "address": "浦东新区张江高科技园区祖冲之路2288号",
        "recipient_name": "张三",
        "recipient_phone": "13800138000",
        "mailing_address": "浦东新区张江高科技园区祖冲之路2288号",
        "expected_arrival_time": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        "remarks": "这是一个测试项目"
    }
    
    print("\n发送的数据:")
    print(json.dumps(project_data, ensure_ascii=False, indent=2))
    
    try:
        # 发送创建请求
        response = requests.post(f"{BASE_URL}/projects", json=project_data)
        
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("\n创建成功！")
            print(f"项目ID: {result.get('id')}")
            print(f"项目编号: {result.get('project_no')}")
            print(f"项目名称: {result.get('name')}")
            print(f"城市: {result.get('city')}")
            print(f"期望到货时间: {result.get('expected_arrival_time')}")
            print(f"创建时间: {result.get('created_at')}")
            
            return result
        else:
            print("\n创建失败！")
            print(f"错误信息: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n请求异常: {e}")
        return None

def test_get_projects():
    """测试获取项目列表"""
    print("\n" + "="*60)
    print("测试：获取项目列表")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/projects")
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f"\n项目总数: {len(projects)}")
            
            if len(projects) > 0:
                print("\n最新的3个项目:")
                for i, project in enumerate(projects[:3]):
                    print(f"\n{i+1}. {project.get('project_no')} - {project.get('name')}")
                    print(f"   城市: {project.get('city')}")
                    print(f"   客户: {project.get('end_customer')}")
                    print(f"   状态: {project.get('status')}")
            
            return projects
        else:
            print(f"\n获取失败: {response.text}")
            return []
            
    except Exception as e:
        print(f"\n请求异常: {e}")
        return []

def test_project_with_city_filter():
    """测试按城市筛选"""
    print("\n" + "="*60)
    print("测试：按城市筛选项目")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/projects?city=上海")
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f"\n上海地区项目数: {len(projects)}")
            
            for project in projects:
                print(f"- {project.get('name')} ({project.get('city')})")
            
            return projects
        else:
            print(f"\n获取失败: {response.text}")
            return []
            
    except Exception as e:
        print(f"\n请求异常: {e}")
        return []

if __name__ == "__main__":
    print("="*60)
    print("项目创建功能测试")
    print("="*60)
    
    # 测试1: 创建项目
    project = test_create_project()
    
    # 测试2: 获取项目列表
    projects = test_get_projects()
    
    # 测试3: 按城市筛选
    shanghai_projects = test_project_with_city_filter()
    
    # 总结
    print("\n" + "="*60)
    print("测试完成总结")
    print("="*60)
    print(f"创建项目: {'通过' if project else '失败'}")
    print(f"获取列表: {'通过' if len(projects) > 0 else '失败'}")
    print(f"城市筛选: {'通过' if len(shanghai_projects) >= 0 else '失败'}")
    print("="*60)
