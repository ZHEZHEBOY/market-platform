# -*- coding: utf-8 -*-
"""
同义词词典 — 扩展搜索查询，提高召回率
"""
import re
from typing import Optional

# 同义词映射 (主词 -> 同义词列表)
SYNONYM_MAP = {
    # 手机
    "手机": ["智能手机", "移动电话", "phone", "手机"],
    "智能手机": ["手机", "移动电话", "phone"],
    "phone": ["手机", "智能手机"],

    # 电脑
    "笔记本": ["笔记本电脑", "laptop", "便携电脑"],
    "笔记本电脑": ["笔记本", "laptop"],
    "laptop": ["笔记本", "笔记本电脑"],
    "台式机": ["台式电脑", "desktop", "PC"],
    "平板": ["平板电脑", "tablet", "pad"],
    "平板电脑": ["平板", "tablet", "pad"],

    # 耳机
    "耳机": ["耳麦", "头戴式耳机", "earphone", "headphone", "耳塞"],
    "耳麦": ["耳机", "headphone"],
    "蓝牙耳机": ["无线耳机", "TWS", "真无线耳机"],
    "无线耳机": ["蓝牙耳机", "TWS"],

    # 音箱
    "音箱": ["音响", "扬声器", "speaker", "蓝牙音箱"],
    "音响": ["音箱", "speaker"],

    # 手表
    "手表": ["腕表", "watch", "智能手表"],
    "智能手表": ["手表", "smartwatch", "运动手表"],
    "运动手表": ["智能手表", "运动腕表"],

    # 手环
    "手环": ["智能手环", "运动手环", "band"],
    "智能手环": ["手环", "band"],

    # 充电
    "充电器": ["电源适配器", "charger", "充电头"],
    "充电宝": ["移动电源", "移动充电器", "power bank"],
    "移动电源": ["充电宝", "power bank"],
    "数据线": ["充电线", "USB线", "连接线"],

    # 电视
    "电视": ["电视机", "智能电视", "TV"],
    "电视机": ["电视", "TV"],
    "智能电视": ["电视", "TV"],

    # 冰箱
    "冰箱": ["电冰箱", "冷藏柜", "refrigerator"],
    "电冰箱": ["冰箱"],

    # 洗衣机
    "洗衣机": ["洗衣设备", "washer", "洗烘一体机"],
    "洗烘一体机": ["洗衣机", "烘干机"],

    # 空调
    "空调": ["冷气机", "冷暖空调", "air conditioner"],
    "冷气机": ["空调"],

    # 吸尘器
    "吸尘器": ["除尘器", "vacuum cleaner", "扫地机", "扫地机器人"],
    "扫地机器人": ["扫地机", "吸尘器", "机器人吸尘器", "扫拖一体机"],
    "扫地机": ["扫地机器人", "吸尘器"],

    # 化妆品
    "洗面奶": ["洁面乳", "洗面乳", "face wash", "洁面"],
    "洁面乳": ["洗面奶", "face wash"],
    "面膜": ["面贴膜", "face mask", "护肤面膜"],
    "口红": ["唇膏", "唇彩", "lipstick"],
    "唇膏": ["口红", "lipstick"],
    "防晒霜": ["防晒乳", "sunscreen", "防晒"],
    "精华": ["精华液", "精华露", "serum"],
    "精华液": ["精华", "serum"],
    "面霜": ["护肤霜", "保湿霜", "cream"],
    "乳液": ["护肤乳", "保湿乳", "lotion"],
    "爽肤水": ["化妆水", "柔肤水", "toner"],

    # 服装
    "T恤": ["T恤衫", "短袖", "t-shirt"],
    "短袖": ["T恤", "t-shirt"],
    "衬衫": ["衬衣", "shirt"],
    "衬衣": ["衬衫", "shirt"],
    "卫衣": ["帽衫", "运动衫", "hoodie", "sweatshirt"],
    "夹克": ["外套", "jacket", "风衣"],
    "外套": ["夹克", "jacket"],
    "羽绒服": ["羽绒外套", "down jacket"],
    "牛仔裤": ["jeans", "牛仔"],
    "运动裤": ["休闲裤", "卫裤", "sweatpants"],
    "运动鞋": ["跑鞋", "球鞋", "sneakers"],
    "跑鞋": ["运动鞋", "跑步鞋", "running shoes"],
    "板鞋": ["休闲鞋", "sneakers"],
    "帆布鞋": ["converse", "匡威"],

    # 食品
    "咖啡": ["coffee", "咖啡豆", "挂耳咖啡"],
    "牛奶": ["纯牛奶", "鲜牛奶", "milk"],
    "酸奶": ["酸牛奶", "yogurt"],
    "坚果": ["干果", "nuts"],
    "薯片": ["土豆片", "chips"],
    "饼干": ["曲奇", "cookie", "biscuit"],
    "可乐": ["可口可乐", "百事可乐", "cola"],

    # 图书
    "书": ["图书", "书籍", "book"],
    "图书": ["书", "书籍", "book"],
    "教材": ["课本", "教科书", "textbook"],
    "小说": ["文学作品", "novel"],

    # 母婴
    "奶粉": ["婴幼儿奶粉", "baby formula", "配方奶粉"],
    "纸尿裤": ["尿不湿", "diaper", "尿片"],
    "尿不湿": ["纸尿裤", "diaper"],
    "奶瓶": ["baby bottle", "喂奶瓶"],

    # 运动
    "瑜伽垫": ["yoga mat", "健身垫"],
    "哑铃": ["dumbbell", "健身哑铃"],
    "跑步机": ["treadmill", "健身跑步机"],
    "自行车": ["单车", "bike", "脚踏车"],
    "泳镜": ["swimming goggles", "游泳镜"],
    "泳帽": ["swimming cap", "游泳帽"],

    # 家居
    "沙发": ["sofa", "座椅"],
    "书架": ["书柜", "置物架"],
    "床架": ["床", "bed frame"],
    "台灯": ["desk lamp", "阅读灯"],
    "香薰机": ["加湿器", "香薰灯", "香薰加湿器"],
    "净水器": ["净水机", "water purifier"],
    "加湿器": ["humidifier", "空气加湿器"],
    "除湿机": ["dehumidifier", "抽湿机"],

    # 厨房
    "电饭煲": ["电饭锅", "rice cooker"],
    "微波炉": ["microwave", "微波烤箱"],
    "烤箱": ["oven", "电烤箱"],
    "空气炸锅": ["air fryer", "无油炸锅"],
    "豆浆机": ["soy milk maker"],
    "洗碗机": ["dishwasher"],
    "咖啡机": ["coffee machine", "咖啡壶"],

    # 数码配件
    "键盘": ["keyboard", "机械键盘"],
    "机械键盘": ["键盘", "mechanical keyboard"],
    "鼠标": ["mouse", "电竞鼠标"],
    "显示器": ["monitor", "屏幕", "电竞显示器"],
    "摄像头": ["webcam", "相机", "网络摄像头"],
    "耳机": ["headphone", "earphone", "耳麦"],
    "麦克风": ["microphone", "话筒", "mic"],

    # 礼物相关
    "送女朋友": ["送女生", "女生礼物", "女性礼物", "送老婆"],
    "送男朋友": ["送男生", "男生礼物", "男性礼物", "送老公"],
    "生日礼物": ["生日", "礼物", "gift"],
    "情人节礼物": ["情人节", "七夕礼物"],
    "礼物": ["礼品", "gift", "present"],
}

