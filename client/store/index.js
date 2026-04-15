/**
 * 花海纪 - Pinia 状态管理
 */
import { defineStore } from 'pinia'

// ==================== 用户 Store ====================
export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null as any,
    token: '',
    userId: '',
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    setToken(token: string) {
      this.token = token
      uni.setStorageSync('token', token)
    },

    setUserInfo(info: any) {
      this.userInfo = info
      uni.setStorageSync('userInfo', JSON.stringify(info))
    },

    logout() {
      this.token = ''
      this.userInfo = null
      this.userId = ''
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
    },

    // 从本地存储恢复
    restoreFromStorage() {
      this.token = uni.getStorageSync('token') || ''
      const info = uni.getStorageSync('userInfo')
      if (info) {
        this.userInfo = typeof info === 'string' ? JSON.parse(info) : info
      }
    },
  },
})

// ==================== 聊天 Store ====================
export const useChatStore = defineStore('chat', {
  state: () => ({
    tripId: '' as string,
    messages: [] as Array<{ role: string; content: string }>,
    isLoading: false,
    isInfoComplete: false,
  }),

  getters: {
    lastMessage: (state) => {
      if (state.messages.length === 0) return null
      return state.messages[state.messages.length - 1]
    },
  },

  actions: {
    addMessage(role: string, content: string) {
      this.messages.push({ role, content })
    },

    clearMessages() {
      this.messages = []
      this.tripId = ''
      this.isInfoComplete = false
    },

    setTripId(tripId: string) {
      this.tripId = tripId
    },

    setLoading(loading: boolean) {
      this.isLoading = loading
    },

    setInfoComplete(complete: boolean) {
      this.isInfoComplete = complete
    },
  },
})

// ==================== 旅行计划 Store ====================
export const useTripStore = defineStore('trip', {
  state: () => ({
    tripId: '' as string,
    plan: {
      people_count: '',
      people_type: '',
      budget: '',
      days: '',
      destination: '',
      dates: '',
      accommodation_preference: '',
      food_preference: '',
      transport_preference: '',
      special_needs: '',
      interests: '',
      confidence: 0,
    } as Record<string, any>,
    searchResult: null as any,
    isSearching: false,
  }),

  getters: {
    hasPlan: (state) => !!state.plan.destination,
    allPlaces: (state) => {
      if (!state.searchResult) return []
      const { attractions = [], restaurants = [], hotels = [] } = state.searchResult
      return [...attractions, ...restaurants, ...hotels]
    },
  },

  actions: {
    setTripId(tripId: string) {
      this.tripId = tripId
    },

    updatePlan(plan: Record<string, any>) {
      this.plan = { ...this.plan, ...plan }
    },

    resetPlan() {
      this.plan = {
        people_count: '',
        people_type: '',
        budget: '',
        days: '',
        destination: '',
        dates: '',
        accommodation_preference: '',
        food_preference: '',
        transport_preference: '',
        special_needs: '',
        interests: '',
        confidence: 0,
      }
    },

    setSearchResult(result: any) {
      this.searchResult = result
    },

    setSearching(searching: boolean) {
      this.isSearching = searching
    },
  },
})
