import { defineStore } from 'pinia'

// 模拟初始数据
const initialData = {
  // 分类列表
  categoryList: [
    { id: 1, name: '餐饮', type: 'expense', status: 1 },
    { id: 2, name: '交通', type: 'expense', status: 1 },
    { id: 3, name: '购物', type: 'expense', status: 1 },
    { id: 4, name: '住房', type: 'expense', status: 1 },
    { id: 5, name: '娱乐', type: 'expense', status: 1 },
    { id: 6, name: '工资', type: 'income', status: 1 },
    { id: 7, name: '兼职', type: 'income', status: 1 },
    { id: 8, name: '理财收益', type: 'income', status: 1 },
  ],
  // 收支记录列表
  recordList: [
    {
      id: 1,
      type: 'expense',
      amount: 150,
      date: '2024-01-05',
      categoryId: 1,
      categoryName: '餐饮',
      remark: '午餐外卖',
      voucherUrl: '',
    },
    {
      id: 2,
      type: 'income',
      amount: 8000,
      date: '2024-01-10',
      categoryId: 6,
      categoryName: '工资',
      remark: '12月工资',
      voucherUrl: '',
    },
  ],
  // 财务数据（用于可视化分析）
  financialData: {
    2024: {
      monthData: [
        { month: '1月', income: 8000, expense: 3500 },
        { month: '2月', income: 8000, expense: 4200 },
        { month: '3月', income: 8200, expense: 3800 },
        { month: '4月', income: 8200, expense: 3600 },
        { month: '5月', income: 8500, expense: 4000 },
        { month: '6月', income: 8500, expense: 4300 },
        { month: '7月', income: 8800, expense: 4500 },
        { month: '8月', income: 8800, expense: 4200 },
        { month: '9月', income: 9000, expense: 3900 },
        { month: '10月', income: 9000, expense: 4100 },
        { month: '11月', income: 9200, expense: 4400 },
        { month: '12月', income: 9200, expense: 4800 },
      ],
      yearData: [
        { year: '2020', income: 58000, expense: 40000 },
        { year: '2021', income: 65000, expense: 45000 },
        { year: '2022', income: 70000, expense: 48000 },
        { year: '2023', income: 78000, expense: 52000 },
        { year: '2024', income: 102600, expense: 49300 },
      ],
      categoryData: [
        { name: '餐饮', value: 18000 },
        { name: '交通', value: 6000 },
        { name: '购物', value: 12000 },
        { name: '娱乐', value: 8000 },
        { name: '住房', value: 5000 },
        { name: '其他', value: 300 },
      ],
    },
    2025: {
      monthData: [
        { month: '1月', income: 9500, expense: 4200 },
        { month: '2月', income: 9500, expense: 4800 },
        { month: '3月', income: 9800, expense: 4500 },
      ],
      yearData: [
        { year: '2021', income: 65000, expense: 45000 },
        { year: '2022', income: 70000, expense: 48000 },
        { year: '2023', income: 78000, expense: 52000 },
        { year: '2024', income: 102600, expense: 49300 },
        { year: '2025', income: 28800, expense: 13500 },
      ],
      categoryData: [
        { name: '餐饮', value: 5000 },
        { name: '交通', value: 1500 },
        { name: '购物', value: 4000 },
        { name: '娱乐', value: 2000 },
        { name: '住房', value: 1000 },
        { name: '其他', value: 0 },
      ],
    },
  },
}

export const useFinancialStore = defineStore('financial', {
  state: () => ({
    categoryList: initialData.categoryList,
    recordList: initialData.recordList,
    financialData: initialData.financialData,
  }),
  actions: {
    // 新增收支记录
    addRecord(record) {
      // 查找分类名称
      const category = this.categoryList.find((item) => item.id === record.categoryId)
      // 生成唯一ID
      const newId =
        this.recordList.length > 0 ? Math.max(...this.recordList.map((item) => item.id)) + 1 : 1
      // 添加记录
      this.recordList.unshift({
        id: newId,
        categoryName: category?.name || '',
        ...record,
      })
      // 同步更新财务数据（此处简化处理，实际项目需根据日期和分类更新对应统计数据）
      this.syncFinancialData()
    },
    // 删除收支记录
    deleteRecord(id) {
      this.recordList = this.recordList.filter((item) => item.id !== id)
      // 同步更新财务数据
      this.syncFinancialData()
    },
    // 同步财务数据（统计收支趋势和分类占比）
    syncFinancialData() {
      // 此处为简化逻辑，实际项目需根据所有记录重新统计
      // 完整逻辑应按年份、月份、分类统计收支数据
      console.log('财务数据同步中...')
    },
    // 新增分类
    addCategory(category) {
      const newId =
        this.categoryList.length > 0 ? Math.max(...this.categoryList.map((item) => item.id)) + 1 : 1
      this.categoryList.push({
        id: newId,
        status: 1,
        ...category,
      })
    },
    // 编辑分类
    editCategory(id, newData) {
      const index = this.categoryList.findIndex((item) => item.id === id)
      if (index !== -1) {
        this.categoryList[index] = { ...this.categoryList[index], ...newData }
      }
    },
    // 禁用/启用分类
    toggleCategoryStatus(id) {
      const index = this.categoryList.findIndex((item) => item.id === id)
      if (index !== -1) {
        this.categoryList[index].status = this.categoryList[index].status === 1 ? 0 : 1
      }
    },
  },
})
