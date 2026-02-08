/**
 * 手机号验证码相关 API
 */
import request from './request'

/**
 * 发送短信验证码
 * @param {Object} data
 * @param {string} data.phone - 手机号
 * @param {number} data.type - 1注册登录 2更新手机 3修改密码 4绑定新手机 5验证手机
 */
export function sendVerifyCode(data) {
  return request({
    url: '/user/send_verify_code',
    method: 'post',
    data,
  })
}

/**
 * 校验短信验证码
 * @param {Object} data
 * @param {string} data.phone - 手机号
 * @param {string} data.verify_code - 验证码
 */
export function verifyCode(data) {
  return request({
    url: '/user/verify_code',
    method: 'post',
    data,
  })
}