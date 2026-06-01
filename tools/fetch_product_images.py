# -*- coding: utf-8 -*-
"""
为 MallHub 所有商品生成精确的品牌风格图片
策略：
1. 优先匹配 real/ 目录已有图片
2. 生成精美品牌 SVG 占位图（带品牌色+Logo文字+品类图标）
"""
import os
import re
import sys
import json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEED_FILE = Path(__file__).parent.parent / "backend" / "seed.py"
REAL_DIR = Path(__file__).parent.parent / "backend" / "static" / "products" / "real"
OUTPUT_DIR = Path(__file__).parent.parent / "backend" / "static" / "products" / "final"
MAPPING_FILE = OUTPUT_DIR / "image_mapping.json"

# 品牌 → (背景色, 文字色, 品牌简称)
BRANDS = {
    "apple":    ("#1a1a1a", "#ffffff", "Apple"),
    "iphone":   ("#1a1a1a", "#ffffff", "iPhone"),
    "macbook":  ("#1a1a1a", "#ffffff", "MacBook"),
    "ipad":     ("#1a1a1a", "#ffffff", "iPad"),
    "airpods":  ("#1a1a1a", "#ffffff", "AirPods"),
    "apple watch": ("#1a1a1a", "#ffffff", "Apple Watch"),
    "homepod":  ("#1a1a1a", "#ffffff", "HomePod"),
    "magsafe":  ("#1a1a1a", "#ffffff", "MagSafe"),
    "小米":     ("#ff6900", "#ffffff", "小米"),
    "xiaomi":   ("#ff6900", "#ffffff", "Xiaomi"),
    "redmi":    ("#ff6900", "#ffffff", "Redmi"),
    "华为":     ("#cf0a2c", "#ffffff", "华为"),
    "huawei":   ("#cf0a2c", "#ffffff", "Huawei"),
    "三星":     ("#1428a0", "#ffffff", "三星"),
    "samsung":  ("#1428a0", "#ffffff", "Samsung"),
    "galaxy":   ("#1428a0", "#ffffff", "Galaxy"),
    "oppo":     ("#1a73e8", "#ffffff", "OPPO"),
    "vivo":     ("#415fff", "#ffffff", "vivo"),
    "一加":     ("#eb0028", "#ffffff", "一加"),
    "oneplus":  ("#eb0028", "#ffffff", "OnePlus"),
    "荣耀":     ("#0ab4e8", "#ffffff", "荣耀"),
    "honor":    ("#0ab4e8", "#ffffff", "Honor"),
    "索尼":     ("#1a1a1a", "#ffffff", "索尼"),
    "sony":     ("#1a1a1a", "#ffffff", "Sony"),
    "戴森":     ("#6b21a8", "#ffffff", "戴森"),
    "dyson":    ("#6b21a8", "#ffffff", "Dyson"),
    "nike":     ("#1a1a1a", "#ffffff", "Nike"),
    "adidas":   ("#1a1a1a", "#ffffff", "Adidas"),
    "联想":     ("#e4002b", "#ffffff", "联想"),
    "lenovo":   ("#e4002b", "#ffffff", "Lenovo"),
    "thinkpad": ("#e4002b", "#ffffff", "ThinkPad"),
    "legion":   ("#e4002b", "#ffffff", "Legion"),
    "戴尔":     ("#007db8", "#ffffff", "戴尔"),
    "dell":     ("#007db8", "#ffffff", "Dell"),
    "xps":      ("#007db8", "#ffffff", "XPS"),
    "华硕":     ("#ff005a", "#ffffff", "华硕"),
    "rog":      ("#ff005a", "#ffffff", "ROG"),
    "罗技":     ("#00b894", "#ffffff", "罗技"),
    "logitech": ("#00b894", "#ffffff", "Logitech"),
    "雷蛇":     ("#44d62c", "#000000", "雷蛇"),
    "razer":    ("#44d62c", "#000000", "Razer"),
    "飞利浦":   ("#0ab4e8", "#ffffff", "飞利浦"),
    "philips":  ("#0ab4e8", "#ffffff", "Philips"),
    "美的":     ("#00b894", "#ffffff", "美的"),
    "九阳":     ("#ff6900", "#ffffff", "九阳"),
    "松下":     ("#00529b", "#ffffff", "松下"),
    "panasonic":("#00529b", "#ffffff", "Panasonic"),
    "迪卡侬":   ("#00529b", "#ffffff", "迪卡侬"),
    "decathlon":("#00529b", "#ffffff", "Decathlon"),
    "anker":    ("#0ab4e8", "#ffffff", "Anker"),
    "安克":     ("#0ab4e8", "#ffffff", "Anker"),
    "jbl":      ("#ff6900", "#ffffff", "JBL"),
    "乐高":     ("#ffd700", "#000000", "乐高"),
    "lego":     ("#ffd700", "#000000", "LEGO"),
    "ikea":     ("#00529b", "#ffffff", "IKEA"),
    "宜家":     ("#00529b", "#ffffff", "IKEA"),
    "muji":     ("#f5f5dc", "#333333", "MUJI"),
    "无印":     ("#f5f5dc", "#333333", "MUJI"),
    "星巴克":   ("#00704a", "#ffffff", "星巴克"),
    "starbucks":("#00704a", "#ffffff", "Starbucks"),
    "dior":     ("#e4002b", "#ffffff", "Dior"),
    "迪奥":     ("#e4002b", "#ffffff", "Dior"),
    "chanel":   ("#1a1a1a", "#ffffff", "Chanel"),
    "香奈儿":   ("#1a1a1a", "#ffffff", "Chanel"),
    "sk-ii":    ("#e4002b", "#ffffff", "SK-II"),
    "skⅱ":     ("#e4002b", "#ffffff", "SK-II"),
    "兰蔻":     ("#00529b", "#ffffff", "兰蔻"),
    "lancome":  ("#00529b", "#ffffff", "Lancôme"),
    "surface":  ("#7c7c7c", "#ffffff", "Surface"),
    "garmin":   ("#00b894", "#ffffff", "Garmin"),
    "佳明":     ("#00b894", "#ffffff", "Garmin"),
    "bose":     ("#1a1a1a", "#ffffff", "Bose"),
    "marshall": ("#1a1a1a", "#ffffff", "Marshall"),
    "马歇尔":   ("#1a1a1a", "#ffffff", "Marshall"),
    "beats":    ("#e4002b", "#ffffff", "Beats"),
    "tcl":      ("#e4002b", "#ffffff", "TCL"),
    "海信":     ("#00529b", "#ffffff", "海信"),
    "hisense":  ("#00529b", "#ffffff", "Hisense"),
    "科沃斯":   ("#00b894", "#ffffff", "科沃斯"),
    "ecovacs":  ("#00b894", "#ffffff", "Ecovacs"),
    "西门子":   ("#1a1a1a", "#ffffff", "西门子"),
    "siemens":  ("#1a1a1a", "#ffffff", "Siemens"),
    "lg":       ("#a50034", "#ffffff", "LG"),
    "惠普":     ("#007db8", "#ffffff", "惠普"),
    "hp":       ("#007db8", "#ffffff", "HP"),
    "微软":     ("#7c7c7c", "#ffffff", "微软"),
    "microsoft":("#7c7c7c", "#ffffff", "Microsoft"),
    "realme":   ("#ffc700", "#000000", "realme"),
    "iqoo":     ("#1a73e8", "#ffffff", "iQOO"),
    "魅族":     ("#0ab4e8", "#ffffff", "魅族"),
    "meizu":    ("#0ab4e8", "#ffffff", "Meizu"),
    "努比亚":   ("#e4002b", "#ffffff", "努比亚"),
    "nubia":    ("#e4002b", "#ffffff", "nubia"),
    "hhkb":     ("#1a1a1a", "#ffffff", "HHKB"),
    "cherry":   ("#1a1a1a", "#ffffff", "Cherry"),
    "明基":     ("#00b894", "#ffffff", "明基"),
    "benq":     ("#00b894", "#ffffff", "BenQ"),
    "贝尔金":   ("#00b894", "#ffffff", "贝尔金"),
    "belkin":   ("#00b894", "#ffffff", "Belkin"),
    "sandisk":  ("#e4002b", "#ffffff", "SanDisk"),
    "闪迪":     ("#e4002b", "#ffffff", "SanDisk"),
    "金士顿":   ("#e4002b", "#ffffff", "金士顿"),
    "kingston": ("#e4002b", "#ffffff", "Kingston"),
    "西部数据": ("#00529b", "#ffffff", "WD"),
    "芝奇":     ("#e4002b", "#ffffff", "G.Skill"),
    "elgato":   ("#1a1a1a", "#ffffff", "Elgato"),
    "奥睿科":   ("#0ab4e8", "#ffffff", "ORICO"),
    "绿联":     ("#00b894", "#ffffff", "绿联"),
    "倍思":     ("#1a73e8", "#ffffff", "Baseus"),
    "倍思":     ("#1a73e8", "#ffffff", "Baseus"),
    "斯伯丁":   ("#ff6900", "#ffffff", "Spalding"),
    "spalding": ("#ff6900", "#ffffff", "Spalding"),
    "红双喜":   ("#e4002b", "#ffffff", "红双喜"),
    "尤尼克斯": ("#00529b", "#ffffff", "Yonex"),
    "yonex":    ("#00529b", "#ffffff", "Yonex"),
    "wilson":   ("#ffd700", "#000000", "Wilson"),
    "speedo":   ("#00529b", "#ffffff", "Speedo"),
    "lululemon":("#1a1a1a", "#ffffff", "lululemon"),
    "北面":     ("#1a1a1a", "#ffffff", "The North Face"),
    "osprey":   ("#00b894", "#ffffff", "Osprey"),
    "keep":     ("#4caf50", "#ffffff", "Keep"),
    "asics":    ("#e4002b", "#ffffff", "ASICS"),
    "new balance":("#e4002b", "#ffffff", "New Balance"),
    "匡威":     ("#1a1a1a", "#ffffff", "Converse"),
    "converse": ("#1a1a1a", "#ffffff", "Converse"),
    "优衣库":   ("#e4002b", "#ffffff", "UNIQLO"),
    "uniqlo":   ("#e4002b", "#ffffff", "UNIQLO"),
    "levis":    ("#00529b", "#ffffff", "Levi's"),
    "新秀丽":   ("#1a1a1a", "#ffffff", "Samsonite"),
    "芙丽芳丝": ("#ffc0cb", "#333333", "freeplus"),
    "freeplus": ("#ffc0cb", "#333333", "freeplus"),
    "敷尔佳":   ("#ffc0cb", "#333333", "敷尔佳"),
    "安耐晒":   ("#ffd700", "#000000", "安耐晒"),
    "anessa":   ("#ffd700", "#000000", "Anessa"),
    "三只松鼠": ("#e4002b", "#ffffff", "三只松鼠"),
    "良品铺子": ("#e4002b", "#ffffff", "良品铺子"),
    "飞鹤":     ("#00529b", "#ffffff", "飞鹤"),
    "好奇":     ("#ffc0cb", "#333333", "Huggies"),
    "huggies":  ("#ffc0cb", "#333333", "Huggies"),
    "蓝月亮":   ("#00529b", "#ffffff", "蓝月亮"),
    "维达":     ("#00b894", "#ffffff", "维达"),
    "水星":     ("#00529b", "#ffffff", "水星家纺"),
    "全棉时代": ("#ffc0cb", "#333333", "全棉时代"),
    "网易严选": ("#e4002b", "#ffffff", "网易严选"),
    "科沃斯":   ("#00b894", "#ffffff", "科沃斯"),
    "戴尔":     ("#007db8", "#ffffff", "Dell"),
    "格兰仕":   ("#e4002b", "#ffffff", "格兰仕"),
    "苏泊尔":   ("#00b894", "#ffffff", "苏泊尔"),
    "太力":     ("#00b894", "#ffffff", "太力"),
    "supor":    ("#00b894", "#ffffff", "苏泊尔"),
    "galanz":   ("#e4002b", "#ffffff", "格兰仕"),
    "斑马":     ("#00529b", "#ffffff", "Zebra"),
    "zebra":    ("#00529b", "#ffffff", "Zebra"),
    "晨光":     ("#e4002b", "#ffffff", "晨光"),
    "飞鹤":     ("#00529b", "#ffffff", "飞鹤"),
    "特仑苏":   ("#00529b", "#ffffff", "特仑苏"),
    "元气森林": ("#00b894", "#ffffff", "元气森林"),
}

