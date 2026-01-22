// src/utils/dashboardLogic.js
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getBillList } from '@/api/bill.js'
import { getTrendDays, getExpenseProportionMonth } from '@/api/analysis.js'
import { useUserStore } from '@/stores/user.js'
import { ElMessage } from 'element-plus'

// 导出所有需要在组件中使用的变量和方法
export default function useDashboardLogic() {
  const userStore = useUserStore()

  // 响应式数据
  const notificationCount = ref(2)
  const monthlyIncome = ref(0)
  const monthlyExpense = ref(0)
  const monthlyBudget = ref(0)
  const incomeGrowth = ref(0)
  const expenseGrowth = ref(0)
  const balanceRate = ref(0)
  const budgetUsage = ref(0)
  const trendTimeRange = ref('month')
  const showAllExpense = ref(false)
  const isLoading = ref(false)
  const recentBills = ref([])

  /**
   * 获取当月的年月字符串（格式：YYYY-MM）
   */
  const getCurrentMonth = () => {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    return `${year}-${month}`
  }

  /**
   * 获取上个月的年月字符串（格式：YYYY-MM）
   */
  const getLastMonth = () => {
    const now = new Date()
    now.setMonth(now.getMonth() - 1)
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    return `${year}-${month}`
  }

  /**
   * 从API获取账单数据并计算统计信息
   */
  const fetchDashboardData = async () => {
    if (!userStore.isLogin) {
      console.warn('用户未登录，无法加载仪表盘数据')
      return
    }

    isLoading.value = true
    try {
      const currentMonth = getCurrentMonth()
      const lastMonth = getLastMonth()

      // 获取当月账单（收入和支出）
      const [incomeBills, expenseBills, lastMonthIncome, lastMonthExpense] = await Promise.all([
        getBillList({
          user_id: userStore.userId,
          the_time: currentMonth,
          page: 1,
          page_size: 100,
          type: 1 // 1=收入
        }),
        getBillList({
          user_id: userStore.userId,
          the_time: currentMonth,
          page: 1,
          page_size: 100,
          type: 2 // 2=支出
        }),
        getBillList({
          user_id: userStore.userId,
          the_time: lastMonth,
          page: 1,
          page_size: 100,
          type: 1
        }),
        getBillList({
          user_id: userStore.userId,
          the_time: lastMonth,
          page: 1,
          page_size: 100,
          type: 2
        })
      ])

      // 计算当月收入和支出总额
      const currentIncome =
        incomeBills?.data?.reduce((sum, bill) => sum + (parseFloat(bill.amount) || 0), 0) || 0
      const currentExpense =
        expenseBills?.data?.reduce((sum, bill) => sum + (parseFloat(bill.amount) || 0), 0) || 0

      // 计算上月总额
      const previousIncome =
        lastMonthIncome?.data?.reduce((sum, bill) => sum + (parseFloat(bill.amount) || 0), 0) || 0
      const previousExpense =
        lastMonthExpense?.data?.reduce((sum, bill) => sum + (parseFloat(bill.amount) || 0), 0) || 0

      // 更新数据
      monthlyIncome.value = currentIncome
      monthlyExpense.value = currentExpense

      // 计算增长率
      if (previousIncome > 0) {
        incomeGrowth.value = parseFloat(
          (((currentIncome - previousIncome) / previousIncome) * 100).toFixed(1)
        )
      } else {
        incomeGrowth.value = currentIncome > 0 ? 100 : 0
      }

      if (previousExpense > 0) {
        expenseGrowth.value = parseFloat(
          (((currentExpense - previousExpense) / previousExpense) * 100).toFixed(1)
        )
      } else {
        expenseGrowth.value = currentExpense > 0 ? 100 : 0
      }

      // 计算结余增长率
      const currentBalance = currentIncome - currentExpense
      const previousBalance = previousIncome - previousExpense
      if (previousBalance !== 0) {
        balanceRate.value = parseFloat(
          (((currentBalance - previousBalance) / Math.abs(previousBalance)) * 100).toFixed(1)
        )
      } else {
        balanceRate.value = currentBalance > 0 ? 100 : 0
      }

      // 计算预算使用率（假设月预算为10000，实际应从API获取）
      monthlyBudget.value = 10000
      budgetUsage.value = parseFloat(((currentExpense / monthlyBudget.value) * 100).toFixed(1))

      // 合并所有账单用于近期账单显示
      const allBills = [
        ...(incomeBills?.data || []).map((bill) => ({
          ...bill,
          type: 'income',
          category: '收入'
        })),
        ...(expenseBills?.data || []).map((bill) => ({
          ...bill,
          type: 'expense',
          category: bill.category_name || '支出'
        }))
      ]

      // 按日期排序，取最近的8条
      allBills.sort(
        (a, b) => new Date(b.bill_time || b.date) - new Date(a.bill_time || a.date)
      )
      recentBills.value = allBills.slice(0, 8).map((bill) => ({
        date: (bill.bill_time || bill.date).split('T')[0],
        category: bill.category,
        amount: parseFloat(bill.amount),
        type: bill.type,
        remark: bill.remark || '-'
      }))
    } catch (error) {
      console.error('获取仪表盘数据失败:', error)
      ElMessage.error('加载数据失败，请稍后重试')
    } finally {
      isLoading.value = false
    }
  }

  // 功能处理函数
  const handleAddBill = () => {
    console.log('添加账单')
  }

  const handleSetBudget = () => {
    console.log('设置预算')
  }

  const handleViewReport = () => {
    console.log('查看年度报告')
  }

  const handleDataExport = () => {
    console.log('导出数据')
  }

  const toggleExpenseType = () => {
    showAllExpense.value = !showAllExpense.value
    initCategoryChart() // 重新渲染图表
  }

  // 初始化趋势图表
  const initTrendChart = async () => {
    const chartDom = document.getElementById('trend-chart')
    if (!chartDom) return // 防止DOM不存在报错

    if (!userStore.isLogin) {
      console.warn('用户未登录，无法加载趋势图表')
      return
    }

    try {
      // 获取近7天的趋势数据
      const response = await getTrendDays({
        user_id: userStore.userId,
        days: 7
      })

      const myChart = echarts.init(chartDom)

      // 处理API返回的数据
      const incomeData = response?.data?.income_list || []
      const expenseData = response?.data?.expense_list || []

      // 生成日期标签
      const xData = []
      for (let i = 6; i >= 0; i--) {
        const date = new Date()
        date.setDate(date.getDate() - i)
        xData.push(`${date.getMonth() + 1}月${date.getDate()}日`)
      }

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
        },
        legend: {
          data: ['收入', '支出'],
          top: 0,
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true,
        },
        xAxis: {
          type: 'category',
          data: xData,
        },
        yAxis: {
          type: 'value',
          name: '金额 (元)',
        },
        series: [
          {
            name: '收入',
            type: 'line',
            stack: 'total',
            data: incomeData,
            lineStyle: { color: '#4CAF50' },
            itemStyle: { color: '#4CAF50' },
            areaStyle: { color: 'rgba(76, 175, 80, 0.1)' },
          },
          {
            name: '支出',
            type: 'line',
            stack: 'total',
            data: expenseData,
            lineStyle: { color: '#F44336' },
            itemStyle: { color: '#F44336' },
            areaStyle: { color: 'rgba(244, 67, 54, 0.1)' },
          },
        ],
      }

      myChart.setOption(option)
      // 响应式适配
      window.addEventListener('resize', () => {
        myChart.resize()
      })
    } catch (error) {
      console.error('获取趋势数据失败:', error)
    }
  }

  // 初始化类别占比图表
  const initCategoryChart = async () => {
    const chartDom = document.getElementById('category-chart')
    if (!chartDom) return // 防止DOM不存在报错

    if (!userStore.isLogin) {
      console.warn('用户未登录，无法加载类别占比图表')
      return
    }

    try {
      // 获取当月的消费类别占比
      const response = await getExpenseProportionMonth({
        user_id: userStore.userId,
        month: 0 // 0=当月
      })

      const myChart = echarts.init(chartDom)

      // 处理API返回的数据
      let chartData = []
      if (response?.data && Array.isArray(response.data)) {
        chartData = response.data.map((item) => ({
          value: parseFloat(item.amount || 0),
          name: item.category_name || '其他'
        }))
      }

      // 如果数据为空，使用默认数据
      if (chartData.length === 0) {
        chartData = [
          { value: 35, name: '餐饮' },
          { value: 20, name: '购物' },
          { value: 15, name: '交通' },
          { value: 30, name: '其他' },
        ]
      }

      // 根据showAllExpense决定显示全部还是主要类别
      const data = showAllExpense.value ? chartData : chartData.slice(0, 4)

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: ¥{c} ({d}%)',
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'center',
        },
        series: [
          {
            name: '消费类别',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2,
            },
            label: {
              show: false,
              position: 'center',
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 16,
                fontWeight: 'bold',
              },
            },
            labelLine: {
              show: false,
            },
            data: data,
          },
        ],
        color: ['#FF9800', '#2196F3', '#9C27B0', '#00BCD4', '#8BC34A', '#FF5722', '#607D8B'],
      }

      myChart.setOption(option)
      window.addEventListener('resize', () => {
        myChart.resize()
      })
    } catch (error) {
      console.error('获取类别占比数据失败:', error)
    }
  }

  // 返回需要在组件中使用的变量和方法
  return {
    notificationCount,
    monthlyIncome,
    monthlyExpense,
    monthlyBudget,
    incomeGrowth,
    expenseGrowth,
    balanceRate,
    budgetUsage,
    trendTimeRange,
    showAllExpense,
    recentBills,
    isLoading,
    fetchDashboardData,
    handleAddBill,
    handleSetBudget,
    handleViewReport,
    handleDataExport,
    toggleExpenseType,
    initTrendChart,
    initCategoryChart,
  }
}
