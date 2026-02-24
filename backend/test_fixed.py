"""
测试修复后的API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

print("="*60)
print("测试修复后的API")
print("="*60)

# 测试1: 创建项目（带尾部斜杠）
print("\n测试1: POST /api/projects/ (带尾部斜杠)")
try:
    data = {
        "name": "修复测试项目",
        "end_customer": "盒马",
        "city": "北京",
        "expected_arrival_time": "2026-02-20"
    }
    response = requests.post(f"{BASE_URL}/projects/", json=data)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("成功！项目已创建")
        result = response.json()
        print(f"项目ID: {result.get('id')}")
        print(f"项目编号: {result.get('project_no')}")
        print(f"项目名称: {result.get('name')}")
    else:
        print(f"失败: {response.text}")
        
except Exception as e:
    print(f"错误: {e}")

# 测试2: 获取项目列表
print("\n测试2: GET /api/projects/ (带尾部斜杠)")
try:
    response = requests.get(f"{BASE_URL}/projects/")
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        projects = response.json()
        print(f"成功！共有 {len(projects)} 个项目")
        if len(projects) > 0:
            print(f"最新项目: {projects[0].get('name')}")
    else:
        print(f"失败: {response.text}")
        
except Exception as e:
    print(f"错误: {e}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
