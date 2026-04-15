/**
 * 花海纪 - 统一请求封装
 * 基于 uni.request 封装，支持拦截器、token、错误处理
 */

// 后端 API 基础地址（开发环境）
const BASE_URL = 'http://47.113.177.25:8000'

class Request {
  constructor(baseUrl) {
    this.baseUrl = baseUrl
    this.requestInterceptors = []
    this.responseInterceptors = []
  }

  /**
   * 添加请求拦截器
   */
  addRequestInterceptor(interceptor) {
    this.requestInterceptors.push(interceptor)
  }

  /**
   * 添加响应拦截器
   */
  addResponseInterceptor(interceptor) {
    this.responseInterceptors.push(interceptor)
  }

  /**
   * 核心请求方法
   */
  request(options) {
    const {
      url,
      method = 'GET',
      data,
      header = {},
      showLoading = false,
      showError = true,
    } = options

    // 执行请求拦截器
    let config = {
      url: this.baseUrl + url,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...header,
      },
    }

    for (const interceptor of this.requestInterceptors) {
      config = interceptor(config)
    }

    return new Promise((resolve, reject) => {
      if (showLoading) {
        uni.showLoading({ title: '加载中...', mask: true })
      }

      uni.request({
        ...config,
        success: (res) => {
          let responseData = res.data

          // 执行响应拦截器
          for (const interceptor of this.responseInterceptors) {
            responseData = interceptor(responseData)
          }

          // 统一响应格式处理
          if (responseData.code === 0) {
            resolve(responseData.data)
          } else {
            if (showError) {
              uni.showToast({
                title: responseData.msg || '请求失败',
                icon: 'none',
              })
            }
            reject(responseData)
          }
        },
        fail: (err) => {
          if (showError) {
            uni.showToast({
              title: '网络异常，请稍后重试',
              icon: 'none',
            })
          }
          reject(err)
        },
        complete: () => {
          if (showLoading) {
            uni.hideLoading()
          }
        },
      })
    })
  }

  /**
   * GET 请求
   */
  get(url, data, options) {
    return this.request({ url, method: 'GET', data, ...options })
  }

  /**
   * POST 请求
   */
  post(url, data, options) {
    return this.request({ url, method: 'POST', data, ...options })
  }

  /**
   * PUT 请求
   */
  put(url, data, options) {
    return this.request({ url, method: 'PUT', data, ...options })
  }

  /**
   * DELETE 请求
   */
  delete(url, data, options) {
    return this.request({ url, method: 'DELETE', data, ...options })
  }

  /**
   * SSE 流式请求（用于 AI 聊天）
   */
  streamChat(url, data, onMessage, onComplete, onError) {
    const requestTask = uni.request({
      url: this.baseUrl + url,
      method: 'POST',
      data,
      header: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      enableChunked: true,
      success: () => {},
      fail: (err) => {
        onError(err)
      },
    })

    return requestTask
  }
}

// 创建请求实例
const http = new Request(BASE_URL)

// 添加请求拦截器 - 自动附加 token
http.addRequestInterceptor((config) => {
  const token = uni.getStorageSync('token')
  if (token) {
    config.header = config.header || {}
    config.header['Authorization'] = `Bearer ${token}`
  }
  return config
})

export default http
export { Request }
