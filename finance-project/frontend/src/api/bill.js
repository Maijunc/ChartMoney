/**
 * 账单管理相关 API
 */
import request from './request'

/**
 * 添加账单
 * @param {Object} data - 账单数据
 * @param {number} data.user_id - 用户ID
 * @param {number} data.category_id - 分类ID
 * @param {number} data.method_id - 支付方式ID
 * @param {string} data.name - 账单名称
 * @param {number} data.amount - 金额
 * @param {string} data.bill_time - 账单时间（ISO格式）
 * @param {string} [data.remark] - 备注
 * @returns {Promise}
 */
export function addBill(data) {
  return request({
    url: '/bill/add',
    method: 'post',
    data: {
      user_id: data.user_id,
      category_id: data.category_id,
      method_id: data.method_id,
      name: data.name,
      amount: data.amount,
      bill_time: data.bill_time,
      remark: data.remark || ''
    }
  })
}

/**
 * 修改账单
 * @param {Object} data - 账单数据
 * @param {number} data.user_id - 用户ID
 * @param {number} data.bill_id - 账单ID
 * @param {number} data.category_id - 分类ID
 * @param {number} data.method_id - 支付方式ID
 * @param {string} data.name - 账单名称
 * @param {number} data.amount - 金额
 * @param {string} data.bill_time - 账单时间（ISO格式）
 * @param {string} [data.remark] - 备注
 * @returns {Promise}
 */
export function updateBill(data) {
  return request({
    url: '/bill/update',
    method: 'put',
    data: {
      user_id: data.user_id,
      bill_id: data.bill_id,
      category_id: data.category_id,
      method_id: data.method_id,
      name: data.name,
      amount: data.amount,
      bill_time: data.bill_time,
      remark: data.remark || ''
    }
  })
}

/**
 * 删除单个账单
 * @param {Object} data
 * @param {number} data.user_id - 用户ID
 * @param {number} data.bill_id - 账单ID
 * @returns {Promise}
 */
export function deleteBill(data) {
  return request({
    url: '/bill/delete',
    method: 'delete',
    data: {
      user_id: data.user_id,
      bill_id: data.bill_id
    }
  })
}

/**
 * 批量删除账单
 * @param {Object} data
 * @param {number} data.user_id - 用户ID
 * @param {Array<number>} data.bill_ids - 账单ID数组
 * @returns {Promise}
 */
export function batchDeleteBill(data) {
  return request({
    url: '/bill/batch-delete',
    method: 'delete',
    data: {
      user_id: data.user_id,
      bill_ids: data.bill_ids
    }
  })
}

/**
 * 获取账单列表（分页）
 * @param {Object} params
 * @param {number} params.user_id - 用户ID
 * @param {string} params.the_time - 月份（YYYY-MM格式，如"2026-01"）
 * @param {number} params.page - 页码（从1开始）
 * @param {number} params.page_size - 每页条数（最小15）
 * @param {number} params.type - 类型：1=收入，2=支出
 * @returns {Promise}
 */
export function getBillList(params) {
  return request({
    url: '/bill/list',
    method: 'get',
    params: {
      user_id: params.user_id,
      the_time: params.the_time,
      page: params.page,
      page_size: params.page_size,
      type: params.type
    }
  })
}

/**
 * 获取账单列表（不分页）
 * @param {Object} params
 * @param {number} params.user_id - 用户ID
 * @param {string} params.the_time - 月份（YYYY-MM格式，如"2026-01"）
 * @param {number} params.type - 类型：1=收入，2=支出
 * @returns {Promise}
 */
export function getBillListFirst(params) {
  return request({
    url: '/bill/list_first',
    method: 'get',
    params: {
      user_id: params.user_id,
      the_time: params.the_time,
      type: params.type
    }
  })
}

/**
 * 账单数据转换工具类
 * 用于前端数据模型与后端数据模型之间的转换
 */
export class BillTransformer {
  /**
   * 前端支出数据 -> 后端账单数据
   * @param {Object} expenseData - 前端支出数据
   * @param {number} userId - 用户ID
   * @param {number} categoryId - 分类ID
   * @returns {Object} 后端账单数据
   */
  static expenseToBackend(expenseData, userId, categoryId) {
    return {
      user_id: userId,
      category_id: categoryId,
      amount: parseFloat(expenseData.money || expenseData.amount),
      bill_time: this.formatDateTime(expenseData.time || expenseData.date),
      remark: expenseData.extra || expenseData.remark || ''
    }
  }

  /**
   * 前端收入数据 -> 后端账单数据
   * @param {Object} incomeData - 前端收入数据
   * @param {number} userId - 用户ID
   * @param {number} categoryId - 分类ID
   * @returns {Object} 后端账单数据
   */
  static incomeToBackend(incomeData, userId, categoryId) {
    return {
      user_id: userId,
      category_id: categoryId,
      amount: parseFloat(incomeData.amount),
      bill_time: this.formatDateTime(incomeData.date),
      remark: incomeData.remark || ''
    }
  }

  /**
   * 后端账单数据 -> 前端支出数据
   * @param {Object} billData - 后端账单数据
   * @param {string} categoryName - 分类名称
   * @returns {Object} 前端支出数据
   */
  static backendToExpense(billData, categoryName) {
    return {
      id: billData.id,
      time: this.formatDate(billData.bill_time),
      type: categoryName,
      name: billData.name,
      money: parseFloat(billData.amount),
      extra: billData.remark || '',
      isEditing: false
    }
  }

  /**
   * 后端账单数据 -> 前端收入数据
   * @param {Object} billData - 后端账单数据
   * @param {string} categoryName - 分类名称
   * @returns {Object} 前端收入数据
   */
  static backendToIncome(billData, categoryName) {
    return {
      id: billData.id,
      date: this.formatDate(billData.bill_time),
      ctype: categoryName,
      source: billData.name,
      amount: parseFloat(billData.amount),
      remark: billData.remark || '',
      isEditing: false
    }
  }

  /**
   * 将日期字符串转换为 ISO 格式的 datetime
   * @param {string} dateStr - 日期字符串（YYYY-MM-DD）
   * @returns {string} ISO格式的datetime（YYYY-MM-DDTHH:mm:ss）
   */
  static formatDateTime(dateStr) {
    if (!dateStr) return new Date().toISOString()

    // 如果已经是完整的datetime格式，直接返回
    if (dateStr.includes('T')) {
      return dateStr
    }

    // 否则添加时间部分（默认12:00:00）
    return `${dateStr}T12:00:00`
  }

  /**
   * 将 datetime 转换为日期字符串
   * @param {string} datetime - ISO格式的datetime
   * @returns {string} 日期字符串（YYYY-MM-DD）
   */
  static formatDate(datetime) {
    if (!datetime) return ''
    return datetime.split('T')[0]
  }

  /**
   * 获取当前月份（YYYY-MM格式）
   * @returns {string}
   */
  static getCurrentMonth() {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    return `${year}-${month}`
  }
}
