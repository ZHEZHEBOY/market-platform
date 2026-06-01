# MallHub

全栈实物电商项目，完整实现「浏览 → 加购 → 下单 → 支付宝沙箱支付 → 订单管理 → 售后」闭环，集成**向量语义搜索**、**以图搜图**、**个性化推荐**等 AI 能力。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI 0.115 |
| ORM / 迁移 | SQLAlchemy 2.0 + Alembic |
| 认证 | JWT（python-jose + bcrypt） |
| 支付 | 支付宝沙箱（官方 alipay-sdk-python，RSA2 签名） |
| 向量数据库 | ChromaDB（持久化存储） |
| 文本 Embedding | BAAI/bge-base-zh-v1.5（中文语义，768 维） |
| 图片 Embedding | openai/clip-vit-base-patch32（多模态，512 维） |
| 前端框架 | Vue 3（Composition API） |
| 状态管理 | Pinia |
| UI 组件 | Element Plus |
| 图表 | ECharts |
| 构建工具 | Vite |
| 数据库 | MySQL / SQLite |

## 功能

### 买家端

- 用户注册 / 登录（JWT 认证 + BCrypt 密码加密）
- 商品浏览（列表 + 详情 + 分类导航 + 轮播图）
- **智能搜索**（关键词 + 语义搜索融合，自动去重合并）
- **搜索建议**（输入时实时推荐关键词）
- **搜索历史**（本地存储最近 10 条记录）
- **同义词扩展**（搜索「耳机」自动扩展为「耳麦、headphone、蓝牙耳机」等）
- 购物车（添加 / 修改数量 / 删除）
- 收货地址管理（省市区分级、设置默认地址）
- 下单结算（地址选择 + 订单摘要确认）
- 支付宝沙箱页面支付（PC 网页版）
- 支付结果页（同步回调）
- 订单列表（按状态筛选）+ 订单详情（物流时间线）
- 商品评价（评分 + 文字评价）
- 收藏夹（收藏/取消收藏）
- 领券中心（领取优惠券）+ 我的优惠券
- 退款/售后（申请退款、取消申请）
- 个人中心（修改资料、修改密码、头像上传）

### 卖家端

- 卖家仪表盘（订单统计、销售数据）
- 商品管理（新增 / 编辑 / 上下架）
- 订单管理（发货 / 查看订单详情）
- 店铺管理（店铺信息编辑）

### 管理端

- 管理面板（订单数 / 销售额 / 用户数 / 热销商品统计）
- 商品管理（查看所有商品）
- 订单管理（查看所有订单）
- 店铺审核（审核卖家入驻申请）
- 分类管理（树形分类 CRUD）
- 优惠券管理（创建 / 启用 / 禁用优惠券）
- 退款审核（审核退款申请）
- 数据报表（销售趋势、用户增长、订单状态、分类销售、热销排行）

### AI 能力

- **语义搜索**：用自然语言描述需求（如「适合跑步的耳机」），AI 理解意图返回相关商品
- **以图搜图**：上传商品图片，找到视觉相似的商品
- **跨模态检索**：用文本搜索图片（如「红色运动鞋」）
- **个性化推荐**：基于用户浏览/购买行为推荐相似商品
- **季节过滤**：搜索「夏天穿的衣服」自动排除羽绒服等冬季商品
- **品牌风格详情图**：每个商品生成 4 张淘宝风格详情图（主图+卖点+规格+保障）

## 支付流程

```
用户下单 ──→ 订单状态: pending_payment
   │
   ├──→ 跳转支付宝沙箱 → 扫码支付
   │         │
   │    ┌────┴────┐
   │  成功      取消/失败
   │    │         │
   │    ↓         ↓
   │  paid    cancelled
   │    │
   │    ├──→ 卖家发货 → shipped
   │    │
   │    └──→ 买家签收 → signed
```

订单状态机：`pending_payment → paid → shipped → signed`（中途可取消：`pending_payment → cancelled`）

## 项目结构

