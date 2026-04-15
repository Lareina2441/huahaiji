<!--
  花海纪 - 首页/入口页
-->
<template>
  <view class="page index-page">
    <!-- 顶部背景 -->
    <view class="index-hero">
      <view class="index-hero__bg">
        <text class="index-hero__title">🌸 花海纪</text>
        <text class="index-hero__subtitle">AI 智能旅行规划助手</text>
        <text class="index-hero__desc">告诉我你的旅行梦想，我来帮你实现</text>
      </view>
    </view>

    <!-- 功能入口 -->
    <view class="index-features">
      <view class="index-feature" @tap="startNewTrip">
        <view class="index-feature__icon">💬</view>
        <text class="index-feature__title">开始规划旅行</text>
        <text class="index-feature__desc">和 AI 聊天，定制你的专属行程</text>
      </view>

      <view class="index-feature" @tap="viewMyTrips">
        <view class="index-feature__icon">📋</view>
        <text class="index-feature__title">我的行程</text>
        <text class="index-feature__desc">查看和管理已保存的行程</text>
      </view>
    </view>

    <!-- 热门目的地 -->
    <view class="index-section">
      <text class="index-section__title">🔥 热门目的地</text>
      <view class="index-destinations">
        <view
          v-for="dest in destinations"
          :key="dest.name"
          class="index-dest"
          @tap="quickStart(dest.name)"
        >
          <text class="index-dest__icon">{{ dest.icon }}</text>
          <text class="index-dest__name">{{ dest.name }}</text>
        </view>
      </view>
    </view>

    <!-- 使用流程 -->
    <view class="index-section">
      <text class="index-section__title">✨ 如何使用</text>
      <view class="index-steps">
        <view class="index-step">
          <view class="index-step__num">1</view>
          <text class="index-step__text">和 AI 聊天描述你的旅行需求</text>
        </view>
        <view class="index-step">
          <view class="index-step__num">2</view>
          <text class="index-step__text">确认旅行计划信息</text>
        </view>
        <view class="index-step">
          <view class="index-step__num">3</view>
          <text class="index-step__text">AI 搜索推荐景点美食酒店</text>
        </view>
        <view class="index-step">
          <view class="index-step__num">4</view>
          <text class="index-step__text">在地图上查看完整行程</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const destinations = ref([
  { name: '成都', icon: '🐼' },
  { name: '丽江', icon: '🏔️' },
  { name: '三亚', icon: '🏖️' },
  { name: '西安', icon: '🏯' },
  { name: '杭州', icon: '🌺' },
  { name: '大理', icon: '🌙' },
])

/**
 * 开始新旅行 - 跳转到聊天页
 */
function startNewTrip() {
  uni.navigateTo({ url: '/pages/chat/index' })
}

/**
 * 快速开始 - 带目的地跳转
 */
function quickStart(destination: string) {
  uni.navigateTo({
    url: `/pages/chat/index?destination=${destination}`,
  })
}

/**
 * 查看我的行程
 */
function viewMyTrips() {
  uni.navigateTo({ url: '/pages/detail/index?mode=trips' })
}
</script>

<style scoped>
.index-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.index-hero {
  padding: 80rpx 40rpx 60rpx;
  background: linear-gradient(135deg, #f093fb, #f5576c, #feca57);
  border-radius: 0 0 48rpx 48rpx;
}

.index-hero__title {
  display: block;
  font-size: 56rpx;
  font-weight: 700;
  color: #ffffff;
  text-align: center;
  margin-bottom: 12rpx;
}

.index-hero__subtitle {
  display: block;
  font-size: 30rpx;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
  margin-bottom: 8rpx;
}

.index-hero__desc {
  display: block;
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.75);
  text-align: center;
}

.index-features {
  display: flex;
  gap: 24rpx;
  padding: 40rpx;
  margin-top: -30rpx;
}

.index-feature {
  flex: 1;
  background: #ffffff;
  border-radius: 24rpx;
  padding: 36rpx 24rpx;
  text-align: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.index-feature:active {
  transform: scale(0.97);
}

.index-feature__icon {
  font-size: 56rpx;
  margin-bottom: 12rpx;
}

.index-feature__title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #333333;
  margin-bottom: 8rpx;
}

.index-feature__desc {
  display: block;
  font-size: 22rpx;
  color: #999999;
}

.index-section {
  padding: 40rpx;
}

.index-section__title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #333333;
  margin-bottom: 24rpx;
}

.index-destinations {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.index-dest {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 20rpx 32rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.index-dest:active {
  background: #f5f5f5;
}

.index-dest__icon {
  font-size: 36rpx;
}

.index-dest__name {
  font-size: 28rpx;
  color: #333333;
  font-weight: 500;
}

.index-steps {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 32rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.index-step {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 16rpx 0;
}

.index-step__num {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: #ffffff;
  font-size: 24rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.index-step__text {
  font-size: 26rpx;
  color: #555555;
}
</style>
