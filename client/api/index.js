/**
 * 花海纪 - API 接口定义
 * 按模块组织所有后端 API 调用
 */
import http from './request'

// ==================== 聊天模块 ====================

/**
 * 发送聊天消息（非流式）
 */
export function sendMessage(data: {
  message: string
  trip_id?: string
  session_id?: string
}) {
  return http.post('/api/chat/send', data, { showLoading: true })
}

/**
 * 发送聊天消息（流式）
 * 注意：微信小程序对 SSE 支持有限，建议使用 WebSocket
 */
export function sendMessageStream(data: {
  message: string
  trip_id?: string
}) {
  return http.streamChat(
    '/api/chat/send/stream',
    data,
    (chunk) => {},  // onMessage
    () => {},        // onComplete
    (err) => {},     // onError
  )
}

/**
 * 提取对话中的结构化信息
 */
export function extractInfo(tripId: string) {
  return http.post('/api/chat/extract', { trip_id: tripId })
}

/**
 * 获取对话历史
 */
export function getChatHistory(tripId: string) {
  return http.get(`/api/chat/history/${tripId}`)
}

/**
 * 清空对话历史
 */
export function clearChatHistory(tripId: string) {
  return http.delete(`/api/chat/history/${tripId}`)
}

// ==================== 搜索模块 ====================

/**
 * 确认旅行计划
 */
export function confirmPlan(tripId: string, plan: any) {
  return http.post(`/api/search/confirm-plan?trip_id=${tripId}`, plan)
}

/**
 * 搜索推荐地点
 */
export function searchPlaces(tripId: string) {
  return http.post('/api/search/places', { trip_id: tripId }, { showLoading: true })
}

/**
 * 获取搜索结果
 */
export function getSearchResult(tripId: string) {
  return http.get(`/api/search/result/${tripId}`)
}

/**
 * 获取旅行计划
 */
export function getTripPlan(tripId: string) {
  return http.get(`/api/search/plan/${tripId}`)
}

// ==================== 地图模块 ====================

/**
 * 搜索地图地点
 */
export function searchMapPlaces(params: {
  keyword: string
  city?: string
  latitude?: number
  longitude?: number
  radius?: number
  limit?: number
}) {
  return http.get('/api/map/search', params)
}

/**
 * 地理编码
 */
export function geocodeAddress(address: string, city?: string) {
  return http.post(`/api/map/geocode?address=${encodeURIComponent(address)}${city ? '&city=' + city : ''}`)
}

/**
 * 批量地理编码
 */
export function batchGeocode(addresses: string[], city?: string) {
  return http.post('/api/map/batch-geocode', { addresses, city })
}

/**
 * 逆地理编码
 */
export function reverseGeocode(latitude: number, longitude: number) {
  return http.get('/api/map/reverse-geocode', { latitude, longitude })
}

/**
 * 路线规划
 */
export function getDirection(params: {
  from_lat: number
  from_lng: number
  to_lat: number
  to_lng: number
  mode?: 'driving' | 'walking' | 'transit' | 'bicycling'
}) {
  return http.get('/api/map/direction', params)
}

// ==================== 行程模块 ====================

/**
 * 创建行程
 */
export function createTrip(userId: string) {
  return http.post('/api/trip/create', { user_id: userId })
}

/**
 * 获取行程列表
 */
export function listTrips(userId: string, status?: string) {
  return http.get('/api/trip/list', { user_id: userId, status })
}

/**
 * 获取行程详情
 */
export function getTrip(tripId: string) {
  return http.get(`/api/trip/${tripId}`)
}

/**
 * 更新行程
 */
export function updateTrip(tripId: string, data: any) {
  return http.put(`/api/trip/${tripId}`, data)
}

/**
 * 删除行程
 */
export function deleteTrip(tripId: string) {
  return http.delete(`/api/trip/${tripId}`)
}

/**
 * 获取行程地点列表
 */
export function getTripPlaces(tripId: string) {
  return http.get(`/api/trip/${tripId}/places`)
}

/**
 * 向行程添加地点
 */
export function addTripPlace(tripId: string, place: any) {
  return http.post(`/api/trip/${tripId}/places`, place)
}
