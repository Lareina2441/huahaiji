<!--
  花海纪 - 地点卡片组件
  用于详情列表页展示单个地点
-->
<template>
  <view class="place-card" @tap="handleTap">
    <!-- 图片区域 -->
    <view class="place-card__image">
      <image
        v-if="place.image_url"
        :src="place.image_url"
        mode="aspectFill"
        class="place-card__img"
      />
      <view v-else class="place-card__img place-card__img--placeholder">
        <text class="place-card__placeholder-icon">{{ typeIcon }}</text>
      </view>
      <!-- 类型标签 -->
      <view class="place-card__tag">
        <text class="place-card__tag-text">{{ typeLabel }}</text>
      </view>
    </view>

    <!-- 信息区域 -->
    <view class="place-card__info">
      <view class="place-card__header">
        <text class="place-card__name">{{ place.name }}</text>
        <view v-if="place.rating" class="place-card__rating">
          <text class="place-card__rating-star">⭐</text>
          <text class="place-card__rating-num">{{ place.rating }}</text>
        </view>
      </view>

      <text v-if="place.address" class="place-card__address">📍 {{ place.address }}</text>
      <text v-if="place.price_range" class="place-card__price">💰 {{ place.price_range }}</text>
      <text v-if="place.opening_hours" class="place-card__hours">🕐 {{ place.opening_hours }}</text>

      <!-- 简介 -->
      <text v-if="place.description" class="place-card__desc">{{ place.description }}</text>

      <!-- 攻略提示 -->
      <view v-if="place.tips" class="place-card__tips">
        <text class="place-card__tips-label">💡 小贴士：</text>
        <text class="place-card__tips-text">{{ place.tips }}</text>
      </view>

      <!-- 操作按钮 -->
      <view class="place-card__actions">
        <view
          v-if="place.latitude && place.longitude"
          class="place-card__btn place-card__btn--nav"
          @tap.stop="handleNavigate"
        >
          <text>🧭 导航</text>
        </view>
        <view
          v-if="place.phone"
          class="place-card__btn place-card__btn--call"
          @tap.stop="handleCall"
        >
          <text>📞 电话</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { placeTypeIcons, placeTypeLabels, openNavigation } from '@/utils/index'

const props = defineProps({
  place: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['tap'])

const typeIcon = computed(() => placeTypeIcons[props.place.type] || '📍')
const typeLabel = computed(() => placeTypeLabels[props.place.type] || '其他')

function handleTap() {
  emit('tap', props.place)
}

function handleNavigate() {
  openNavigation(props.place.latitude, props.place.longitude, props.place.name)
}

function handleCall() {
  if (props.place.phone) {
    uni.makePhoneCall({ phoneNumber: props.place.phone })
  }
}
</script>

<style scoped>
.place-card {
  background: #ffffff;
  border-radius: 24rpx;
  overflow: hidden;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.place-card__image {
  position: relative;
  width: 100%;
  height: 300rpx;
}

.place-card__img {
  width: 100%;
  height: 100%;
}

.place-card__img--placeholder {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  display: flex;
  align-items: center;
  justify-content: center;
}

.place-card__placeholder-icon {
  font-size: 80rpx;
}

.place-card__tag {
  position: absolute;
  top: 16rpx;
  left: 16rpx;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 16rpx;
  padding: 4rpx 16rpx;
}

.place-card__tag-text {
  color: #ffffff;
  font-size: 22rpx;
}

.place-card__info {
  padding: 24rpx;
}

.place-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.place-card__name {
  font-size: 32rpx;
  font-weight: 600;
  color: #333333;
  flex: 1;
}

.place-card__rating {
  display: flex;
  align-items: center;
}

.place-card__rating-star {
  font-size: 24rpx;
}

.place-card__rating-num {
  font-size: 26rpx;
  color: #ff9500;
  font-weight: 500;
  margin-left: 4rpx;
}

.place-card__address,
.place-card__price,
.place-card__hours {
  display: block;
  font-size: 24rpx;
  color: #888888;
  margin-top: 8rpx;
}

.place-card__desc {
  display: block;
  font-size: 26rpx;
  color: #555555;
  margin-top: 16rpx;
  line-height: 1.6;
}

.place-card__tips {
  background: #fff8e1;
  border-radius: 12rpx;
  padding: 16rpx;
  margin-top: 16rpx;
}

.place-card__tips-label {
  font-size: 24rpx;
  color: #f5a623;
  font-weight: 500;
}

.place-card__tips-text {
  font-size: 24rpx;
  color: #666666;
}

.place-card__actions {
  display: flex;
  gap: 16rpx;
  margin-top: 20rpx;
}

.place-card__btn {
  padding: 12rpx 32rpx;
  border-radius: 32rpx;
  font-size: 24rpx;
}

.place-card__btn--nav {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  color: #ffffff;
}

.place-card__btn--call {
  background: #f5f5f5;
  color: #333333;
}
</style>
