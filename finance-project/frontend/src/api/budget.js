/**
 * 预算管理相关 API
 */
import request from './request'

/**
 * 添加预算
 * @param {Object} data - 预算数据
 * @param {number} data.user_id - 用户ID
 * @param {number|null} data.category_id - 分类ID（总预算时为null）
 * @param {boolean} data.is_total - 是否是月度总预算
 * @param {number} data.amount - 金额
 * @param {string} data.month - 月份（YYYY-MM格式）
 * @returns {Promise}
 */
export function addBudget(data) {
  return request({
    url: '/budget/add',
    method: 'post',
    data: {
      user_id: data.user_id,
      category_id: data.category_id,
      is_total: data.is_total,
      amount: data.amount,
      month: data.month
    }
  })
}

/**
 * 删除预算
 * @param {Object} data
 * @param {number} data.user_id - 用户ID
 * @param {number} data.budget_id - 预算ID
 * @returns {Promise}
 */
export function deleteBudget(data) {
  return request({
    url: '/budget/delete',
    method: 'delete',
    data: {
      user_id: data.user_id,
      budget_id: data.budget_id
    }
  })
}

/**
 * 修改预算
 * @param {Object} data
 * @param {number} data.user_id - 用户ID
 * @param {number} data.budget_id - 预算ID
 * @param {number} data.amount - 金额
 * @returns {Promise}
 */
export function updateBudget(data) {
  return request({
    url: '/budget/update',
    method: 'put',
    data: {
      user_id: data.user_id,
      budget_id: data.budget_id,
      amount: data.amount
    }
  })
}

/**
 * 获取月度预算列表
 * @param {Object} params
 * @param {number} params.user_id - 用户ID
 * @param {string} params.month - 月份（YYYY-MM格式）
 * @returns {Promise}
 */
export function getBudgetListByMonth(params) {
  return request({
    url: '/budget/list_month',
    method: 'get',
    params: {
      user_id: params.user_id,
      month: params.month
    }
  })
}
