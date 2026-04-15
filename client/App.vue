<template>
  <view>
    <!-- uni-app 根组件 -->
  </view>
</template>

<script setup>
import { onLaunch } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/index'

onLaunch(() => {
  // 从本地存储恢复用户状态
  const userStore = useUserStore()
  userStore.restoreFromStorage()
})
</script>

<style>
/* 全局样式 */
page {
  background: #f8f9fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 28rpx;
  color: #333333;
}

/* 全局滚动条隐藏 */
::-webkit-scrollbar {
  display: none;
}
</style>
