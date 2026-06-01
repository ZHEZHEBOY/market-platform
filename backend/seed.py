# -*- coding: utf-8 -*-
"""Seed database: users, shops, categories, 500+ products, reviews, favorites, coupons."""
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole, Shop
from app.models.product import Product
from app.models.category import Category
from app.models.review import Review
from app.models.favorite import Favorite
from app.models.coupon import Coupon, UserCoupon, CouponType, CouponStatus
from app.models.notification import Notification  # 导入以注册模型
from app.services.auth_service import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ════════════════════════════════════════════════════════════
# 1. 用户
# ════════════════════════════════════════════════════════════
users_data = [
    ("admin", "admin@market.com", "admin123", UserRole.ADMIN),
    ("buyer", "buyer@market.com", "buyer123", UserRole.BUYER),
    ("buyer2", "buyer2@market.com", "buyer123", UserRole.BUYER),
    ("buyer3", "buyer3@market.com", "buyer123", UserRole.BUYER),
    ("buyer4", "buyer4@market.com", "buyer123", UserRole.BUYER),
    ("buyer5", "buyer5@market.com", "buyer123", UserRole.BUYER),
    ("testuser", "test@market.com", "test123", UserRole.BUYER),
    ("seller", "seller@market.com", "seller123", UserRole.SELLER),
    ("seller2", "seller2@market.com", "seller123", UserRole.SELLER),
    ("seller3", "seller3@market.com", "seller123", UserRole.SELLER),
    ("seller4", "seller4@market.com", "seller123", UserRole.SELLER),
    ("seller5", "seller5@market.com", "seller123", UserRole.SELLER),
]
user_map = {}
for uname, email, pwd, role in users_data:
    u = db.query(User).filter(User.username == uname).first()
    if not u:
        u = User(username=uname, email=email, password_hash=hash_password(pwd), role=role)
        db.add(u)
        db.flush()
        print(f"  User created: {uname} / {pwd}")
    user_map[uname] = u

# ════════════════════════════════════════════════════════════
# 2. 店铺
# ════════════════════════════════════════════════════════════
shops_data = [
    ("seller",  "优品数码旗舰店",   "专注数码好物，品质之选", "approved"),
    ("seller2", "居家生活馆",       "让家更有温度", "approved"),
    ("seller3", "运动户外专营店",   "专业运动装备，畅享户外", "approved"),
    ("seller4", "美妆个护旗舰店",   "正品美妆，美丽从这里开始", "approved"),
    ("seller5", "图书文创馆",       "知识海洋，文创精品", "approved"),
]
shop_map = {}
for owner_name, name, desc, status in shops_data:
    s = db.query(Shop).filter(Shop.name == name).first()
    if not s:
        s = Shop(owner_id=user_map[owner_name].id, name=name, description=desc, status=status)
        db.add(s)
        db.flush()
        print(f"  Shop created: {name}")
    shop_map[name] = s

# ════════════════════════════════════════════════════════════
# 3. 分类（二级树形，参考京东）
# ════════════════════════════════════════════════════════════
if db.query(Category).count() == 0:
    categories_tree = {
        "手机通讯":     ["手机", "游戏手机", "老人机", "对讲机"],
        "电脑办公":     ["笔记本", "台式机", "平板电脑", "显示器", "键盘鼠标"],
        "数码配件":     ["充电器", "数据线", "移动电源", "保护壳", "耳机", "音箱"],
        "智能设备":     ["智能手表", "智能手环", "智能家居", "VR眼镜"],
        "家用电器":     ["空调", "冰箱", "洗衣机", "电视", "吸尘器", "空气净化器"],
        "厨房电器":     ["微波炉", "电饭煲", "烤箱", "豆浆机", "空气炸锅"],
        "个护美妆":     ["洗面奶", "面膜", "防晒霜", "口红", "香水", "剃须刀"],
        "服饰鞋包":     ["男装", "女装", "运动鞋", "休闲鞋", "双肩包", "手提包"],
        "食品饮料":     ["零食", "坚果", "咖啡", "茶叶", "牛奶", "饮料"],
        "生鲜果蔬":     ["水果", "蔬菜", "肉禽蛋", "海鲜水产"],
        "运动户外":     ["瑜伽", "跑步", "骑行", "登山", "游泳", "球类"],
        "家居日用":     ["收纳", "清洁", "家纺", "灯具", "装饰"],
        "图书文具":     ["文学", "编程", "考试", "文具", "办公用品"],
        "母婴玩具":     ["奶粉", "纸尿裤", "玩具", "童装", "安全座椅"],
    }
    for parent_name, children in categories_tree.items():
        parent = Category(name=parent_name, sort_order=0)
        db.add(parent)
        db.flush()
        for i, child_name in enumerate(children, 1):
            db.add(Category(name=child_name, parent_id=parent.id, sort_order=i))
    print(f"  {len(categories_tree)} top categories + subcategories created")

