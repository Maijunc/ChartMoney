/**
 * 支付方式相关 API
 */
import request from './request'

/**
 * 获取支付方式列表
 * @returns {Promise}
 */
export function getPaymentMethodList() {
  return request({
    url: '/payment_method/list',
    method: 'get'
  })
}

/**
 * 支付方式映射管理类
 * 用于管理前端支付方式名称与后端 method_id 的映射关系
 */
export class PaymentMethodMapper {
  constructor() {
    this.paymentMethods = [] // 支付方式列表
    this.paymentMap = new Map() // 支付方式名 -> ID
    this.paymentIdMap = new Map() // 支付方式ID -> 名称
  }

  /**
   * 初始化支付方式映射
   * 需要在应用启动时调用，或在用户登录后调用
   */
  async init() {
    try {
      const res = await getPaymentMethodList()
      if (res.code === 200 && res.data) {
        this.paymentMethods = res.data
        res.data.forEach((item) => {
          this.paymentMap.set(item.name, item.method_id)
          this.paymentIdMap.set(item.method_id, item.name)
        })

        console.log('✅ 支付方式映射初始化成功')
        console.log('支付方式列表:', this.paymentMethods)
      }
    } catch (error) {
      console.error('❌ 支付方式映射初始化失败:', error)
    }
  }

  /**
   * 根据支付方式名称获取ID
   * @param {string} name - 支付方式名称（如"微信"）
   * @returns {number|null}
   */
  getPaymentMethodId(name) {
    return this.paymentMap.get(name) || null
  }

  /**
   * 根据支付方式ID获取名称
   * @param {number} id - 支付方式ID
   * @returns {string|null}
   */
  getPaymentMethodName(id) {
    return this.paymentIdMap.get(id) || null
  }

  /**
   * 获取所有支付方式列表（用于下拉框）
   * @returns {Array}
   */
  getPaymentMethodList() {
    return this.paymentMethods
  }

  /**
   * 获取默认支付方式ID（返回第一个）
   * @returns {number|null}
   */
  getDefaultPaymentMethodId() {
    if (this.paymentMethods.length > 0) {
      return this.paymentMethods[0].method_id
    }
    return null
  }
}

/**
 * 全局单例（可选）
 * 如果想在整个应用中共享一个实例，可以使用这个
 */
export const paymentMethodMapper = new PaymentMethodMapper()
