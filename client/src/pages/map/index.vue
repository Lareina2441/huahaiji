<!--
  花海纪 - 地图展示页
  在地图上显示所有推荐地点，支持分类筛选
-->
<template>
  <view class="page map-page">
    <!-- 地图区域 -->
    <map
      class="map-container"
      :latitude="centerLatitude"
      :longitude="centerLongitude"
      :scale="mapScale"
      :markers="markers"
      :show-location="true"
      @markertap="handleMarkerTap"
      @regionchange="handleRegionChange"
    >
      <!-- 地图上的控制按钮 -->
      <view class="map-controls">
        <view class="map-control" @tap="resetView">
          <text>🔄</text>
        </view>
      </view>
    </map>

    <!-- 分类筛选 Tab -->
    <view class="map-tabs">
      <scroll-view scroll-x class="map-tabs__scroll">
        <view
          v-for="tab in tabs"
          :key="tab.key"
          :class="['map-tab', activeTab === tab.key ? 'map-tab--active' : '']"
          @tap="switchTab(tab.key)"
        >
          <text>{{ tab.icon }} {{ tab.label }}</text>
          <text v-if="tab.count > 0" class="map-tab__count">({{ tab.count }})</text>
        </view>
      </scroll-view>
    </view>

    <!-- 行程概要 -->
    <view v-if="tripStore.searchResult?.summary" class="map-summary">
      <text class="map-summary__text">{{ tripStore.searchResult.summary }}</text>
    </view>

    <!-- 向下滑动提示 -->
    <view class="map-swipe-hint" @tap="goToDetail">
      <text class="map-swipe-hint__text">向下滑动查看详情</text>
      <text class="map-swipe-hint__arrow">↓</text>
    </view>

    <!-- 选中地点的气泡信息 -->
    <view v-if="selectedPlace" class="map-callout">
      <view class="map-callout__content">
        <text class="map-callout__name">{{ selectedPlace.name }}</text>
        <text class="map-callout__type">{{ getTypeLabel(selectedPlace.type) }}</text>
        <text v-if="selectedPlace.address" class="map-callout__address">{{ selectedPlace.address }}</text>
      </view>
      <view class="map-callout__actions">
        <view class="map-callout__btn" @tap="goToDetail">
          <text>查看详情</text>
        </view>
        <view
          v-if="selectedPlace.latitude && selectedPlace.longitude"
          class="map-callout__btn map-callout__btn--nav"
          @tap="navigateTo(selectedPlace)"
        >
          <text>导航</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useTripStore } from '@/store/index'
import { placeTypeIcons, placeTypeLabels, openNavigation } from '@/utils/index'

const tripStore = useTripStore()
const activeTab = ref('all')
const selectedPlace = ref<any>(null)
const mapScale = ref(12)

// 地图中心点（默认成都）
const centerLatitude = ref(30.5728)
const centerLongitude = ref(104.0668)

// 筛选 Tab 配置
const tabs = computed(() => {
  const result = tripStore.searchResult
  return [
    { key: 'all', label: '全部', icon: '🗺️', count: getFilteredPlaces('all').length },
    { key: 'attraction', label: '景点', icon: '📍', count: result?.attractions?.length || 0 },
    { key: 'restaurant', label: '美食', icon: '🍽️', count: result?.restaurants?.length || 0 },
    { key: 'hotel', label: '住宿', icon: '🏨', count: result?.hotels?.length || 0 },
  ]
})

/**
 * 获取筛选后的地点列表
 */
function getFilteredPlaces(type) {
  const result = tripStore.searchResult
  if (!result) return []

  let places = []
  if (type === 'all' || type === 'attraction') {
    places.push(...(result.attractions || []))
  }
  if (type === 'all' || type === 'restaurant') {
    places.push(...(result.restaurants || []))
  }
  if (type === 'all' || type === 'hotel') {
    places.push(...(result.hotels || []))
  }
  return places
}

/**
 * 地图 markers（带不同图标）
 */
const markers = computed(() => {
  const places = getFilteredPlaces(activeTab.value)
  return places
    .filter(p => p.latitude && p.longitude)
    .map((place, index) => ({
      id: index,
      latitude: place.latitude,
      longitude: place.longitude,
      title: place.name,
      iconPath: '',  // 可自定义图标路径
      width: 32,
      height: 32,
      callout: {
        content: `${placeTypeIcons[place.type] || '📍'} ${place.name}`,
        display: 'ALWAYS',
        fontSize: 12,
        borderRadius: 8,
        padding: 6,
        bgColor: '#ffffff',
      },
      label: {
        content: place.name,
        fontSize: 12,
        anchorX: 0,
        anchorY: -36,
      },
    }))
})

