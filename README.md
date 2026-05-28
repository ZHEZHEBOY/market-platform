# MallHub

全栈实物电商练手项目，完整实现「浏览 → 加购 → 下单 → 支付宝沙箱支付 → 订单管理」闭环。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI 0.115 |
| ORM / 迁移 | SQLAlchemy 2.0 + Alembic |
| 认证 | JWT（python-jose + bcrypt） |
| 支付 | 支付宝沙箱（官方 alipay-sdk-python，RSA2 签名） |
| 前端框架 | Vue 3（Composition API） |
| 状态管理 | Pinia |
| UI 组件 | Element Plus |
| 构建工具 | Vite |
| 数据库 | SQLite（可通过一行配置切换 PostgreSQL / MySQL） |

## 功能

### 买家端

- 用户注册 / 登录（JWT 认证 + BCrypt 密码加密）
- 商品浏览（列表 + 详情）
- 购物车（添加 / 修改数量 / 删除）
- 收货地址管理（省市区分级、设置默认地址）
- 下单结算（地址选择 + 订单摘要确认）
- 支付宝沙箱页面支付（PC 网页版）
- 支付结果页（同步回调）
- 订单列表（按状态筛选）

### 卖家 / 管理端

- 管理面板（订单数 / 销售额 / 用户数 / 热销商品统计）
- 商品管理（新增 / 编辑商品）
- 订单管理（发货 / 取消订单）
- 权限控制（普通用户无法访问管理接口）

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
market-platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理（环境变量 / PEM 密钥读取）
│   │   ├── database.py          # SQLAlchemy 引擎 & Session
│   │   ├── dependencies.py      # 依赖注入（获取当前用户、权限校验）
│   │   ├── utils.py             # 工具函数（订单号生成等）
│   │   ├── models/              # 数据模型（User, Product, Order, Cart, Address）
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   ├── routers/             # API 路由
│   │   │   ├── auth.py          # 注册/登录
│   │   │   ├── products.py      # 商品浏览
│   │   │   ├── cart.py          # 购物车
│   │   │   ├── addresses.py     # 收货地址
│   │   │   ├── orders.py        # 订单
│   │   │   ├── payment.py       # 支付宝支付
│   │   │   └── admin.py         # 后台管理
│   │   └── services/            # 业务逻辑层
│   │       ├── auth_service.py  # JWT 签发/验证
│   │       ├── order_service.py # 下单（原子库存扣减）
│   │       └── alipay_service.py# 支付宝 SDK 封装
│   ├── alembic/                 # 数据库迁移
│   ├── requirements.txt
│   ├── seed.py                  # 测试数据填充
│   └── .env.example             # 环境变量模板
│
├── frontend/
│   ├── src/
│   │   ├── main.js              # Vue 应用入口
│   │   ├── App.vue
│   │   ├── api/                 # Axios 请求封装（含 Token 注入 & 401 拦截）
│   │   ├── router/              # Vue Router（含路由守卫）
│   │   ├── stores/              # Pinia 状态管理（user, cart）
│   │   ├── components/          # 公共组件（Navbar）
│   │   └── views/               # 页面组件（12 个页面）
│   │       └── admin/           # 管理端页面
│   ├── vite.config.js           # Vite 代理配置（/api → localhost:8000）
│   └── package.json
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
  └──1:N── orders ──1:N── order_items ──N:1── products
```

- **User** — 用户（username, email, password_hash, role: ADMIN/USER）
- **Product** — 商品（name, description, price, stock, image_url, category）
- **Order** — 订单（order_no, total_amount, status, address_snapshot）
- **OrderItem** — 订单明细（product_id, quantity, price_at_time 快照）
- **CartItem** — 购物车项
- **Address** — 收货地址（province/city/district/detail, is_default）

## 本地启动

### 1. 克隆 & 环境变量

```bash
git clone <repo-url>
cd market-platform
```

```bash
cd backend
cp .env.example .env
```

编辑 `backend/.env`，填入：

```env
DATABASE_URL=sqlite:///market.db
JWT_SECRET_KEY=<自定义随机字符串>
ALIPAY_APPID=<支付宝沙箱 APPID>
ALIPAY_PRIVATE_KEY=alipay_private_key.pem    # 或直接填入密钥文本
ALIPAY_PUBLIC_KEY=alipay_public_key.pem      # 或直接填入密钥文本
```

### 2. 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows 用: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head           # 执行数据库迁移
python seed.py                 # 填充测试数据
uvicorn app.main:app --reload  # 启动 http://localhost:8000
```

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev                    # 启动 http://localhost:5173
```

### 4. 测试账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 可访问 /admin 后台 |
| 普通用户 | testuser | test123 | 买家功能 |

### 支付宝沙箱配置

1. 注册 [支付宝开放平台](https://open.alipay.com/) → 控制台 → 沙箱环境
2. 获取 APPID、应用私钥、支付宝公钥
3. 写入 `backend/.env` 或保存为 `.pem` 文件
4. 支付时使用沙箱买家账号 + 沙箱余额 / 沙箱钱包扫码

## API 概览

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/auth/register` | 注册 | 公开 |
| POST | `/api/auth/login` | 登录 | 公开 |
| GET | `/api/products` | 商品列表 | 公开 |
| GET | `/api/products/{id}` | 商品详情 | 公开 |
| GET/POST/PATCH/DELETE | `/api/cart` | 购物车 CRUD | 需登录 |
| GET/POST/PUT/DELETE | `/api/addresses` | 地址管理 | 需登录 |
| POST/GET | `/api/orders` | 创建/查看订单 | 需登录 |
| PATCH | `/api/orders/{id}/cancel` | 取消订单 | 需登录 |
| POST | `/api/payment/pay` | 发起支付宝支付 | 需登录 |
| POST | `/api/payment/notify` | 支付宝异步通知 | 公开 |
| GET | `/api/admin/stats` | 管理面板统计 | 管理员 |
| GET/POST/PATCH | `/api/admin/products` | 商品管理 | 管理员 |
| GET | `/api/admin/orders` | 订单管理 | 管理员 |
| PATCH | `/api/admin/orders/{id}/ship` | 发货 | 管理员 |

## 开发历程

| 阶段 | 内容 |
|------|------|
| 1 | 项目初始化 + 后端基础（FastAPI、SQLAlchemy、JWT 认证） |
| 2 | 商品管理 + 购物车 + 收货地址 API |
| 3 | 订单管理 + 支付宝沙箱支付（官方 SDK、RSA2 签名） |
| 4 | 后台管理 API（数据统计、商品/订单管理、权限控制） |
| 5 | Vue 3 前端项目搭建（路由守卫、状态管理、API 封装） |
| 6 | 结算下单 + 前端模板修复 |
| 7 | 联调修复 + 种子数据填充 |
| 8 | 密钥安全管理（PEM 文件读取、Gitleaks 防泄密钩子） |
| 9 | 项目收尾 + 清理文件 |
