<!--
  花海纪 - 信息确认表单页
  展示从对话中抽取的结构化旅行信息，允许用户修改确认
-->
<template>
  <view class="page confirm-page">
    <!-- 导航栏 -->
    <view class="confirm-nav">
      <view class="confirm-nav__back" @tap="goBack">
        <text>←</text>
      </view>
      <text class="confirm-nav__title">确认旅行信息</text>
      <view style="width: 64rpx;" />
    </view>

    <!-- 加载中 -->
    <view v-if="loading" class="confirm-loading">
      <text class="confirm-loading__text">正在分析对话内容...</text>
    </view>

    <!-- 加载失败 -->
    <view v-else-if="loadError" class="confirm-error">
      <text class="confirm-error__icon">😅</text>
      <text class="confirm-error__text">信息分析失败，请手动填写旅行信息</text>
      <view class="confirm-error__btn" @tap="goBack">
        <text>返回继续对话</text>
      </view>
    </view>

    <template v-else>
      <!-- 信息完整度 -->
      <view class="confirm-header">
        <view class="confirm-progress">
          <view
            class="confirm-progress__bar"
            :style="{ width: (tripStore.plan.confidence * 100) + '%' }"
          />
        </view>
        <text class="confirm-header__text">
          信息完整度：{{ Math.round(tripStore.plan.confidence * 100) }}%
        </text>
      </view>

      <!-- 表单字段 -->
      <view class="confirm-form">
        <view
          v-for="field in formFields"
          :key="field.key"
          class="confirm-field"
          @tap="editField(field)"
        >
          <text class="confirm-field__icon">{{ field.icon }}</text>
          <view class="confirm-field__content">
            <text class="confirm-field__label">{{ field.label }}</text>
            <text
              :class="['confirm-field__value', !tripStore.plan[field.key] ? 'confirm-field__value--empty' : '']"
            >
              {{ tripStore.plan[field.key] || '点击填写' }}
            </text>
          </view>
          <text class="confirm-field__arrow">›</text>
        </view>
      </view>

      <!-- 操作按钮 -->
      <view class="confirm-actions">
        <view class="confirm-btn confirm-btn--secondary" @tap="goBack">
          <text>返回修改</text>
        </view>
        <view
          :class="['confirm-btn confirm-btn--primary', canConfirm ? '' : 'confirm-btn--disabled']"
          @tap="handleConfirm"
        >
          <text>确认并搜索 🚀</text>
        </view>
      </view>
    </template>

    <!-- 编辑弹窗 -->
    <uni-popup ref="editPopup" type="bottom">
      <view class="edit-popup">
        <view class="edit-popup__header">
          <text class="edit-popup__title">{{ editingField?.label }}</text>
          <text class="edit-popup__close" @tap="closeEdit">✕</text>
        </view>
        <input
          v-model="editValue"
          class="edit-popup__input"
          :placeholder="`请输入${editingField?.label}`"
          :focus="true"
        />
        <view class="edit-popup__actions">
          <view class="edit-popup__btn" @tap="closeEdit">
            <text>取消</text>
          </view>
          <view class="edit-popup__btn edit-popup__btn--confirm" @tap="saveEdit">
            <text>确定</text>
          </view>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useTripStore, useChatStore } from '@/store/index'
import { extractInfo, confirmPlan, searchPlaces } from '@/api/index'

const tripStore = useTripStore()
const chatStore = useChatStore()
const loading = ref(true)
const loadError = ref(false)
const editPopup = ref(null)
const editingField = ref(null)
const editValue = ref('')

// 表单字段配置
const formFields = [
  { key: 'destination', label: '目的地', icon: '📍', required: true },
  { key: 'days', label: '出行天数', icon: '📅', required: true },
  { key: 'people_count', label: '出行人数', icon: '👥', required: true },
  { key: 'budget', label: '预算范围', icon: '💰', required: true },
  { key: 'dates', label: '出行日期', icon: '📆', required: false },
  { key: 'people_type', label: '人群类型', icon: '👨‍👩‍👧‍👦', required: false },
  { key: 'accommodation_preference', label: '住宿偏好', icon: '🏨', required: false },
  { key: 'food_preference', label: '饮食偏好', icon: '🍜', required: false },
  { key: 'transport_preference', label: '交通偏好', icon: '🚗', required: false },
  { key: 'interests', label: '兴趣偏好', icon: '🎯', required: false },
  { key: 'special_needs', label: '特殊需求', icon: '⚡', required: false },
]

// 是否可以确认（核心字段已填）
const canConfirm = computed(() => {
  const core = ['destination', 'days', 'people_count', 'budget']
  return core.every(key => tripStore.plan[key])
})

onLoad(async (options) => {
  const tripId = options?.trip_id || chatStore.tripId
  if (!tripId) {
    uni.showToast({ title: '缺少行程信息', icon: 'none' })
    return
  }

  tripStore.setTripId(tripId)

  try {
    // 调用后端抽取信息
    const result = await extractInfo(tripId)
    if (result.trip_plan) {
      tripStore.updatePlan(result.trip_plan)
    }
  } catch (err) {
    loadError.value = true
    uni.showToast({ title: '信息分析失败，请手动填写', icon: 'none' })
  } finally {
    loading.value = false
  }
})

