<!--
  花海纪 - AI 聊天页
  核心交互页面：与 AI 对话收集旅行需求
-->
<template>
  <view class="page chat-page">
    <!-- 导航栏 -->
    <view class="chat-nav">
      <view class="chat-nav__back" @tap="goBack">
        <text>←</text>
      </view>
      <text class="chat-nav__title">🌸 花海纪</text>
      <view class="chat-nav__action" @tap="handleExtract">
        <text>📋</text>
      </view>
    </view>

    <!-- 消息列表 -->
    <scroll-view
      class="chat-messages"
      scroll-y
      :scroll-top="scrollTop"
      :scroll-into-view="scrollIntoView"
    >
      <!-- 欢迎消息 -->
      <view v-if="chatStore.messages.length === 0" class="chat-welcome">
        <text class="chat-welcome__icon">🌸</text>
        <text class="chat-welcome__title">你好，我是花海纪！</text>
        <text class="chat-welcome__desc">你的 AI 旅行规划助手</text>
        <text class="chat-welcome__hint">告诉我你想去哪里旅行吧～</text>
      </view>

      <!-- 消息列表 -->
      <view
        v-for="(msg, index) in chatStore.messages"
        :key="index"
        :id="'msg-' + index"
      >
        <MsgBubble :content="msg.content" :is-user="msg.role === 'user'" />
      </view>

      <!-- 加载中 -->
      <view v-if="chatStore.isLoading" class="chat-loading">
        <text class="chat-loading__dots">正在思考中<span class="dot-anim">...</span></text>
      </view>

      <!-- 信息完整提示 -->
      <view v-if="chatStore.isInfoComplete" class="chat-complete-tip">
        <text class="chat-complete-tip__text">✅ 旅行信息已收集完整</text>
        <view class="chat-complete-tip__btn" @tap="goToConfirm">
          <text>查看并确认 →</text>
        </view>
      </view>

      <view style="height: 20rpx;" />
    </scroll-view>

    <!-- 底部输入区 -->
    <view class="chat-input-bar">
      <view class="chat-input-wrap">
        <input
          v-model="inputText"
          class="chat-input"
          placeholder="描述你的旅行计划..."
          :disabled="chatStore.isLoading"
          confirm-type="send"
          @confirm="handleSend"
        />
        <view
          :class="['chat-send-btn', inputText.trim() ? 'chat-send-btn--active' : '']"
          @tap="handleSend"
        >
          <text class="chat-send-btn__text">发送</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import MsgBubble from '@/components/MsgBubble.vue'
import { useChatStore } from '@/store/index'
import { sendMessage, extractInfo } from '@/api/index'

const chatStore = useChatStore()
const inputText = ref('')
const scrollTop = ref(0)
const scrollIntoView = ref('')

onLoad((options) => {
  // 如果从首页带目的地参数过来，自动发送
  if (options?.destination) {
    inputText.value = `我想去${options.destination}旅行`
    nextTick(() => handleSend())
  }
})

/**
 * 发送消息
 */
async function handleSend() {
  const text = inputText.value.trim()
  if (!text || chatStore.isLoading) return

  // 添加用户消息
  chatStore.addMessage('user', text)
  inputText.value = ''
  chatStore.setLoading(true)

  // 滚动到底部
  await scrollToBottom()

  try {
    const result = await sendMessage({
      message: text,
      trip_id: chatStore.tripId || undefined,
    })

    // 添加 AI 回复
    chatStore.addMessage('assistant', result.reply)

    // 保存 trip_id
    if (result.trip_id) {
      chatStore.setTripId(result.trip_id)
    }

    // 检查信息是否完整
    if (result.is_info_complete) {
      chatStore.setInfoComplete(true)
    }
  } catch (err) {
    chatStore.addMessage('assistant', '抱歉，我遇到了一些问题，请稍后再试～')
  } finally {
    chatStore.setLoading(false)
    await scrollToBottom()
  }
}

/**
 * 手动触发信息抽取
 */
async function handleExtract() {
  if (!chatStore.tripId) {
    uni.showToast({ title: '请先开始对话', icon: 'none' })
    return
  }

  uni.showLoading({ title: '正在分析...' })
  try {
    const result = await extractInfo(chatStore.tripId)
    if (result.completeness?.is_complete) {
      chatStore.setInfoComplete(true)
      uni.showToast({ title: '信息已收集完整', icon: 'success' })
    } else {
      const missing = result.completeness?.missing_fields || []
      uni.showToast({
        title: `还需了解：${missing.join('、')}`,
        icon: 'none',
      })
    }
  } catch (err) {
    uni.showToast({ title: '分析失败', icon: 'none' })
  } finally {
    uni.hideLoading()
  }
}

/**
 * 跳转到确认页
 */
function goToConfirm() {
  uni.navigateTo({
    url: `/pages/confirm/index?trip_id=${chatStore.tripId}`,
  })
}

/**
 * 返回
 */
function goBack() {
  uni.navigateBack()
}

/**
 * 滚动到底部
 */
async function scrollToBottom() {
  await nextTick()
  const index = chatStore.messages.length - 1
  scrollIntoView.value = ''
  await nextTick()
  scrollIntoView.value = 'msg-' + index
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.chat-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24rpx;
  height: 88rpx;
  background: #ffffff;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
  position: relative;
  z-index: 10;
}

.chat-nav__back,
.chat-nav__action {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
}

.chat-nav__title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333333;
}

.chat-messages {
  flex: 1;
  padding: 20rpx 0;
}

.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 40rpx;
}

.chat-welcome__icon {
  font-size: 100rpx;
  margin-bottom: 24rpx;
}

.chat-welcome__title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333333;
  margin-bottom: 12rpx;
}

.chat-welcome__desc {
  font-size: 28rpx;
  color: #888888;
  margin-bottom: 32rpx;
}

.chat-welcome__hint {
  font-size: 26rpx;
  color: #f5576c;
  background: #fff0f3;
  padding: 16rpx 32rpx;
  border-radius: 32rpx;
}

.chat-loading {
  padding: 24rpx 48rpx;
}

.chat-loading__dots {
  font-size: 26rpx;
  color: #999999;
}

.dot-anim {
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0%, 20% { opacity: 0; }
  50% { opacity: 1; }
  100% { opacity: 0; }
}

.chat-complete-tip {
  margin: 24rpx 48rpx;
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-complete-tip__text {
  font-size: 26rpx;
  color: #2e7d32;
  font-weight: 500;
}

.chat-complete-tip__btn {
  background: #2e7d32;
  color: #ffffff;
  padding: 12rpx 24rpx;
  border-radius: 24rpx;
  font-size: 24rpx;
}

.chat-input-bar {
  background: #ffffff;
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.chat-input-wrap {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #f5f5f5;
  border-radius: 40rpx;
  padding: 8rpx 8rpx 8rpx 28rpx;
}

.chat-input {
  flex: 1;
  font-size: 28rpx;
  height: 72rpx;
  color: #333333;
}

.chat-send-btn {
  width: 96rpx;
  height: 72rpx;
  border-radius: 36rpx;
  background: #cccccc;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.chat-send-btn--active {
  background: linear-gradient(135deg, #f093fb, #f5576c);
}

.chat-send-btn__text {
  font-size: 26rpx;
  color: #ffffff;
  font-weight: 500;
}
</style>