onLoad(async (options) => {
  const tripId = options?.trip_id
  if (tripId) {
    tripStore.setTripId(tripId)
  }

  // 如果有搜索结果，自动调整地图视野
  if (tripStore.searchResult) {
    adjustMapView()
  }
})

/**
 * 切换筛选 Tab
 */
function switchTab(key) {
  activeTab.value = key
  selectedPlace.value = null
}

/**
 * 点击 marker
 */
function handleMarkerTap(e) {
  const markerId = e.markerId || e.detail?.markerId
  const places = getFilteredPlaces(activeTab.value)
  if (markerId !== undefined && places[markerId]) {
    selectedPlace.value = places[markerId]
  }
}

/**
 * 调整地图视野以包含所有标记点
 */
function adjustMapView() {
  const places = getFilteredPlaces('all')
  const validPlaces = places.filter(p => p.latitude && p.longitude)
  if (validPlaces.length === 0) return

  // 计算中心点
  const avgLat = validPlaces.reduce((sum, p) => sum + p.latitude, 0) / validPlaces.length
  const avgLng = validPlaces.reduce((sum, p) => sum + p.longitude, 0) / validPlaces.length
  centerLatitude.value = avgLat
  centerLongitude.value = avgLng
  mapScale.value = validPlaces.length > 10 ? 10 : 12
}

/**
 * 重置地图视图
 */
function resetView() {
  adjustMapView()
  selectedPlace.value = null
}

/**
 * 导航到地点
 */
function navigateTo(place) {
  openNavigation(place.latitude, place.longitude, place.name)
}

/**
 * 跳转到详情列表页
 */
function goToDetail() {
  uni.navigateTo({
    url: `/pages/detail/index?trip_id=${tripStore.tripId}`,
  })
}

/**
 * 获取类型标签
 */
function getTypeLabel(type) {
  return placeTypeLabels[type] || '其他'
}

function handleRegionChange() {
  // 地图区域变化时的处理
}
</script>

<style scoped>
.map-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.map-container {
  flex: 1;
  width: 100%;
}

.map-controls {
  position: absolute;
  right: 24rpx;
  top: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.map-control {
  width: 72rpx;
  height: 72rpx;
  background: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.15);
  font-size: 32rpx;
}

.map-tabs {
  background: #ffffff;
  padding: 16rpx 0;
  box-shadow: 0 -2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.map-tabs__scroll {
  white-space: nowrap;
  padding: 0 24rpx;
}

.map-tab {
  display: inline-flex;
  align-items: center;
  padding: 12rpx 28rpx;
  margin-right: 16rpx;
  border-radius: 32rpx;
  background: #f5f5f5;
  font-size: 26rpx;
  color: #666666;
}

.map-tab--active {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: #ffffff;
}

.map-tab__count {
  font-size: 22rpx;
  margin-left: 4rpx;
  opacity: 0.8;
}

.map-summary {
  background: #fff8e1;
  padding: 20rpx 32rpx;
}

.map-summary__text {
  font-size: 24rpx;
  color: #666666;
  line-height: 1.6;
}

.map-swipe-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20rpx;
  background: #ffffff;
}

.map-swipe-hint__text {
  font-size: 24rpx;
  color: #999999;
  margin-right: 8rpx;
}

.map-swipe-hint__arrow {
  font-size: 24rpx;
  color: #f5576c;
  animation: bounce 1.5s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(8rpx); }
}

.map-callout {
  position: absolute;
  bottom: 200rpx;
  left: 24rpx;
  right: 24rpx;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.12);
}

.map-callout__name {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #333333;
  margin-bottom: 8rpx;
}

.map-callout__type {
  display: inline-block;
  font-size: 22rpx;
  color: #f5576c;
  background: #fff0f3;
  padding: 4rpx 16rpx;
  border-radius: 16rpx;
  margin-bottom: 8rpx;
}

.map-callout__address {
  display: block;
  font-size: 24rpx;
  color: #888888;
  margin-bottom: 16rpx;
}

.map-callout__actions {
  display: flex;
  gap: 16rpx;
}

.map-callout__btn {
  flex: 1;
  height: 72rpx;
  border-radius: 36rpx;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  color: #333333;
}

.map-callout__btn--nav {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  color: #ffffff;
}
</style>
