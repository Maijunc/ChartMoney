/**
 * 用户认证相关 API
 */
import request from './request'

/**
 * 用户登录
 * @param {Object} data - 登录数据
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @returns {Promise}
 */
export function login(data) {
  return request({
    url: '/user/login',
    method: 'post',
    data: {
      username: data.username,
      password: data.password
    }
  })
}

/**
 * 用户注册
 * @param {Object} data - 注册数据
 * @param {string} data.username - 用户名
 * @param {string} data.phone - 手机号（11位数字）
 * @param {string} data.password - 密码
 * @returns {Promise}
 */
export function register(data) {
  return request({
    url: '/user/register',
    method: 'post',
    data: {
      username: data.username,
      phone: data.phone,
      password: data.password
    }
  })
}

/**
 * 退出登录（前端操作）
 */
export function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  localStorage.removeItem('userId')
}

/**
 * 获取当前用户信息（需要 Token）
 * @returns {Promise}
 */
export function getUserInfo() {
  return request({
    url: '/user/me',
    method: 'get'
  })
}

/**
 * 更新用户信息
 * @param {Object} data - 用户信息
 * @param {string} data.phone - 手机号
 * @param {string} data.avatar - 头像URL
 * @returns {Promise}
 */
export function updateUserInfo(data) {
  return request({
    url: '/user/update',
    method: 'put',
    data
  })
}

/**
 * 校验短信验证码
 * @param {Object} data
 * @param {string} data.phone - 手机号
 * @param {string} data.verify_code - 验证码
 */
export function loginByPhone(data) {
  return request({
    url: '/user/login_by_phone',
    method: 'post',
    data
  })
}