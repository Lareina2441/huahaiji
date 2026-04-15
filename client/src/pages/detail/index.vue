<!--
  花海纪 - 地点详情列表页
  可向下滑动查看所有推荐地点，搭配攻略信息
-->
<template>
  <view class="page detail-page">
    <!-- 导航栏 -->
    <view class="detail-nav">
      <view class="detail-nav__back" @tap="goBack">
        <text>←</text>
      </view>
      <text class="detail-nav__title">推荐详情</text>
      <view class="detail-nav__action" @tap="goToMap">
        <text>🗺️</text>
      </view>
    </view>

    <!-- 行程概要 -->
    <view v-if="tripStore.searchResult?.summary" class="detail-summary">
      <text class="detail-summary__label">📋 行程概要</text>
      <text class="detail-summary__text">{{ tripStore.searchResult.summary }}</text>
    </view>

    <!-- 分类筛选 -->
    <scroll-view scroll-x class="detail-tabs">
      <view
        v-for="tab in categoryTabs"
        :key="tab.key"
        :class="['detail-tab', activeCategory === tab.key ? 'detail-tab--active' : '']"
        @tap="activeCategory = tab.key"
      >
        <text>{{ tab.icon }} {{ tab.label }}</text>
      </view>
    </scroll-view>

    <!-- 地点列表 -->
    <scroll-view
      scroll-y
      class="detail-list"
      @scrolltolower="loadMore"
    >
      <!-- 景点列表 -->
      <template v-if="activeCategory === 'all' || activeCategory === 'attraction'">
        <view v-if="activeCategory === 'all' && currentPlaces.attractions.length" class="detail-section">
          <text class="detail-section__title">📍 推荐景点</text>
        </view>
        <PlaceCard
          v-for="place in currentPlaces.attractions"
          :key="place.name"
          :place="place"
          @tap="showPlaceDetail(place)"
        />
      </template>

      <!-- 餐厅列表 -->
      <template v-if="activeCategory === 'all' || activeCategory === 'restaurant'">
        <view v-if="activeCategory === 'all' && currentPlaces.restaurants.length" class="detail-section">
          <text class="detail-section__title">🍽️ 推荐美食</text>
        </view>
        <PlaceCard
          v-for="place in currentPlaces.restaurants"
          :key="place.name"
          :place="place"
          @tap="showPlaceDetail(place)"
        />
      </template>

      <!-- 酒店列表 -->
      <template v-if="activeCategory === 'all' || activeCategory === 'hotel'">
        <view v-if="activeCategory === 'all' && currentPlaces.hotels.length" class="detail-section">
          <text class="detail-section__title">🏨 推荐住宿</text>
        </view>
        <PlaceCard
          v-for="place in currentPlaces.hotels"
          :key="place.name"
          :place="place"
          @tap="showPlaceDetail(place)"
        />
      </template>

      <!-- 空状态 -->
      <view v-if="isEmpty" class="detail-empty">
        <text class="detail-empty__icon">🌸</text>
        <text class="detail-empty__text">暂无推荐内容</text>
      </view>

      <view style="height: 40rpx;" />
    </scroll-view>

    <!-- 地点详情弹窗 -->
    <uni-popup ref="detailPopup" type="bottom" :safe-area="true">
      <view class="detail-popup">
        <view class="detail-popup__handle" />
        <view v-if="selectedPlace" class="detail-popup__content">
          <!-- 图片 -->
          <image
            v-if="selectedPlace.image_url"
            :src="selectedPlace.image_url"
            mode="aspectFill"
            class="detail-popup__image"
          />
          <view v-else class="detail-popup__image detail-popup__image--placeholder">
            <text class="detail-popup__placeholder-icon">
              {{ placeTypeIcons[selectedPlace.type] || '📍' }}
            </text>
          </view>

          <!-- 信息 -->
          <view class="detail-popup__info">
            <view class="detail-popup__header">
              <text class="detail-popup__name">{{ selectedPlace.name }}</text>
              <view v-if="selectedPlace.rating" class="detail-popup__rating">
                <text>⭐ {{ selectedPlace.rating }}</text>
              </view>
            </view>

            <text v-if="selectedPlace.address" class="detail-popup__address">
              📍 {{ selectedPlace.address }}
            </text>
            <text v-if="selectedPlace.price_range" class="detail-popup__price">
              💰 {{ selectedPlace.price_range }}
            </text>
            <text v-if="selectedPlace.opening_hours" class="detail-popup__hours">
              🕐 {{ selectedPlace.opening_hours }}
            </text>

            <text class="detail-popup__desc">{{ selectedPlace.description }}</text>

            <!-- 攻略 -->
            <view v-if="selectedPlace.tips" class="detail-popup__tips">
              <text class="detail-popup__tips-title">💡 攻略小贴士</text>
              <text class="detail-popup__tips-text">{{ selectedPlace.tips }}</text>
            </view>
          </view>

          <!-- 操作按钮 -->
          <view class="detail-popup__actions">
            <view
              v-if="selectedPlace.latitude && selectedPlace.longitude"
              class="detail-popup__btn detail-popup__btn--nav"
              @tap="navigateTo(selectedPlace)"
            >
              <text>🧭 导航前往</text>
            </view>
            <view class="detail-popup__btn detail-popup__btn--save" @tap="addToTrip(selectedPlace)">
              <text>📌 加入行程</text>
            </view>
          </view>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import PlaceCard from '@/components/PlaceCard.vue'
