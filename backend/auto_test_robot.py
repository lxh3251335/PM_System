"""
智能虚拟测试机器人
自动测试所有已开发功能
"""
import requests
import json
import time
from datetime import datetime, timedelta
import sqlite3

BASE_URL = "http://localhost:8000/api"
DB_PATH = "pm_system.db"

class TestRobot:
    def __init__(self):
        self.test_results = []
        self.created_project_id = None
        self.created_cold_room_ids = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "[INFO]",
            "SUCCESS": "[SUCCESS]",
            "ERROR": "[ERROR]",
            "TEST": "[TEST]"
        }.get(level, "[INFO]")
        print(f"{timestamp} {prefix} {message}")
        
    def test_case(self, name, success):
        self.test_results.append({"name": name, "success": success})
        status = "PASS" if success else "FAIL"
        icon = "OK" if success else "X"
        self.log(f"{status} - {name}", "SUCCESS" if success else "ERROR")
        
    def test_backend_health(self):
        """测试1: 后端健康检查"""
        self.log("开始测试后端健康状态...", "TEST")
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            success = response.status_code == 200
            self.test_case("后端健康检查", success)
            if success:
                self.log(f"后端响应: {response.json()}")
            return success
        except Exception as e:
            self.log(f"后端连接失败: {e}", "ERROR")
            self.test_case("后端健康检查", False)
            return False
    
    def test_cors_headers(self):
        """测试2: CORS配置"""
        self.log("开始测试CORS配置...", "TEST")
        try:
            headers = {
                'Origin': 'null',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'content-type'
            }
            response = requests.options(f"{BASE_URL}/projects/", headers=headers, timeout=5)
            
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_methods = response.headers.get('Access-Control-Allow-Methods')
            
            success = (response.status_code == 200 and 
                      cors_origin is not None and
                      'POST' in (cors_methods or ''))
            
            self.test_case("CORS预检请求", success)
            if success:
                self.log(f"CORS Origin: {cors_origin}")
                self.log(f"CORS Methods: {cors_methods}")
            return success
        except Exception as e:
            self.log(f"CORS测试失败: {e}", "ERROR")
            self.test_case("CORS预检请求", False)
            return False
    
    def test_create_project(self):
        """测试3: 创建项目"""
        self.log("开始测试创建项目...", "TEST")
        try:
            project_data = {
                "name": f"机器人自动测试项目-{datetime.now().strftime('%H%M%S')}",
                "end_customer": "盒马",
                "business_type": "前置仓",
                "city": "北京",
                "address": "朝阳区机器人测试大街100号",
                "recipient_name": "测试机器人",
                "recipient_phone": "13800138000",
                "mailing_address": "朝阳区机器人测试大街100号",
                "expected_arrival_time": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "remarks": "这是机器人自动创建的测试项目"
            }
            
            self.log("发送创建项目请求...")
            response = requests.post(f"{BASE_URL}/projects/", json=project_data, timeout=10)
            
            if response.status_code in [200, 201]:
                result = response.json()
                self.created_project_id = result.get('id')
                project_no = result.get('project_no')
                
                self.test_case("创建项目", True)
                self.log(f"项目创建成功！")
                self.log(f"  项目ID: {self.created_project_id}")
                self.log(f"  项目编号: {project_no}")
                self.log(f"  项目名称: {result.get('name')}")
                return True
            else:
                self.log(f"创建失败: HTTP {response.status_code}", "ERROR")
                self.log(f"响应: {response.text}", "ERROR")
                self.test_case("创建项目", False)
                return False
                
        except Exception as e:
            self.log(f"创建项目异常: {e}", "ERROR")
            self.test_case("创建项目", False)
            return False
    
    def test_get_projects(self):
        """测试4: 获取项目列表"""
        self.log("开始测试获取项目列表...", "TEST")
        try:
            response = requests.get(f"{BASE_URL}/projects/", timeout=10)
            
            if response.status_code == 200:
                projects = response.json()
                self.test_case("获取项目列表", True)
                self.log(f"成功获取项目列表，共 {len(projects)} 个项目")
                
                if len(projects) > 0:
                    latest = projects[0]
                    self.log(f"  最新项目: {latest.get('name')}")
                    self.log(f"  城市: {latest.get('city')}")
                    self.log(f"  状态: {latest.get('status')}")
                return True
            else:
                self.log(f"获取失败: HTTP {response.status_code}", "ERROR")
                self.test_case("获取项目列表", False)
                return False
                
        except Exception as e:
            self.log(f"获取项目列表异常: {e}", "ERROR")
            self.test_case("获取项目列表", False)
            return False
    
    def test_get_project_detail(self):
        """测试5: 获取项目详情"""
        if not self.created_project_id:
            self.log("跳过：没有可用的项目ID", "ERROR")
            self.test_case("获取项目详情", False)
            return False
            
        self.log(f"开始测试获取项目详情 (ID: {self.created_project_id})...", "TEST")
        try:
            response = requests.get(f"{BASE_URL}/projects/{self.created_project_id}", timeout=10)
            
            if response.status_code == 200:
                project = response.json()
                self.test_case("获取项目详情", True)
                self.log(f"成功获取项目详情:")
                self.log(f"  项目名称: {project.get('name')}")
                self.log(f"  最终用户: {project.get('end_customer')}")
                self.log(f"  城市: {project.get('city')}")
                self.log(f"  冷库数量: {len(project.get('cold_rooms', []))}")
                return True
            else:
                self.log(f"获取失败: HTTP {response.status_code}", "ERROR")
                self.test_case("获取项目详情", False)
                return False
                
        except Exception as e:
            self.log(f"获取项目详情异常: {e}", "ERROR")
            self.test_case("获取项目详情", False)
            return False
    
    def test_create_cold_room(self):
        """测试6: 创建冷库"""
        if not self.created_project_id:
            self.log("跳过：没有可用的项目ID", "ERROR")
            self.test_case("创建冷库", False)
            return False
            
        self.log(f"开始测试创建冷库 (项目ID: {self.created_project_id})...", "TEST")
        
        cold_rooms = [
            {
                "name": "1号低温库",
                "room_type": "low_temp",
                "design_temp_min": -18.0,
                "design_temp_max": -15.0,
                "area": 50.0,
                "height": 3.0,
                "refrigerant_type": "R404A"
            },
            {
                "name": "2号中温库",
                "room_type": "medium_temp",
                "design_temp_min": 2.0,
                "design_temp_max": 8.0,
                "area": 60.0,
                "height": 3.5,
                "refrigerant_type": "R410A"
            }
        ]
        
        success_count = 0
        for cold_room_data in cold_rooms:
            try:
                self.log(f"创建冷库: {cold_room_data['name']}...")
                response = requests.post(
                    f"{BASE_URL}/projects/{self.created_project_id}/cold-rooms",
                    json=cold_room_data,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    cold_room_id = result.get('id')
                    self.created_cold_room_ids.append(cold_room_id)
                    success_count += 1
                    self.log(f"  冷库创建成功！ID: {cold_room_id}")
                    self.log(f"  容积: {result.get('volume')}m³")
                else:
                    self.log(f"  创建失败: HTTP {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"  创建异常: {e}", "ERROR")
        
        success = success_count == len(cold_rooms)
        self.test_case(f"创建冷库 ({success_count}/{len(cold_rooms)})", success)
        return success
    
    def test_get_cold_rooms(self):
        """测试7: 获取冷库列表"""
        if not self.created_project_id:
            self.log("跳过：没有可用的项目ID", "ERROR")
            self.test_case("获取冷库列表", False)
            return False
            
        self.log(f"开始测试获取冷库列表 (项目ID: {self.created_project_id})...", "TEST")
        try:
            response = requests.get(
                f"{BASE_URL}/projects/{self.created_project_id}/cold-rooms",
                timeout=10
            )
            
            if response.status_code == 200:
                cold_rooms = response.json()
                self.test_case("获取冷库列表", True)
                self.log(f"成功获取冷库列表，共 {len(cold_rooms)} 个冷库")
                
                for cr in cold_rooms:
                    self.log(f"  - {cr.get('name')}: {cr.get('design_temp_min')}℃~{cr.get('design_temp_max')}℃")
                return True
            else:
                self.log(f"获取失败: HTTP {response.status_code}", "ERROR")
                self.test_case("获取冷库列表", False)
                return False
                
        except Exception as e:
            self.log(f"获取冷库列表异常: {e}", "ERROR")
            self.test_case("获取冷库列表", False)
            return False
    
    def test_filter_projects(self):
        """测试8: 项目筛选"""
        self.log("开始测试项目筛选功能...", "TEST")
        
        filters = [
            ("按城市筛选", {"city": "北京"}),
            ("按最终用户筛选", {"end_customer": "盒马"}),
            ("按业务类型筛选", {"business_type": "前置仓"})
        ]
        
        success_count = 0
        for filter_name, params in filters:
            try:
                self.log(f"测试: {filter_name} - {params}")
                response = requests.get(f"{BASE_URL}/projects/", params=params, timeout=10)
                
                if response.status_code == 200:
                    projects = response.json()
                    success_count += 1
                    self.log(f"  筛选成功，找到 {len(projects)} 个项目")
                else:
                    self.log(f"  筛选失败: HTTP {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"  筛选异常: {e}", "ERROR")
        
        success = success_count == len(filters)
        self.test_case(f"项目筛选 ({success_count}/{len(filters)})", success)
        return success
    
    def test_database_integrity(self):
        """测试9: 数据库完整性"""
        self.log("开始测试数据库完整性...", "TEST")
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 检查项目表
            cursor.execute("SELECT COUNT(*) FROM projects")
            project_count = cursor.fetchone()[0]
            self.log(f"数据库中共有 {project_count} 个项目")
            
            # 检查冷库表
            cursor.execute("SELECT COUNT(*) FROM cold_rooms")
            cold_room_count = cursor.fetchone()[0]
            self.log(f"数据库中共有 {cold_room_count} 个冷库")
            
            # 检查最新创建的项目
            if self.created_project_id:
                cursor.execute(
                    "SELECT name, city, status FROM projects WHERE id = ?",
                    (self.created_project_id,)
                )
                result = cursor.fetchone()
                if result:
                    self.log(f"验证项目数据:")
                    self.log(f"  名称: {result[0]}")
                    self.log(f"  城市: {result[1]}")
                    self.log(f"  状态: {result[2]}")
            
            conn.close()
            self.test_case("数据库完整性检查", True)
            return True
            
        except Exception as e:
            self.log(f"数据库检查异常: {e}", "ERROR")
            self.test_case("数据库完整性检查", False)
            return False
    
    def test_equipment_library(self):
        """测试10: 设备库查询"""
        self.log("开始测试设备库查询...", "TEST")
        try:
            response = requests.get(f"{BASE_URL}/equipment-library/brands", timeout=10)
            
            if response.status_code == 200:
                brands = response.json()
                self.test_case("获取设备品牌列表", True)
                self.log(f"成功获取设备品牌列表，共 {len(brands)} 个品牌")
                
                if len(brands) > 0:
                    sample_brand = brands[0]
                    self.log(f"  示例品牌: {sample_brand.get('name')}")
                    
                    # 测试获取型号
                    brand_id = sample_brand.get('id')
                    model_response = requests.get(
                        f"{BASE_URL}/equipment-library/models",
                        params={"brand_id": brand_id},
                        timeout=10
                    )
                    
                    if model_response.status_code == 200:
                        models = model_response.json()
                        self.log(f"  该品牌下有 {len(models)} 个型号")
                
                return True
            else:
                self.log(f"获取失败: HTTP {response.status_code}", "ERROR")
                self.test_case("获取设备品牌列表", False)
                return False
                
        except Exception as e:
            self.log(f"设备库查询异常: {e}", "ERROR")
            self.test_case("获取设备品牌列表", False)
            return False
    
    def generate_report(self):
        """生成测试报告"""
        self.log("", "INFO")
        self.log("="*60, "INFO")
        self.log("测试报告", "INFO")
        self.log("="*60, "INFO")
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        self.log(f"测试总数: {total}", "INFO")
        self.log(f"通过: {passed}", "SUCCESS")
        self.log(f"失败: {failed}", "ERROR" if failed > 0 else "INFO")
        self.log(f"通过率: {pass_rate:.1f}%", "SUCCESS" if pass_rate >= 80 else "ERROR")
        self.log("", "INFO")
        
        self.log("详细结果:", "INFO")
        for i, result in enumerate(self.test_results, 1):
            status = "PASS" if result['success'] else "FAIL"
            self.log(f"  {i}. [{status}] {result['name']}", 
                    "SUCCESS" if result['success'] else "ERROR")
        
        self.log("="*60, "INFO")
        
        if self.created_project_id:
            self.log("", "INFO")
            self.log("测试数据信息:", "INFO")
            self.log(f"  创建的项目ID: {self.created_project_id}", "INFO")
            self.log(f"  创建的冷库数量: {len(self.created_cold_room_ids)}", "INFO")
            self.log("="*60, "INFO")
        
        return pass_rate >= 80
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("", "INFO")
        self.log("="*60, "INFO")
        self.log("智能虚拟测试机器人启动", "INFO")
        self.log("="*60, "INFO")
        self.log("", "INFO")
        
        start_time = time.time()
        
        # 执行所有测试
        self.test_backend_health()
        time.sleep(0.5)
        
        self.test_cors_headers()
        time.sleep(0.5)
        
        self.test_equipment_library()
        time.sleep(0.5)
        
        self.test_get_projects()
        time.sleep(0.5)
        
        self.test_create_project()
        time.sleep(1)
        
        self.test_get_project_detail()
        time.sleep(0.5)
        
        self.test_create_cold_room()
        time.sleep(1)
        
        self.test_get_cold_rooms()
        time.sleep(0.5)
        
        self.test_filter_projects()
        time.sleep(0.5)
        
        self.test_database_integrity()
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        self.log("", "INFO")
        self.log(f"测试耗时: {elapsed:.2f} 秒", "INFO")
        
        # 生成报告
        success = self.generate_report()
        
        return success


if __name__ == "__main__":
    robot = TestRobot()
    success = robot.run_all_tests()
    
    exit(0 if success else 1)