# 品类关键词 -> 分类映射
CATEGORY_KEYWORDS = {
    "手机": "手机通讯",
    "电话": "手机通讯",
    "笔记本": "电脑办公",
    "电脑": "电脑办公",
    "平板": "电脑办公",
    "显示器": "电脑办公",
    "键盘": "电脑办公",
    "鼠标": "电脑办公",
    "耳机": "数码配件",
    "音箱": "数码配件",
    "充电器": "数码配件",
    "充电宝": "数码配件",
    "数据线": "数码配件",
    "手表": "智能设备",
    "手环": "智能设备",
    "电视": "家用电器",
    "冰箱": "家用电器",
    "洗衣机": "家用电器",
    "空调": "家用电器",
    "吸尘器": "家用电器",
    "扫地机": "家用电器",
    "电饭煲": "厨房电器",
    "微波炉": "厨房电器",
    "烤箱": "厨房电器",
    "空气炸锅": "厨房电器",
    "洗面奶": "个护美妆",
    "面膜": "个护美妆",
    "口红": "个护美妆",
    "精华": "个护美妆",
    "防晒": "个护美妆",
    "T恤": "服饰鞋包",
    "衬衫": "服饰鞋包",
    "牛仔裤": "服饰鞋包",
    "运动鞋": "服饰鞋包",
    "跑鞋": "服饰鞋包",
    "咖啡": "食品饮料",
    "牛奶": "食品饮料",
    "坚果": "食品饮料",
    "奶粉": "母婴玩具",
    "纸尿裤": "母婴玩具",
    "玩具": "母婴玩具",
    "书": "图书文具",
    "瑜伽": "运动户外",
    "跑步": "运动户外",
    "自行车": "运动户外",
    "泳镜": "运动户外",
    "沙发": "家居日用",
    "台灯": "家居日用",
    "净水器": "家居日用",
    "苹果": "生鲜果蔬",
    "草莓": "生鲜果蔬",
    "牛排": "生鲜果蔬",
}


def expand_query(query: str) -> list[str]:
    """扩展搜索查询

    Args:
        query: 原始查询

    Returns:
        扩展后的查询列表 (包含原始查询)
    """
    queries = [query]
    query_lower = query.lower().strip()

    # 1. 精确匹配同义词
    for key, synonyms in SYNONYM_MAP.items():
        if key in query_lower or query_lower in key:
            for syn in synonyms:
                expanded = query_lower.replace(key, syn)
                if expanded not in queries:
                    queries.append(expanded)

    # 2. 模糊匹配 (包含关系)
    for key, synonyms in SYNONYM_MAP.items():
        if any(kw in query_lower for kw in key.split()):
            for syn in synonyms[:2]:  # 只取前2个同义词
                if syn not in queries and len(syn) > 1:
                    queries.append(syn)

    # 去重并限制数量
    unique = []
    seen = set()
    for q in queries:
        q_clean = q.strip()
        if q_clean and q_clean not in seen:
            seen.add(q_clean)
            unique.append(q_clean)

    return unique[:5]  # 最多5个扩展查询


def get_category_hint(query: str) -> Optional[str]:
    """从查询中推断可能的商品分类

    Args:
        query: 搜索查询

    Returns:
        推断的分类名，或 None
    """
    query_lower = query.lower()
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in query_lower:
            return category
    return None
