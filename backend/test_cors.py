"""
测试CORS和路径重定向问题
"""
import requests

BASE_URL = "http://localhost:8000"

print("="*60)
print("测试CORS和路径问题")
print("="*60)

# 测试1: 不带尾部斜杠的POST请求
print("\n测试1: POST /api/projects (不带尾部斜杠)")
try:
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'null'  # 模拟file://协议
    }
    data = {
        "name": "CORS测试项目",
        "city": "北京",
        "expected_arrival_time": "2026-02-15"
    }
    response = requests.post(f"{BASE_URL}/api/projects", json=data, headers=headers, allow_redirects=False)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 307:
        print("❌ 仍然有重定向问题！")
        print(f"重定向到: {response.headers.get('Location')}")
    elif response.status_code in [200, 201]:
        print("✅ 成功！无重定向，直接创建")
        result = response.json()
        print(f"项目ID: {result.get('id')}")
        print(f"项目编号: {result.get('project_no')}")
    else:
        print(f"响应: {response.text}")
        
except Exception as e:
    print(f"错误: {e}")

# 测试2: OPTIONS预检请求
print("\n测试2: OPTIONS /api/projects (CORS预检)")
try:
    headers = {
        'Origin': 'null',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type'
    }
    response = requests.options(f"{BASE_URL}/api/projects", headers=headers)
    
    print(f"状态码: {response.status_code}")
    print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
    print(f"Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods')}")
    
    if response.status_code == 200 and response.headers.get('Access-Control-Allow-Origin'):
        print("✅ CORS预检通过！")
    else:
        print("❌ CORS预检失败！")
        
except Exception as e:
    print(f"错误: {e}")

print("\n" + "="*60)
