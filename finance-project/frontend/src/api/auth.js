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