```
MallHub/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理（环境变量 / PEM 密钥读取）
│   │   ├── database.py          # SQLAlchemy 引擎 & Session
│   │   ├── dependencies.py      # 依赖注入（获取当前用户、权限校验）
│   │   ├── utils.py             # 工具函数（订单号生成等）
│   │   ├── models/              # 数据模型
│   │   │   ├── user.py          # User, Shop
│   │   │   ├── product.py       # Product
│   │   │   ├── order.py         # Order, OrderItem
│   │   │   ├── cart.py          # CartItem
│   │   │   ├── address.py       # Address
│   │   │   ├── review.py        # Review
│   │   │   ├── favorite.py      # Favorite
│   │   │   ├── category.py      # Category
│   │   │   ├── coupon.py        # Coupon, UserCoupon
│   │   │   ├── notification.py  # Notification
│   │   │   └── refund.py        # Refund
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   ├── routers/             # API 路由
│   │   │   ├── auth.py          # 注册/登录
│   │   │   ├── products.py      # 商品浏览
│   │   │   ├── cart.py          # 购物车
│   │   │   ├── addresses.py     # 收货地址
│   │   │   ├── orders.py        # 订单
│   │   │   ├── payment.py       # 支付宝支付
│   │   │   ├── admin.py         # 后台管理
│   │   │   ├── seller.py        # 卖家端
│   │   │   ├── reviews.py       # 商品评价
│   │   │   ├── favorites.py     # 收藏夹
│   │   │   ├── categories.py    # 商品分类
│   │   │   ├── coupons.py       # 优惠券
│   │   │   ├── refunds.py       # 退款/售后
│   │   │   ├── analytics.py     # 数据报表
│   │   │   ├── notifications.py # 消息通知
│   │   │   ├── images.py        # 图片服务
│   │   │   └── vector_search.py # 向量搜索 API
│   │   ├── vector/              # 向量搜索模块
│   │   │   ├── embeddings.py    # Embedding 模型管理 (BGE + CLIP)
│   │   │   ├── chroma_client.py # ChromaDB 客户端
│   │   │   ├── indexer.py       # 商品索引服务
│   │   │   ├── searcher.py      # 搜索服务（语义/图搜图/推荐）
│   │   │   └── synonyms.py      # 同义词词典（200+ 词条）
│   │   └── services/            # 业务逻辑层
│   │       ├── auth_service.py  # JWT 签发/验证
│   │       ├── order_service.py # 下单（原子库存扣减）
│   │       └── alipay_service.py# 支付宝 SDK 封装
│   ├── alembic/                 # 数据库迁移
│   ├── data/chroma/             # ChromaDB 持久化数据
│   ├── static/products/         # 商品图片
│   │   ├── real_v2/             # 商品主图（329 张）
│   │   └── details/             # 详情图（2031 张，每商品 4 张）
│   ├── requirements.txt
│   ├── seed.py                  # 测试数据填充（461 商品、12 用户、5 店铺）
│   └── .env.example             # 环境变量模板
│
├── frontend/
│   ├── src/
│   │   ├── main.js              # Vue 应用入口
│   │   ├── App.vue
│   │   ├── api/                 # Axios 请求封装（含 Token 注入 & 401 拦截）
│   │   ├── router/              # Vue Router（含路由守卫 + 404 兜底）
│   │   ├── stores/              # Pinia 状态管理（user, cart）
│   │   ├── components/          # 公共组件
│   │   │   ├── Navbar.vue       # 导航栏（含搜索建议）
│   │   │   └── ProductCard.vue  # 商品卡片
│   │   └── views/               # 页面组件
│   │       ├── Home.vue         # 首页（轮播图 + 分类 + 品牌 + 推荐）
│   │       ├── SearchResults.vue# 搜索结果（融合搜索 + 搜索历史）
│   │       ├── ProductDetail.vue# 商品详情（图文详情 + 规格 + 评价 + 推荐）
│   │       ├── NotFound.vue     # 404 页面
│   │       ├── Cart.vue         # 购物车
│   │       ├── Checkout.vue     # 结算
│   │       ├── Orders.vue       # 订单列表
│   │       ├── OrderDetail.vue  # 订单详情
│   │       ├── Favorites.vue    # 收藏夹
│   │       ├── CouponCenter.vue # 领券中心
│   │       ├── MyCoupons.vue    # 我的优惠券
│   │       ├── MyRefunds.vue    # 退款/售后
│   │       ├── Profile.vue      # 个人中心
│   │       ├── Login.vue        # 登录
│   │       ├── Register.vue     # 注册
│   │       ├── RegisterSeller.vue# 卖家注册
│   │       ├── seller/          # 卖家端页面
│   │       └── admin/           # 管理端页面
│   ├── vite.config.js           # Vite 代理配置（/api → localhost:8001）
│   └── package.json
│
├── tools/                       # 工具脚本
│   ├── fetch_real_images.py     # Bing 图片爬虫
│   ├── gen_taobao_style_details.py # 淘宝风格详情图生成
│   ├── gen_multi_detail_images.py  # 多图详情生成（4张/商品）
│   ├── run_indexer.py           # 向量索引构建
│   └── update_products_2026.py  # 商品数据更新
│
├── .gitignore
├── .pre-commit-config.yaml      # Gitleaks 防泄密钩子
└── README.md
```

## 数据库模型

