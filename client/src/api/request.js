/**
 * 花海纪 - 统一请求封装
 * 基于 uni.request 封装，支持拦截器、token、错误处理
 */

// 后端 API 基础地址（开发环境）
const BASE_URL = 'http://localhost:8000'

// 请求拦截器类型
type RequestInterceptor = (config: UniApp.RequestOptions) => UniApp.RequestOptions
// 响应拦截器类型
type ResponseInterceptor = (response: any) => any

class Request {
  private baseUrl: string
  private requestInterceptors: RequestInterceptor[] = []
  private responseInterceptors: ResponseInterceptor[] = []

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  /**
   * 添加请求拦截器
   */
  addRequestInterceptor(interceptor: RequestInterceptor) {
    this.requestInterceptors.push(interceptor)
  }

  /**
   * 添加响应拦截器
   */
  addResponseInterceptor(interceptor: ResponseInterceptor) {
    this.responseInterceptors.push(interceptor)
  }

  /**
   * 核心请求方法
   */
  request<T = any>(options: {
    url: string
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
    data?: any
    header?: Record<string, string>
    showLoading?: boolean
    showError?: boolean
  }): Promise<T> {
    const {
      url,
      method = 'GET',
      data,
      header = {},
      showLoading = false,
      showError = true,
    } = options

    // 执行请求拦截器
    let config: UniApp.RequestOptions = {
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
            resolve(responseData.data as T)
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
  get<T = any>(url: string, data?: any, options?: any): Promise<T> {
    return this.request<T>({ url, method: 'GET', data, ...options })
  }

  /**
   * POST 请求
   */
  post<T = any>(url: string, data?: any, options?: any): Promise<T> {
    return this.request<T>({ url, method: 'POST', data, ...options })
  }

  /**
   * PUT 请求
   */
  put<T = any>(url: string, data?: any, options?: any): Promise<T> {
    return this.request<T>({ url, method: 'PUT', data, ...options })
  }

  /**
   * DELETE 请求
   */
  delete<T = any>(url: string, data?: any, options?: any): Promise<T> {
    return this.request<T>({ url, method: 'DELETE', data, ...options })
  }

  /**
   * SSE 流式请求（用于 AI 聊天）
   */
  streamChat(
    url: string,
    data: any,
    onMessage: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: any) => void,
  ) {
    const requestTask = uni.request({
      url: this.baseUrl + url,
      method: 'POST',
      data,
      header: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      enableChunked: true, // 开启分块传输
      success: () => {},
      fail: (err) => {
        onError(err)
      },
    })

    // 注意：微信小程序对 SSE 的支持有限
    // 生产环境建议使用 WebSocket 替代
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
