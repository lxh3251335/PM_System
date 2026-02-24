"""
API功能测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_health():
    """测试健康检查"""
    print("\n===== 测试1: 健康检查 =====")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_projects():
    """测试获取项目列表"""
    print("\n===== 测试2: 获取项目列表 =====")
    try:
        response = requests.get(f"{BASE_URL}/projects")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"项目数量: {len(data) if isinstance(data, list) else 'N/A'}")
        print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_create_project():
    """测试创建项目"""
    print("\n===== 测试3: 创建项目 =====")
    try:
        project_data = {
            "name": "API测试项目",
            "end_customer": "盒马",
            "business_type": "前置仓",
            "city": "上海",
            "address": "浦东新区测试路123号",
            "recipient_name": "测试员",
            "recipient_phone": "13800138000",
            "expected_arrival_time": "2024-03-15",
            "status": "pending"
        }
        response = requests.post(f"{BASE_URL}/projects", json=project_data)
        print(f"状态码: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"创建成功！项目ID: {data.get('id')}")
            print(f"项目编号: {data.get('project_no')}")
            return data.get('id')
        else:
            print(f"❌ 创建失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_create_cold_room(project_id):
    """测试创建冷库"""
    print(f"\n===== 测试4: 创建冷库 (项目ID: {project_id}) =====")
    if not project_id:
        print("⚠️ 跳过测试：没有项目ID")
        return False
    
    try:
        cold_room_data = {
            "project_id": project_id,
            "name": "1号低温库",
            "room_type": "low_temp",
            "design_temp_min": -18.0,
            "design_temp_max": -15.0,
            "area": 50.0,
            "height": 3.0,
            "volume": 150.0,
            "refrigerant_type": "R404A"
        }
        response = requests.post(f"{BASE_URL}/projects/{project_id}/cold-rooms", json=cold_room_data)
        print(f"状态码: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"创建成功！冷库ID: {data.get('id')}")
            print(f"冷库名称: {data.get('name')}")
            return True
        else:
            print(f"❌ 创建失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_get_brands():
    """测试获取品牌列表"""
    print("\n===== 测试5: 获取设备品牌列表 =====")
    try:
        response = requests.get(f"{BASE_URL}/equipment-library/brands")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"品牌数量: {len(data) if isinstance(data, list) else 'N/A'}")
        if isinstance(data, list) and len(data) > 0:
            print(f"示例品牌: {data[0].get('name')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("开始API功能测试")
    print("="*50)
    
    results = []
    
    # 测试1: 健康检查
    results.append(("健康检查", test_health()))
    
    # 测试2: 获取项目列表
    results.append(("获取项目列表", test_get_projects()))
    
    # 测试3: 创建项目
    project_id = test_create_project()
    results.append(("创建项目", project_id is not None))
    
    # 测试4: 创建冷库
    results.append(("创建冷库", test_create_cold_room(project_id)))
    
    # 测试5: 获取品牌列表
    results.append(("获取品牌列表", test_get_brands()))
    
    # 总结
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n总计: {passed}/{total} 测试通过")
    print("="*50)
