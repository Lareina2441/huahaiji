# 花海纪 - API 接口文档

## 基础信息

- Base URL: `http://localhost:8000`
- 响应格式: JSON
- 统一响应结构:
```json
{
  "code": 0,
  "data": {},
  "msg": "success"
}
```

---

## 一、聊天模块 `/api/chat`

### 1.1 发送消息

**POST** `/api/chat/send`

请求体:
```json
{
  "message": "我想去成都玩5天",
  "trip_id": "可选，已有行程ID",
  "session_id": "可选，会话ID"
}
```

响应:
```json
{
  "code": 0,
  "data": {
    "reply": "成都是个很棒的选择！...",
    "trip_id": "uuid",
    "is_info_complete": false
  }
}
```

### 1.2 流式聊天

**POST** `/api/chat/send/stream`

请求体同上，返回 SSE 流式数据。

### 1.3 信息抽取

**POST** `/api/chat/extract`

请求体:
```json
{
  "trip_id": "行程ID"
}
```

响应:
```json
{
  "code": 0,
  "data": {
    "trip_plan": {
      "destination": "成都",
      "days": "5",
      "people_count": "2人",
      "budget": "5000-8000",
      "confidence": 0.85
    },
    "completeness": {
      "is_complete": true,
      "missing_fields": ["dates", "transport_preference"]
    }
  }
}
```

---

## 二、搜索模块 `/api/search`

### 2.1 确认旅行计划

**POST** `/api/search/confirm-plan?trip_id=xxx`

请求体: TripPlan JSON 对象

### 2.2 搜索推荐地点

**POST** `/api/search/places`

请求体:
```json
{
  "trip_id": "行程ID"
}
```

响应:
```json
{
  "code": 0,
  "data": {
    "attractions": [...],
    "restaurants": [...],
    "hotels": [...],
    "summary": "行程概要..."
  }
}
```

---

## 三、地图模块 `/api/map`

### 3.1 POI 搜索

**GET** `/api/map/search?keyword=宽窄巷子&city=成都`

### 3.2 地理编码

**POST** `/api/map/geocode?address=成都市宽窄巷子`

### 3.3 路线规划

**GET** `/api/map/direction?from_lat=30.57&from_lng=104.07&to_lat=30.65&to_lng=104.05&mode=driving`

---

## 四、行程模块 `/api/trip`

### 4.1 创建行程

**POST** `/api/trip/create`
```json
{ "user_id": "用户ID" }
```

### 4.2 获取行程列表

**GET** `/api/trip/list?user_id=xxx&status=draft`

### 4.3 获取行程详情

**GET** `/api/trip/{trip_id}`

### 4.4 更新行程

**PUT** `/api/trip/{trip_id}`

### 4.5 删除行程

**DELETE** `/api/trip/{trip_id}`