```
users ──1:N── addresses
  │
  ├──1:N── cart_items ──N:1── products
  │
  ├──1:N── orders ──1:N── order_items ──N:1── products
  │
  ├──1:N── reviews ──N:1── products
  │
  ├──1:N── favorites ──N:1── products
  │
  ├──1:N── user_coupons ──N:1── coupons
  │
  ├──1:N── notifications
  │
  └──1:N── refunds ──N:1── orders

shops ──1:N── products
categories ──1:N── subcategories (自引用树形)
```

- **User** — 用户（username, email, password_hash, role: ADMIN/BUYER/SELLER）
- **Shop** — 店铺（owner_id, name, description, status）
- **Product** — 商品（name, description, price, stock, image_url, detail_image, category）
- **Category** — 分类（name, parent_id, sort_order，树形结构）
- **Order** — 订单（order_no, total_amount, status, address_snapshot）
- **OrderItem** — 订单明细（product_id, quantity, price_at_time 快照）
- **CartItem** — 购物车项
- **Address** — 收货地址（province/city/district/detail, is_default）
- **Review** — 商品评价（user_id, product_id, rating, content）
- **Favorite** — 收藏（user_id, product_id）
- **Coupon** — 优惠券（code, type, value, min_amount, max_discount）
- **UserCoupon** — 用户优惠券（user_id, coupon_id, status）
- **Notification** — 消息通知（user_id, type, content, is_read）
- **Refund** — 退款申请（order_id, reason, amount, status）

## 本地启动

### 1. 克隆 & 环境变量

```bash
git clone https://github.com/ZHEZHEBOY/MallHub.git
cd MallHub
```

```bash
cd backend
cp .env.example .env
```

编辑 `backend/.env`，填入：

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/mallhub?charset=utf8mb4
JWT_SECRET_KEY=<自定义随机字符串>
ALIPAY_APPID=<支付宝沙箱 APPID>
ALIPAY_PRIVATE_KEY=alipay_private_key.pem
ALIPAY_PUBLIC_KEY=alipay_public_key.pem
```

### 2. 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows 用: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head           # 执行数据库迁移
python seed.py                 # 填充测试数据（461 商品、12 用户、5 店铺）
uvicorn app.main:app --reload  # 启动 http://localhost:8000
```

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev                    # 启动 http://localhost:5173
```

### 4. 向量搜索初始化（可选）

```bash
# 首次使用需要下载模型（约 500MB，使用 HuggingFace 镜像）
set HF_ENDPOINT=https://hf-mirror.com

# 构建向量索引
python tools/run_indexer.py

# 生成商品图片
python tools/fetch_real_images.py
python tools/gen_taobao_style_details.py
python tools/gen_multi_detail_images.py
```

### 5. 测试账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 可访问 /admin 后台 |
| 买家 | buyer | buyer123 | 买家功能 |
| 买家 | buyer2 ~ buyer5 | buyer123 | 买家功能 |
| 卖家 | seller | seller123 | 优品数码旗舰店 |
| 卖家 | seller2 | seller123 | 居家生活馆 |
| 卖家 | seller3 | seller123 | 运动户外专营店 |
| 卖家 | seller4 | seller123 | 美妆个护旗舰店 |
| 卖家 | seller5 | seller123 | 图书文创馆 |

### 支付宝沙箱配置

1. 注册 [支付宝开放平台](https://open.alipay.com/) → 控制台 → 沙箱环境
2. 获取 APPID、应用私钥、支付宝公钥
3. 写入 `backend/.env` 或保存为 `.pem` 文件
4. 支付时使用沙箱买家账号 + 沙箱余额 / 沙箱钱包扫码

## API 概览

### 商品 & 搜索

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/products` | 商品列表（支持 shop_id/category/keyword/排序筛选） | 公开 |
| GET | `/api/products/{id}` | 商品详情 | 公开 |
| POST | `/api/vector/semantic` | 语义搜索（支持自然语言 + 同义词扩展） | 公开 |
| POST | `/api/vector/image` | 以图搜图（上传图片） | 公开 |
| POST | `/api/vector/text-image` | 文本搜图片（跨模态） | 公开 |
| GET | `/api/vector/suggest` | 搜索建议（输入时实时推荐） | 公开 |
| GET | `/api/vector/health` | 向量搜索健康检查 | 公开 |
| GET | `/api/vector/recommend` | 个性化推荐 | 需登录 |
| POST | `/api/vector/behavior` | 记录用户行为 | 需登录 |
| POST | `/api/vector/reindex` | 重建向量索引 | 管理员 |