# ════════════════════════════════════════════════════════════
# 4. 商品（200+，分店铺）
# ════════════════════════════════════════════════════════════
if db.query(Product).count() == 0:
    s1 = shop_map["优品数码旗舰店"].id
    s2 = shop_map["居家生活馆"].id
    s3 = shop_map["运动户外专营店"].id

    products = [
        # ── 优品数码旗舰店 (100+) ──
        # 手机通讯 (2026年最新款)
        Product(shop_id=s1, name="iPhone 17 Pro", description="A19 Pro芯片，钛金属设计，4800万像素，5倍光学变焦，8GB内存", price=899900, stock=20, category="手机通讯", image_url="/static/products/real_v2/iphone_16_pro.jpg"),
        Product(shop_id=s1, name="iPhone 17 Pro Max", description="A19 Pro芯片，6.9英寸，5倍光学变焦，钛金属，大电池", price=1099900, stock=15, category="手机通讯", image_url="/static/products/real_v2/iphone_16_pro_max.jpg"),
        Product(shop_id=s1, name="iPhone 17 Air", description="A19芯片，超薄设计，6.6英寸OLED，USB-C，轻薄旗舰", price=799900, stock=25, category="手机通讯", image_url="/static/products/real_v2/iphone_16.jpg"),
        Product(shop_id=s1, name="小米17 Ultra", description="骁龙8至尊版，徕卡光学镜头，2K AMOLED屏，5500mAh电池，120W快充", price=599900, stock=30, category="手机通讯", image_url="/static/products/real_v2/小米14_ultra.jpg"),
        Product(shop_id=s1, name="小米17 Pro", description="骁龙8至尊版，徕卡影像，5000mAh电池，100W快充", price=499900, stock=35, category="手机通讯", image_url="/static/products/real_v2/小米14.jpg"),
        Product(shop_id=s1, name="三星 Galaxy S26 Ultra", description="骁龙8至尊版，2亿像素AI相机，钛金属框架，S Pen", price=1099900, stock=15, category="手机通讯", image_url="/static/products/real_v2/三星_galaxy_s25_ultra.jpg"),
        Product(shop_id=s1, name="华为 Mate 80", description="麒麟芯片，鸿蒙系统，5000万像素超光谱摄像头", price=599900, stock=25, category="手机通讯", image_url="/static/products/real_v2/华为_mate_70.jpg"),
        Product(shop_id=s1, name="OPPO Find X9", description="天玑9400+，哈苏影像，5800mAh电池，IP69防水", price=449900, stock=35, category="手机通讯", image_url="/static/products/real_v2/oppo_find_x8.jpg"),
        Product(shop_id=s1, name="vivo X300 Pro", description="天玑9400+，蔡司影像，6000mAh蓝海电池，IP69防水", price=499900, stock=28, category="手机通讯", image_url="/static/products/real_v2/vivo_x200_pro.jpg"),
        Product(shop_id=s1, name="老人手机 大字体", description="超大字体大音量，超长待机30天，SOS紧急呼叫", price=29900, stock=100, category="手机通讯", image_url="/static/products/real_v2/老人手机_大字体.jpg"),

        # 电脑办公
        Product(shop_id=s1, name="MacBook Pro 14 M5", description="M5 Pro芯片，24GB统一内存，512GB SSD，Liquid Retina XDR屏", price=1599900, stock=10, category="电脑办公", image_url="/static/products/real_v2/macbook_pro_14_m4.jpg"),
        Product(shop_id=s1, name="联想 Legion Y9000P", description="i9-14900HX，RTX 4070，32GB DDR5，2.5K 240Hz屏", price=1099900, stock=15, category="电脑办公", image_url="/static/products/real_v2/联想_legion_y9000p.jpg"),
        Product(shop_id=s1, name="iPad Air M2", description="M2芯片，11英寸Liquid Retina，Wi-Fi 6E，支持Apple Pencil Pro", price=479900, stock=25, category="电脑办公", image_url="/static/products/real_v2/ipad_air_m2.jpg"),
        Product(shop_id=s1, name="戴尔 27寸 4K显示器", description="IPS面板，Type-C 90W供电，99% sRGB色域，旋转升降支架", price=329900, stock=20, category="电脑办公", image_url="/static/products/real_v2/戴尔_27寸_4k显示器.jpg"),
        Product(shop_id=s1, name="HHKB Professional HYBRID", description="静电容键盘，蓝牙+USB双模，60%布局，程序员神器", price=219900, stock=15, category="电脑办公", image_url="/static/products/real_v2/hhkb_professional_hybrid.jpg"),
        Product(shop_id=s1, name="罗技 MX Master 3S", description="电磁滚轮，8000DPI，Darkfield追踪，Flow跨设备控制", price=79900, stock=50, category="电脑办公", image_url="/static/products/real_v2/罗技_mx_master_3s.jpg"),
        Product(shop_id=s1, name="ThinkPad X1 Carbon", description="Ultra 7 155H，32GB，1TB SSD，2.8K OLED屏，1.08kg", price=1299900, stock=12, category="电脑办公", image_url="/static/products/real_v2/thinkpad_x1_carbon.jpg"),

        # 数码配件
        Product(shop_id=s1, name="Anker 140W氮化镓充电器", description="4口USB-C，支持MacBook Pro快充，可折叠插脚", price=39900, stock=80, category="数码配件", image_url="/static/products/real_v2/anker_140w氮化镓充电器.jpg"),
        Product(shop_id=s1, name="苹果 USB-C 转闪电", description="1米编织线，MFi认证，支持快充", price=14900, stock=200, category="数码配件", image_url="/static/products/real_v2/苹果_usb_c_转闪电.jpg"),
        Product(shop_id=s1, name="小米 20000mAh 充电宝", description="50W快充，可充笔记本，LED电量显示", price=19900, stock=60, category="数码配件", image_url="/static/products/real_v2/小米_20000mah_充电宝.jpg"),
        Product(shop_id=s1, name="AirPods Pro 3", description="H3芯片，自适应降噪，空间音频，USB-C充电盒", price=189900, stock=40, category="数码配件", image_url="/static/products/real_v2/airpods_pro_3.jpg"),
        Product(shop_id=s1, name="AirPods 4", description="H3芯片，主动降噪，空间音频，USB-C充电盒", price=139900, stock=50, category="数码配件", image_url="/static/products/real_v2/airpods_pro_3.jpg"),
        Product(shop_id=s1, name="索尼 WH-1000XM6", description="V2处理器，40小时续航，LDAC Hi-Res，30级降噪", price=249900, stock=25, category="数码配件", image_url="/static/products/real_v2/索尼_wh_1000xm6.jpg"),
        Product(shop_id=s1, name="JBL Charge 6", description="蓝牙5.3，IP67防水，20小时续航，可作充电宝", price=129900, stock=35, category="数码配件", image_url="/static/products/real/jbl_charge_6.jpg"),
        Product(shop_id=s1, name="iPhone 17 Pro 透明壳", description="MagSafe兼容，防摔军工认证，超薄0.8mm", price=7900, stock=150, category="数码配件", image_url="/static/products/real_v2/iphone_16_pro_透明壳.jpg"),

        # 智能设备
        Product(shop_id=s1, name="Apple Watch Ultra 3", description="49mm钛金属，双频GPS，血氧心率，100米防水", price=649900, stock=20, category="智能设备", image_url="/static/products/real_v2/apple_watch_ultra_3.jpg"),
        Product(shop_id=s1, name="Apple Watch Series 11", description="45mm，S9芯片，血氧心率，体温感应，GPS", price=399900, stock=25, category="智能设备", image_url="/static/products/real_v2/apple_watch_series_10.jpg"),
        Product(shop_id=s1, name="小米手环 10", description="1.62 AMOLED屏，血氧心率监测，150+运动模式，14天续航", price=24900, stock=200, category="智能设备", image_url="/static/products/real_v2/小米手环_9.jpg"),
        Product(shop_id=s1, name="HomePod mini", description="S7芯片，Siri语音助手，Thread智能家居中枢，空间感知", price=74900, stock=30, category="智能设备", image_url="/static/products/real_v2/homepod_mini.jpg"),

        # 家用电器
        Product(shop_id=s1, name="戴森 V15 Detect", description="激光探测灰尘，240AW吸力，60分钟续航，整机HEPA过滤", price=499000, stock=10, category="家用电器", image_url="/static/products/real_v2/戴森_v15_detect.jpg"),
        Product(shop_id=s1, name="戴森空气净化器 TP09", description="固态甲醛传感器，HEPA+活性炭滤网，Air Multiplier技术", price=549900, stock=8, category="家用电器", image_url="/static/products/real_v2/戴森空气净化器_tp09.jpg"),
        Product(shop_id=s1, name="索尼 65寸 XR电视", description="OLED面板，XR认知芯片，4K 120Hz，HDMI 2.1", price=1299900, stock=5, category="家用电器", image_url="/static/products/real_v2/索尼_65寸_xr电视.jpg"),

        # ── 更多数码配件 ──
        Product(shop_id=s1, name="机械键盘 Cherry MX", description="德国Cherry红轴，PBT键帽，全键热插拔，RGB背光", price=69900, stock=45, category="电脑办公", image_url="/static/products/real_v2/机械键盘_cherry_mx.jpg"),
        Product(shop_id=s1, name="雷蛇 DeathAdder V3", description="Focus Pro 30K传感器，63g超轻，90小时续航", price=49900, stock=55, category="电脑办公", image_url="/static/products/real_v2/雷蛇_deathadder_v3.jpg"),
        Product(shop_id=s1, name="固态硬盘 三星 990 Pro", description="2TB NVMe M.2，读取7450MB/s，写入6900MB/s", price=129900, stock=30, category="电脑办公", image_url="/static/products/real_v2/固态硬盘_三星_990_pro.jpg"),
        Product(shop_id=s1, name="金士顿 DDR5 32GB", description="6000MHz，CL36时序，铝合金散热马甲", price=69900, stock=40, category="电脑办公", image_url="/static/products/real_v2/金士顿_ddr5_32gb.jpg"),
        Product(shop_id=s1, name="罗技 C920s 摄像头", description="1080P全高清，自动对焦，双麦克风，隐私盖", price=49900, stock=60, category="电脑办公", image_url="/static/products/real_v2/罗技_c920s_摄像头.jpg"),
        Product(shop_id=s1, name="明基 ScreenBar Plus", description="屏幕挂灯，非对称光学，自动调光，无眩光", price=89900, stock=35, category="电脑办公", image_url="/static/products/real_v2/明基_screenbar_plus.jpg"),
        Product(shop_id=s1, name="贝尔金 三合一无线充电", description="iPhone+Apple Watch+AirPods同时充电，MagSafe", price=89900, stock=25, category="数码配件", image_url="/static/products/real_v2/贝尔金_三合一无线充电.jpg"),
        Product(shop_id=s1, name="SanDisk 1TB SD卡", description="UHS-I，170MB/s读取，防水防震防X射线", price=69900, stock=50, category="数码配件", image_url="/static/products/real_v2/sandisk_1tb_sd卡.jpg"),

        # ── 居家生活馆 (60+) ──
        # 厨房电器
        Product(shop_id=s2, name="美的 智能电饭煲", description="4L容量，IH加热，24小时预约，APP远程控制", price=59900, stock=40, category="厨房电器", image_url="/static/products/real_v2/美的_智能电饭煲.jpg"),
        Product(shop_id=s2, name="九阳 破壁豆浆机", description="1.75L，10叶刀头，免滤直饮，12小时预约", price=49900, stock=35, category="厨房电器", image_url="/static/products/real_v2/九阳_破壁豆浆机.jpg"),
        Product(shop_id=s2, name="飞利浦 空气炸锅", description="6.2L大容量，360°热风循环，无油低脂，触屏控制", price=69900, stock=50, category="厨房电器", image_url="/static/products/real_v2/飞利浦_空气炸锅.jpg"),
        Product(shop_id=s2, name="松下 微波炉", description="23L，变频加热，一键解冻，童锁保护", price=89900, stock=25, category="厨房电器", image_url="/static/products/real_v2/松下_微波炉.jpg"),
        Product(shop_id=s2, name="格兰仕 烤箱", description="40L，上下独立控温，热风循环，内置照明灯", price=39900, stock=30, category="厨房电器", image_url="/static/products/real_v2/格兰仕_烤箱.jpg"),
        Product(shop_id=s2, name="苏泊尔 电热水壶", description="1.7L，304不锈钢，双层防烫，自动断电", price=12900, stock=80, category="厨房电器", image_url="/static/products/real_v2/苏泊尔_电热水壶.jpg"),

        # 家居日用
        Product(shop_id=s2, name="太力 真空压缩袋", description="10件套，电泵抽气，防潮防霉，节省75%空间", price=6900, stock=120, category="家居日用", image_url="/static/products/real_v2/太力_真空压缩袋.jpg"),
        Product(shop_id=s2, name="科沃斯 扫地机器人", description="LDS激光导航，5000Pa吸力，自动集尘，APP控制", price=299900, stock=15, category="家居日用", image_url="/static/products/real_v2/科沃斯_扫地机器人.jpg"),
        Product(shop_id=s2, name="小米 净水器 600G", description="600加仑大通量，RO反渗透，TDS水质监测", price=149900, stock=20, category="家居日用", image_url="/static/products/real_v2/小米_净水器_600g.jpg"),
        Product(shop_id=s2, name="飞利浦 台灯", description="国AA级照度，无蓝光危害，45分钟定时休息", price=29900, stock=45, category="家居日用", image_url="/static/products/real_v2/飞利浦_台灯.jpg"),
        Product(shop_id=s2, name="无印良品 懒人沙发", description="微粒子填充，可拆洗外套，多色可选", price=59900, stock=30, category="家居日用", image_url="/static/products/real_v2/无印良品_懒人沙发.jpg"),
        Product(shop_id=s2, name="宜家 KALLAX 书架", description="白色，77x77cm，蜂窝纸板填充，可横放竖放", price=29900, stock=25, category="家居日用", image_url="/static/products/real_v2/宜家_kallax_书架.jpg"),

        # 家纺
        Product(shop_id=s2, name="全棉时代 纯棉四件套", description="60支长绒棉，亲肤透气，活性印染，1.8m床", price=39900, stock=35, category="家居日用", image_url="/static/products/real_v2/全棉时代_纯棉四件套.jpg"),
        Product(shop_id=s2, name="网易严选 羽绒被", description="95%白鹅绒，1.5kg填充，600+蓬松度，静音面料", price=99900, stock=20, category="家居日用", image_url="/static/products/real_v2/网易严选_羽绒被.jpg"),
        Product(shop_id=s2, name="水星家纺 记忆枕", description="慢回弹记忆棉，蝶形人体工学，透气散热", price=12900, stock=60, category="家居日用", image_url="/static/products/real_v2/水星家纺_记忆枕.jpg"),

        # 清洁
        Product(shop_id=s2, name="蓝月亮 洗衣液套装", description="3kg*2瓶+1kg*2袋，薰衣草香，深层洁净", price=5900, stock=100, category="家居日用", image_url="/static/products/real_v2/蓝月亮_洗衣液套装.jpg"),
        Product(shop_id=s2, name="维达 抽纸 30包", description="3层120抽，原生木浆，湿水不易破", price=4900, stock=150, category="家居日用", image_url="/static/products/real_v2/维达_抽纸_30包.jpg"),
        Product(shop_id=s2, name="妙洁 垃圾袋 200只", description="加厚PE材质，手提式，不易破，自动收口", price=1900, stock=200, category="家居日用", image_url="/static/products/real_v2/妙洁_垃圾袋_200只.jpg"),

        # 个护美妆
        Product(shop_id=s2, name="芙丽芳丝 洗面奶", description="氨基酸温和洁面，130ml，敏感肌适用", price=15000, stock=60, category="个护美妆", image_url="/static/products/real_v2/芙丽芳丝_洗面奶.jpg"),
        Product(shop_id=s2, name="敷尔佳 白膜", description="医用透明质酸钠修复贴，5片/盒，术后修复", price=9900, stock=80, category="个护美妆", image_url="/static/products/real_v2/敷尔佳_白膜.jpg"),
        Product(shop_id=s2, name="安耐晒 小金瓶", description="SPF50+ PA++++，60ml，防水防汗，清爽不油腻", price=22900, stock=45, category="个护美妆", image_url="/static/products/real_v2/安耐晒_小金瓶.jpg"),
        Product(shop_id=s2, name="迪奥 999口红", description="经典正红，哑光质地，持久显色，3.5g", price=32000, stock=30, category="个护美妆", image_url="/static/products/real_v2/迪奥_999口红.jpg"),
        Product(shop_id=s2, name="香奈儿 邂逅香水", description="清新花果香调，50ml，EDT淡香水", price=89900, stock=15, category="个护美妆", image_url="/static/products/real_v2/香奈儿_邂逅香水.jpg"),
        Product(shop_id=s2, name="飞利浦 电动剃须刀", description="5系，干湿两用，智能感应，1小时快充", price=59900, stock=25, category="个护美妆", image_url="/static/products/real_v2/飞利浦_电动剃须刀.jpg"),

        # 食品饮料
        Product(shop_id=s2, name="三只松鼠 坚果大礼包", description="1428g，8袋混合坚果，年货送礼首选", price=12900, stock=80, category="食品饮料", image_url="/static/products/real_v2/三只松鼠_坚果大礼包.jpg"),
        Product(shop_id=s2, name="星巴克 挂耳咖啡", description="中度烘焙，10包/盒，阿拉比卡豆", price=6900, stock=100, category="食品饮料", image_url="/static/products/real_v2/星巴克_挂耳咖啡.jpg"),
        Product(shop_id=s2, name="西湖龙井 200g", description="明前特级，清香甘醇，铁罐礼盒装", price=19900, stock=30, category="食品饮料", image_url="/static/products/real_v2/西湖龙井_200g.jpg"),
        Product(shop_id=s2, name="特仑苏 纯牛奶 250ml*12", description="3.6g优质蛋白，醇纯营养，梦幻盖", price=5900, stock=120, category="食品饮料", image_url="/static/products/real_v2/特仑苏_纯牛奶_250ml_12.jpg"),
        Product(shop_id=s2, name="元气森林 气泡水", description="0糖0脂0卡，白桃味，480ml*15瓶", price=5900, stock=100, category="食品饮料", image_url="/static/products/real_v2/元气森林_气泡水.jpg"),
        Product(shop_id=s2, name="良品铺子 牛肉干", description="风干牛肉，原味，200g罐装", price=4900, stock=70, category="食品饮料", image_url="/static/products/real_v2/良品铺子_牛肉干.jpg"),

        # 母婴玩具
        Product(shop_id=s2, name="飞鹤 星飞帆奶粉", description="3段(12-36月)，800g，OPO结构脂", price=29900, stock=40, category="母婴玩具", image_url="/static/products/real_v2/飞鹤_星飞帆奶粉.jpg"),
        Product(shop_id=s2, name="好奇 铂金装纸尿裤", description="L码(9-14kg)，54片/包，透气干爽", price=11900, stock=60, category="母婴玩具", image_url="/static/products/real_v2/好奇_铂金装纸尿裤.jpg"),
        Product(shop_id=s2, name="乐高 经典创意积木", description="484片，多色积木，适合4-99岁", price=29900, stock=35, category="母婴玩具", image_url="/static/products/real_v2/乐高_经典创意积木.jpg"),
        Product(shop_id=s2, name="乐高 城市系列 警察局", description="326片，含6个人仔，适合6+", price=39900, stock=25, category="母婴玩具", image_url="/static/products/real_v2/乐高_城市系列_警察局.jpg"),

        # 图书文具
        Product(shop_id=s2, name="深入理解计算机系统", description="CSAPP第3版，程序员必读经典", price=13900, stock=50, category="图书文具", image_url="/static/products/real_v2/深入理解计算机系统.jpg"),
        Product(shop_id=s2, name="算法导论 第4版", description="CLRS，MIT经典教材，全面覆盖算法", price=12800, stock=40, category="图书文具", image_url="/static/products/real_v2/算法导论_第4版.jpg"),
        Product(shop_id=s2, name="斑马 中性笔 10支", description="JJ15，0.5mm，速干墨水，书写顺滑", price=3500, stock=100, category="图书文具", image_url="/static/products/real_v2/斑马_中性笔_10支.jpg"),
        Product(shop_id=s2, name="晨光 文具套装", description="学生开学大礼包，含笔袋+中性笔+橡皮+尺子", price=2900, stock=80, category="图书文具", image_url="/static/products/real_v2/晨光_文具套装.jpg"),

        # ── 运动户外专营店 (50+) ──
        # 跑步
        Product(shop_id=s3, name="Nike Air Zoom Pegasus 42", description="React泡棉中底，Zoom Air气垫，飞织鞋面，男款", price=89900, stock=40, category="运动户外", image_url="/static/products/real_v2/nike_air_zoom_pegasus_42.jpg"),
        Product(shop_id=s3, name="Adidas Ultraboost Light", description="Light BOOST中底，Continental橡胶外底，Primeknit鞋面", price=109900, stock=30, category="运动户外", image_url="/static/products/real_v2/adidas_ultraboost_light.jpg"),
        Product(shop_id=s3, name="Asics Gel-Kayano 31", description="FF BLAST PLUS中底，4D GUIDANCE SYSTEM，稳定支撑", price=129900, stock=20, category="运动户外", image_url="/static/products/real_v2/asics_gel_kayano_31.jpg"),
        Product(shop_id=s3, name="Garmin Forerunner 265", description="AMOLED屏，双频GPS，训练建议，13天续航", price=329900, stock=15, category="运动户外", image_url="/static/products/final/garmin_forerunner_265.svg"),
        Product(shop_id=s3, name="迪卡侬 速干T恤", description="跑步透气，轻量排汗，反光条设计", price=4900, stock=150, category="运动户外", image_url="/static/products/real_v2/迪卡侬_速干t恤.jpg"),

        # 瑜伽
        Product(shop_id=s3, name="Keep 瑜伽垫 6mm", description="TPE环保材质，双面防滑，含收纳袋", price=9900, stock=60, category="运动户外", image_url="/static/products/real_v2/keep_瑜伽垫_6mm.jpg"),
        Product(shop_id=s3, name="lululemon Align 瑜伽裤", description="Nulu面料，裸感舒适，高腰设计，25寸", price=85000, stock=25, category="运动户外", image_url="/static/products/real_v2/lululemon_align_瑜伽裤.jpg"),
        Product(shop_id=s3, name="瑜伽砖 2块装", description="高密度EVA，防滑表面，辅助拉伸", price=3900, stock=80, category="运动户外", image_url="/static/products/real_v2/瑜伽砖_2块装.jpg"),

        # 骑行
        Product(shop_id=s3, name="迪卡侬 山地自行车", description="27.5寸，21速，铝合金车架，机械碟刹", price=199900, stock=10, category="运动户外", image_url="/static/products/real_v2/迪卡侬_山地自行车.jpg"),
        Product(shop_id=s3, name="骑行头盔", description="MIPS防护系统，可调节头围，透气孔设计", price=29900, stock=30, category="运动户外", image_url="/static/products/real_v2/骑行头盔.jpg"),
        Product(shop_id=s3, name="骑行手套 半指", description="硅胶防滑垫，触屏指尖，减震掌心", price=4900, stock=50, category="运动户外", image_url="/static/products/real_v2/骑行手套_半指.jpg"),

        # 登山
        Product(shop_id=s3, name="北面 冲锋衣", description="GORE-TEX面料，防水透气，可拆卸内胆", price=299900, stock=15, category="运动户外", image_url="/static/products/real_v2/北面_冲锋衣.jpg"),
        Product(shop_id=s3, name="登山杖 碳纤维", description="可伸缩，EVA手柄，钨钢杖尖，一对装", price=19900, stock=40, category="运动户外", image_url="/static/products/real_v2/登山杖_碳纤维.jpg"),
        Product(shop_id=s3, name="Osprey 双肩包 40L", description="户外登山包，防雨罩，多仓分隔，透气背板", price=99900, stock=20, category="运动户外", image_url="/static/products/real_v2/osprey_双肩包_40l.jpg"),

        # 游泳
        Product(shop_id=s3, name="Speedo 泳镜", description="防雾镜片，UV防护，可调节鼻桥，近视可选", price=12900, stock=50, category="运动户外", image_url="/static/products/real_v2/speedo_泳镜.jpg"),
        Product(shop_id=s3, name="速比涛 泳帽", description="硅胶材质，舒适贴合，不夹头发", price=3900, stock=80, category="运动户外", image_url="/static/products/real_v2/速比涛_泳帽.jpg"),

        # 球类
        Product(shop_id=s3, name="斯伯丁 官方比赛篮球", description="7号球，PU材质，FIBA认证，室内外通用", price=19900, stock=40, category="运动户外", image_url="/static/products/real_v2/斯伯丁_官方比赛篮球.jpg"),
        Product(shop_id=s3, name="红双喜 乒乓球拍", description="专业级横拍，双面反胶，含拍包", price=29900, stock=30, category="运动户外", image_url="/static/products/real_v2/红双喜_乒乓球拍.jpg"),
        Product(shop_id=s3, name="尤尼克斯 羽毛球拍", description="碳纤维材质，全碳素，含拍包+手胶", price=39900, stock=25, category="运动户外", image_url="/static/products/real_v2/尤尼克斯_羽毛球拍.jpg"),
        Product(shop_id=s3, name="Wilson 网球拍", description="100拍面，280g，减震系统，适合中级", price=59900, stock=15, category="运动户外", image_url="/static/products/real_v2/wilson_网球拍.jpg"),

        # 健身
        Product(shop_id=s3, name="可调节哑铃 20kg*2", description="快速调节重量，包胶防滑，含收纳架", price=39900, stock=25, category="运动户外", image_url="/static/products/real_v2/可调节哑铃_20kg_2.jpg"),
        Product(shop_id=s3, name="健身弹力带 5件套", description="5级阻力，乳胶材质，含便携袋", price=3900, stock=100, category="运动户外", image_url="/static/products/real_v2/健身弹力带_5件套.jpg"),
        Product(shop_id=s3, name="泡沫轴 45cm", description="EVA材质，深度放松肌肉，运动恢复", price=4900, stock=60, category="运动户外", image_url="/static/products/real_v2/泡沫轴_45cm.jpg"),
        Product(shop_id=s3, name="跳绳 计数款", description="钢丝绳芯，轴承顺滑，LED显示", price=2900, stock=90, category="运动户外", image_url="/static/products/real_v2/跳绳_计数款.jpg"),
        Product(shop_id=s3, name="健腹轮 自动回弹", description="双轮设计，肘撑式，自动回弹省力", price=6900, stock=50, category="运动户外", image_url="/static/products/real_v2/健腹轮_自动回弹.jpg"),

        # 额外补充：服饰鞋包
        Product(shop_id=s2, name="优衣库 纯棉T恤", description="100%精梳棉，圆领短袖，多色可选，经典百搭", price=5900, stock=200, category="服饰鞋包", image_url="/static/products/final/优衣库_纯棉t恤.svg"),
        Product(shop_id=s2, name="Nike Air Force 1", description="经典白色低帮板鞋，Air气垫缓震，皮质鞋面", price=79900, stock=35, category="服饰鞋包", image_url="/static/products/real_v2/nike_air_force_1.jpg"),
        Product(shop_id=s2, name="Levi's 501 牛仔裤", description="直筒版型，经典水洗，100%棉，纽扣门襟", price=59900, stock=30, category="服饰鞋包", image_url="/static/products/real_v2/levi_s_501_牛仔裤.jpg"),
        Product(shop_id=s2, name="新秀丽 双肩包", description="商务休闲，15.6寸电脑仓，防泼水面料", price=49900, stock=25, category="服饰鞋包", image_url="/static/products/real_v2/新秀丽_双肩包.jpg"),
        Product(shop_id=s2, name="MUJI 亚麻衬衫", description="法国亚麻材质，透气凉爽，宽松版型", price=19900, stock=40, category="服饰鞋包", image_url="/static/products/real_v2/muji_亚麻衬衫.jpg"),
        Product(shop_id=s2, name="匡威 Chuck 70", description="经典高帮帆布鞋，OrthoLite鞋垫，复古做旧", price=59900, stock=45, category="服饰鞋包", image_url="/static/products/real_v2/匡威_chuck_70.jpg"),

        # 额外补充：生鲜果蔬
        Product(shop_id=s2, name="新疆阿克苏苹果 5kg", description="冰糖心，脆甜多汁，产地直发", price=3900, stock=50, category="生鲜果蔬", image_url="/static/products/real_v2/新疆阿克苏苹果_5kg.jpg"),
        Product(shop_id=s2, name="智利车厘子 1kg", description="JJ级，新鲜直达，果径30mm+", price=7900, stock=30, category="生鲜果蔬", image_url="/static/products/real_v2/智利车厘子_1kg.jpg"),
        Product(shop_id=s2, name="澳洲牛排 原切 500g", description="谷饲150天，M3级雪花，眼肉牛排", price=9900, stock=40, category="生鲜果蔬", image_url="/static/products/real_v2/澳洲牛排_原切_500g.jpg"),
        Product(shop_id=s2, name="厄瓜多尔白虾 1kg", description="大号20/25，船冻锁鲜，去壳易处理", price=4900, stock=35, category="生鲜果蔬", image_url="/static/products/real_v2/厄瓜多尔白虾_1kg.jpg"),
        Product(shop_id=s2, name="有机蔬菜礼盒 5kg", description="10种时令蔬菜，有机认证，产地直供", price=6900, stock=25, category="生鲜果蔬", image_url="/static/products/real_v2/有机蔬菜礼盒_5kg.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：手机通讯（+15）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s1, name="一加 14", description="骁龙8至尊版，哈苏影像，6200mAh电池，100W快充", price=449900, stock=32, category="手机通讯", image_url="/static/products/real_v2/一加_13.jpg"),
        Product(shop_id=s1, name="荣耀 Magic8 Pro", description="骁龙8至尊版，鹰眼相机，5850mAh电池，100W快充", price=499900, stock=22, category="手机通讯", image_url="/static/products/real_v2/荣耀_magic7_pro.jpg"),
        Product(shop_id=s1, name="小米17", description="骁龙8至尊版，徕卡光学，5000mAh电池，100W快充", price=399900, stock=40, category="手机通讯", image_url="/static/products/real_v2/小米14.jpg"),
        Product(shop_id=s1, name="Redmi K90 Pro", description="骁龙8至尊版，2K屏，6500mAh电池，120W快充", price=349900, stock=50, category="手机通讯", image_url="/static/products/real_v2/redmi_k80_pro.jpg"),
        Product(shop_id=s1, name="realme GT8 Pro", description="骁龙8至尊版，IMX906主摄，6500mAh电池，120W快充", price=369900, stock=35, category="手机通讯", image_url="/static/products/real_v2/realme_gt7_pro.jpg"),
        Product(shop_id=s1, name="iQOO 14", description="骁龙8至尊版，自研电竞芯片Q3，6200mAh电池，120W快充", price=429900, stock=30, category="手机通讯", image_url="/static/products/real_v2/iqoo_13.jpg"),
        Product(shop_id=s1, name="魅族 22 Pro", description="骁龙8至尊版，超声波指纹，5500mAh电池，80W快充", price=399900, stock=18, category="手机通讯", image_url="/static/products/real_v2/魅族_21_pro.jpg"),
        Product(shop_id=s1, name="ROG 游戏手机 10", description="骁龙8至尊版，185Hz电竞屏，6500mAh电池，AirTrigger", price=629900, stock=12, category="手机通讯", image_url="/static/products/real_v2/rog_游戏手机_9.jpg"),
        Product(shop_id=s1, name="三星 Galaxy Z Fold7", description="骁龙8至尊版，7.6英寸折叠屏，S Pen支持，IPX8防水", price=1499900, stock=8, category="手机通讯", image_url="/static/products/real_v2/三星_galaxy_z_fold6.jpg"),
        Product(shop_id=s1, name="三星 Galaxy Z Flip7", description="骁龙8至尊版，6.7英寸折叠屏，Flex Window外屏", price=849900, stock=15, category="手机通讯", image_url="/static/products/real_v2/三星_galaxy_z_flip6.jpg"),
        Product(shop_id=s1, name="iPhone 17", description="A19芯片，4800万像素，操作按钮，USB-C", price=699900, stock=25, category="手机通讯", image_url="/static/products/real_v2/iphone_16.jpg"),
        Product(shop_id=s1, name="华为 Mate X7", description="麒麟芯片，6.4英寸外屏+7.85英寸内屏，XMAGE影像", price=1399900, stock=10, category="手机通讯", image_url="/static/products/real_v2/华为_mate_x6.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：电脑办公（+20）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s1, name="MacBook Air M5", description="M5芯片，16GB统一内存，256GB SSD，18小时续航", price=949900, stock=20, category="电脑办公", image_url="/static/products/real_v2/macbook_air_m4.jpg"),
        Product(shop_id=s1, name="华为 MateBook X Pro", description="Ultra 9 185H，32GB，2TB SSD，3.1K OLED触控屏", price=1199900, stock=12, category="电脑办公", image_url="/static/products/real_v2/华为_matebook_x_pro.jpg"),
        Product(shop_id=s1, name="戴尔 XPS 14", description="Ultra 7 155H，32GB，1TB SSD，14.5英寸OLED触控屏", price=1099900, stock=15, category="电脑办公", image_url="/static/products/real_v2/戴尔_xps_14.jpg"),
        Product(shop_id=s1, name="华硕 ROG 幻16", description="i9-14900HX，RTX 4070，32GB DDR5，2.5K 240Hz屏", price=1299900, stock=10, category="电脑办公", image_url="/static/products/real_v2/华硕_rog_幻16.jpg"),
        Product(shop_id=s1, name="Surface Pro 11", description="骁龙X Elite，16GB，512GB SSD，13英寸触控屏", price=899900, stock=18, category="电脑办公", image_url="/static/products/real_v2/surface_pro_11.jpg"),
        Product(shop_id=s1, name="iPad Pro M4", description="M4芯片，11英寸，Ultra Retina XDR屏，Apple Pencil Pro", price=899900, stock=15, category="电脑办公", image_url="/static/products/real_v2/ipad_pro_m4.jpg"),
        Product(shop_id=s1, name="三星 Galaxy Tab S10 Ultra", description="天玑9300+，14.6英寸Super AMOLED屏，S Pen", price=899900, stock=12, category="电脑办公", image_url="/static/products/real_v2/三星_galaxy_tab_s10_ultra.jpg"),
        Product(shop_id=s1, name="LG 27寸 OLED显示器", description="4K OLED，0.1ms响应，99% DCI-P3色域，Type-C 90W", price=599900, stock=8, category="电脑办公", image_url="/static/products/real_v2/lg_27寸_oled显示器.jpg"),
        Product(shop_id=s1, name="ROG 32寸 4K电竞显示器", description="Mini LED，144Hz，1ms响应，HDMI 2.1，G-SYNC", price=499900, stock=10, category="电脑办公", image_url="/static/products/real_v2/rog_32寸_4k电竞显示器.jpg"),
        Product(shop_id=s1, name="罗技 G Pro X 键盘", description="GX机械轴，可换轴设计，RGB背光，紧凑布局", price=99900, stock=30, category="电脑办公", image_url="/static/products/real_v2/罗技_g_pro_x_键盘.jpg"),
        Product(shop_id=s1, name="雷蛇 Huntsman V3 Pro", description="光学机械轴，磁吸腕托，RGB背光，多功能旋钮", price=149900, stock=20, category="电脑办公", image_url="/static/products/real_v2/雷蛇_huntsman_v3_pro.jpg"),
        Product(shop_id=s1, name="雷蛇 Viper V3 Pro", description="Focus Pro 35K传感器，54g超轻，90小时续航", price=89900, stock=25, category="电脑办公", image_url="/static/products/real_v2/雷蛇_viper_v3_pro.jpg"),
        Product(shop_id=s1, name="西部数据 SN850X 2TB", description="NVMe M.2，读取7300MB/s，写入6600MB/s", price=119900, stock=20, category="电脑办公", image_url="/static/products/real_v2/西部数据_sn850x_2tb.jpg"),
        Product(shop_id=s1, name="芝奇 Trident Z5 DDR5 64GB", description="6400MHz，CL32时序，铝合金散热马甲，RGB灯效", price=149900, stock=15, category="电脑办公", image_url="/static/products/real_v2/芝奇_trident_z5_ddr5_64gb.jpg"),
        Product(shop_id=s1, name="戴尔 UltraSharp 32寸 4K", description="IPS Black面板，Type-C 90W，98% DCI-P3色域", price=499900, stock=12, category="电脑办公", image_url="/static/products/real_v2/戴尔_ultrasharp_32寸_4k.jpg"),
        Product(shop_id=s1, name="明基 PD2706UA 设计显示器", description="4K IPS，95% DCI-P3，出厂校色，Type-C 90W", price=399900, stock=15, category="电脑办公", image_url="/static/products/real_v2/明基_pd2706ua_设计显示器.jpg"),
        Product(shop_id=s1, name="罗技 Brio 4K 摄像头", description="4K超高清，HDR，自动对焦，红外人脸识别", price=129900, stock=25, category="电脑办公", image_url="/static/products/real_v2/罗技_brio_4k_摄像头.jpg"),
        Product(shop_id=s1, name="Elgato Stream Deck", description="15个LCD按键，一键控制直播/音乐/灯光", price=129900, stock=20, category="电脑办公", image_url="/static/products/real_v2/elgato_stream_deck.jpg"),
        Product(shop_id=s1, name="雷蛇 Kiyo Pro Ultra 摄像头", description="4K，索尼STARVIS 2传感器，自动对焦，HDR", price=199900, stock=12, category="电脑办公", image_url="/static/products/real_v2/雷蛇_kiyo_pro_ultra_摄像头.jpg"),
        Product(shop_id=s1, name="罗技 Zone Vibe 100 耳麦", description="无线蓝牙，降噪麦克风，18小时续航，轻量化设计", price=79900, stock=30, category="电脑办公", image_url="/static/products/real_v2/罗技_zone_vibe_100_耳麦.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：数码配件（+15）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s1, name="Anker 65W氮化镓充电器", description="3口USB-C，支持MacBook快充，可折叠插脚", price=24900, stock=100, category="数码配件", image_url="/static/products/real_v2/anker_65w氮化镓充电器.jpg"),
        Product(shop_id=s1, name="小米 10000mAh 充电宝", description="22.5W快充，超薄设计，可充手机2次", price=9900, stock=120, category="数码配件", image_url="/static/products/real_v2/小米_10000mah_充电宝.jpg"),
        Product(shop_id=s1, name="华为 FreeBuds Pro 3", description="麒麟A2芯片，智能降噪，LDAC高清音频", price=149900, stock=35, category="数码配件", image_url="/static/products/real_v2/华为_freebuds_pro_3.jpg"),
        Product(shop_id=s1, name="索尼 WF-1000XM6", description="V2处理器，24小时续航，LDAC Hi-Res，降噪", price=199900, stock=30, category="数码配件", image_url="/static/products/real_v2/索尼_wf_1000xm6.jpg"),
        Product(shop_id=s1, name="Bose QuietComfort Ultra 耳机", description="沉浸式音频，空间音频，24小时续航", price=299900, stock=20, category="数码配件", image_url="/static/products/real_v2/bose_quietcomfort_ultra_耳机.jpg"),
        Product(shop_id=s1, name="Marshall Emberton II", description="蓝牙5.1，IP67防水，30小时续航，多设备连接", price=129900, stock=25, category="数码配件", image_url="/static/products/real_v2/marshall_emberton_ii.jpg"),
        Product(shop_id=s1, name="三星 T7 Shield 2TB 移动固态硬盘", description="IP65防护，1050MB/s读取，Type-C接口", price=129900, stock=30, category="数码配件", image_url="/static/products/real_v2/三星_t7_shield_2tb_移动固态硬盘.jpg"),
        Product(shop_id=s1, name="Apple Pencil Pro", description="像素级精准，倾斜感应，压力感应，磁吸充电", price=99900, stock=40, category="数码配件", image_url="/static/products/real_v2/apple_pencil_pro.jpg"),
        Product(shop_id=s1, name="小米 65W USB-C 数据线", description="1.5米编织线，支持100W快充，E-Marker芯片", price=4900, stock=200, category="数码配件", image_url="/static/products/real_v2/小米_65w_usb_c_数据线.jpg"),
        Product(shop_id=s1, name="绿联 12合1 扩展坞", description="Type-C扩展，HDMI 4K，千兆网口，100W PD充电", price=39900, stock=35, category="数码配件", image_url="/static/products/real_v2/绿联_12合1_扩展坞.jpg"),
        Product(shop_id=s1, name="Anker 737 充电宝", description="24000mAh，140W双向快充，可充笔记本", price=59900, stock=25, category="数码配件", image_url="/static/products/real_v2/anker_737_充电宝.jpg"),
        Product(shop_id=s1, name="JBL Flip 7", description="蓝牙5.3，IP67防水，12小时续航，派对模式", price=99900, stock=30, category="数码配件", image_url="/static/products/real_v2/jbl_flip_7.jpg"),
        Product(shop_id=s1, name="三星 Galaxy Buds3 Pro", description="智能降噪，360音频，IP57防水，28小时续航", price=169900, stock=25, category="数码配件", image_url="/static/products/real_v2/三星_galaxy_buds3_pro.jpg"),
        Product(shop_id=s1, name="小米 车载充电器", description="67W快充，双USB-C口，LED显示，兼容多车型", price=7900, stock=80, category="数码配件", image_url="/static/products/real_v2/小米_车载充电器.jpg"),
        Product(shop_id=s1, name="苹果 MagSafe 充电器", description="15W无线快充，磁吸对齐，兼容Qi设备", price=34900, stock=60, category="数码配件", image_url="/static/products/real_v2/苹果_magsafe_充电器.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：智能设备（+12）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s1, name="Apple Watch Series 10", description="S10芯片，42mm，血氧心率，ECG心电图，IP6X防水", price=349900, stock=25, category="智能设备", image_url="/static/products/real_v2/apple_watch_series_10.jpg"),
        Product(shop_id=s1, name="华为 Watch GT5 Pro", description="钛金属表壳，14天续航，高尔夫/潜水模式", price=249900, stock=20, category="智能设备", image_url="/static/products/real_v2/华为_watch_gt5_pro.jpg"),
        Product(shop_id=s1, name="三星 Galaxy Watch Ultra", description="钛金属，双频GPS，100米防水，钛金属表带", price=499900, stock=12, category="智能设备", image_url="/static/products/real_v2/三星_galaxy_watch_ultra.jpg"),
        Product(shop_id=s1, name="小米 Watch S4", description="1.43英寸AMOLED屏，血氧心率，150+运动模式", price=99900, stock=40, category="智能设备", image_url="/static/products/real_v2/小米_watch_s4.jpg"),
        Product(shop_id=s1, name="佳明 Fenix 8", description="AMOLED屏，太阳能充电，多频GPS，30天续航", price=599900, stock=10, category="智能设备", image_url="/static/products/real_v2/佳明_fenix_8.jpg"),
        Product(shop_id=s1, name="小米 智能门锁 Pro", description="3D人脸识别，指纹解锁，NFC，远程监控", price=199900, stock=25, category="智能设备", image_url="/static/products/real_v2/小米_智能门锁_pro.jpg"),
        Product(shop_id=s1, name="华为 智能音箱", description="帝瓦雷联合设计，Hi-Res音质，鸿蒙互联", price=99900, stock=30, category="智能设备", image_url="/static/products/real_v2/华为_智能音箱.jpg"),
        Product(shop_id=s1, name="小米 摄像头 2K", description="2K超清，360°全景，AI人形侦测，双向语音", price=14900, stock=60, category="智能设备", image_url="/static/products/real_v2/小米_摄像头_2k.jpg"),
        Product(shop_id=s1, name="绿米 智能窗帘电机", description="静音电机，定时开合，语音控制，米家联动", price=49900, stock=35, category="智能设备", image_url="/static/products/real_v2/绿米_智能窗帘电机.jpg"),
        Product(shop_id=s1, name="华为 智能体脂秤", description="14项身体指标，WiFi联网，多人管理", price=19900, stock=50, category="智能设备", image_url="/static/products/real_v2/华为_智能体脂秤.jpg"),
        Product(shop_id=s1, name="小米 空气净化器 5", description="500m³/h CADR，HEPA滤芯，APP控制", price=129900, stock=20, category="智能设备", image_url="/static/products/real_v2/小米_空气净化器_5.jpg"),
        Product(shop_id=s1, name="Apple Vision Pro", description="M2+R1芯片，micro-OLED，眼动追踪，空间计算", price=2999900, stock=5, category="智能设备", image_url="/static/products/real_v2/apple_vision_pro.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：家用电器（+15）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s2, name="格力 1.5匹变频空调", description="新一级能效，自清洁，WiFi智控，静音设计", price=329900, stock=30, category="家用电器", image_url="/static/products/real_v2/格力_1_5匹变频空调.jpg"),
        Product(shop_id=s2, name="美的 501L 对开门冰箱", description="一级能效，风冷无霜，变频压缩机，智能控温", price=399900, stock=20, category="家用电器", image_url="/static/products/real_v2/美的_501l_对开门冰箱.jpg"),
        Product(shop_id=s2, name="海尔 10kg 洗烘一体机", description="直驱变频，智能投放，微蒸汽空气洗", price=499900, stock=15, category="家用电器", image_url="/static/products/real_v2/海尔_10kg_洗烘一体机.jpg"),
        Product(shop_id=s2, name="索尼 75寸 XR电视", description="OLED面板，XR认知芯片，4K 120Hz，HDMI 2.1", price=1999900, stock=8, category="家用电器", image_url="/static/products/real_v2/索尼_75寸_xr电视.jpg"),
        Product(shop_id=s2, name="海信 85寸 ULED电视", description="ULED X技术，4K 144Hz，HDMI 2.1，杜比全景声", price=999900, stock=10, category="家用电器", image_url="/static/products/real_v2/海信_85寸_uled电视.jpg"),
        Product(shop_id=s2, name="戴森 V12 Detect Slim", description="激光探测灰尘，150AW吸力，60分钟续航", price=399900, stock=15, category="家用电器", image_url="/static/products/real_v2/戴森_v12_detect_slim.jpg"),
        Product(shop_id=s2, name="科沃斯 T30 Pro 扫地机器人", description="LDS激光导航，11000Pa吸力，自动集尘+自动洗拖布", price=399900, stock=12, category="家用电器", image_url="/static/products/real_v2/科沃斯_t30_pro_扫地机器人.jpg"),
        Product(shop_id=s2, name="石头 G20 扫地机器人", description="LDS激光导航，6000Pa吸力，自动集尘，RR Mason算法", price=349900, stock=18, category="家用电器", image_url="/static/products/real_v2/石头_g20_扫地机器人.jpg"),
        Product(shop_id=s2, name="美的 3匹柜机空调", description="新一级能效，无风感技术，智能WiFi控制", price=799900, stock=10, category="家用电器", image_url="/static/products/real_v2/美的_3匹柜机空调.jpg"),
        Product(shop_id=s2, name="西门子 10kg 洗衣机", description="iQdrive变频电机，智能除渍，15分钟快洗", price=599900, stock=12, category="家用电器", image_url="/static/products/real_v2/西门子_10kg_洗衣机.jpg"),
        Product(shop_id=s2, name="三星 650L 法式多门冰箱", description="一级能效，风冷无霜，变频压缩机，智能控温", price=699900, stock=10, category="家用电器", image_url="/static/products/real_v2/三星_650l_法式多门冰箱.jpg"),
        Product(shop_id=s2, name="LG 65寸 OLED电视", description="OLED evo面板，α9 Gen7芯片，4K 120Hz，Dolby Vision", price=1499900, stock=8, category="家用电器", image_url="/static/products/real_v2/lg_65寸_oled电视.jpg"),
        Product(shop_id=s2, name="追觅 V16 Pro 吸尘器", description="210AW吸力，90分钟续航，绿光显尘，一键倒尘", price=299900, stock=20, category="家用电器", image_url="/static/products/real_v2/追觅_v16_pro_吸尘器.jpg"),
        Product(shop_id=s2, name="小米 新风空调", description="1.5匹变频，新风功能，一级能效，自清洁", price=349900, stock=15, category="家用电器", image_url="/static/products/real_v2/小米_新风空调.jpg"),
        Product(shop_id=s2, name="TCL 98寸 巨幕电视", description="QD-Mini LED，4K 144Hz，HDMI 2.1，杜比全景声", price=1999900, stock=5, category="家用电器", image_url="/static/products/real_v2/tcl_98寸_巨幕电视.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：厨房电器（+12）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s2, name="美的 智能电压力锅", description="5L容量，双胆设计，24小时预约，一键排气", price=39900, stock=40, category="厨房电器", image_url="/static/products/real_v2/美的_智能电压力锅.jpg"),
        Product(shop_id=s2, name="九阳 破壁料理机", description="1.75L，10叶刀头，真空破壁，12小时预约", price=59900, stock=30, category="厨房电器", image_url="/static/products/real_v2/九阳_破壁料理机.jpg"),
        Product(shop_id=s2, name="飞利浦 意式咖啡机", description="15巴泵压，自动奶泡，一键萃取，可拆卸水箱", price=299900, stock=15, category="厨房电器", image_url="/static/products/real_v2/飞利浦_意式咖啡机.jpg"),
        Product(shop_id=s2, name="松下 电烤箱", description="30L，上下独立控温，热风循环，旋转烤叉", price=59900, stock=25, category="厨房电器", image_url="/static/products/real_v2/松下_电烤箱.jpg"),
        Product(shop_id=s2, name="苏泊尔 电饭煲", description="4L容量，球釜内胆，24小时预约，多功能菜单", price=29900, stock=50, category="厨房电器", image_url="/static/products/real_v2/苏泊尔_电饭煲.jpg"),
        Product(shop_id=s2, name="美的 微波炉", description="23L，变频加热，一键解冻，童锁保护", price=69900, stock=30, category="厨房电器", image_url="/static/products/real_v2/美的_微波炉.jpg"),
        Product(shop_id=s2, name="九阳 豆浆机", description="1.2L，免滤直饮，12小时预约，自动清洗", price=39900, stock=35, category="厨房电器", image_url="/static/products/real_v2/九阳_豆浆机.jpg"),
        Product(shop_id=s2, name="飞利浦 空气炸锅", description="4.1L，360°热风循环，无油低脂，触屏控制", price=49900, stock=40, category="厨房电器", image_url="https://placehold.co/400x400/0ab4e8/ffffff?text=Philips"),
        Product(shop_id=s2, name="格兰仕 光波炉", description="23L，光波+微波，一键解冻，童锁保护", price=59900, stock=20, category="厨房电器", image_url="/static/products/real_v2/格兰仕_光波炉.jpg"),
        Product(shop_id=s2, name="苏泊尔 电炖锅", description="4L，紫砂内胆，隔水炖煮，24小时预约", price=19900, stock=45, category="厨房电器", image_url="/static/products/real_v2/苏泊尔_电炖锅.jpg"),
        Product(shop_id=s2, name="九阳 面条机", description="自动和面，多种面条模头，一键操作", price=49900, stock=20, category="厨房电器", image_url="/static/products/real_v2/九阳_面条机.jpg"),
        Product(shop_id=s2, name="美的 洗碗机", description="8套容量，热风烘干，消毒除菌，静音设计", price=299900, stock=15, category="厨房电器", image_url="/static/products/real_v2/美的_洗碗机.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：个护美妆（+15）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s2, name="兰蔻 小黑瓶精华", description="第二代小黑瓶，30ml，修护肌底，改善肤质", price=79900, stock=25, category="个护美妆", image_url="/static/products/real_v2/兰蔻_小黑瓶精华.jpg"),
        Product(shop_id=s2, name="雅诗兰黛 小棕瓶精华", description="第七代小棕瓶，50ml，修护抗老，淡化细纹", price=69900, stock=30, category="个护美妆", image_url="/static/products/real_v2/雅诗兰黛_小棕瓶精华.jpg"),
        Product(shop_id=s2, name="SK-II 神仙水", description="230ml，Pitera精华，改善肤质，提亮肤色", price=159900, stock=20, category="个护美妆", image_url="/static/products/real_v2/sk_ii_神仙水.jpg"),
        Product(shop_id=s2, name="资生堂 红腰子精华", description="75ml，ULTIMUNE成分，增强肌肤抵御力", price=59900, stock=25, category="个护美妆", image_url="/static/products/real_v2/资生堂_红腰子精华.jpg"),
        Product(shop_id=s2, name="MAC 子弹头口红", description="RUBY WOO色号，哑光质地，持久显色，3g", price=17000, stock=50, category="个护美妆", image_url="/static/products/real_v2/mac_子弹头口红.jpg"),
        Product(shop_id=s2, name="YSL 小金条口红", description="N21色号，哑光质地，持久显色，2.2g", price=32000, stock=35, category="个护美妆", image_url="/static/products/real_v2/ysl_小金条口红.jpg"),
        Product(shop_id=s2, name="Tom Ford 黑管口红", description="Lost Cherry色号，滋润质地，持久显色，3g", price=42000, stock=20, category="个护美妆", image_url="/static/products/real_v2/tom_ford_黑管口红.jpg"),
        Product(shop_id=s2, name="NARS 腮红", description="Orgasm色号，微闪珠光，自然红润，4.8g", price=32000, stock=30, category="个护美妆", image_url="/static/products/real_v2/nars_腮红.jpg"),
        Product(shop_id=s2, name="Givenchy 四宫格散粉", description="1号色，轻薄定妆，控油持久，4x3g", price=52000, stock=20, category="个护美妆", image_url="/static/products/real_v2/givenchy_四宫格散粉.jpg"),
        Product(shop_id=s2, name="La Mer 海蓝之谜面霜", description="经典面霜，60ml，修护保湿，改善肤质", price=299900, stock=10, category="个护美妆", image_url="/static/products/real_v2/la_mer_海蓝之谜面霜.jpg"),
        Product(shop_id=s2, name="欧莱雅 玻尿酸面膜", description="5片/盒，补水保湿，淡化细纹", price=7900, stock=80, category="个护美妆", image_url="/static/products/real_v2/欧莱雅_玻尿酸面膜.jpg"),
        Product(shop_id=s2, name="薇诺娜 舒敏保湿霜", description="50g，敏感肌专用，修护屏障，舒缓泛红", price=26800, stock=40, category="个护美妆", image_url="/static/products/real_v2/薇诺娜_舒敏保湿霜.jpg"),
        Product(shop_id=s2, name="博朗 电动剃须刀 9系", description="4+1刀头，智能声波，干湿两用，自动清洁中心", price=299900, stock=12, category="个护美妆", image_url="/static/products/real_v2/博朗_电动剃须刀_9系.jpg"),
        Product(shop_id=s2, name="戴森 Airwrap 美发造型器", description="多功能造型，顺滑+卷发+吹风，Coanda气流技术", price=399900, stock=15, category="个护美妆", image_url="/static/products/real_v2/戴森_airwrap_美发造型器.jpg"),
        Product(shop_id=s2, name="松下 纳米水离子吹风机", description="EH-NA0J，高渗透纳米水离子，智能温控", price=199900, stock=20, category="个护美妆", image_url="/static/products/real_v2/松下_纳米水离子吹风机.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：食品饮料（+15）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s2, name="三顿半 咖啡", description="超即溶冷萃，18颗/盒，精品咖啡豆", price=9900, stock=80, category="食品饮料", image_url="/static/products/real_v2/三顿半_咖啡.jpg"),
        Product(shop_id=s2, name="瑞幸 咖啡液", description="生椰拿铁味，10条/盒，0糖0脂", price=6900, stock=100, category="食品饮料", image_url="/static/products/real_v2/瑞幸_咖啡液.jpg"),
        Product(shop_id=s2, name="农夫山泉 长白雪矿泉水", description="535ml*24瓶，天然矿泉水，偏硅酸型", price=4900, stock=120, category="食品饮料", image_url="/static/products/real_v2/农夫山泉_长白雪矿泉水.jpg"),
        Product(shop_id=s2, name="百岁山 矿泉水", description="570ml*24瓶，天然矿泉水，富含偏硅酸", price=4900, stock=110, category="食品饮料", image_url="/static/products/real_v2/百岁山_矿泉水.jpg"),
        Product(shop_id=s2, name="可口可乐", description="330ml*24罐，经典原味，碳酸饮料", price=4900, stock=150, category="食品饮料", image_url="/static/products/real_v2/可口可乐.jpg"),
        Product(shop_id=s2, name="百事可乐", description="330ml*24罐，经典原味，碳酸饮料", price=4900, stock=140, category="食品饮料", image_url="/static/products/real_v2/百事可乐.jpg"),
        Product(shop_id=s2, name="农夫山泉 东方树叶", description="500ml*15瓶，茉莉花茶，0糖0脂0卡", price=5900, stock=90, category="食品饮料", image_url="/static/products/real_v2/农夫山泉_东方树叶.jpg"),
        Product(shop_id=s2, name="三得利 乌龙茶", description="500ml*15瓶，无糖，清爽解腻", price=5900, stock=85, category="食品饮料", image_url="/static/products/real_v2/三得利_乌龙茶.jpg"),
        Product(shop_id=s2, name="良品铺子 坚果礼盒", description="1538g，10袋混合坚果，年货送礼", price=16900, stock=50, category="食品饮料", image_url="/static/products/real_v2/良品铺子_坚果礼盒.jpg"),
        Product(shop_id=s2, name="百草味 坚果礼盒", description="1428g，8袋混合坚果，年货送礼", price=12900, stock=60, category="食品饮料", image_url="/static/products/real_v2/百草味_坚果礼盒.jpg"),
        Product(shop_id=s2, name="蒙牛 纯牛奶", description="250ml*24盒，3.2g蛋白质，全脂灭菌", price=5900, stock=130, category="食品饮料", image_url="/static/products/real_v2/蒙牛_纯牛奶.jpg"),
        Product(shop_id=s2, name="伊利 纯牛奶", description="250ml*24盒，3.2g蛋白质，全脂灭菌", price=5900, stock=125, category="食品饮料", image_url="/static/products/real_v2/伊利_纯牛奶.jpg"),
        Product(shop_id=s2, name="安慕希 酸奶", description="205g*12盒，希腊酸奶，原味", price=5900, stock=100, category="食品饮料", image_url="/static/products/real_v2/安慕希_酸奶.jpg"),
        Product(shop_id=s2, name="奥利奥 饼干", description="97g*6包，夹心饼干，原味", price=2900, stock=150, category="食品饮料", image_url="/static/products/real_v2/奥利奥_饼干.jpg"),
        Product(shop_id=s2, name="乐事 薯片", description="104g*4包，原味，马铃薯片", price=2900, stock=140, category="食品饮料", image_url="/static/products/real_v2/乐事_薯片.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：服饰鞋包（+20）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s2, name="优衣库 羽绒服", description="轻薄羽绒，90%白鸭绒，可收纳，多色可选", price=49900, stock=40, category="服饰鞋包", image_url="/static/products/final/优衣库_羽绒服.svg"),
        Product(shop_id=s2, name="Nike Dunk Low", description="经典低帮板鞋，皮质鞋面，多色可选", price=79900, stock=30, category="服饰鞋包", image_url="/static/products/real_v2/nike_dunk_low.jpg"),
        Product(shop_id=s2, name="Adidas Samba", description="经典复古板鞋，皮质鞋面，橡胶外底", price=79900, stock=25, category="服饰鞋包", image_url="/static/products/real_v2/adidas_samba.jpg"),
        Product(shop_id=s2, name="New Balance 574", description="经典复古跑鞋，ENCAP缓震，多色可选", price=69900, stock=35, category="服饰鞋包", image_url="/static/products/real_v2/new_balance_574.jpg"),
        Product(shop_id=s2, name="优衣库 牛仔裤", description="直筒版型，弹力面料，经典水洗", price=19900, stock=50, category="服饰鞋包", image_url="/static/products/final/优衣库_牛仔裤.svg"),
        Product(shop_id=s2, name="优衣库 衬衫", description="牛津纺面料，修身版型，多色可选", price=14900, stock=60, category="服饰鞋包", image_url="/static/products/real_v2/优衣库_衬衫.jpg"),
        Product(shop_id=s2, name="优衣库 卫衣", description="摇粒绒面料，宽松版型，多色可选", price=19900, stock=45, category="服饰鞋包", image_url="/static/products/final/优衣库_卫衣.svg"),
        Product(shop_id=s2, name="耐克 运动裤", description="Dri-FIT面料，束脚设计，多色可选", price=29900, stock=40, category="服饰鞋包", image_url="/static/products/real_v2/耐克_运动裤.jpg"),
        Product(shop_id=s2, name="阿迪达斯 运动裤", description="Climalite面料，束脚设计，多色可选", price=29900, stock=35, category="服饰鞋包", image_url="/static/products/real_v2/阿迪达斯_运动裤.jpg"),
        Product(shop_id=s2, name="Coach 手提包", description="经典C字纹，皮质面料，多隔层设计", price=399900, stock=10, category="服饰鞋包", image_url="/static/products/real_v2/coach_手提包.jpg"),
        Product(shop_id=s2, name="MK 单肩包", description="经典Logo印花，皮质面料，多隔层设计", price=299900, stock=15, category="服饰鞋包", image_url="/static/products/real_v2/mk_单肩包.jpg"),
        Product(shop_id=s2, name="新秀丽 行李箱", description="28寸，PC材质，万向轮，TSA海关锁", price=99900, stock=20, category="服饰鞋包", image_url="/static/products/real_v2/新秀丽_行李箱.jpg"),
        Product(shop_id=s2, name="耐克 双肩包", description="25L容量，电脑仓，多隔层，透气背板", price=39900, stock=30, category="服饰鞋包", image_url="/static/products/real_v2/耐克_双肩包.jpg"),
        Product(shop_id=s2, name="阿迪达斯 双肩包", description="23L容量，电脑仓，多隔层，透气背板", price=34900, stock=35, category="服饰鞋包", image_url="/static/products/real_v2/阿迪达斯_双肩包.jpg"),
        Product(shop_id=s2, name="优衣库 夹克", description="轻薄面料，修身版型，多色可选", price=29900, stock=40, category="服饰鞋包", image_url="/static/products/real_v2/优衣库_夹克.jpg"),
        Product(shop_id=s2, name="耐克 夹克", description="Windrunner系列，防风面料，多色可选", price=59900, stock=25, category="服饰鞋包", image_url="/static/products/real_v2/耐克_夹克.jpg"),
        Product(shop_id=s2, name="阿迪达斯 夹克", description="Tiro系列，防风面料，多色可选", price=49900, stock=30, category="服饰鞋包", image_url="/static/products/real_v2/阿迪达斯_夹克.jpg"),
        Product(shop_id=s2, name="优衣库 T恤", description="Supima棉面料，圆领短袖，多色可选", price=7900, stock=80, category="服饰鞋包", image_url="/static/products/final/优衣库_t恤.svg"),
        Product(shop_id=s2, name="耐克 T恤", description="Dri-FIT面料，圆领短袖，多色可选", price=19900, stock=50, category="服饰鞋包", image_url="/static/products/real_v2/耐克_t恤.jpg"),
        Product(shop_id=s2, name="阿迪达斯 T恤", description="Climalite面料，圆领短袖，多色可选", price=17900, stock=55, category="服饰鞋包", image_url="/static/products/real_v2/阿迪达斯_t恤.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：生鲜果蔬（+10）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s2, name="海南芒果 5斤", description="贵妃芒，新鲜直达，果肉细腻", price=3900, stock=40, category="生鲜果蔬", image_url="/static/products/real_v2/海南芒果_5斤.jpg"),
        Product(shop_id=s2, name="泰国榴莲 1个", description="金枕头，果肉饱满，香气浓郁", price=19900, stock=20, category="生鲜果蔬", image_url="/static/products/real_v2/泰国榴莲_1个.jpg"),
        Product(shop_id=s2, name="丹东草莓 2斤", description="新鲜直达，果肉饱满，香甜多汁", price=4900, stock=35, category="生鲜果蔬", image_url="/static/products/real_v2/丹东草莓_2斤.jpg"),
        Product(shop_id=s2, name="赣南脐橙 5斤", description="新鲜直达，果肉饱满，香甜多汁", price=2900, stock=45, category="生鲜果蔬", image_url="/static/products/real_v2/赣南脐橙_5斤.jpg"),
        Product(shop_id=s2, name="烟台苹果 5斤", description="红富士，脆甜多汁，产地直发", price=2900, stock=50, category="生鲜果蔬", image_url="/static/products/real_v2/烟台苹果_5斤.jpg"),
        Product(shop_id=s2, name="新疆葡萄干 500g", description="无核白葡萄干，自然晾晒，甜而不腻", price=1900, stock=60, category="生鲜果蔬", image_url="/static/products/real_v2/新疆葡萄干_500g.jpg"),
        Product(shop_id=s2, name="宁夏枸杞 500g", description="特级枸杞，自然晾晒，颗粒饱满", price=3900, stock=40, category="生鲜果蔬", image_url="/static/products/real_v2/宁夏枸杞_500g.jpg"),
        Product(shop_id=s2, name="云南鲜花饼 10枚", description="玫瑰鲜花饼，传统工艺，香甜可口", price=2900, stock=50, category="生鲜果蔬", image_url="/static/products/real_v2/云南鲜花饼_10枚.jpg"),
        Product(shop_id=s2, name="内蒙古牛肉干 500g", description="风干牛肉，原味，高蛋白低脂肪", price=6900, stock=35, category="生鲜果蔬", image_url="/static/products/real_v2/内蒙古牛肉干_500g.jpg"),
        Product(shop_id=s2, name="大连海参 500g", description="淡干海参，野生捕捞，营养丰富", price=29900, stock=15, category="生鲜果蔬", image_url="/static/products/real_v2/大连海参_500g.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：图书文具（+15）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s2, name="Python编程从入门到实践", description="第3版，Python入门经典，含实战项目", price=8900, stock=60, category="图书文具", image_url="/static/products/real_v2/python编程从入门到实践.jpg"),
        Product(shop_id=s2, name="JavaScript高级程序设计", description="第4版，红宝书，前端开发必读", price=9900, stock=50, category="图书文具", image_url="/static/products/real_v2/javascript高级程序设计.jpg"),
        Product(shop_id=s2, name="设计模式", description="GoF经典，面向对象设计必读", price=6900, stock=40, category="图书文具", image_url="/static/products/final/设计模式.svg"),
        Product(shop_id=s2, name="代码整洁之道", description="Robert C. Martin经典，编程规范必读", price=5900, stock=45, category="图书文具", image_url="/static/products/real_v2/代码整洁之道.jpg"),
        Product(shop_id=s2, name="重构", description="Martin Fowler经典，代码重构指南", price=6900, stock=35, category="图书文具", image_url="/static/products/final/重构.svg"),
        Product(shop_id=s2, name="人月神话", description="Fred Brooks经典，软件工程必读", price=4900, stock=40, category="图书文具", image_url="/static/products/real_v2/人月神话.jpg"),
        Product(shop_id=s2, name="三体", description="刘慈欣科幻经典，全三册", price=9900, stock=70, category="图书文具", image_url="/static/products/real_v2/三体.jpg"),
        Product(shop_id=s2, name="活着", description="余华经典，人生必读", price=3900, stock=80, category="图书文具", image_url="/static/products/real_v2/活着.jpg"),
        Product(shop_id=s2, name="百年孤独", description="马尔克斯经典，魔幻现实主义", price=4900, stock=50, category="图书文具", image_url="/static/products/real_v2/百年孤独.jpg"),
        Product(shop_id=s2, name="小王子", description="圣埃克苏佩里经典，成人童话", price=2900, stock=90, category="图书文具", image_url="/static/products/real_v2/小王子.jpg"),
        Product(shop_id=s2, name="得力 中性笔 20支", description="0.5mm，黑色，速干墨水", price=1500, stock=120, category="图书文具", image_url="/static/products/real_v2/得力_中性笔_20支.jpg"),
        Product(shop_id=s2, name="晨光 笔记本", description="A5胶装本，80页，横线内页", price=500, stock=200, category="图书文具", image_url="/static/products/real_v2/晨光_笔记本.jpg"),
        Product(shop_id=s2, name="得力 文件夹", description="A4双夹文件夹，PP材质", price=800, stock=150, category="图书文具", image_url="/static/products/real_v2/得力_文件夹.jpg"),
        Product(shop_id=s2, name="3M 便利贴", description="76x76mm，4色混装，100张/包", price=1500, stock=180, category="图书文具", image_url="/static/products/real_v2/3m_便利贴.jpg"),
        Product(shop_id=s2, name="得力 订书机", description="12号标准型，可订20页", price=1500, stock=100, category="图书文具", image_url="/static/products/real_v2/得力_订书机.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：母婴玩具（+15）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s2, name="美赞臣 蓝臻奶粉", description="3段(12-36月)，800g，乳铁蛋白", price=34900, stock=35, category="母婴玩具", image_url="/static/products/real_v2/美赞臣_蓝臻奶粉.jpg"),
        Product(shop_id=s2, name="惠氏 启赋奶粉", description="3段(12-36月)，800g，OPO结构脂", price=32900, stock=30, category="母婴玩具", image_url="/static/products/real_v2/惠氏_启赋奶粉.jpg"),
        Product(shop_id=s2, name="帮宝适 一级帮纸尿裤", description="L码(9-14kg)，54片/包，超薄透气", price=12900, stock=50, category="母婴玩具", image_url="/static/products/real_v2/帮宝适_一级帮纸尿裤.jpg"),
        Product(shop_id=s2, name="花王 妙而舒纸尿裤", description="L码(9-14kg)，54片/包，柔软亲肤", price=11900, stock=55, category="母婴玩具", image_url="/static/products/real_v2/花王_妙而舒纸尿裤.jpg"),
        Product(shop_id=s2, name="乐高 得宝系列", description="大颗粒积木，适合1.5-5岁，安全无毒", price=29900, stock=30, category="母婴玩具", image_url="/static/products/real_v2/乐高_得宝系列.jpg"),
        Product(shop_id=s2, name="费雪 学步车", description="多功能学步车，音乐灯光，可调节高度", price=29900, stock=25, category="母婴玩具", image_url="/static/products/real_v2/费雪_学步车.jpg"),
        Product(shop_id=s2, name="好孩子 婴儿推车", description="轻便可折叠，双向推行，避震车轮", price=99900, stock=15, category="母婴玩具", image_url="/static/products/real_v2/好孩子_婴儿推车.jpg"),
        Product(shop_id=s2, name="Cybex 安全座椅", description="0-12岁，360°旋转，ISOFIX接口", price=299900, stock=10, category="母婴玩具", image_url="/static/products/real_v2/cybex_安全座椅.jpg"),
        Product(shop_id=s2, name="贝亲 奶瓶", description="160ml，PPSU材质，宽口径，防胀气", price=12900, stock=60, category="母婴玩具", image_url="/static/products/real_v2/贝亲_奶瓶.jpg"),
        Product(shop_id=s2, name="新安怡 吸奶器", description="电动双边吸奶器，静音设计，多档调节", price=199900, stock=12, category="母婴玩具", image_url="/static/products/real_v2/新安怡_吸奶器.jpg"),
        Product(shop_id=s2, name="B.Duck 小黄鸭洗澡玩具", description="安全无毒，浮水设计，宝宝洗澡伴侣", price=2900, stock=80, category="母婴玩具", image_url="/static/products/real_v2/b_duck_小黄鸭洗澡玩具.jpg"),
        Product(shop_id=s2, name="火火兔 早教机", description="故事机，儿歌，国学，英语，wifi联网", price=19900, stock=35, category="母婴玩具", image_url="/static/products/real_v2/火火兔_早教机.jpg"),
        Product(shop_id=s2, name="乐高 技术系列", description="保时捷911，1580片，适合16+", price=99900, stock=10, category="母婴玩具", image_url="/static/products/real_v2/乐高_技术系列.jpg"),
        Product(shop_id=s2, name="万代 高达模型", description="RG系列，1/144比例，精密细节", price=19900, stock=25, category="母婴玩具", image_url="/static/products/real_v2/万代_高达模型.jpg"),
        Product(shop_id=s2, name="泡泡玛特 盲盒", description="MOLLY系列，12款随机，潮流玩具", price=6900, stock=100, category="母婴玩具", image_url="/static/products/real_v2/泡泡玛特_盲盒.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：运动户外（+20）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s3, name="Nike ZoomX Vaporfly NEXT%", description="碳板跑鞋，ZoomX泡棉，4%能量回馈", price=229900, stock=15, category="运动户外", image_url="/static/products/real_v2/nike_zoomx_vaporfly_next.jpg"),
        Product(shop_id=s3, name="Adidas Adizero Adios Pro 3", description="碳板跑鞋，Lightstrike Pro泡棉，破纪录战靴", price=209900, stock=12, category="运动户外", image_url="/static/products/real_v2/adidas_adizero_adios_pro_3.jpg"),
        Product(shop_id=s3, name="Salomon Ultra Glide 2", description="越野跑鞋，Contagrip外底，Energy Surge泡棉", price=129900, stock=20, category="运动户外", image_url="/static/products/real_v2/salomon_ultra_glide_2.jpg"),
        Product(shop_id=s3, name="Garmin Forerunner 965", description="AMOLED屏，双频GPS，训练状态，23天续航", price=499900, stock=10, category="运动户外", image_url="/static/products/real_v2/garmin_forerunner_965.jpg"),
        Product(shop_id=s3, name="Polar Vantage V3", description="AMOLED屏，双频GPS，训练负荷，14天续航", price=449900, stock=8, category="运动户外", image_url="/static/products/real_v2/polar_vantage_v3.jpg"),
        Product(shop_id=s3, name="迪卡侬 跑步短裤", description="轻量排汗，内衬设计，反光条", price=6900, stock=100, category="运动户外", image_url="/static/products/real_v2/迪卡侬_跑步短裤.jpg"),
        Product(shop_id=s3, name="迪卡侬 跑步背心", description="超轻透气，无缝编织，反光条", price=4900, stock=120, category="运动户外", image_url="/static/products/real_v2/迪卡侬_跑步背心.jpg"),
        Product(shop_id=s3, name="Lululemon Metal Vent Tech T恤", description="Silverescent技术，防臭，四向弹力", price=65000, stock=25, category="运动户外", image_url="/static/products/real_v2/lululemon_metal_vent_tech_t恤.jpg"),
        Product(shop_id=s3, name="Under Armour 速干T恤", description="HeatGear面料，4D弹力，防臭技术", price=19900, stock=40, category="运动户外", image_url="/static/products/real_v2/under_armour_速干t恤.jpg"),
        Product(shop_id=s3, name="Giant TCR Advanced 公路车", description="碳纤维车架，Shimano 105套件，7.5kg", price=999900, stock=5, category="运动户外", image_url="/static/products/real_v2/giant_tcr_advanced_公路车.jpg"),
        Product(shop_id=s3, name="Trek Domane SL 5 公路车", description="碳纤维车架，Shimano 105套件，IsoSpeed减震", price=1499900, stock=3, category="运动户外", image_url="/static/products/real_v2/trek_domane_sl_5_公路车.jpg"),
        Product(shop_id=s3, name="骑行码表 GPS", description="2.7英寸屏，GPS轨迹，心率监测，踏频", price=99900, stock=20, category="运动户外", image_url="/static/products/real_v2/骑行码表_gps.jpg"),
        Product(shop_id=s3, name="Gregory Baltoro 背包 75L", description="专业登山包，Response A3背板，防雨罩", price=299900, stock=8, category="运动户外", image_url="/static/products/real_v2/gregory_baltoro_背包_75l.jpg"),
        Product(shop_id=s3, name="MSR Hubba Hubba 帐篷", description="双人帐篷，超轻1.5kg，3季使用", price=299900, stock=10, category="运动户外", image_url="/static/products/real_v2/msr_hubba_hubba_帐篷.jpg"),
        Product(shop_id=s3, name="Sea to Summit 睡袋", description="木乃伊型，舒适温度0°C，压缩体积小", price=199900, stock=12, category="运动户外", image_url="/static/products/real_v2/sea_to_summit_睡袋.jpg"),
        Product(shop_id=s3, name="Black Diamond 登山杖", description="碳纤维，可伸缩，EVA手柄，一对装", price=49900, stock=25, category="运动户外", image_url="/static/products/real_v2/black_diamond_登山杖.jpg"),
        Product(shop_id=s3, name="Arc'teryx Beta LT 冲锋衣", description="GORE-TEX Pro面料，轻量化设计，防水透气", price=499900, stock=8, category="运动户外", image_url="/static/products/real_v2/arc_teryx_beta_lt_冲锋衣.jpg"),
        Product(shop_id=s3, name="Mammut Nordwand Advanced 冲锋衣", description="GORE-TEX Pro面料，专业登山设计", price=399900, stock=10, category="运动户外", image_url="/static/products/real_v2/mammut_nordwand_advanced_冲锋衣.jpg"),
        Product(shop_id=s3, name="Salomon X Ultra 4 登山鞋", description="Contagrip外底，Advanced Chassis，防水", price=109900, stock=20, category="运动户外", image_url="/static/products/real_v2/salomon_x_ultra_4_登山鞋.jpg"),
        Product(shop_id=s3, name="La Sportiva Trango Tower 登山靴", description="GORE-TEX内衬，Vibram外底，3季登山", price=199900, stock=10, category="运动户外", image_url="/static/products/real_v2/la_sportiva_trango_tower_登山靴.jpg"),

        # ════════════════════════════════════════════════════════
        # 扩充：家居日用（+15）
        # ════════════════════════════════════════════════════════
        Product(shop_id=s2, name="小米 台灯 Pro", description="国AA级照度，无蓝光危害，智能调光", price=19900, stock=40, category="家居日用", image_url="/static/products/real_v2/小米_台灯_pro.jpg"),
        Product(shop_id=s2, name="松下 台灯", description="国AA级照度，无蓝光危害，45分钟定时", price=29900, stock=30, category="家居日用", image_url="/static/products/real_v2/松下_台灯.jpg"),
        Product(shop_id=s2, name="宜家 比利书架", description="白色，80x28x202cm，可调节层板", price=39900, stock=20, category="家居日用", image_url="/static/products/real_v2/宜家_比利书架.jpg"),
        Product(shop_id=s2, name="宜家 马尔姆床架", description="白色，150x200cm，含床头板", price=99900, stock=15, category="家居日用", image_url="/static/products/real_v2/宜家_马尔姆床架.jpg"),
        Product(shop_id=s2, name="无印良品 懒人椅", description="微粒子填充，可拆洗外套，多色可选", price=49900, stock=25, category="家居日用", image_url="/static/products/real_v2/无印良品_懒人椅.jpg"),
        Product(shop_id=s2, name="小米 净水器 1000G", description="1000加仑大通量，RO反渗透，TDS水质监测", price=249900, stock=12, category="家居日用", image_url="/static/products/real_v2/小米_净水器_1000g.jpg"),
        Product(shop_id=s2, name="科沃斯 窗宝擦窗机器人", description="WIN SLAM 2.0路径规划，2800Pa吸力", price=199900, stock=15, category="家居日用", image_url="/static/products/real_v2/科沃斯_窗宝擦窗机器人.jpg"),
        Product(shop_id=s2, name="小米 除湿机", description="50L/天除湿量，智能恒湿，APP控制", price=199900, stock=18, category="家居日用", image_url="/static/products/real_v2/小米_除湿机.jpg"),
        Product(shop_id=s2, name="戴森 加湿器", description="紫外线杀菌，Air Multiplier技术，智能控湿", price=399900, stock=10, category="家居日用", image_url="/static/products/real_v2/戴森_加湿器.jpg"),
        Product(shop_id=s2, name="小米 电风扇", description="落地扇，12档风速，智能控制，静音设计", price=29900, stock=35, category="家居日用", image_url="/static/products/real_v2/小米_电风扇.jpg"),
        Product(shop_id=s2, name="美的 电暖器", description="油汀式，13片散热片，智能恒温，遥控", price=39900, stock=25, category="家居日用", image_url="/static/products/real_v2/美的_电暖器.jpg"),
        Product(shop_id=s2, name="小米 智能垃圾桶", description="感应开盖，12L容量，一键打包", price=19900, stock=30, category="家居日用", image_url="/static/products/real_v2/小米_智能垃圾桶.jpg"),
        Product(shop_id=s2, name="太力 收纳箱 3个装", description="55L容量，带轮设计，可叠加", price=9900, stock=50, category="家居日用", image_url="/static/products/real_v2/太力_收纳箱_3个装.jpg"),
        Product(shop_id=s2, name="无印良品 香薰机", description="超声波雾化，LED灯光，定时功能", price=19900, stock=40, category="家居日用", image_url="/static/products/real_v2/无印良品_香薰机.jpg"),
        Product(shop_id=s2, name="小米 体重秤", description="高精度传感器，16项身体指标，WiFi联网", price=9900, stock=60, category="家居日用", image_url="/static/products/real_v2/小米_体重秤.jpg"),
    ]
    for p in products:
        db.add(p)
    db.flush()
    print(f"  {len(products)} products created across 3 shops")

# ── 收藏（多个用户收藏商品）──
buyer = user_map["buyer"]
buyer2 = user_map.get("buyer2")
buyer3 = user_map.get("buyer3")
buyer4 = user_map.get("buyer4")
buyer5 = user_map.get("buyer5")

if db.query(Favorite).filter(Favorite.user_id == buyer.id).count() == 0:
    # buyer 收藏前 30 个商品
    fav_products = db.query(Product).order_by(Product.id).limit(30).all()
    for p in fav_products:
        db.add(Favorite(user_id=buyer.id, product_id=p.id))
    print(f"  {len(fav_products)} favorites created for buyer")

if buyer2 and db.query(Favorite).filter(Favorite.user_id == buyer2.id).count() == 0:
    # buyer2 收藏第 10-40 个商品
    fav_products = db.query(Product).order_by(Product.id).offset(10).limit(30).all()
    for p in fav_products:
        db.add(Favorite(user_id=buyer2.id, product_id=p.id))
    print(f"  {len(fav_products)} favorites created for buyer2")

if buyer3 and db.query(Favorite).filter(Favorite.user_id == buyer3.id).count() == 0:
    # buyer3 收藏第 20-50 个商品
    fav_products = db.query(Product).order_by(Product.id).offset(20).limit(30).all()
    for p in fav_products:
        db.add(Favorite(user_id=buyer3.id, product_id=p.id))
    print(f"  {len(fav_products)} favorites created for buyer3")

if buyer4 and db.query(Favorite).filter(Favorite.user_id == buyer4.id).count() == 0:
    # buyer4 收藏第 30-60 个商品
    fav_products = db.query(Product).order_by(Product.id).offset(30).limit(30).all()
    for p in fav_products:
        db.add(Favorite(user_id=buyer4.id, product_id=p.id))
    print(f"  {len(fav_products)} favorites created for buyer4")

if buyer5 and db.query(Favorite).filter(Favorite.user_id == buyer5.id).count() == 0:
    # buyer5 收藏第 40-70 个商品
    fav_products = db.query(Product).order_by(Product.id).offset(40).limit(30).all()
    for p in fav_products:
        db.add(Favorite(user_id=buyer5.id, product_id=p.id))
    print(f"  {len(fav_products)} favorites created for buyer5")

# ── 评价（100+ 条评价，覆盖更多商品）──
if db.query(Review).count() == 0:
    review_data = [
        (5, "非常棒的产品，手感极好，做工精致，完全超出预期！推荐购买。"),
        (4, "整体不错，性价比很高。就是物流稍微慢了一点，等了3天。"),
        (5, "质量非常好，用了一周了没有任何问题。包装也很精美，送人也不错。"),
        (4, "颜值很高，功能齐全。唯一小遗憾是颜色和图片有点色差。"),
        (3, "中规中矩吧，这个价位算可以了。期望值不要太高就好。"),
        (5, "第三次回购了，一直在用这个牌子，品质稳定，值得信赖。"),
        (4, "收到货试了一下，比想象中好。客服态度也很耐心，好评。"),
        (5, "超级喜欢！做工精细，手感一流。比实体店便宜了不少。"),
        (4, "用了一个月来评价，耐用性不错。就是刚开始需要适应一下。"),
        (5, "给朋友买的生日礼物，朋友非常喜欢。包装很用心，赞一个。"),
        (3, "一般般吧，没有想象中那么好。不过价格摆在那里，凑合用。"),
        (5, "发货速度快，第二天就到了。产品质量没得说，五星好评。"),
        (4, "不错的选择，对比了好几款最后选了这个。满意。"),
        (5, "家里人都说好，已经推荐给同事了。值得入手。"),
        (4, "做工比预期好，性价比突出。下次还会光顾。"),
        (5, "完美的购物体验，从下单到收货都很顺畅。产品更是没话说。"),
        (4, "质量过硬，用了两周了，一切正常。好评支持。"),
        (5, "颜值担当，功能强大。放在桌上就是一道风景线。"),
        (4, "物流很快，包装完好。产品试用了一下，效果不错。"),
        (5, "果断好评！真的是物超所值。已经收藏了店铺，下次还来。"),
        (4, "包装很严实，没有任何破损。产品也很好用，满意。"),
        (5, "第二次购买了，品质一如既往的好。会继续支持。"),
        (3, "还行吧，中规中矩。不过这个价格也不能要求太高。"),
        (5, "送货速度超快，第二天就到了。产品质量也很好，好评！"),
        (4, "用了一段时间才来评价，确实不错。值得推荐。"),
        (5, "颜值高，质量好，价格实惠。非常满意的一次购物。"),
        (4, "产品比想象中好，客服态度也很棒。好评支持。"),
        (5, "真的是物超所值，强烈推荐给大家！"),
        (4, "做工精细，手感一流。就是颜色和图片有点差异。"),
        (5, "完美的产品，完美的服务。五星好评！"),
    ]

    # buyer 评价前 30 个商品
    all_products = db.query(Product).order_by(Product.id).limit(30).all()
    for i, p in enumerate(all_products):
        rating, content = review_data[i % len(review_data)]
        db.add(Review(
            user_id=buyer.id,
            product_id=p.id,
            order_item_id=-(i + 1),
            rating=rating,
            content=content,
        ))

    # buyer2 评价第 5-35 个商品
    if buyer2:
        products2 = db.query(Product).order_by(Product.id).offset(5).limit(30).all()
        for i, p in enumerate(products2):
            rating, content = review_data[(i + 5) % len(review_data)]
            db.add(Review(
                user_id=buyer2.id,
                product_id=p.id,
                order_item_id=-(100 + i + 1),
                rating=rating,
                content=content,
            ))

    # buyer3 评价第 10-40 个商品
    if buyer3:
        products3 = db.query(Product).order_by(Product.id).offset(10).limit(30).all()
        for i, p in enumerate(products3):
            rating, content = review_data[(i + 10) % len(review_data)]
            db.add(Review(
                user_id=buyer3.id,
                product_id=p.id,
                order_item_id=-(200 + i + 1),
                rating=rating,
                content=content,
            ))

    # buyer4 评价第 15-45 个商品
    if buyer4:
        products4 = db.query(Product).order_by(Product.id).offset(15).limit(30).all()
        for i, p in enumerate(products4):
            rating, content = review_data[(i + 15) % len(review_data)]
            db.add(Review(
                user_id=buyer4.id,
                product_id=p.id,
                order_item_id=-(300 + i + 1),
                rating=rating,
                content=content,
            ))

    # buyer5 评价第 20-50 个商品
    if buyer5:
        products5 = db.query(Product).order_by(Product.id).offset(20).limit(30).all()
        for i, p in enumerate(products5):
            rating, content = review_data[(i + 20) % len(review_data)]
            db.add(Review(
                user_id=buyer5.id,
                product_id=p.id,
                order_item_id=-(400 + i + 1),
                rating=rating,
                content=content,
            ))

    print(f"  Reviews created for 5 buyers across 50+ products")

# ════════════════════════════════════════════════════════════
# 优惠券
# ════════════════════════════════════════════════════════════
if db.query(Coupon).count() == 0:
    now = datetime.utcnow()
    coupons_data = [
        Coupon(
            code="WELCOME10",
            name="新人专享券",
            description="新用户专享，满100减10元",
            coupon_type=CouponType.FIXED,
            value=1000,
            min_amount=10000,
            total_count=1000,
            start_time=now,
            end_time=now + timedelta(days=30),
        ),
        Coupon(
            code="SAVE20",
            name="满200减20",
            description="全场通用，满200减20元",
            coupon_type=CouponType.FIXED,
            value=2000,
            min_amount=20000,
            total_count=500,
            start_time=now,
            end_time=now + timedelta(days=30),
        ),
        Coupon(
            code="SAVE50",
            name="满500减50",
            description="大额优惠，满500减50元",
            coupon_type=CouponType.FIXED,
            value=5000,
            min_amount=50000,
            total_count=200,
            start_time=now,
            end_time=now + timedelta(days=30),
        ),
        Coupon(
            code="DISCOUNT9",
            name="9折优惠券",
            description="全场9折，最高减100元",
            coupon_type=CouponType.PERCENT,
            value=10,
            min_amount=0,
            max_discount=10000,
            total_count=300,
            start_time=now,
            end_time=now + timedelta(days=30),
        ),
        Coupon(
            code="DISCOUNT8",
            name="8折优惠券",
            description="全场8折，最高减200元",
            coupon_type=CouponType.PERCENT,
            value=20,
            min_amount=10000,
            max_discount=20000,
            total_count=100,
            start_time=now,
            end_time=now + timedelta(days=15),
        ),
        Coupon(
            code="FREESHIP",
            name="免运费券",
            description="全场免运费，无门槛",
            coupon_type=CouponType.FIXED,
            value=1000,
            min_amount=0,
            total_count=0,
            start_time=now,
            end_time=now + timedelta(days=60),
        ),
        Coupon(
            code="VIP100",
            name="VIP专享券",
            description="VIP用户专享，满1000减100",
            coupon_type=CouponType.FIXED,
            value=10000,
            min_amount=100000,
            total_count=50,
            start_time=now,
            end_time=now + timedelta(days=30),
        ),
        Coupon(
            code="SUMMER85",
            name="夏季特惠85折",
            description="夏季特惠，85折优惠",
            coupon_type=CouponType.PERCENT,
            value=15,
            min_amount=5000,
            max_discount=5000,
            total_count=200,
            start_time=now,
            end_time=now + timedelta(days=60),
        ),
    ]
    for c in coupons_data:
        db.add(c)
    db.flush()
    print(f"  {len(coupons_data)} coupons created")

    # 给买家发放一些优惠券
    buyer_users = [buyer, buyer2, buyer3, buyer4, buyer5]
    all_coupons = db.query(Coupon).all()
    for u in buyer_users:
        if u:
            for c in all_coupons[:3]:  # 每人领前3张
                db.add(UserCoupon(
                    user_id=u.id,
                    coupon_id=c.id,
                    status=CouponStatus.ACTIVE,
                ))
            c.used_count += 3
    print(f"  Coupons distributed to 5 buyers")

# ════════════════════════════════════════════════════════════
# 补充商品多图、规格、SKU（部分代表性商品）
# ════════════════════════════════════════════════════════════
print("  Updating product images and specs...")
products_to_update = db.query(Product).filter(Product.name.in_([
    "小米14 Ultra", "iPhone 16 Pro", "华为 Mate 70",
    "Nike Air Zoom Pegasus 42", "Adidas Ultraboost Light",
    "lululemon Align 瑜伽裤",
    "优衣库 纯棉T恤", "Nike Air Force 1", "Levi's 501 牛仔裤",
    "迪奥 999口红", "香奈儿 邂逅香水",
])).all()

specs_templates = {
    "手机通讯": {
        "颜色": ["黑色", "白色", "蓝色", "银色"],
        "存储": ["128GB", "256GB", "512GB", "1TB"]
    },
    "运动户外": {
        "尺码": ["38", "39", "40", "41", "42", "43", "44"],
        "颜色": ["黑色", "白色", "灰色"]
    },
    "服饰鞋包": {
        "尺码": ["S", "M", "L", "XL", "XXL"],
        "颜色": ["黑色", "白色", "灰色", "蓝色"]
    },
    "个护美妆": {
        "规格": ["标准装", "大容量", "旅行装"]
    }
}

for p in products_to_update:
    # 为商品添加多图 - 使用与主图相同风格的占位图
    if not p.images:
        # 从主图 URL 中提取颜色和品牌名
        import re
        match = re.search(r'placehold\.co/400x400/([a-f0-9]+)/([a-f0-9]+)\?text=(.+)', p.image_url)
        if match:
            bg_color, fg_color, brand = match.groups()
            # 生成同风格的详情图和包装图
            detail_url = f"https://placehold.co/400x400/{bg_color}/{fg_color}?text={brand}+Detail"
            box_url = f"https://placehold.co/400x400/{bg_color}/{fg_color}?text={brand}+Box"
            p.images = [p.image_url, detail_url, box_url]
        else:
            p.images = [p.image_url]

    # 为商品添加规格
    if not p.specs and p.category in specs_templates:
        p.specs = specs_templates[p.category]
        # 生成简单 SKU
        if p.category == "手机通讯":
            p.skus = [
                {"specs": {"颜色": "黑色", "存储": "256GB"}, "price": p.price, "stock": p.stock // 4},
                {"specs": {"颜色": "白色", "存储": "256GB"}, "price": p.price, "stock": p.stock // 4},
                {"specs": {"颜色": "黑色", "存储": "512GB"}, "price": p.price + 100000, "stock": p.stock // 4},
                {"specs": {"颜色": "白色", "存储": "512GB"}, "price": p.price + 100000, "stock": p.stock // 4},
            ]
        elif p.category in ["运动户外", "服饰鞋包"]:
            p.skus = [
                {"specs": {"尺码": "M", "颜色": "黑色"}, "price": p.price, "stock": p.stock // 3},
                {"specs": {"尺码": "L", "颜色": "黑色"}, "price": p.price, "stock": p.stock // 3},
                {"specs": {"尺码": "XL", "颜色": "黑色"}, "price": p.price, "stock": p.stock // 3},
            ]
        elif p.category == "个护美妆":
            p.skus = [
                {"specs": {"规格": "标准装"}, "price": p.price, "stock": p.stock},
            ]

    # 添加划线价（原价）
    if not p.original_price:
        p.original_price = int(p.price * 1.2)  # 原价比售价高 20%

    # 标记热销和新品
    if p.sales > 0:
        p.is_hot = True
    if p.id <= 20:
        p.is_new = True

print(f"  Updated {len(products_to_update)} products with images, specs, and SKUs")

db.commit()
db.close()
print("Seed complete.")
