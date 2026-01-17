/**
 * 用户状态管理 Store
 * 管理用户登录状态、用户信息等
 */
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { login as apiLogin, register as apiRegister, logout as apiLogout } from '../api/index.js'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  // 状态
  const userId = ref(null)
  const username = ref('')
  const phone = ref('')
  const avatar = ref('')
  const token = ref('')
  const isLogin = computed(() => !!userId.value)

  /**
   * 初始化用户信息（从 localStorage 恢复）
   */
  function initUserInfo() {
    const storedUserId = localStorage.getItem('userId')
    const storedUsername = localStorage.getItem('username')
    const storedPhone = localStorage.getItem('phone')
    const storedAvatar = localStorage.getItem('avatar')
    const storedToken = localStorage.getItem('token')

    if (storedUserId) {
      userId.value = parseInt(storedUserId)
      username.value = storedUsername || ''
      phone.value = storedPhone || ''
      avatar.value = storedAvatar || ''
      token.value = storedToken || ''
      console.log('✅ 用户信息已从缓存恢复:', { userId: userId.value, username: username.value })
    }
  }

  /**
   * 保存用户信息到 localStorage
   */
  function saveUserInfo() {
    localStorage.setItem('userId', userId.value)
    localStorage.setItem('username', username.value)
    localStorage.setItem('phone', phone.value)
    localStorage.setItem('avatar', avatar.value)
    localStorage.setItem('token', token.value)
  }

  /**
   * 用户登录
   * @param {Object} loginData
   * @param {string} loginData.username - 用户名
   * @param {string} loginData.password - 密码
   */
  async function login(loginData) {
    try {
      const res = await apiLogin({
        username: loginData.username,
        password: loginData.password
      })

      if (res.code === 200 && res.data) {
        // ✅ 保存后端返回的用户信息和 Token
        userId.value = res.data.user_id
        username.value = res.data.username
        phone.value = res.data.phone || ''
        avatar.value = res.data.avatar || ''
        token.value = res.data.token  // ✅ 保存 JWT Token

        saveUserInfo()

        console.log('✅ 登录成功，Token 已保存:', {
          userId: userId.value,
          username: username.value,
          tokenPreview: token.value.substring(0, 20) + '...'
        })

        ElMessage.success('登录成功！')
        return true
      }
      return false
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  /**
   * 用户注册
   * @param {Object} registerData
   * @param {string} registerData.username - 用户名
   * @param {string} registerData.phone - 手机号
   * @param {string} registerData.password - 密码
   */
  async function register(registerData) {
    try {
      const res = await apiRegister({
        username: registerData.username,
        phone: registerData.phone,
        password: registerData.password
      })

      if (res.code === 200 && res.data) {
        // ✅ 注册成功后，保存用户信息（可选：直接登录）
        userId.value = res.data.user_id
        username.value = res.data.username
        phone.value = res.data.phone || ''
        avatar.value = res.data.avatar || ''
        // 注意：注册接口目前不返回 Token，需要再次登录
        // 如果需要注册后自动登录，可以调用登录接口

        saveUserInfo()

        ElMessage.success('注册成功！')
        return true
      }
      return false
    } catch (error) {
      console.error('注册失败:', error)
      return false
    }
  }

  /**
   * 用户退出登录
   */
  function logout() {
    userId.value = null
    username.value = ''
    phone.value = ''
    avatar.value = ''
    token.value = ''

    apiLogout()

    ElMessage.success('已退出登录')
    // 重定向到登录页
    window.location.href = '/login'
  }

  /**
   * 设置用户信息（用于登录后手动设置）
   */
  function setUserInfo(userInfo) {
    if (userInfo.id) userId.value = userInfo.id
    if (userInfo.user_id) userId.value = userInfo.user_id
    if (userInfo.username) username.value = userInfo.username
    if (userInfo.phone) phone.value = userInfo.phone
    if (userInfo.avatar) avatar.value = userInfo.avatar
    if (userInfo.token) token.value = userInfo.token

    saveUserInfo()
  }

  // 初始化时恢复用户信息
  initUserInfo()

  return {
    // 状态
    userId,
    username,
    phone,
    avatar,
    token,
    isLogin,

    // 方法
    login,
    register,
    logout,
    setUserInfo,
    initUserInfo
  }
})