### 用户 & 订单

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/auth/register` | 注册 | 公开 |
| POST | `/api/auth/login` | 登录 | 公开 |
| GET/POST/PATCH/DELETE | `/api/cart` | 购物车 CRUD | 需登录 |
| GET/POST/PUT/DELETE | `/api/addresses` | 地址管理 | 需登录 |
| POST/GET | `/api/orders` | 创建/查看订单 | 需登录 |
| PATCH | `/api/orders/{id}/cancel` | 取消订单 | 需登录 |
| POST | `/api/payment/pay` | 发起支付宝支付 | 需登录 |
| POST | `/api/payment/notify` | 支付宝异步通知 | 公开 |

### 评价 & 收藏

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/reviews/product/{id}` | 商品评价 | 公开 |
| POST | `/api/reviews` | 创建评价 | 需登录 |
| GET/POST/DELETE | `/api/favorites` | 收藏管理 | 需登录 |

### 优惠券 & 退款

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/categories` | 分类列表 | 公开 |
| GET | `/api/coupons/available` | 可领优惠券 | 公开 |
| POST | `/api/coupons/claim/{id}` | 领取优惠券 | 需登录 |
| GET | `/api/coupons/my` | 我的优惠券 | 需登录 |
| POST | `/api/refunds/create` | 申请退款 | 需登录 |
| GET | `/api/refunds/my` | 我的退款 | 需登录 |

### 管理端

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/admin/stats` | 管理面板统计 | 管理员 |
| GET/POST/PATCH | `/api/admin/products` | 商品管理 | 管理员 |
| GET | `/api/admin/orders` | 订单管理 | 管理员 |
| PATCH | `/api/admin/orders/{id}/ship` | 发货 | 管理员 |
| POST | `/api/coupons/admin/create` | 创建优惠券 | 管理员 |
| GET | `/api/coupons/admin/list` | 优惠券列表 | 管理员 |
| GET | `/api/refunds/admin/list` | 退款列表 | 管理员 |
| PATCH | `/api/refunds/admin/{id}/review` | 审核退款 | 管理员 |
| GET | `/api/analytics/*` | 数据报表 | 管理员 |

## 向量搜索架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户输入查询                           │
│            "适合跑步的耳机"                               │
└─────────────────┬───────────────────────────────────────┘
                  │
       ┌──────────▼──────────┐
       │   同义词扩展          │
       │   耳机 → 耳麦/蓝牙耳机 │
       └──────────┬──────────┘
                  │
       ┌──────────▼──────────┐
       │   BGE 编码 (768维)   │
       │   GPU/CPU 自动选择    │
       └──────────┬──────────┘
                  │
       ┌──────────▼──────────┐
       │   ChromaDB 检索      │
       │   余弦相似度 Top-K    │
       └──────────┬──────────┘
                  │
       ┌──────────▼──────────┐
       │   季节过滤            │
       │   排除不相关商品       │
       └──────────┬──────────┘
                  │
       ┌──────────▼──────────┐
       │   返回结果            │
       │   name + score + ... │
       └─────────────────────┘
```

## 开发历程

| 阶段 | 内容 | 状态 |
|------|------|------|
| 1 | 项目初始化 + 后端基础（FastAPI、SQLAlchemy、JWT 认证） | ✅ |
| 2 | 商品管理 + 购物车 + 收货地址 API | ✅ |
| 3 | 订单管理 + 支付宝沙箱支付（官方 SDK、RSA2 签名） | ✅ |
| 4 | 后台管理 API（数据统计、商品/订单管理、权限控制） | ✅ |
| 5 | Vue 3 前端项目搭建（路由守卫、状态管理、API 封装） | ✅ |
| 6 | 结算下单 + 前端模板修复 | ✅ |
| 7 | 联调修复 + 种子数据填充 | ✅ |
| 8 | 密钥安全管理（PEM 文件读取、Gitleaks 防泄密钩子） | ✅ |
| 9 | 项目收尾 + 清理文件 | ✅ |
| 10 | 第一批：首页改版、搜索、个人中心、订单详情、卖家端 | ✅ |
| 11 | 第二批：商品评价、收藏夹、分类管理 | ✅ |
| 12 | 第三批：优惠券系统、退款/售后、数据报表 | ✅ |
| 13 | 扩充种子数据（461 商品、5 店铺、真实商品图片） | ✅ |
| 14 | 项目重命名为 MallHub | ✅ |
| 15 | 向量语义搜索（ChromaDB + BGE + CLIP） | ✅ |
| 16 | 搜索优化（GPU加速、搜索建议、搜索历史、同义词扩展） | ✅ |
| 17 | 商品详情图（淘宝风格，每商品 4 张） | ✅ |
| 18 | 商品数据更新（iPhone 17、小米 17 等最新款） | ✅ |

## 下一步计划

| 功能 | 说明 |
|------|------|
| WebSocket 实时通知 | 订单状态变更实时推送 |
| Docker 部署 | 前后端 + 数据库容器化 |
| 图片搜索优化 | CLIP 索引覆盖全量商品 |
| 用户行为推荐 | 基于浏览/购买历史的协同过滤 |

## License

MIT