import { useTripStore } from '@/store/index'
import { placeTypeIcons, openNavigation } from '@/utils/index'
import { addTripPlace } from '@/api/index'

const tripStore = useTripStore()
const detailPopup = ref(null)
const selectedPlace = ref(null)
const activeCategory = ref('all')

const categoryTabs = [
  { key: 'all', label: '全部', icon: '🗺️' },
  { key: 'attraction', label: '景点', icon: '📍' },
  { key: 'restaurant', label: '美食', icon: '🍽️' },
  { key: 'hotel', label: '住宿', icon: '🏨' },
]

// 当前显示的地点数据
const currentPlaces = computed(() => {
  const result = tripStore.searchResult || {}
  return {
    attractions: result.attractions || [],
    restaurants: result.restaurants || [],
    hotels: result.hotels || [],
  }
})

// 是否为空
const isEmpty = computed(() => {
  const p = currentPlaces.value
  return p.attractions.length === 0 && p.restaurants.length === 0 && p.hotels.length === 0
})

onLoad((options) => {
  if (options?.trip_id) {
    tripStore.setTripId(options.trip_id)
  }
})

/**
 * 显示地点详情弹窗
 */
function showPlaceDetail(place) {
  selectedPlace.value = place
  detailPopup.value?.open()
}

/**
 * 导航到地点
 */
function navigateTo(place) {
  detailPopup.value?.close()
  openNavigation(place.latitude, place.longitude, place.name)
}

/**
 * 加入行程
 */
async function addToTrip(place) {
  try {
    await addTripPlace(tripStore.tripId, place)
    uni.showToast({ title: '已加入行程', icon: 'success' })
    detailPopup.value?.close()
  } catch (err) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

/**
 * 跳转到地图页
 */
function goToMap() {
  uni.navigateTo({
    url: `/pages/map/index?trip_id=${tripStore.tripId}`,
  })
}

function goBack() {
  uni.navigateBack()
}

function loadMore() {
  // 预留加载更多功能
}
</script>

<style scoped>
.detail-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.detail-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24rpx;
  height: 88rpx;
  background: #ffffff;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.detail-nav__back,
.detail-nav__action {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
}

.detail-nav__title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333333;
}

.detail-summary {
  background: linear-gradient(135deg, #fff8e1, #fff3e0);
  padding: 24rpx 32rpx;
}

.detail-summary__label {
  display: block;
  font-size: 24rpx;
  color: #f5a623;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.detail-summary__text {
  display: block;
  font-size: 26rpx;
  color: #666666;
  line-height: 1.6;
}

.detail-tabs {
  background: #ffffff;
  white-space: nowrap;
  padding: 16rpx 24rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.detail-tab {
  display: inline-flex;
  align-items: center;
  padding: 12rpx 28rpx;
  margin-right: 16rpx;
  border-radius: 32rpx;
  background: #f5f5f5;
  font-size: 26rpx;
  color: #666666;
}

.detail-tab--active {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: #ffffff;
}

.detail-list {
  flex: 1;
  padding: 24rpx;
}

.detail-section {
  padding: 16rpx 0;
}

.detail-section__title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333333;
}

.detail-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 0;
}

.detail-empty__icon {
  font-size: 80rpx;
  margin-bottom: 16rpx;
}

.detail-empty__text {
  font-size: 28rpx;
  color: #999999;
}

/* 详情弹窗 */
.detail-popup {
  background: #ffffff;
  border-radius: 32rpx 32rpx 0 0;
  max-height: 85vh;
  overflow-y: auto;
}

.detail-popup__handle {
  width: 64rpx;
  height: 8rpx;
  background: #e0e0e0;
  border-radius: 4rpx;
  margin: 16rpx auto;
}

.detail-popup__image {
  width: 100%;
  height: 360rpx;
}

.detail-popup__image--placeholder {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-popup__placeholder-icon {
  font-size: 100rpx;
}

.detail-popup__info {
  padding: 28rpx;
}

.detail-popup__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.detail-popup__name {
  font-size: 36rpx;
  font-weight: 700;
  color: #333333;
  flex: 1;
}

.detail-popup__rating {
  font-size: 28rpx;
  color: #ff9500;
  font-weight: 500;
}

.detail-popup__address,
.detail-popup__price,
.detail-popup__hours {
  display: block;
  font-size: 26rpx;
  color: #888888;
  margin-top: 8rpx;
}

.detail-popup__desc {
  display: block;
  font-size: 28rpx;
  color: #555555;
  margin-top: 20rpx;
  line-height: 1.8;
}

.detail-popup__tips {
  background: #f0f7ff;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-top: 20rpx;
}

.detail-popup__tips-title {
  display: block;
  font-size: 26rpx;
  color: #4facfe;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.detail-popup__tips-text {
  display: block;
  font-size: 26rpx;
  color: #555555;
  line-height: 1.6;
}

.detail-popup__actions {
  display: flex;
  gap: 20rpx;
  padding: 24rpx 28rpx;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid #f0f0f0;
}

.detail-popup__btn {
  flex: 1;
  height: 88rpx;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 500;
}

.detail-popup__btn--nav {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  color: #ffffff;
}

.detail-popup__btn--save {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: #ffffff;
}
</style>
