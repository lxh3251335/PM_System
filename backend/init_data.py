"""
数据库初始化脚本 - 创建初始数据
"""
import sys
from app.database import SessionLocal, engine, Base
from app.models import User, EquipmentBrand, EquipmentModel
from passlib.context import CryptContext

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_database():
    """初始化数据库"""
    print("========================================")
    print("初始化数据库...")
    print("========================================")
    
    # 创建所有表
    print("\n1. 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")
    
    db = SessionLocal()
    
    try:
        # 创建初始用户
        print("\n2. 创建初始用户...")
        
        # 检查是否已存在用户
        existing_user = db.query(User).first()
        if existing_user:
            print("⚠️  用户已存在，跳过创建")
        else:
            # 用户方
            user1 = User(
                username="user",
                password_hash=pwd_context.hash("user123"),
                role="user"
            )
            db.add(user1)
            
            # 厂家方
            user2 = User(
                username="factory",
                password_hash=pwd_context.hash("factory123"),
                role="factory"
            )
            db.add(user2)
            
            db.commit()
            print("✅ 创建用户成功:")
            print("   - 用户名: user, 密码: user123 (用户方)")
            print("   - 用户名: factory, 密码: factory123 (厂家方)")
        
        # 创建示例品牌数据
        print("\n3. 创建示例品牌数据...")
        
        existing_brand = db.query(EquipmentBrand).first()
        if existing_brand:
            print("⚠️  品牌数据已存在，跳过创建")
        else:
            brands_data = [
                # 温控器品牌
                {"name": "精创", "equipment_type": "thermostat", "description": "专业温控器品牌"},
                {"name": "小精灵", "equipment_type": "thermostat", "description": "智能温控解决方案"},
                {"name": "卡乐", "equipment_type": "thermostat", "description": "Carel温控器"},
                
                # 冷风机品牌
                {"name": "格力", "equipment_type": "air_cooler", "description": "格力冷风机"},
                {"name": "美的", "equipment_type": "air_cooler", "description": "美的冷风机"},
                
                # 机组品牌
                {"name": "比泽尔", "equipment_type": "unit", "description": "Bitzer压缩机组"},
                {"name": "谷轮", "equipment_type": "unit", "description": "Copeland压缩机组"},
                
                # 电表品牌
                {"name": "正泰", "equipment_type": "meter", "description": "正泰电表"},
                {"name": "德力西", "equipment_type": "meter", "description": "德力西电表"},
            ]
            
            for brand_data in brands_data:
                brand = EquipmentBrand(**brand_data, created_by=1)
                db.add(brand)
            
            db.commit()
            print(f"✅ 创建 {len(brands_data)} 个品牌")
        
        # 创建示例型号数据
        print("\n4. 创建示例型号数据...")
        
        existing_model = db.query(EquipmentModel).first()
        if existing_model:
            print("⚠️  型号数据已存在，跳过创建")
        else:
            models_data = [
                # 温控器型号
                {
                    "brand_id": 1, "model_name": "STC-200+", "equipment_type": "thermostat",
                    "comm_port_type": "RS485", "comm_protocol": "Modbus RTU",
                    "description": "精创温控器STC-200+"
                },
                {
                    "brand_id": 2, "model_name": "XJL-8000", "equipment_type": "thermostat",
                    "comm_port_type": "RS485", "comm_protocol": "Modbus RTU",
                    "description": "小精灵温控器XJL-8000"
                },
                
                # 冷风机型号
                {
                    "brand_id": 4, "model_name": "GL-CF-200", "equipment_type": "air_cooler",
                    "defrost_method": "electric", "has_intelligent_defrost": "yes",
                    "expansion_valve_type": "electronic",
                    "description": "格力冷风机GL-CF-200"
                },
                {
                    "brand_id": 5, "model_name": "MD-CF-150", "equipment_type": "air_cooler",
                    "defrost_method": "hot_gas", "has_intelligent_defrost": "no",
                    "expansion_valve_type": "thermal",
                    "description": "美的冷风机MD-CF-150"
                },
                
                # 机组型号
                {
                    "brand_id": 6, "model_name": "BZ-250", "equipment_type": "unit",
                    "comm_port_type": "RS485", "comm_protocol": "Modbus RTU",
                    "description": "比泽尔机组BZ-250"
                },
            ]
            
            for model_data in models_data:
                model = EquipmentModel(**model_data, created_by=1)
                db.add(model)
            
            db.commit()
            print(f"✅ 创建 {len(models_data)} 个型号")
        
        print("\n========================================")
        print("✅ 数据库初始化完成！")
        print("========================================")
        print("\n下一步:")
        print("1. 启动后端服务: python -m uvicorn app.main:app --reload")
        print("2. 访问API文档: http://localhost:8000/docs")
        print("3. 使用用户名密码登录测试")
        print("\n========================================")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
