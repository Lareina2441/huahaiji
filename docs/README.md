# 花海纪 - AI 智能旅行规划助手

## 项目简介

花海纪是一款基于 AI 的微信小程序，通过自然对话帮助用户规划旅行，自动搜索推荐景点、美食、酒店，并在地图上展示完整行程。

## 技术栈

### 前端
- **框架：** uni-app (Vue 3)
- **状态管理：** Pinia
- **地图：** 腾讯地图微信小程序 SDK
- **UI：** 自定义组件 + 渐变主题

### 后端
- **框架：** FastAPI (Python 3.11+)
- **AI：** DeepSeek API (OpenAI 兼容接口)
- **搜索：** Serper Google Search API
- **地图：** 腾讯地图 WebService API
- **数据库：** MySQL 8.0 + Redis 7
- **部署：** Docker + Nginx

## 项目结构

```
huahaiji/
├── client/                  # 前端 uni-app 项目
│   ├── pages/               # 页面
│   │   ├── index/           # 首页
│   │   ├── chat/            # AI 聊天页
│   │   ├── confirm/         # 信息确认页
│   │   ├── map/             # 地图展示页
│   │   └── detail/          # 详情列表页
│   ├── components/          # 公共组件
│   │   ├── MsgBubble.vue    # 消息气泡
│   │   └── PlaceCard.vue    # 地点卡片
│   ├── api/                 # API 封装
│   ├── store/               # Pinia 状态管理
│   └── utils/               # 工具函数
│
├── server/                  # 后端 FastAPI 项目
│   ├── app/
│   │   ├── main.py          # 入口
│   │   ├── config.py        # 配置
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 业务服务
│   │   │   ├── deepseek.py  # AI 对话
│   │   │   ├── extractor.py # 信息抽取
│   │   │   ├── searcher.py  # 搜索服务
│   │   │   └── mapper.py    # 地图服务
│   │   └── routers/         # API 路由
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── docs/                    # 文档
```

## 快速开始

### 1. 环境准备

- Node.js 18+
- Python 3.11+
- MySQL 8.0
- Redis 7
- Docker (可选)

### 2. 后端启动

```bash
cd server

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Keys

# 启动服务
python -m app.main
# 或使用 uvicorn
uvicorn app.main:app --reload --port 8000
```

### 3. 前端启动

```bash
cd client

# 安装依赖
npm install

# 微信小程序开发
npm run dev:mp-weixin

# H5 开发
npm run dev:h5
```

### 4. Docker 部署

```bash
cd server
docker-compose up -d
```

## API 文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 核心 API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat/send` | POST | 发送聊天消息 |
| `/api/chat/send/stream` | POST | 流式聊天 (SSE) |
| `/api/chat/extract` | POST | 抽取结构化信息 |
| `/api/search/places` | POST | 搜索推荐地点 |
| `/api/map/search` | GET | 地图 POI 搜索 |
| `/api/map/direction` | GET | 路线规划 |
| `/api/trip/create` | POST | 创建行程 |
| `/api/trip/{id}` | GET | 获取行程详情 |

## 需要申请的 API Key

1. **DeepSeek API** - https://platform.deepseek.com
2. **腾讯地图 Key** - https://lbs.qq.com
3. **Serper API** - https://serper.dev
4. **微信小程序 AppID** - https://mp.weixin.qq.com

## 开发计划

- [x] 项目骨架搭建
- [x] DeepSeek AI 对话集成
- [x] 结构化信息抽取
- [x] 搜索服务 + AI 总结
- [x] 地图服务集成
- [x] 前端页面开发
- [ ] WebSocket 流式对话
- [ ] 数据库持久化
- [ ] 微信登录集成
- [ ] 行程分享功能
- [ ] 用户收藏功能