/**
 * 编辑字段
 */
function editField(field) {
  editingField.value = field
  editValue.value = tripStore.plan[field.key] || ''
  editPopup.value?.open()
}

/**
 * 保存编辑
 */
function saveEdit() {
  if (editingField.value && editValue.value.trim()) {
    tripStore.updatePlan({
      [editingField.value.key]: editValue.value.trim(),
    })
  }
  closeEdit()
}

/**
 * 关闭编辑弹窗
 */
function closeEdit() {
  editPopup.value?.close()
}

/**
 * 确认并开始搜索
 */
async function handleConfirm() {
  if (!canConfirm.value) {
    uni.showToast({ title: '请至少填写目的地、天数、人数和预算', icon: 'none' })
    return
  }

  try {
    // 1. 确认计划
    await confirmPlan(tripStore.tripId, tripStore.plan)

    // 2. 开始搜索
    uni.showLoading({ title: '正在为你搜索推荐...', mask: true })
    const result = await searchPlaces(tripStore.tripId)
    tripStore.setSearchResult(result)

    uni.hideLoading()

    // 3. 跳转到地图页
    uni.redirectTo({
      url: `/pages/map/index?trip_id=${tripStore.tripId}`,
    })
  } catch (err) {
    uni.hideLoading()
    uni.showToast({ title: '搜索失败，请重试', icon: 'none' })
  }
}

function goBack() {
  uni.navigateBack()
}
</script>

<style scoped>
.confirm-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.confirm-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24rpx;
  height: 88rpx;
  background: #ffffff;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.confirm-nav__back {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
}

.confirm-nav__title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333333;
}

.confirm-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 200rpx 0;
}

.confirm-loading__text {
  font-size: 28rpx;
  color: #999999;
}

.confirm-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 160rpx 40rpx;
}

.confirm-error__icon {
  font-size: 80rpx;
  margin-bottom: 24rpx;
}

.confirm-error__text {
  font-size: 28rpx;
  color: #888888;
  margin-bottom: 40rpx;
  text-align: center;
}

.confirm-error__btn {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: #ffffff;
  padding: 20rpx 48rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
}

.confirm-header {
  padding: 32rpx 40rpx;
  background: #ffffff;
  margin-bottom: 2rpx;
}

.confirm-progress {
  height: 12rpx;
  background: #f0f0f0;
  border-radius: 6rpx;
  overflow: hidden;
  margin-bottom: 12rpx;
}

.confirm-progress__bar {
  height: 100%;
  background: linear-gradient(90deg, #f093fb, #f5576c);
  border-radius: 6rpx;
  transition: width 0.5s ease;
}

.confirm-header__text {
  font-size: 24rpx;
  color: #888888;
}

.confirm-form {
  background: #ffffff;
  margin: 24rpx 0;
}

.confirm-field {
  display: flex;
  align-items: center;
  padding: 28rpx 40rpx;
  border-bottom: 1rpx solid #f5f5f5;
}

.confirm-field:active {
  background: #fafafa;
}

.confirm-field__icon {
  font-size: 36rpx;
  margin-right: 20rpx;
  width: 48rpx;
  text-align: center;
}

.confirm-field__content {
  flex: 1;
}

.confirm-field__label {
  display: block;
  font-size: 22rpx;
  color: #999999;
  margin-bottom: 4rpx;
}

.confirm-field__value {
  display: block;
  font-size: 28rpx;
  color: #333333;
  font-weight: 500;
}

.confirm-field__value--empty {
  color: #cccccc;
  font-weight: 400;
}

.confirm-field__arrow {
  font-size: 32rpx;
  color: #cccccc;
}

.confirm-actions {
  display: flex;
  gap: 24rpx;
  padding: 40rpx;
}

.confirm-btn {
  flex: 1;
  height: 88rpx;
  border-radius: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  font-weight: 500;
}

.confirm-btn--secondary {
  background: #f5f5f5;
  color: #666666;
}

.confirm-btn--primary {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: #ffffff;
}

.confirm-btn--disabled {
  opacity: 0.5;
}

/* 编辑弹窗 */
.edit-popup {
  background: #ffffff;
  border-radius: 32rpx 32rpx 0 0;
  padding: 40rpx;
  padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
}

.edit-popup__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32rpx;
}

.edit-popup__title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333333;
}

.edit-popup__close {
  font-size: 36rpx;
  color: #999999;
  padding: 8rpx;
}

.edit-popup__input {
  background: #f5f5f5;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 28rpx;
  margin-bottom: 32rpx;
}

.edit-popup__actions {
  display: flex;
  gap: 24rpx;
}

.edit-popup__btn {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  font-size: 28rpx;
  color: #666666;
}

.edit-popup__btn--confirm {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: #ffffff;
}
</style>