# 品类图标（SVG path）
CATEGORY_ICONS = {
    "手机": "M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z",
    "电脑": "M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z",
    "笔记本": "M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z",
    "平板": "M12 18h.01M7 3h10a2 2 0 012 2v14a2 2 0 01-2 2H7a2 2 0 01-2-2V5a2 2 0 012-2z",
    "耳机": "M3 18v-6a9 9 0 0118 0v6M21 19a2 2 0 01-2 2h-1a2 2 0 01-2-2v-3a2 2 0 012-2h3zM3 19a2 2 0 002 2h1a2 2 0 002-2v-3a2 2 0 00-2-2H3z",
    "手表": "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
    "音箱": "M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m-4 0h8",
    "充电": "M13 10V3L4 14h7v7l9-11h-7z",
    "键盘": "M4 6h16M4 10h16M4 14h16M4 18h16",
    "鼠标": "M12 2a7 7 0 017 7v4a7 7 0 01-14 0V9a7 7 0 017-7z",
    "相机": "M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z M15 13a3 3 0 11-6 0 3 3 0 016 0z",
    "电视": "M3 7a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V7z",
    "冰箱": "M3 3h18v18H3V3zm6 0v18M3 12h18",
    "洗衣机": "M12 2a10 10 0 100 20 10 10 0 000-20z M12 6a4 4 0 100 8 4 4 0 000-8z",
    "吸尘器": "M13 10V3L4 14h7v7l9-11h-7z",
    "空调": "M3 12h18M12 3v18",
    "鞋": "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14",
    "衣服": "M4 6h16M4 10h16M4 14h16M4 18h16",
    "包": "M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z",
    "食品": "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
    "饮料": "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
    "美妆": "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
    "香水": "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
    "玩具": "M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    "书": "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
    "运动": "M13 10V3L4 14h7v7l9-11h-7z",
    "健身": "M13 10V3L4 14h7v7l9-11h-7z",
    "骑行": "M13 10V3L4 14h7v7l9-11h-7z",
    "游泳": "M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z",
    "登山": "M3 21h18M9 21V3l6 18",
    "瑜伽": "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
    "护肤": "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
    "母婴": "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z",
    "家居": "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
    "厨房": "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
    "清洁": "M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z",
    "收纳": "M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4",
    "日用": "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
    "生鲜": "M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z",
    "水果": "M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z",
    "蔬菜": "M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z",
    "肉": "M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z",
    "海鲜": "M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z",
    "奶粉": "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197",
    "纸尿裤": "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197",
    "显示器": "M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z",
    "充电器": "M13 10V3L4 14h7v7l9-11h-7z",
    "数据线": "M13 10V3L4 14h7v7l9-11h-7z",
    "移动电源": "M13 10V3L4 14h7v7l9-11h-7z",
    "保护壳": "M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z",
    "剃须刀": "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
    "面膜": "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
    "洗面奶": "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
    "防晒": "M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707",
    "口红": "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
    "坚果": "M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z",
    "咖啡": "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
    "茶叶": "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
    "牛奶": "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
    "篮球": "M13 10V3L4 14h7v7l9-11h-7z",
    "乒乓球": "M13 10V3L4 14h7v7l9-11h-7z",
    "羽毛球": "M13 10V3L4 14h7v7l9-11h-7z",
    "网球": "M13 10V3L4 14h7v7l9-11h-7z",
    "泳镜": "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z",
    "头盔": "M12 2a7 7 0 017 7v4a7 7 0 01-14 0V9a7 7 0 017-7z",
    "手套": "M4 6h16M4 10h16M4 14h16M4 18h16",
    "哑铃": "M13 10V3L4 14h7v7l9-11h-7z",
    "跳绳": "M13 10V3L4 14h7v7l9-11h-7z",
    "泡沫轴": "M13 10V3L4 14h7v7l9-11h-7z",
    "弹力带": "M13 10V3L4 14h7v7l9-11h-7z",
    "健腹轮": "M13 10V3L4 14h7v7l9-11h-7z",
    "牛仔裤": "M4 6h16M4 10h16M4 14h16M4 18h16",
    "衬衫": "M4 6h16M4 10h16M4 14h16M4 18h16",
    "T恤": "M4 6h16M4 10h16M4 14h16M4 18h16",
    "积木": "M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
    "文具": "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
    "笔": "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
    "硬盘": "M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4",
    "内存": "M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4",
    "摄像头": "M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z",
    "灯具": "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
    "装饰": "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
    "家纺": "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
    "酒": "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
}


