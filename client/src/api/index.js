/**
 * 花海纪 - API 接口定义
 * 按模块组织所有后端 API 调用
 */
import http from './request'

// ==================== 聊天模块 ====================

/**
 * 发送聊天消息（非流式）
 */
export function sendMessage(data) {
  return http.post('/api/chat/send', data, { showLoading: true })
}

/**
 * 发送聊天消息（流式）
 */
export function sendMessageStream(data) {
  return http.streamChat(
    '/api/chat/send/stream',
    data,
    (chunk) => {},
    () => {},
    (err) => {},
  )
}

/**
 * 提取对话中的结构化信息
 */
export function extractInfo(tripId) {
  return http.post('/api/chat/extract', { trip_id: tripId })
}

/**
 * 获取对话历史
 */
export function getChatHistory(tripId) {
  return http.get(`/api/chat/history/${tripId}`)
}

/**
 * 清空对话历史
 */
export function clearChatHistory(tripId) {
  return http.delete(`/api/chat/history/${tripId}`)
}

// ==================== 搜索模块 ====================

/**
 * 确认旅行计划
 */
export function confirmPlan(tripId, plan) {
  return http.post(`/api/search/confirm-plan?trip_id=${tripId}`, plan)
}

/**
 * 搜索推荐地点
 */
export function searchPlaces(tripId) {
  return http.post('/api/search/places', { trip_id: tripId }, { showLoading: true })
}

/**
 * 获取搜索结果
 */
export function getSearchResult(tripId) {
  return http.get(`/api/search/result/${tripId}`)
}

/**
 * 获取旅行计划
 */
export function getTripPlan(tripId) {
  return http.get(`/api/search/plan/${tripId}`)
}

// ==================== 地图模块 ====================

/**
 * 搜索地图地点
 */
export function searchMapPlaces(params) {
  return http.get('/api/map/search', params)
}

/**
 * 地理编码
 */
export function geocodeAddress(address, city) {
  return http.post(`/api/map/geocode?address=${encodeURIComponent(address)}${city ? '&city=' + city : ''}`)
}

/**
 * 批量地理编码
 */
export function batchGeocode(addresses, city) {
  return http.post('/api/map/batch-geocode', { addresses, city })
}

/**
 * 逆地理编码
 */
export function reverseGeocode(latitude, longitude) {
  return http.get('/api/map/reverse-geocode', { latitude, longitude })
}

/**
 * 路线规划
 */
export function getDirection(params) {
  return http.get('/api/map/direction', params)
}

// ==================== 行程模块 ====================

/**
 * 创建行程
 */
export function createTrip(userId) {
  return http.post('/api/trip/create', { user_id: userId })
}

/**
 * 获取行程列表
 */
export function listTrips(userId, status) {
  return http.get('/api/trip/list', { user_id: userId, status })
}

/**
 * 获取行程详情
 */
export function getTrip(tripId) {
  return http.get(`/api/trip/${tripId}`)
}

/**
 * 更新行程
 */
export function updateTrip(tripId, data) {
  return http.put(`/api/trip/${tripId}`, data)
}

/**
 * 删除行程
 */
export function deleteTrip(tripId) {
  return http.delete(`/api/trip/${tripId}`)
}

/**
 * 获取行程地点列表
 */
export function getTripPlaces(tripId) {
  return http.get(`/api/trip/${tripId}/places`)
}

/**
 * 向行程添加地点
 */
export function addTripPlace(tripId, place) {
  return http.post(`/api/trip/${tripId}/places`, place)
}
