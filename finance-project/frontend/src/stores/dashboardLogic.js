// src/utils/dashboardLogic.js
import { ref } from 'vue'
import * as echarts from 'echarts'

// 导出所有需要在组件中使用的变量和方法
export default function useDashboardLogic() {
  // 模拟数据
  const notificationCount = ref(2)
  const monthlyIncome = ref(15800.5)
  const monthlyExpense = ref(8950.8)
  const monthlyBudget = ref(10000.0)
  const incomeGrowth = ref(8.5)
  const expenseGrowth = ref(3.2)
  const balanceRate = ref(15.3)
  const budgetUsage = ref(89.5)
  const trendTimeRange = ref('month')
  const showAllExpense = ref(false)

  // 近期账单数据
  const recentBills = ref([
    { date: '2026-01-07', category: '餐饮', amount: 89.9, type: 'expense', remark: '午餐' },
    { date: '2026-01-06', category: '工资', amount: 15000, type: 'income', remark: '12月工资' },
    { date: '2026-01-05', category: '交通', amount: 45.5, type: 'expense', remark: '打车' },
    { date: '2026-01-04', category: '购物', amount: 1299, type: 'expense', remark: '衣服' },
    { date: '2026-01-03', category: '理财', amount: 800.5, type: 'income', remark: '基金收益' },
  ])

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
  const initTrendChart = () => {
    const chartDom = document.getElementById('trend-chart')
    if (!chartDom) return // 防止DOM不存在报错
    const myChart = echarts.init(chartDom)

    // 模拟趋势数据
    const xData = ['1日', '5日', '10日', '15日', '20日', '25日', '30日']
    const incomeData = [1200, 2500, 1800, 3000, 2200, 1500, 3600]
    const expenseData = [800, 1500, 1200, 2000, 1800, 1000, 1650]

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
  }

  // 初始化类别占比图表
  const initCategoryChart = () => {
    const chartDom = document.getElementById('category-chart')
    if (!chartDom) return // 防止DOM不存在报错
    const myChart = echarts.init(chartDom)

    // 模拟类别数据
    const fullData = [
      { value: 35, name: '餐饮' },
      { value: 20, name: '购物' },
      { value: 15, name: '交通' },
      { value: 10, name: '娱乐' },
      { value: 8, name: '住房' },
      { value: 7, name: '通讯' },
      { value: 5, name: '其他' },
    ]

    const mainData = [
      { value: 35, name: '餐饮' },
      { value: 20, name: '购物' },
      { value: 15, name: '交通' },
      { value: 30, name: '其他' },
    ]

    const data = showAllExpense.value ? fullData : mainData

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c}% ({d}%)',
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
    handleAddBill,
    handleSetBudget,
    handleViewReport,
    handleDataExport,
    toggleExpenseType,
    initTrendChart,
    initCategoryChart,
  }
}
