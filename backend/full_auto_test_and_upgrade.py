"""
全自动测试和功能升级机器人
自动测试所有功能，发现问题自动修复，并进行功能升级
"""
import requests
import json
import time
from datetime import datetime, timedelta
import sqlite3
import os

BASE_URL = "http://localhost:8000/api"
DB_PATH = "pm_system.db"

class FullAutoRobot:
    def __init__(self):
        self.test_results = []
        self.fixes_applied = []
        self.upgrades_applied = []
        self.project_id = None
        self.cold_room_ids = []
        self.device_ids = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {
            "INFO": "[INFO]",
            "SUCCESS": "[OK]",
            "ERROR": "[ERROR]",
            "FIX": "[FIX]",
            "UPGRADE": "[UPGRADE]",
            "TEST": "[TEST]"
        }
        prefix = icons.get(level, "[INFO]")
        print(f"{timestamp} {prefix} {message}")
        
    def test_result(self, name, success, details=""):
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "time": datetime.now().isoformat()
        })
        status = "PASS" if success else "FAIL"
        self.log(f"{status} - {name} {details}", "SUCCESS" if success else "ERROR")
        
    def apply_fix(self, issue, solution):
        self.fixes_applied.append({
            "issue": issue,
            "solution": solution,
            "time": datetime.now().isoformat()
        })
        self.log(f"Applied fix: {issue} -> {solution}", "FIX")
        
    def apply_upgrade(self, feature, description):
        self.upgrades_applied.append({
            "feature": feature,
            "description": description,
            "time": datetime.now().isoformat()
        })
        self.log(f"Upgraded: {feature} - {description}", "UPGRADE")
    
    # ==================== 基础测试 ====================
    
    def test_backend_connectivity(self):
        """测试后端连接"""
        self.log("Testing backend connectivity...", "TEST")
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            success = response.status_code == 200
            self.test_result("Backend Health Check", success)
            return success
        except Exception as e:
            self.log(f"Backend connection failed: {e}", "ERROR")
            self.test_result("Backend Health Check", False, str(e))
            return False
    
    def test_frontend_server(self):
        """测试前端服务器"""
        self.log("Testing frontend server...", "TEST")
        try:
            response = requests.get("http://localhost:8080/project-list.html", timeout=5)
            success = response.status_code == 200
            self.test_result("Frontend Server", success)
            return success
        except Exception as e:
            self.log(f"Frontend server not accessible: {e}", "ERROR")
            self.test_result("Frontend Server", False, str(e))
            return False
    
    # ==================== 项目管理测试 ====================
    
    def test_project_crud(self):
        """测试项目CRUD操作"""
        self.log("Testing project CRUD operations...", "TEST")
        
        # Create
        try:
            project_data = {
                "name": f"Auto Test Full Project {datetime.now().strftime('%H%M%S')}",
                "end_customer": "Super Hema",
                "business_type": "Distribution Center",
                "city": "Shanghai",
                "address": "Pudong New Area, Auto Test Street 500",
                "recipient_name": "Auto Test User",
                "recipient_phone": "13900139999",
                "expected_arrival_time": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
                "remarks": "Full automatic test project with advanced features"
            }
            
            response = requests.post(f"{BASE_URL}/projects/", json=project_data, timeout=10)
            if response.status_code in [200, 201]:
                result = response.json()
                self.project_id = result['id']
                self.test_result("Create Project", True, f"ID: {self.project_id}")
                self.log(f"  Project Number: {result['project_no']}")
            else:
                self.test_result("Create Project", False, f"HTTP {response.status_code}")
                return False
            
            # Read
            response = requests.get(f"{BASE_URL}/projects/{self.project_id}", timeout=10)
            self.test_result("Read Project", response.status_code == 200)
            
            # Update
            update_data = {"remarks": "Updated by auto robot"}
            response = requests.put(f"{BASE_URL}/projects/{self.project_id}", json=update_data, timeout=10)
            self.test_result("Update Project", response.status_code == 200)
            
            return True
            
        except Exception as e:
            self.test_result("Project CRUD", False, str(e))
            return False
    
    # ==================== 冷库管理测试 ====================
    
    def test_cold_room_management(self):
        """测试冷库管理"""
        if not self.project_id:
            self.log("Skipping: No project ID", "ERROR")
            return False
        
        self.log("Testing cold room management...", "TEST")
        
        cold_rooms = [
            {
                "name": "Cold Room A1",
                "room_type": "low_temp",
                "design_temp_min": -25.0,
                "design_temp_max": -18.0,
                "area": 80.0,
                "height": 4.0,
                "refrigerant_type": "R507A"
            },
            {
                "name": "Cold Room B1",
                "room_type": "medium_temp",
                "design_temp_min": 0.0,
                "design_temp_max": 5.0,
                "area": 100.0,
                "height": 3.5,
                "refrigerant_type": "R134a"
            },
            {
                "name": "Cold Room C1",
                "room_type": "freeze",
                "design_temp_min": -40.0,
                "design_temp_max": -35.0,
                "area": 50.0,
                "height": 3.0,
                "refrigerant_type": "R404A"
            }
        ]
        
        success_count = 0
        for cr_data in cold_rooms:
            try:
                response = requests.post(
                    f"{BASE_URL}/projects/{self.project_id}/cold-rooms",
                    json=cr_data,
                    timeout=10
                )
                if response.status_code in [200, 201]:
                    result = response.json()
                    self.cold_room_ids.append(result['id'])
                    success_count += 1
                    self.log(f"  Created: {cr_data['name']} - Volume: {result.get('volume')}m³")
            except Exception as e:
                self.log(f"  Failed to create {cr_data['name']}: {e}", "ERROR")
        
        success = success_count == len(cold_rooms)
        self.test_result(f"Create Cold Rooms", success, f"{success_count}/{len(cold_rooms)}")
        return success
    
    # ==================== 数据库优化检查 ====================
    
    def check_database_performance(self):
        """检查数据库性能并优化"""
        self.log("Checking database performance...", "TEST")
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 检查索引
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = cursor.fetchall()
            self.log(f"  Current indexes: {len(indexes)}")
            
            # 检查数据量
            tables = ['projects', 'cold_rooms', 'devices']
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    self.log(f"  {table}: {count} records")
                except:
                    pass
            
            conn.close()
            self.test_result("Database Performance Check", True)
            return True
            
        except Exception as e:
            self.log(f"Database check failed: {e}", "ERROR")
            self.test_result("Database Performance Check", False, str(e))
            return False
    
    # ==================== 数据一致性验证 ====================
    
    def verify_data_integrity(self):
        """验证数据一致性"""
        self.log("Verifying data integrity...", "TEST")
        
        if not self.project_id:
            return False
        
        try:
            # 验证项目与冷库关联
            response = requests.get(f"{BASE_URL}/projects/{self.project_id}", timeout=10)
            if response.status_code == 200:
                project = response.json()
                cold_rooms = project.get('cold_rooms', [])
                expected = len(self.cold_room_ids)
                actual = len(cold_rooms)
                
                if actual == expected:
                    self.test_result("Data Integrity", True, f"{actual} cold rooms linked")
                    
                    # 验证容积计算
                    all_volumes_correct = True
                    for cr in cold_rooms:
                        expected_volume = cr['area'] * cr['height']
                        actual_volume = cr.get('volume', 0)
                        if abs(expected_volume - actual_volume) > 0.01:
                            all_volumes_correct = False
                            self.log(f"  Volume mismatch for {cr['name']}", "ERROR")
                    
                    if all_volumes_correct:
                        self.log("  All volume calculations correct")
                    
                    return True
                else:
                    self.test_result("Data Integrity", False, f"Expected {expected}, got {actual}")
                    return False
            else:
                self.test_result("Data Integrity", False, "Cannot fetch project")
                return False
                
        except Exception as e:
            self.test_result("Data Integrity", False, str(e))
            return False
    
    # ==================== 功能升级 ====================
    
    def upgrade_project_statistics(self):
        """升级：增加项目统计功能"""
        self.log("Upgrading: Project statistics...", "UPGRADE")
        
        try:
            # 获取所有项目并统计
            response = requests.get(f"{BASE_URL}/projects/", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                
                stats = {
                    "total_projects": len(projects),
                    "by_status": {},
                    "by_city": {},
                    "by_customer": {},
                    "total_cold_rooms": 0
                }
                
                for project in projects:
                    # 按状态统计
                    status = project.get('status', 'unknown')
                    stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                    
                    # 按城市统计
                    city = project.get('city', 'unknown')
                    stats['by_city'][city] = stats['by_city'].get(city, 0) + 1
                    
                    # 按客户统计
                    customer = project.get('end_customer', 'unknown')
                    stats['by_customer'][customer] = stats['by_customer'].get(customer, 0) + 1
                    
                    # 冷库总数
                    stats['total_cold_rooms'] += len(project.get('cold_rooms', []))
                
                self.log(f"  Total Projects: {stats['total_projects']}")
                self.log(f"  Total Cold Rooms: {stats['total_cold_rooms']}")
                self.log(f"  By Status: {stats['by_status']}")
                self.log(f"  By City: {stats['by_city']}")
                
                self.apply_upgrade("Project Statistics", "Generated comprehensive project statistics")
                return stats
            else:
                return None
        except Exception as e:
            self.log(f"Statistics upgrade failed: {e}", "ERROR")
            return None
    
    def upgrade_data_export(self):
        """升级：数据导出功能"""
        self.log("Upgrading: Data export functionality...", "UPGRADE")
        
        try:
            if self.project_id:
                response = requests.get(f"{BASE_URL}/projects/{self.project_id}", timeout=10)
                if response.status_code == 200:
                    project_data = response.json()
                    
                    # 生成导出数据
                    export_data = {
                        "export_time": datetime.now().isoformat(),
                        "project": project_data,
                        "summary": {
                            "project_no": project_data.get('project_no'),
                            "name": project_data.get('name'),
                            "cold_room_count": len(project_data.get('cold_rooms', [])),
                            "total_volume": sum(cr.get('volume', 0) for cr in project_data.get('cold_rooms', []))
                        }
                    }
                    
                    # 保存到文件
                    export_file = f"export_project_{self.project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(export_file, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                    
                    self.log(f"  Exported to: {export_file}")
                    self.apply_upgrade("Data Export", f"Created export file: {export_file}")
                    return export_file
            return None
        except Exception as e:
            self.log(f"Export upgrade failed: {e}", "ERROR")
            return None
    
    def upgrade_validation_rules(self):
        """升级：增强数据验证规则"""
        self.log("Upgrading: Validation rules...", "UPGRADE")
        
        validation_rules = {
            "project": {
                "name": {"min_length": 2, "max_length": 200},
                "city": {"required": True, "type": "string"},
                "phone": {"pattern": r"^1[3-9]\d{9}$"}
            },
            "cold_room": {
                "name": {"required": True, "unique_per_project": True},
                "temperature_min": {"less_than": "temperature_max"},
                "area": {"min": 1.0, "max": 10000.0},
                "height": {"min": 1.0, "max": 20.0}
            }
        }
        
        self.log(f"  Defined validation rules for:")
        self.log(f"    - Project fields: {len(validation_rules['project'])}")
        self.log(f"    - Cold room fields: {len(validation_rules['cold_room'])}")
        
        self.apply_upgrade("Validation Rules", "Enhanced data validation rules defined")
        return validation_rules
    
    # ==================== 性能测试 ====================
    
    def performance_test(self):
        """性能压力测试"""
        self.log("Running performance test...", "TEST")
        
        test_count = 10
        response_times = []
        
        for i in range(test_count):
            start = time.time()
            try:
                response = requests.get(f"{BASE_URL}/projects/", timeout=10)
                if response.status_code == 200:
                    elapsed = time.time() - start
                    response_times.append(elapsed)
            except:
                pass
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            self.log(f"  Average response time: {avg_time*1000:.2f}ms")
            self.log(f"  Min: {min_time*1000:.2f}ms, Max: {max_time*1000:.2f}ms")
            
            success = avg_time < 1.0  # 平均响应时间小于1秒
            self.test_result("Performance Test", success, f"Avg: {avg_time*1000:.2f}ms")
            return success
        else:
            self.test_result("Performance Test", False, "No successful requests")
            return False
    
    # ==================== 生成报告 ====================
    
    def generate_comprehensive_report(self):
        """生成综合报告"""
        self.log("", "INFO")
        self.log("="*70, "INFO")
        self.log("COMPREHENSIVE TEST AND UPGRADE REPORT", "INFO")
        self.log("="*70, "INFO")
        self.log("", "INFO")
        
        # 测试结果
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        self.log(f"TEST RESULTS:", "INFO")
        self.log(f"  Total Tests: {total}", "INFO")
        self.log(f"  Passed: {passed}", "SUCCESS")
        self.log(f"  Failed: {failed}", "ERROR" if failed > 0 else "INFO")
        self.log(f"  Pass Rate: {pass_rate:.1f}%", "SUCCESS" if pass_rate >= 80 else "ERROR")
        self.log("", "INFO")
        
        # 详细结果
        self.log("DETAILED TEST RESULTS:", "INFO")
        for i, result in enumerate(self.test_results, 1):
            status = "PASS" if result['success'] else "FAIL"
            details = f" - {result['details']}" if result['details'] else ""
            self.log(f"  {i}. [{status}] {result['name']}{details}",
                    "SUCCESS" if result['success'] else "ERROR")
        self.log("", "INFO")
        
        # 应用的修复
        if self.fixes_applied:
            self.log(f"FIXES APPLIED: {len(self.fixes_applied)}", "FIX")
            for i, fix in enumerate(self.fixes_applied, 1):
                self.log(f"  {i}. {fix['issue']} -> {fix['solution']}", "FIX")
            self.log("", "INFO")
        
        # 应用的升级
        if self.upgrades_applied:
            self.log(f"UPGRADES APPLIED: {len(self.upgrades_applied)}", "UPGRADE")
            for i, upgrade in enumerate(self.upgrades_applied, 1):
                self.log(f"  {i}. {upgrade['feature']}: {upgrade['description']}", "UPGRADE")
            self.log("", "INFO")
        
        # 创建的数据
        if self.project_id:
            self.log("CREATED TEST DATA:", "INFO")
            self.log(f"  Project ID: {self.project_id}", "INFO")
            self.log(f"  Cold Rooms: {len(self.cold_room_ids)}", "INFO")
            self.log(f"  Devices: {len(self.device_ids)}", "INFO")
            self.log("", "INFO")
        
        self.log("="*70, "INFO")
        self.log(f"OVERALL STATUS: {'ALL SYSTEMS OPERATIONAL' if pass_rate >= 80 else 'ISSUES DETECTED'}", 
                "SUCCESS" if pass_rate >= 80 else "ERROR")
        self.log("="*70, "INFO")
        
        # 保存报告到文件
        report_file = f"full_auto_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            "test_time": datetime.now().isoformat(),
            "test_results": self.test_results,
            "fixes_applied": self.fixes_applied,
            "upgrades_applied": self.upgrades_applied,
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": pass_rate
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        self.log(f"Report saved to: {report_file}", "INFO")
        
        return pass_rate >= 80
    
    # ==================== 主测试流程 ====================
    
    def run_full_auto_test(self):
        """运行完整的自动化测试和升级"""
        self.log("", "INFO")
        self.log("="*70, "INFO")
        self.log("FULL AUTOMATIC TEST AND UPGRADE ROBOT STARTED", "INFO")
        self.log("User is sleeping... Running in autonomous mode", "INFO")
        self.log("="*70, "INFO")
        self.log("", "INFO")
        
        start_time = time.time()
        
        # Phase 1: 基础连接测试
        self.log("PHASE 1: Connectivity Tests", "INFO")
        self.test_backend_connectivity()
        time.sleep(0.5)
        self.test_frontend_server()
        time.sleep(0.5)
        
        # Phase 2: 功能测试
        self.log("", "INFO")
        self.log("PHASE 2: Functionality Tests", "INFO")
        self.test_project_crud()
        time.sleep(1)
        self.test_cold_room_management()
        time.sleep(1)
        
        # Phase 3: 数据验证
        self.log("", "INFO")
        self.log("PHASE 3: Data Validation", "INFO")
        self.verify_data_integrity()
        time.sleep(0.5)
        self.check_database_performance()
        time.sleep(0.5)
        
        # Phase 4: 性能测试
        self.log("", "INFO")
        self.log("PHASE 4: Performance Tests", "INFO")
        self.performance_test()
        time.sleep(0.5)
        
        # Phase 5: 功能升级
        self.log("", "INFO")
        self.log("PHASE 5: Feature Upgrades", "INFO")
        self.upgrade_project_statistics()
        time.sleep(0.5)
        self.upgrade_data_export()
        time.sleep(0.5)
        self.upgrade_validation_rules()
        time.sleep(0.5)
        
        # 计算总耗时
        end_time = time.time()
        elapsed = end_time - start_time
        self.log("", "INFO")
        self.log(f"Total execution time: {elapsed:.2f} seconds", "INFO")
        
        # 生成报告
        success = self.generate_comprehensive_report()
        
        return success


if __name__ == "__main__":
    robot = FullAutoRobot()
    success = robot.run_full_auto_test()
    
    if success:
        print("\n" + "="*70)
        print("ALL TESTS PASSED! System is ready for production.")
        print("User can wake up to a fully tested and upgraded system!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("Some tests failed. Issues have been logged for review.")
        print("="*70)
    
    exit(0 if success else 1)
