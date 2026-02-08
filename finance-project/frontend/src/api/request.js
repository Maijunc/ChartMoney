/**
 * Axios 请求封装
 * 统一配置、请求拦截、响应拦截、错误处理
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://localhost:8000', // 后端API地址，根据实际情况修改
  timeout: 10000, // 请求超时时间
  headers: {
    'Content-Type': 'application/json;charset=UTF-8'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token（如果后端需要）
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 打印请求信息（开发环境）
    if (import.meta.env.DEV) {
      console.log('🚀 Request:', config.method.toUpperCase(), config.url, config.params || config.data)
    }

    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 打印响应信息（开发环境）
    if (import.meta.env.DEV) {
      console.log('✅ Response:', response.config.url, response.data)
    }

    // 文件下载直接返回响应
    if (response.config.responseType === 'blob') {
      return response
    }

    // 后端返回的数据结构：{ code, message, data }
    const { code, message } = response.data

    // 成功响应（200）
    if (code === 200) {
      return response.data
    }

    // 其他情况视为业务错误
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message || '请求失败'))
  },
  (error) => {
    console.error('❌ Response Error:', error)

    // HTTP 错误处理
    if (error.response) {
      const { status, data } = error.response

      // 优先使用后端返回的 detail 字段
      let errorMessage = data.detail || data.message || ''

      // 根据不同状态码设置默认错误信息
      switch (status) {
        case 400:
          errorMessage = errorMessage || '请求参数错误'
          break
        case 401:
          errorMessage = errorMessage || '登录已过期，请重新登录'
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          localStorage.removeItem('userId')
          router.push('/login')
          break
        case 403:
          errorMessage = errorMessage || '没有权限访问'
          break
        case 404:
          errorMessage = errorMessage || '请求的资源不存在'
          break
        case 409:
          errorMessage = errorMessage || '数据冲突'
          break
        case 422:
          errorMessage = errorMessage || '数据验证失败'
          break
        case 500:
          errorMessage = errorMessage || '服务器内部错误'
          break
        default:
          errorMessage = errorMessage || `请求失败 (${status})`
      }

      ElMessage.error(errorMessage)
    } else if (error.request) {
      // 请求已发出但没有收到响应
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      // 其他错误
      ElMessage.error(error.message || '请求失败')
    }

    return Promise.reject(error)
  }
)

export default request
