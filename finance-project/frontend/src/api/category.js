/**
 * 账单分类相关 API
 */
import request from './request'

/**
 * 获取账单分类列表
 * @param {number} type - 分类类型：1=收入，2=支出
 * @returns {Promise}
 */
export function getCategoryList(type) {
  return request({
    url: '/category/list',
    method: 'get',
    params: { type }
  })
}

/**
 * 分类映射管理类
 * 用于管理前端中文类型名称与后端 category_id 的映射关系
 */
export class CategoryMapper {
  constructor() {
    this.expenseCategories = [] // 支出分类列表
    this.incomeCategories = [] // 收入分类列表
    this.expenseMap = new Map() // 支出类型名 -> ID
    this.incomeMap = new Map() // 收入类型名 -> ID
    this.expenseIdMap = new Map() // 支出ID -> 类型名
    this.incomeIdMap = new Map() // 收入ID -> 类型名
  }

  /**
   * 初始化分类映射
   * 需要在应用启动时调用，或在用户登录后调用
   */
  async init() {
    try {
      // 获取支出分类
      const expenseRes = await getCategoryList(2)
      if (expenseRes.code === 200 && expenseRes.data) {
        this.expenseCategories = expenseRes.data
        expenseRes.data.forEach((item) => {
          this.expenseMap.set(item.name, item.id)
          this.expenseIdMap.set(item.id, item.name)
        })
      }

      // 获取收入分类
      const incomeRes = await getCategoryList(1)
      if (incomeRes.code === 200 && incomeRes.data) {
        this.incomeCategories = incomeRes.data
        incomeRes.data.forEach((item) => {
          this.incomeMap.set(item.name, item.id)
          this.incomeIdMap.set(item.id, item.name)
        })
      }

      console.log('✅ 分类映射初始化成功')
      console.log('支出分类:', this.expenseCategories)
      console.log('收入分类:', this.incomeCategories)
    } catch (error) {
      console.error('❌ 分类映射初始化失败:', error)
    }
  }

  /**
   * 根据支出类型名称获取ID
   * @param {string} name - 类型名称（如"餐饮美食"）
   * @returns {number|null}
   */
  getExpenseCategoryId(name) {
    return this.expenseMap.get(name) || null
  }

  /**
   * 根据收入类型名称获取ID
   * @param {string} name - 类型名称（如"工资"）
   * @returns {number|null}
   */
  getIncomeCategoryId(name) {
    return this.incomeMap.get(name) || null
  }

  /**
   * 根据支出分类ID获取名称
   * @param {number} id - 分类ID
   * @returns {string|null}
   */
  getExpenseCategoryName(id) {
    return this.expenseIdMap.get(id) || null
  }

  /**
   * 根据收入分类ID获取名称
   * @param {number} id - 分类ID
   * @returns {string|null}
   */
  getIncomeCategoryName(id) {
    return this.incomeIdMap.get(id) || null
  }

  /**
   * 获取所有支出分类
   * @returns {Array}
   */
  getExpenseCategories() {
    return this.expenseCategories
  }

  /**
   * 获取所有收入分类
   * @returns {Array}
   */
  getIncomeCategories() {
    return this.incomeCategories
  }
}

// 创建全局单例
export const categoryMapper = new CategoryMapper()
