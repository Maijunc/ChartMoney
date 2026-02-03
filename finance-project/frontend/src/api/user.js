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
 * 导出用户数据（CSV/XLSX）
 * @param {string} format - csv 或 xlsx
 * @returns {Promise}
 */
export function exportUserData(format = 'csv') {
  return request({
    url: '/user/export',
    method: 'get',
    params: { format },
    responseType: 'blob'
  })
}

/**
 * 导入用户数据（CSV/XLSX）
 * @param {File} file - 导入文件
 * @param {string} strategy - merge 或 replace
 * @returns {Promise}
 */
export function importUserData(file, strategy = 'merge') {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/user/import',
    method: 'post',
    params: { strategy },
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
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