def get_brand_info(name: str) -> tuple[str, str, str]:
    """获取品牌信息：(背景色, 文字色, 品牌名)"""
    name_lower = name.lower()
    for keyword, (bg, fg, brand) in BRANDS.items():
        if keyword in name_lower:
            return bg, fg, brand
    return "#e0e0e0", "#333333", ""


def get_category_icon(name: str, category: str = "") -> str:
    """根据商品名和分类获取图标 SVG path"""
    search_text = (name + " " + category).lower()
    for keyword, path in CATEGORY_ICONS.items():
        if keyword in search_text:
            return path
    # 默认图标
    return "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"


def extract_products(seed_path: str) -> list[dict]:
    """从 seed.py 提取所有商品"""
    with open(seed_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配 Product(...) 语句
    pattern = r'Product\((.*?)\)'
    raw_products = re.findall(pattern, content, re.DOTALL)

    products = []
    for raw in raw_products:
        name_match = re.search(r'name="([^"]+)"', raw)
        cat_match = re.search(r'category="([^"]+)"', raw)
        if name_match:
            products.append({
                "name": name_match.group(1),
                "category": cat_match.group(1) if cat_match else "",
            })
    return products


def sanitize_filename(name: str) -> str:
    clean = re.sub(r'[^\w一-鿿]', '_', name)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean.lower()


def check_existing_image(name: str) -> str | None:
    """检查 real/ 目录是否已有匹配图片"""
    keywords = [kw.lower() for kw in re.findall(r'[一-鿿]+|[a-zA-Z]+|\d+', name) if len(kw) > 1]

    for f in REAL_DIR.glob("*.jpg"):
        fname = f.name.lower().replace(".jpg", "").replace("_", "")
        name_clean = name.lower().replace(" ", "").replace("_", "")
        # 精确匹配
        if fname == sanitize_filename(name).replace("_", ""):
            return f"/static/products/real/{f.name}"
        # 关键词匹配
        if keywords and all(kw in fname for kw in keywords):
            return f"/static/products/real/{f.name}"

    return None


def create_brand_svg(name: str, category: str, save_path: Path):
    """创建精美品牌风格 SVG"""
    bg, fg, brand = get_brand_info(name)
    icon_path = get_category_icon(name, category)

    # 如果有品牌名，用品牌做主标题，商品名做副标题
    if brand and brand.lower() not in name.lower():
        title = brand
        subtitle = name
    else:
        title = name[:10] if len(name) > 10 else name
        subtitle = category if category else ""

    # 装饰性几何图形
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg};stop-opacity:1"/>
      <stop offset="100%" style="stop-color:{bg};stop-opacity:0.85"/>
    </linearGradient>
    <linearGradient id="shine" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{fg};stop-opacity:0.05"/>
      <stop offset="50%" style="stop-color:{fg};stop-opacity:0.02"/>
      <stop offset="100%" style="stop-color:{fg};stop-opacity:0.08"/>
    </linearGradient>
  </defs>

  <!-- 背景 -->
  <rect width="400" height="400" fill="url(#bg)" rx="12"/>

  <!-- 装饰元素 -->
  <circle cx="350" cy="50" r="80" fill="{fg}" opacity="0.03"/>
  <circle cx="50" cy="350" r="60" fill="{fg}" opacity="0.03"/>
  <rect x="30" y="30" width="340" height="340" rx="8" fill="none" stroke="{fg}" stroke-opacity="0.06" stroke-width="1"/>

  <!-- 光泽叠加 -->
  <rect width="400" height="400" fill="url(#shine)" rx="12"/>

  <!-- 图标 -->
  <g transform="translate(170, 100) scale(2.5)" fill="none" stroke="{fg}" stroke-opacity="0.3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="{icon_path}"/>
  </g>

  <!-- 品牌名 -->
  <text x="200" y="230" font-family="'Segoe UI', Arial, sans-serif" font-size="26" fill="{fg}" text-anchor="middle" font-weight="bold" letter-spacing="1">{title}</text>

  <!-- 副标题/商品名 -->
  <text x="200" y="260" font-family="'Segoe UI', Arial, sans-serif" font-size="13" fill="{fg}" text-anchor="middle" opacity="0.6" letter-spacing="0.5">{subtitle}</text>

  <!-- 底部装饰线 -->
  <line x1="160" y1="280" x2="240" y2="280" stroke="{fg}" stroke-opacity="0.15" stroke-width="1"/>

  <!-- 品质标签 -->
  <rect x="155" y="295" width="90" height="24" rx="12" fill="{fg}" fill-opacity="0.08"/>
  <text x="200" y="311" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="{fg}" text-anchor="middle" opacity="0.5" letter-spacing="2">PREMIUM</text>
