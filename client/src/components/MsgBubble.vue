<!--
  花海纪 - 消息气泡组件
  用于聊天页面的单条消息展示
-->
<template>
  <view :class="['msg-bubble', isUser ? 'msg-bubble--user' : 'msg-bubble--ai']">
    <!-- AI 头像 -->
    <view v-if="!isUser" class="msg-avatar">
      <text class="msg-avatar__icon">🌸</text>
    </view>

    <!-- 消息内容 -->
    <view class="msg-content">
      <rich-text
        v-if="!isUser"
        :nodes="formattedContent"
        class="msg-content__text msg-content__text--ai"
      />
      <text v-else class="msg-content__text msg-content__text--user">{{ content }}</text>
    </view>

    <!-- 用户头像 -->
    <view v-if="isUser" class="msg-avatar msg-avatar--user">
      <text class="msg-avatar__icon">😊</text>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { simpleMarkdown } from '@/utils/index'

const props = defineProps({
  content: {
    type: String,
    default: '',
  },
  isUser: {
    type: Boolean,
    default: false,
  },
})

// AI 消息支持简单 Markdown 渲染
const formattedContent = computed(() => {
  if (props.isUser) return props.content
  return simpleMarkdown(props.content)
})
</script>

<style scoped>
.msg-bubble {
  display: flex;
  align-items: flex-start;
  margin-bottom: 32rpx;
  padding: 0 24rpx;
}

.msg-bubble--user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #f093fb, #f5576c);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.msg-avatar--user {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.msg-avatar__icon {
  font-size: 36rpx;
}

.msg-content {
  max-width: 75%;
  margin: 0 16rpx;
}

.msg-content__text {
  padding: 20rpx 28rpx;
  border-radius: 24rpx;
  font-size: 28rpx;
  line-height: 1.6;
  word-break: break-all;
}

.msg-content__text--ai {
  background: #ffffff;
  color: #333333;
  border-top-left-radius: 8rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.msg-content__text--user {
  background: linear-gradient(135deg, #f093fb, #f5576c);
  color: #ffffff;
  border-top-right-radius: 8rpx;
}
</style>
