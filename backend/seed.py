"""Seed database with admin user and sample products."""
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.product import Product
from app.services.auth_service import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Create admin if not exists
admin = db.query(User).filter(User.username == "admin").first()
if not admin:
    admin = User(
        username="admin",
        email="admin@market.com",
        password_hash=hash_password("admin123"),
        role=UserRole.ADMIN,
    )
    db.add(admin)
    print("Admin created: admin / admin123")

# Create test user if not exists
user = db.query(User).filter(User.username == "testuser").first()
if not user:
    user = User(
        username="testuser",
        email="test@market.com",
        password_hash=hash_password("test123"),
        role=UserRole.USER,
    )
    db.add(user)
    print("Test user created: testuser / test123")

# Create sample products if table is empty
if db.query(Product).count() == 0:
    products = [
        Product(name="机械键盘", description="RGB 背光青轴机械键盘，办公游戏两用", price=29900, stock=50, category="数码", image_url=""),
        Product(name="无线鼠标", description="人体工学静音无线鼠标，续航 3 个月", price=7900, stock=100, category="数码", image_url=""),
        Product(name="Type-C 数据线", description="100W 快充数据线 1.5 米，支持数据传输", price=1900, stock=200, category="数码", image_url=""),
        Product(name="显示器支架", description="双屏显示器支架，气压弹簧升降", price=19900, stock=30, category="办公", image_url=""),
        Product(name="笔记本散热架", description="铝合金笔记本支架，6 档高度调节", price=8900, stock=80, category="办公", image_url=""),
        Product(name="保温杯", description="316 不锈钢真空保温杯 500ml", price=5900, stock=60, category="生活", image_url=""),
        Product(name="台灯", description="LED 护眼台灯，无频闪三档色温", price=12900, stock=40, category="生活", image_url=""),
        Product(name="帆布袋", description="加厚纯棉帆布袋，文艺简约风格", price=2900, stock=150, category="生活", image_url=""),
    ]
    for p in products:
        db.add(p)
    print(f"{len(products)} sample products created")

db.commit()
db.close()
print("Seed complete.")