</svg>'''

    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(svg)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    products = extract_products(str(SEED_FILE))
    print(f"共 {len(products)} 个商品\n")

    mapping = {}
    stats = {"existing": 0, "generated": 0}

    for i, product in enumerate(products, 1):
        name = product["name"]
        category = product["category"]
        filename = sanitize_filename(name)

        # 1. 检查已有图片
        existing = check_existing_image(name)
        if existing:
            print(f"[{i:3d}/{len(products)}] ✅ 已有: {name}")
            mapping[name] = existing
            stats["existing"] += 1
            continue

        # 2. 生成品牌 SVG
        svg_path = OUTPUT_DIR / f"{filename}.svg"
        if svg_path.exists():
            print(f"[{i:3d}/{len(products)}] ⏭️ 已生成: {name}")
            mapping[name] = f"/static/products/final/{filename}.svg"
            stats["existing"] += 1
            continue

        print(f"[{i:3d}/{len(products)}] 🎨 生成: {name}")
        create_brand_svg(name, category, svg_path)
        mapping[name] = f"/static/products/final/{filename}.svg"
        stats["generated"] += 1

    # 保存映射
    with open(MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"完成!")
    print(f"  已有图片: {stats['existing']}")
    print(f"  新生成: {stats['generated']}")
    print(f"  总计: {len(mapping)}")
    print(f"  输出目录: {OUTPUT_DIR}")
    print(f"  映射文件: {MAPPING_FILE}")


if __name__ == "__main__":
    main()
