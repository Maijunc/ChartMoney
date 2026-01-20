/**
 * 用户设置相关 API
 */
import request from './request'

/**
 * 获取当前用户信息
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
 * @param {Object} data - 用户数据
 * @param {string} data.phone - 手机号（可选）
 * @param {string} data.avatar - 头像URL（可选）
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
 * 上传头像
 * @param {File} file - 头像文件
 * @returns {Promise}
 */
export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/upload/avatar',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 导出用户数据
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export function exportUserData(userId) {
  return request({
    url: '/user/export',
    method: 'get',
    params: { user_id: userId },
    responseType: 'blob'
  })
}

/**
 * 清理过期数据
 * @param {number} userId - 用户ID
 * @param {number} days - 保留天数
 * @returns {Promise}
 */
export function clearExpiredData(userId, days = 365) {
  return request({
    url: '/user/clear-expired',
    method: 'delete',
    data: { user_id: userId, days }
  })
}

/**
 * 清空所有数据
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export function clearAllData(userId) {
  return request({
    url: '/user/clear-all',
    method: 'delete',
    data: { user_id: userId }
  })
}
