/**
 * 分析统计相关 API
 */
import request from './request'

/**
 * 获取趋势数据（按天）
 * @param {Object} params
 * @param {number} params.user_id - 用户ID
 * @param {number} params.days - 天数（最少7天）
 * @returns {Promise}
 */
export function getTrendDays(params) {
  return request({
    url: '/analysis/trend/days',
    method: 'get',
    params: {
      user_id: params.user_id,
      days: params.days || 7
    }
  })
}

/**
 * 获取趋势数据（按月）
 * @param {Object} params
 * @param {number} params.user_id - 用户ID
 * @param {number} params.months - 月数（最少3个月）
 * @returns {Promise}
 */
export function getTrendMonths(params) {
  return request({
    url: '/analysis/trend/months',
    method: 'get',
    params: {
      user_id: params.user_id,
      months: params.months || 6
    }
  })
}

/**
 * 获取近期账单(只获取近6条账单记录)
 * @param {Object} params
 * @param {number} params.user_id - 用户ID
 * @returns {Promise}
 */
export function getRecentBills(params) {
  return request({
    url: '/analysis/recent_bills',
    method: 'get',
    params: {
      user_id: params.user_id,
    }
  })
}

/**
 * 获取消费类别占比（单个月）
 * @param {Object} params
 * @param {number} params.user_id - 用户ID
 * @param {number} params.month - 月份（-1=全部，0=当月数据，1=两个月数据，以此类推，最多获取一年的数据）
 * @returns {Promise}
 */
export function getExpenseProportionMonth(params) {
  return request({
    url: '/analysis/expense_propotion_month',
    method: 'get',
    params: {
      user_id: params.user_id,
      month: params.month || 0
    }
  })
}
