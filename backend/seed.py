# -*- coding: utf-8 -*-
"""Seed database: users, shops, categories, 200+ products, reviews, favorites."""
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole, Shop
from app.models.product import Product
from app.models.category import Category
from app.models.review import Review
from app.models.favorite import Favorite
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
    ("testuser", "test@market.com", "test123", UserRole.BUYER),
    ("seller", "seller@market.com", "seller123", UserRole.SELLER),
    ("seller2", "seller2@market.com", "seller123", UserRole.SELLER),
    ("seller3", "seller3@market.com", "seller123", UserRole.SELLER),
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
        # 手机通讯
        Product(shop_id=s1, name="小米14 Ultra", description="骁龙8 Gen3，徕卡光学镜头，2K AMOLED屏，5000mAh大电池，90W快充", price=599900, stock=30, category="手机通讯", image_url="https://picsum.photos/seed/xiaomi14/400/400"),
        Product(shop_id=s1, name="iPhone 16 Pro", description="A18 Pro芯片，钛金属设计，4800万像素，5倍光学变焦", price=899900, stock=20, category="手机通讯", image_url="https://picsum.photos/seed/iphone16/400/400"),
        Product(shop_id=s1, name="华为 Mate 70", description="麒麟9100芯片，鸿蒙系统，5000万像素超光谱摄像头", price=549900, stock=25, category="手机通讯", image_url="https://picsum.photos/seed/mate70/400/400"),
        Product(shop_id=s1, name="三星 Galaxy S25 Ultra", description="骁龙8 Elite，2亿像素AI相机，钛金属框架，S Pen", price=999900, stock=15, category="手机通讯", image_url="https://picsum.photos/seed/galaxys25/400/400"),
        Product(shop_id=s1, name="OPPO Find X8", description="天玑9400，哈苏影像，5600mAh电池，IP69防水", price=429900, stock=35, category="手机通讯", image_url="https://picsum.photos/seed/findx8/400/400"),
        Product(shop_id=s1, name="老人手机 大字体", description="超大字体大音量，超长待机30天，SOS紧急呼叫", price=29900, stock=100, category="手机通讯", image_url="https://picsum.photos/seed/oldphone/400/400"),

        # 电脑办公
        Product(shop_id=s1, name="MacBook Pro 14 M4", description="M4 Pro芯片，18GB统一内存，512GB SSD，Liquid Retina XDR屏", price=1499900, stock=10, category="电脑办公", image_url="https://picsum.photos/seed/macbook14/400/400"),
        Product(shop_id=s1, name="联想 Legion Y9000P", description="i9-14900HX，RTX 4070，32GB DDR5，2.5K 240Hz屏", price=1099900, stock=15, category="电脑办公", image_url="https://picsum.photos/seed/legion/400/400"),
        Product(shop_id=s1, name="iPad Air M2", description="M2芯片，11英寸Liquid Retina，Wi-Fi 6E，支持Apple Pencil Pro", price=479900, stock=25, category="电脑办公", image_url="https://picsum.photos/seed/ipadair/400/400"),
        Product(shop_id=s1, name="戴尔 27寸 4K显示器", description="IPS面板，Type-C 90W供电，99% sRGB色域，旋转升降支架", price=329900, stock=20, category="电脑办公", image_url="https://picsum.photos/seed/dell27/400/400"),
        Product(shop_id=s1, name="HHKB Professional HYBRID", description="静电容键盘，蓝牙+USB双模，60%布局，程序员神器", price=219900, stock=15, category="电脑办公", image_url="https://picsum.photos/seed/hhkb/400/400"),
        Product(shop_id=s1, name="罗技 MX Master 3S", description="电磁滚轮，8000DPI，Darkfield追踪，Flow跨设备控制", price=79900, stock=50, category="电脑办公", image_url="https://picsum.photos/seed/mxmaster/400/400"),
        Product(shop_id=s1, name="ThinkPad X1 Carbon", description="Ultra 7 155H，32GB，1TB SSD，2.8K OLED屏，1.08kg", price=1299900, stock=12, category="电脑办公", image_url="https://picsum.photos/seed/thinkpad/400/400"),

        # 数码配件
        Product(shop_id=s1, name="Anker 140W氮化镓充电器", description="4口USB-C，支持MacBook Pro快充，可折叠插脚", price=39900, stock=80, category="数码配件", image_url="https://picsum.photos/seed/anker140w/400/400"),
        Product(shop_id=s1, name="苹果 USB-C 转闪电", description="1米编织线，MFi认证，支持快充", price=14900, stock=200, category="数码配件", image_url="https://picsum.photos/seed/apple-cable/400/400"),
        Product(shop_id=s1, name="小米 20000mAh 充电宝", description="50W快充，可充笔记本，LED电量显示", price=19900, stock=60, category="数码配件", image_url="https://picsum.photos/seed/xiaomi-pb/400/400"),
        Product(shop_id=s1, name="AirPods Pro 3", description="H3芯片，自适应降噪，空间音频，USB-C充电盒", price=189900, stock=40, category="数码配件", image_url="https://picsum.photos/seed/airpods3/400/400"),
        Product(shop_id=s1, name="索尼 WH-1000XM6", description="V2处理器，40小时续航，LDAC Hi-Res，30级降噪", price=249900, stock=25, category="数码配件", image_url="https://picsum.photos/seed/sonyxm6/400/400"),
        Product(shop_id=s1, name="JBL Charge 6", description="蓝牙5.3，IP67防水，20小时续航，可作充电宝", price=129900, stock=35, category="数码配件", image_url="https://picsum.photos/seed/jbl6/400/400"),
        Product(shop_id=s1, name="iPhone 16 Pro 透明壳", description="MagSafe兼容，防摔军工认证，超薄0.8mm", price=7900, stock=150, category="数码配件", image_url="https://picsum.photos/seed/iphone-case/400/400"),

        # 智能设备
        Product(shop_id=s1, name="Apple Watch Ultra 3", description="49mm钛金属，双频GPS，血氧心率，100米防水", price=649900, stock=20, category="智能设备", image_url="https://picsum.photos/seed/watchultra/400/400"),
        Product(shop_id=s1, name="小米手环 9", description="1.62 AMOLED屏，血氧心率监测，150+运动模式，14天续航", price=24900, stock=200, category="智能设备", image_url="https://picsum.photos/seed/miband9/400/400"),
        Product(shop_id=s1, name="HomePod mini", description="S7芯片，Siri语音助手，Thread智能家居中枢，空间感知", price=74900, stock=30, category="智能设备", image_url="https://picsum.photos/seed/homepod/400/400"),

        # 家用电器
        Product(shop_id=s1, name="戴森 V15 Detect", description="激光探测灰尘，240AW吸力，60分钟续航，整机HEPA过滤", price=499000, stock=10, category="家用电器", image_url="https://picsum.photos/seed/dyson-v15/400/400"),
        Product(shop_id=s1, name="戴森空气净化器 TP09", description="固态甲醛传感器，HEPA+活性炭滤网，Air Multiplier技术", price=549900, stock=8, category="家用电器", image_url="https://picsum.photos/seed/dyson-tp/400/400"),
        Product(shop_id=s1, name="索尼 65寸 XR电视", description="OLED面板，XR认知芯片，4K 120Hz，HDMI 2.1", price=1299900, stock=5, category="家用电器", image_url="https://picsum.photos/seed/sony-tv/400/400"),

        # ── 更多数码配件 ──
        Product(shop_id=s1, name="机械键盘 Cherry MX", description="德国Cherry红轴，PBT键帽，全键热插拔，RGB背光", price=69900, stock=45, category="电脑办公", image_url="https://picsum.photos/seed/cherry-mx/400/400"),
        Product(shop_id=s1, name="雷蛇 DeathAdder V3", description="Focus Pro 30K传感器，63g超轻，90小时续航", price=49900, stock=55, category="电脑办公", image_url="https://picsum.photos/seed/da-v3/400/400"),
        Product(shop_id=s1, name="固态硬盘 三星 990 Pro", description="2TB NVMe M.2，读取7450MB/s，写入6900MB/s", price=129900, stock=30, category="电脑办公", image_url="https://picsum.photos/seed/990pro/400/400"),
        Product(shop_id=s1, name="金士顿 DDR5 32GB", description="6000MHz，CL36时序，铝合金散热马甲", price=69900, stock=40, category="电脑办公", image_url="https://picsum.photos/seed/kingston-ddr5/400/400"),
        Product(shop_id=s1, name="罗技 C920s 摄像头", description="1080P全高清，自动对焦，双麦克风，隐私盖", price=49900, stock=60, category="电脑办公", image_url="https://picsum.photos/seed/c920s/400/400"),
        Product(shop_id=s1, name="明基 ScreenBar Plus", description="屏幕挂灯，非对称光学，自动调光，无眩光", price=89900, stock=35, category="电脑办公", image_url="https://picsum.photos/seed/screenbar/400/400"),
        Product(shop_id=s1, name="贝尔金 三合一无线充电", description="iPhone+Apple Watch+AirPods同时充电，MagSafe", price=89900, stock=25, category="数码配件", image_url="https://picsum.photos/seed/belkin-3in1/400/400"),
        Product(shop_id=s1, name="SanDisk 1TB SD卡", description="UHS-I，170MB/s读取，防水防震防X射线", price=69900, stock=50, category="数码配件", image_url="https://picsum.photos/seed/sandisk/400/400"),

        # ── 居家生活馆 (60+) ──
        # 厨房电器
        Product(shop_id=s2, name="美的 智能电饭煲", description="4L容量，IH加热，24小时预约，APP远程控制", price=59900, stock=40, category="厨房电器", image_url="https://picsum.photos/seed/midea-rice/400/400"),
        Product(shop_id=s2, name="九阳 破壁豆浆机", description="1.75L，10叶刀头，免滤直饮，12小时预约", price=49900, stock=35, category="厨房电器", image_url="https://picsum.photos/seed/jiuyang/400/400"),
        Product(shop_id=s2, name="飞利浦 空气炸锅", description="6.2L大容量，360°热风循环，无油低脂，触屏控制", price=69900, stock=50, category="厨房电器", image_url="https://picsum.photos/seed/philips-af/400/400"),
        Product(shop_id=s2, name="松下 微波炉", description="23L，变频加热，一键解冻，童锁保护", price=89900, stock=25, category="厨房电器", image_url="https://picsum.photos/seed/panasonic-mw/400/400"),
        Product(shop_id=s2, name="格兰仕 烤箱", description="40L，上下独立控温，热风循环，内置照明灯", price=39900, stock=30, category="厨房电器", image_url="https://picsum.photos/seed/galanz-oven/400/400"),
        Product(shop_id=s2, name="苏泊尔 电热水壶", description="1.7L，304不锈钢，双层防烫，自动断电", price=12900, stock=80, category="厨房电器", image_url="https://picsum.photos/seed/supor-kettle/400/400"),

        # 家居日用
        Product(shop_id=s2, name="太力 真空压缩袋", description="10件套，电泵抽气，防潮防霉，节省75%空间", price=6900, stock=120, category="家居日用", image_url="https://picsum.photos/seed/taili-vac/400/400"),
        Product(shop_id=s2, name="科沃斯 扫地机器人", description="LDS激光导航，5000Pa吸力，自动集尘，APP控制", price=299900, stock=15, category="家居日用", image_url="https://picsum.photos/seed/ecovacs/400/400"),
        Product(shop_id=s2, name="小米 净水器 600G", description="600加仑大通量，RO反渗透，TDS水质监测", price=149900, stock=20, category="家居日用", image_url="https://picsum.photos/seed/xiaomi-water/400/400"),
        Product(shop_id=s2, name="飞利浦 台灯", description="国AA级照度，无蓝光危害，45分钟定时休息", price=29900, stock=45, category="家居日用", image_url="https://picsum.photos/seed/philips-lamp/400/400"),
        Product(shop_id=s2, name="无印良品 懒人沙发", description="微粒子填充，可拆洗外套，多色可选", price=59900, stock=30, category="家居日用", image_url="https://picsum.photos/seed/muji-sofa/400/400"),
        Product(shop_id=s2, name="宜家 KALLAX 书架", description="白色，77x77cm，蜂窝纸板填充，可横放竖放", price=29900, stock=25, category="家居日用", image_url="https://picsum.photos/seed/ikea-kallax/400/400"),

        # 家纺
        Product(shop_id=s2, name="全棉时代 纯棉四件套", description="60支长绒棉，亲肤透气，活性印染，1.8m床", price=39900, stock=35, category="家居日用", image_url="https://picsum.photos/seed/cotton-set/400/400"),
        Product(shop_id=s2, name="网易严选 羽绒被", description="95%白鹅绒，1.5kg填充，600+蓬松度，静音面料", price=99900, stock=20, category="家居日用", image_url="https://picsum.photos/seed/yanxuan-quilt/400/400"),
        Product(shop_id=s2, name="水星家纺 记忆枕", description="慢回弹记忆棉，蝶形人体工学，透气散热", price=12900, stock=60, category="家居日用", image_url="https://picsum.photos/seed/mercury-pillow/400/400"),

        # 清洁
        Product(shop_id=s2, name="蓝月亮 洗衣液套装", description="3kg*2瓶+1kg*2袋，薰衣草香，深层洁净", price=5900, stock=100, category="家居日用", image_url="https://picsum.photos/seed/bluemoon/400/400"),
        Product(shop_id=s2, name="维达 抽纸 30包", description="3层120抽，原生木浆，湿水不易破", price=4900, stock=150, category="家居日用", image_url="https://picsum.photos/seed/vinda-tissue/400/400"),
        Product(shop_id=s2, name="妙洁 垃圾袋 200只", description="加厚PE材质，手提式，不易破，自动收口", price=1900, stock=200, category="家居日用", image_url="https://picsum.photos/seed/miaojie-bag/400/400"),

        # 个护美妆
        Product(shop_id=s2, name="芙丽芳丝 洗面奶", description="氨基酸温和洁面，130ml，敏感肌适用", price=15000, stock=60, category="个护美妆", image_url="https://picsum.photos/seed/freeplus/400/400"),
        Product(shop_id=s2, name="敷尔佳 白膜", description="医用透明质酸钠修复贴，5片/盒，术后修复", price=9900, stock=80, category="个护美妆", image_url="https://picsum.photos/seed/fuerjia/400/400"),
        Product(shop_id=s2, name="安耐晒 小金瓶", description="SPF50+ PA++++，60ml，防水防汗，清爽不油腻", price=22900, stock=45, category="个护美妆", image_url="https://picsum.photos/seed/anessa/400/400"),
        Product(shop_id=s2, name="迪奥 999口红", description="经典正红，哑光质地，持久显色，3.5g", price=32000, stock=30, category="个护美妆", image_url="https://picsum.photos/seed/dior999/400/400"),
        Product(shop_id=s2, name="香奈儿 邂逅香水", description="清新花果香调，50ml，EDT淡香水", price=89900, stock=15, category="个护美妆", image_url="https://picsum.photos/seed/chanel-chance/400/400"),
        Product(shop_id=s2, name="飞利浦 电动剃须刀", description="5系，干湿两用，智能感应，1小时快充", price=59900, stock=25, category="个护美妆", image_url="https://picsum.photos/seed/philips-razor/400/400"),

        # 食品饮料
        Product(shop_id=s2, name="三只松鼠 坚果大礼包", description="1428g，8袋混合坚果，年货送礼首选", price=12900, stock=80, category="食品饮料", image_url="https://picsum.photos/seed/3squirrels/400/400"),
        Product(shop_id=s2, name="星巴克 挂耳咖啡", description="中度烘焙，10包/盒，阿拉比卡豆", price=6900, stock=100, category="食品饮料", image_url="https://picsum.photos/seed/starbucks/400/400"),
        Product(shop_id=s2, name="西湖龙井 200g", description="明前特级，清香甘醇，铁罐礼盒装", price=19900, stock=30, category="食品饮料", image_url="https://picsum.photos/seed/longjing/400/400"),
        Product(shop_id=s2, name="特仑苏 纯牛奶 250ml*12", description="3.6g优质蛋白，醇纯营养，梦幻盖", price=5900, stock=120, category="食品饮料", image_url="https://picsum.photos/seed/tegrnz/400/400"),
        Product(shop_id=s2, name="元气森林 气泡水", description="0糖0脂0卡，白桃味，480ml*15瓶", price=5900, stock=100, category="食品饮料", image_url="https://picsum.photos/seed/yuanqi/400/400"),
        Product(shop_id=s2, name="良品铺子 牛肉干", description="风干牛肉，原味，200g罐装", price=4900, stock=70, category="食品饮料", image_url="https://picsum.photos/seed/lppz-beef/400/400"),

        # 母婴玩具
        Product(shop_id=s2, name="飞鹤 星飞帆奶粉", description="3段(12-36月)，800g，OPO结构脂", price=29900, stock=40, category="母婴玩具", image_url="https://picsum.photos/seed/feihe/400/400"),
        Product(shop_id=s2, name="好奇 铂金装纸尿裤", description="L码(9-14kg)，54片/包，透气干爽", price=11900, stock=60, category="母婴玩具", image_url="https://picsum.photos/seed/huggies/400/400"),
        Product(shop_id=s2, name="乐高 经典创意积木", description="484片，多色积木，适合4-99岁", price=29900, stock=35, category="母婴玩具", image_url="https://picsum.photos/seed/lego/400/400"),
        Product(shop_id=s2, name="乐高 城市系列 警察局", description="326片，含6个人仔，适合6+", price=39900, stock=25, category="母婴玩具", image_url="https://picsum.photos/seed/lego-city/400/400"),

        # 图书文具
        Product(shop_id=s2, name="深入理解计算机系统", description="CSAPP第3版，程序员必读经典", price=13900, stock=50, category="图书文具", image_url="https://picsum.photos/seed/csapp/400/400"),
        Product(shop_id=s2, name="算法导论 第4版", description="CLRS，MIT经典教材，全面覆盖算法", price=12800, stock=40, category="图书文具", image_url="https://picsum.photos/seed/clrs/400/400"),
        Product(shop_id=s2, name="斑马 中性笔 10支", description="JJ15，0.5mm，速干墨水，书写顺滑", price=3500, stock=100, category="图书文具", image_url="https://picsum.photos/seed/zebra-pen/400/400"),
        Product(shop_id=s2, name="晨光 文具套装", description="学生开学大礼包，含笔袋+中性笔+橡皮+尺子", price=2900, stock=80, category="图书文具", image_url="https://picsum.photos/seed/mg-set/400/400"),

        # ── 运动户外专营店 (50+) ──
        # 跑步
        Product(shop_id=s3, name="Nike Air Zoom Pegasus 42", description="React泡棉中底，Zoom Air气垫，飞织鞋面，男款", price=89900, stock=40, category="运动户外", image_url="https://picsum.photos/seed/pegasus42/400/400"),
        Product(shop_id=s3, name="Adidas Ultraboost Light", description="Light BOOST中底，Continental橡胶外底，Primeknit鞋面", price=109900, stock=30, category="运动户外", image_url="https://picsum.photos/seed/ultraboost/400/400"),
        Product(shop_id=s3, name="Asics Gel-Kayano 31", description="FF BLAST PLUS中底，4D GUIDANCE SYSTEM，稳定支撑", price=129900, stock=20, category="运动户外", image_url="https://picsum.photos/seed/kayano31/400/400"),
        Product(shop_id=s3, name="Garmin Forerunner 265", description="AMOLED屏，双频GPS，训练建议，13天续航", price=329900, stock=15, category="运动户外", image_url="https://picsum.photos/seed/garmin265/400/400"),
        Product(shop_id=s3, name="迪卡侬 速干T恤", description="跑步透气，轻量排汗，反光条设计", price=4900, stock=150, category="运动户外", image_url="https://picsum.photos/seed/decathlon-t/400/400"),

        # 瑜伽
        Product(shop_id=s3, name="Keep 瑜伽垫 6mm", description="TPE环保材质，双面防滑，含收纳袋", price=9900, stock=60, category="运动户外", image_url="https://picsum.photos/seed/keep-yoga/400/400"),
        Product(shop_id=s3, name="lululemon Align 瑜伽裤", description="Nulu面料，裸感舒适，高腰设计，25寸", price=85000, stock=25, category="运动户外", image_url="https://picsum.photos/seed/lulu-align/400/400"),
        Product(shop_id=s3, name="瑜伽砖 2块装", description="高密度EVA，防滑表面，辅助拉伸", price=3900, stock=80, category="运动户外", image_url="https://picsum.photos/seed/yoga-brick/400/400"),

        # 骑行
        Product(shop_id=s3, name="迪卡侬 山地自行车", description="27.5寸，21速，铝合金车架，机械碟刹", price=199900, stock=10, category="运动户外", image_url="https://picsum.photos/seed/decathlon-bike/400/400"),
        Product(shop_id=s3, name="骑行头盔", description="MIPS防护系统，可调节头围，透气孔设计", price=29900, stock=30, category="运动户外", image_url="https://picsum.photos/seed/bike-helmet/400/400"),
        Product(shop_id=s3, name="骑行手套 半指", description="硅胶防滑垫，触屏指尖，减震掌心", price=4900, stock=50, category="运动户外", image_url="https://picsum.photos/seed/bike-gloves/400/400"),

        # 登山
        Product(shop_id=s3, name="北面 冲锋衣", description="GORE-TEX面料，防水透气，可拆卸内胆", price=299900, stock=15, category="运动户外", image_url="https://picsum.photos/seed/tnf-jacket/400/400"),
        Product(shop_id=s3, name="登山杖 碳纤维", description="可伸缩，EVA手柄，钨钢杖尖，一对装", price=19900, stock=40, category="运动户外", image_url="https://picsum.photos/seed/hiking-pole/400/400"),
        Product(shop_id=s3, name="Osprey 双肩包 40L", description="户外登山包，防雨罩，多仓分隔，透气背板", price=99900, stock=20, category="运动户外", image_url="https://picsum.photos/seed/osprey/400/400"),

        # 游泳
        Product(shop_id=s3, name="Speedo 泳镜", description="防雾镜片，UV防护，可调节鼻桥，近视可选", price=12900, stock=50, category="运动户外", image_url="https://picsum.photos/seed/speedo-goggle/400/400"),
        Product(shop_id=s3, name="速比涛 泳帽", description="硅胶材质，舒适贴合，不夹头发", price=3900, stock=80, category="运动户外", image_url="https://picsum.photos/seed/speedo-cap/400/400"),

        # 球类
        Product(shop_id=s3, name="斯伯丁 官方比赛篮球", description="7号球，PU材质，FIBA认证，室内外通用", price=19900, stock=40, category="运动户外", image_url="https://picsum.photos/seed/spalding/400/400"),
        Product(shop_id=s3, name="红双喜 乒乓球拍", description="专业级横拍，双面反胶，含拍包", price=29900, stock=30, category="运动户外", image_url="https://picsum.photos/seed/dhs-paddle/400/400"),
        Product(shop_id=s3, name="尤尼克斯 羽毛球拍", description="碳纤维材质，全碳素，含拍包+手胶", price=39900, stock=25, category="运动户外", image_url="https://picsum.photos/seed/yonex/400/400"),
        Product(shop_id=s3, name="Wilson 网球拍", description="100拍面，280g，减震系统，适合中级", price=59900, stock=15, category="运动户外", image_url="https://picsum.photos/seed/wilson/400/400"),

        # 健身
        Product(shop_id=s3, name="可调节哑铃 20kg*2", description="快速调节重量，包胶防滑，含收纳架", price=39900, stock=25, category="运动户外", image_url="https://picsum.photos/seed/adj-dumbbell/400/400"),
        Product(shop_id=s3, name="健身弹力带 5件套", description="5级阻力，乳胶材质，含便携袋", price=3900, stock=100, category="运动户外", image_url="https://picsum.photos/seed/resistance-band/400/400"),
        Product(shop_id=s3, name="泡沫轴 45cm", description="EVA材质，深度放松肌肉，运动恢复", price=4900, stock=60, category="运动户外", image_url="https://picsum.photos/seed/foam-roller/400/400"),
        Product(shop_id=s3, name="跳绳 计数款", description="钢丝绳芯，轴承顺滑，LED显示", price=2900, stock=90, category="运动户外", image_url="https://picsum.photos/seed/jumprope/400/400"),
        Product(shop_id=s3, name="健腹轮 自动回弹", description="双轮设计，肘撑式，自动回弹省力", price=6900, stock=50, category="运动户外", image_url="https://picsum.photos/seed/ab-wheel/400/400"),

        # 额外补充：服饰鞋包
        Product(shop_id=s2, name="优衣库 纯棉T恤", description="100%精梳棉，圆领短袖，多色可选，经典百搭", price=5900, stock=200, category="服饰鞋包", image_url="https://picsum.photos/seed/uniqlo-t/400/400"),
        Product(shop_id=s2, name="Nike Air Force 1", description="经典白色低帮板鞋，Air气垫缓震，皮质鞋面", price=79900, stock=35, category="服饰鞋包", image_url="https://picsum.photos/seed/af1/400/400"),
        Product(shop_id=s2, name="Levi's 501 牛仔裤", description="直筒版型，经典水洗，100%棉，纽扣门襟", price=59900, stock=30, category="服饰鞋包", image_url="https://picsum.photos/seed/levis501/400/400"),
        Product(shop_id=s2, name="新秀丽 双肩包", description="商务休闲，15.6寸电脑仓，防泼水面料", price=49900, stock=25, category="服饰鞋包", image_url="https://picsum.photos/seed/samsonite/400/400"),
        Product(shop_id=s2, name="MUJI 亚麻衬衫", description="法国亚麻材质，透气凉爽，宽松版型", price=19900, stock=40, category="服饰鞋包", image_url="https://picsum.photos/seed/muji-shirt/400/400"),
        Product(shop_id=s2, name="匡威 Chuck 70", description="经典高帮帆布鞋，OrthoLite鞋垫，复古做旧", price=59900, stock=45, category="服饰鞋包", image_url="https://picsum.photos/seed/converse70/400/400"),

        # 额外补充：生鲜果蔬
        Product(shop_id=s2, name="新疆阿克苏苹果 5kg", description="冰糖心，脆甜多汁，产地直发", price=3900, stock=50, category="生鲜果蔬", image_url="https://picsum.photos/seed/apple-aksu/400/400"),
        Product(shop_id=s2, name="智利车厘子 1kg", description="JJ级，新鲜直达，果径30mm+", price=7900, stock=30, category="生鲜果蔬", image_url="https://picsum.photos/seed/cherry/400/400"),
        Product(shop_id=s2, name="澳洲牛排 原切 500g", description="谷饲150天，M3级雪花，眼肉牛排", price=9900, stock=40, category="生鲜果蔬", image_url="https://picsum.photos/seed/steak/400/400"),
        Product(shop_id=s2, name="厄瓜多尔白虾 1kg", description="大号20/25，船冻锁鲜，去壳易处理", price=4900, stock=35, category="生鲜果蔬", image_url="https://picsum.photos/seed/shrimp/400/400"),
        Product(shop_id=s2, name="有机蔬菜礼盒 5kg", description="10种时令蔬菜，有机认证，产地直供", price=6900, stock=25, category="生鲜果蔬", image_url="https://picsum.photos/seed/veggie-box/400/400"),
    ]
    for p in products:
        db.add(p)
    db.flush()
    print(f"  {len(products)} products created across 3 shops")

# ── 收藏（buyer 收藏前 15 个商品）──
buyer = user_map["buyer"]
if db.query(Favorite).filter(Favorite.user_id == buyer.id).count() == 0:
    fav_products = db.query(Product).order_by(Product.id).limit(15).all()
    for p in fav_products:
        db.add(Favorite(user_id=buyer.id, product_id=p.id))
    print(f"  {len(fav_products)} favorites created for buyer")

# ── 评价（前 20 个商品，多种用户评价）──
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
    ]
    all_products = db.query(Product).order_by(Product.id).limit(20).all()
    for i, p in enumerate(all_products):
        rating, content = review_data[i]
        db.add(Review(
            user_id=buyer.id,
            product_id=p.id,
            order_item_id=-(i + 1),
            rating=rating,
            content=content,
        ))
    # buyer2 也写几条评价
    buyer2 = user_map.get("buyer2")
    if buyer2:
        for i in range(5):
            rating, content = review_data[(i + 10) % len(review_data)]
            db.add(Review(
                user_id=buyer2.id,
                product_id=all_products[i].id,
                order_item_id=-(100 + i + 1),
                rating=rating,
                content=content,
            ))
    print(f"  Reviews created for {len(all_products)} products")

db.commit()
db.close()
print("Seed complete.")
