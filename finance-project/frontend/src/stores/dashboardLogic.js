// src/utils/dashboardLogic.js
import { ref } from 'vue'
import * as echarts from 'echarts'
import { getBillListFirst } from '@/api/bill.js'
import { getTrendDays, getTrendMonths, getExpenseProportionMonth } from '@/api/analysis.js'
import { getBudgetListByMonth } from '@/api/budget.js'
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
  const trendDayRange = ref('30')
  const trendMonthRange = ref("6")
  const propotionTimeRange = ref("0")
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
      const [incomeBills, expenseBills, lastMonthIncome, lastMonthExpense, budgetData] = await Promise.all([
        getBillListFirst({
          user_id: userStore.userId,
          the_time: currentMonth,
          page: 1,
          page_size: 100,
          type: 1 // 1=收入
        }),
        getBillListFirst({
          user_id: userStore.userId,
          the_time: currentMonth,
          page: 1,
          page_size: 100,
          type: 2 // 2=支出
        }),
        getBillListFirst({
          user_id: userStore.userId,
          the_time: lastMonth,
          page: 1,
          page_size: 100,
          type: 1
        }),
        getBillListFirst({
          user_id: userStore.userId,
          the_time: lastMonth,
          page: 1,
          page_size: 100,
          type: 2
        }),
        // 获取当月预算数据
        getBudgetListByMonth({
          user_id: userStore.userId,
          month: currentMonth
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

      // 计算预算使用率
      // 从API获取的预算数据中提取月度总预算（is_total === true）
      let totalMonthlyBudget = 0
      if (budgetData?.data && Array.isArray(budgetData.data)) {
        const totalBudget = budgetData.data.find((item) => item.is_total === true)
        totalMonthlyBudget = totalBudget ? parseFloat(totalBudget.amount || 0) : 0
      }

      // 如果没有设置预算，使用默认值10000
      monthlyBudget.value = totalMonthlyBudget > 0 ? totalMonthlyBudget : 10000
      budgetUsage.value = monthlyBudget.value > 0
        ? parseFloat(((currentExpense / monthlyBudget.value) * 100).toFixed(1))
        : 0

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
  const initDayTrendChart = async () => {
    const chartDom = document.getElementById('day-trend-chart')
    if (!chartDom) return // 防止DOM不存在报错

    if (!userStore.isLogin) {
      console.warn('用户未登录，无法加载趋势图表')
      return
    }

    try {
      const dayMap = {
        '7': 7,
        '30': 30,
        '90': 90
      }

      const days = dayMap[trendDayRange.value] || 30
      // 获取近7天的趋势数据
      const response = await getTrendDays({
        user_id: userStore.userId,
        days: days
      })

      console.log('趋势数据响应:', response)  // 查看完整响应结构

      const myChart = echarts.init(chartDom)

      // ✅ 修复：正确处理后端返回的数据结构
      // 后端返回的是对象数组 [{date: "...", amount: ...}, ...]
      // 我们需要提取 amount 字段组成数字数组
      const incomeList = response?.data?.income_list || []
      const expenseList = response?.data?.expense_list || []

      // 提取金额数据
      const incomeData = incomeList.map(item => parseFloat(item.amount || 0))
      const expenseData = expenseList.map(item => parseFloat(item.amount || 0))

      // 生成日期标签（可以使用后端返回的日期，也可以自己生成）
      const xData = []
      const now = new Date()

      // 根据天数生成日期标签
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date()
        date.setDate(now.getDate() - i)
        xData.push(`${date.getMonth() + 1}月${date.getDate()}日`)
      }

      // 或者使用后端返回的日期
      // const xData = incomeList.map(item => {
      //   const date = new Date(item.date)
      //   return `${date.getMonth() + 1}月${date.getDate()}日`
      // })

      console.log('处理后的数据:')
      console.log('日期标签:', xData)
      console.log('收入数据:', incomeData)
      console.log('支出数据:', expenseData)

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: function(params) {
            let result = params[0].axisValue + '<br/>'
            params.forEach(param => {
              result += `${param.seriesName}: ¥${param.value}<br/>`
            })
            return result
          }
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
          axisLabel: {
            rotate: 45  // 如果日期太多可以旋转
          }
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
            smooth: true,  // 平滑曲线
          },
          {
            name: '支出',
            type: 'line',
            stack: 'total',
            data: expenseData,
            lineStyle: { color: '#F44336' },
            itemStyle: { color: '#F44336' },
            areaStyle: { color: 'rgba(244, 67, 54, 0.1)' },
            smooth: true,  // 平滑曲线
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
      // 可以在这里显示错误提示
    }
  }

  const initMonthTrendChart = async () => {
    const chartDom = document.getElementById('month-trend-chart')
    if (!chartDom) {
      console.error('找不到图表DOM元素: month-trend-chart')
      return
    }

    if (!userStore.isLogin) {
      console.warn('用户未登录，无法加载月度趋势图表')
      return
    }

    try {
      // 月份映射关系
      const monthMap = {
        '3': 3,   // 近3个月
        '6': 6,   // 近6个月
        '9': 9,   // 近9个月
        '12': 12  // 近12个月
      }

      const months = monthMap[trendMonthRange.value] || 6

      console.log('请求月度趋势数据，月数:', months, '趋势范围:', trendMonthRange.value)

      // 使用 getTrendMonths API
      const response = await getTrendMonths({
        user_id: userStore.userId,
        months: months
      })

      console.log('月度趋势数据响应:', response)

      // 清除旧图表
      const oldChart = echarts.getInstanceByDom(chartDom)
      if (oldChart) {
        oldChart.dispose()
      }

      const myChart = echarts.init(chartDom)

      // 处理后端返回的数据结构
      const incomeList = response?.data?.income_list || []
      const expenseList = response?.data?.expense_list || []

      console.log('原始数据:', {
        incomeList,
        expenseList
      })

      // 提取金额数据
      const incomeData = incomeList.map(item => parseFloat(item.amount || 0))
      const expenseData = expenseList.map(item => parseFloat(item.amount || 0))

      // 生成月份标签
      const xData = incomeList.map(item => {
        // 从 "2024-01" 格式转换为 "2024年1月"
        const [year, month] = item.time.split('-')
        return `${year}年${parseInt(month)}月`
      })

      console.log('处理后的数据:')
      console.log('月份标签:', xData)
      console.log('收入数据:', incomeData)
      console.log('支出数据:', expenseData)

      // ✅ 修改为和第一个图表一样的配置
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow',
            label: {
              backgroundColor: '#6a7985'
            }
          },
          formatter: function(params) {
            let result = params[0].axisValue + '<br/>'
            params.forEach(param => {
              // 格式化金额，保留两位小数
              const formattedAmount = param.value.toFixed(2)
              result += `${param.seriesName}: ¥${formattedAmount}<br/>`
            })
            return result
          }
        },
        legend: {
          data: ['收入', '支出'],
          top: 0,
          textStyle: {
            fontSize: 12
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '12%',  // 调整为和第一个图表一致
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,  // 折线图从坐标轴开始
          data: xData,
          axisLabel: {
            rotate: xData.length > 6 ? 45 : 0,  // 月份多时旋转
            fontSize: 11
          },
          axisTick: {
            alignWithLabel: true
          }
        },
        yAxis: {
          type: 'value',
          name: '金额 (元)',
          axisLabel: {
            formatter: '¥{value}'
          },
          splitLine: {
            lineStyle: {
              type: 'dashed',
              color: '#e0e0e0'
            }
          }
        },
        series: [
          {
            name: '收入',
            type: 'line',  // ✅ 改为折线图
            smooth: true,   // ✅ 平滑曲线
            symbol: 'circle',  // 数据点显示为圆点
            symbolSize: 6,
            lineStyle: {
              color: '#4CAF50',
              width: 2
            },
            itemStyle: {
              color: '#4CAF50',
              borderColor: '#fff',
              borderWidth: 1
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(76, 175, 80, 0.3)' },
                  { offset: 1, color: 'rgba(76, 175, 80, 0.05)' }
                ]
              }
            },
            data: incomeData,
            emphasis: {
              focus: 'series',
              itemStyle: {
                borderColor: '#4CAF50',
                borderWidth: 2,
                shadowBlur: 10,
                shadowColor: 'rgba(76, 175, 80, 0.5)'
              }
            }
          },
          {
            name: '支出',
            type: 'line',  // ✅ 改为折线图
            smooth: true,   // ✅ 平滑曲线
            symbol: 'circle',
            symbolSize: 6,
            lineStyle: {
              color: '#F44336',
              width: 2
            },
            itemStyle: {
              color: '#F44336',
              borderColor: '#fff',
              borderWidth: 1
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(244, 67, 54, 0.3)' },
                  { offset: 1, color: 'rgba(244, 67, 54, 0.05)' }
                ]
              }
            },
            data: expenseData,
            emphasis: {
              focus: 'series',
              itemStyle: {
                borderColor: '#F44336',
                borderWidth: 2,
                shadowBlur: 10,
                shadowColor: 'rgba(244, 67, 54, 0.5)'
              }
            }
          }
        ]
      }

      myChart.setOption(option)

      // 响应式适配
      window.addEventListener('resize', () => {
        myChart.resize()
      })

      // 图表点击事件（可选保留）
      myChart.on('click', function(params) {
        if (params.componentType === 'series') {
          console.log('点击了图表:', params)
        }
      })

    } catch (error) {
      console.error('获取月度趋势数据失败:', error)
    }
  }

  // 初始化类别占比图表
  const initCategoryChart = async () => {
    const chartDom = document.getElementById('category-chart')
    if (!chartDom) {
      console.error('找不到图表DOM元素: category-chart')
      return
    }

    if (!userStore.isLogin) {
      console.warn('用户未登录，无法加载类别占比图表')
      return
    }

    try {
      // 根据选择的时间范围获取对应的 month 参数
      const monthMap = {
        '0': 0,     // 近1个月（当月）
        '2': 2,     // 近3个月
        '5': 5,     // 近6个月
        '8': 8,     // 近9个月
        '11': 11,   // 近12个月
        '-1': -1    // 全部历史
      }

      // 获取用户选择的月份参数
      const monthParam = monthMap[propotionTimeRange.value] || 0

      console.log('请求类别占比数据:', {
        选择的值: propotionTimeRange.value,
        映射的month参数: monthParam,
        用户ID: userStore.userId
      })

      // 调用API获取数据
      const response = await getExpenseProportionMonth({
        user_id: userStore.userId,
        month: monthParam  // 使用动态参数
      })

      console.log('类别占比数据响应:', response)

      // 清除旧图表
      const oldChart = echarts.getInstanceByDom(chartDom)
      if (oldChart) {
        oldChart.dispose()
      }

      const myChart = echarts.init(chartDom)

      // 处理后端返回的数据结构
      const timeDescription = response?.time || ''
      const categoryData = response?.data || []

      console.log('原始数据:', {
        时间段: timeDescription,
        分类数据: categoryData,
        数据长度: categoryData.length
      })

      // 准备图表数据 - 直接显示所有分类
      let chartData = []
      if (categoryData && Array.isArray(categoryData)) {
        // 直接使用所有分类数据，不过滤
        chartData = categoryData.map((item) => ({
          value: parseFloat(item.amount || 0),
          name: item.category_name || '未分类',
          percentage: item.percentage || 0,
          count: item.count || 0,
          categoryId: item.category_id
        }))

        // 按金额降序排序，让金额大的排在前面
        chartData.sort((a, b) => b.value - a.value)

        console.log('所有分类数据:', chartData)
      }

      // 如果数据为空，显示提示信息
      if (chartData.length === 0 || chartData.every(item => item.value === 0)) {
        console.log('没有消费数据，显示提示')
        chartData = [
          {
            value: 1,  // 使用1作为占位值，确保饼图能显示
            name: '暂无消费数据',
            percentage: 100,
            count: 0,
            categoryId: 0
          }
        ]
      }

      // ✅ 直接使用所有数据，不需要根据showAllExpense判断
      const displayData = chartData

      // 准备ECharts数据格式
      const seriesData = displayData.map((item, index) => {
        // 如果只有"暂无消费数据"这一项，使用灰色
        if (item.name === '暂无消费数据') {
          return {
            value: item.value,
            name: item.name,
            itemStyle: {
              color: '#e0e0e0',
              opacity: 0.7
            }
          }
        }

        // 正常数据使用彩色
        return {
          value: item.value,
          name: item.name,
          itemStyle: {
            // 使用预设颜色或默认颜色
            color: null // 让ECharts自动分配颜色
          }
        }
      })

      const option = {
        title: {
          text: '消费类别占比',
          subtext: timeDescription || '暂无数据',
          left: 'center',
          top: 10,
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          },
          subtextStyle: {
            fontSize: 12,
            color: '#666'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            const data = params.data
            // 计算总金额（排除占位数据）
            const totalAmount = chartData
              .filter(item => item.name !== '暂无消费数据')
              .reduce((sum, item) => sum + item.value, 0)

            // 如果是"暂无消费数据"提示
            if (data.name === '暂无消费数据') {
              return `
                <div style="font-weight: bold; margin-bottom: 5px; color: #999;">${data.name}</div>
                <div>在当前时间段内没有消费记录</div>
              `
            }

            // 正常数据的tooltip
            const percentage = totalAmount > 0 ? ((data.value / totalAmount) * 100).toFixed(2) : '0.00'
            return `
              <div style="font-weight: bold; margin-bottom: 5px;">${data.name}</div>
              <div>金额: ¥${data.value.toFixed(2)}</div>
              <div>占比: ${percentage}%</div>
              ${params.data.count ? `<div>交易笔数: ${params.data.count}笔</div>` : ''}
            `
          },
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#ddd',
          borderWidth: 1,
          textStyle: {
            color: '#333'
          },
          extraCssText: 'box-shadow: 0 2px 8px rgba(0,0,0,0.15);'
        },
        legend: {
          type: 'scroll',  // 可滚动的图例
          orient: 'vertical',
          left: 'left',
          top: 'center',
          height: '70%',
          textStyle: {
            fontSize: 12
          },
          pageTextStyle: {
            color: '#666'
          },
          // 当分类很多时，限制图例显示数量
          pageIconSize: 12,
          pageButtonItemGap: 2,
          pageButtonPosition: 'end'
        },
        series: [
          {
            name: '消费类别',
            type: 'pie',
            radius: ['40%', '65%'],
            center: ['60%', '50%'],
            avoidLabelOverlap: true,
            itemStyle: {
              borderRadius: 8,
              borderColor: '#fff',
              borderWidth: 2,
              shadowColor: 'rgba(0, 0, 0, 0.1)',
              shadowBlur: 4,
              shadowOffsetX: 2,
              shadowOffsetY: 2
            },
            label: {
              show: false,
              position: 'center',
              formatter: '{b}\n{c}元 ({d}%)',
              fontSize: 14,
              fontWeight: 'bold'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 16,
                fontWeight: 'bold'
              },
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            labelLine: {
              show: true,
              length: 10,
              length2: 20,
              smooth: true
            },
            data: seriesData,
            // 添加最小角度设置，确保小数值也能显示
            minAngle: 3
          }
        ],
        color: [
          '#FF6B6B', '#4ECDC4', '#FFD166', '#06D6A0',
          '#118AB2', '#073B4C', '#EF476F', '#FFD166',
          '#06D6A0', '#118AB2', '#7209B7', '#F72585',
          '#3A86FF', '#FB5607', '#8338EC', '#3A86FF',
          '#FF006E', '#FB5607', '#8338EC', '#FFBE0B'
        ],
        // 添加一个环形中间的文字
        graphic: (chartData.length > 0 && chartData[0].name !== '暂无消费数据') ? [
          {
            type: 'text',
            left: '70%',
            top: '50%',
            style: {
              text: '总消费\n¥' + chartData.reduce((sum, item) => sum + item.value, 0).toFixed(2),
              textAlign: 'center',
              fill: '#333',
              fontSize: 14,
              fontWeight: 'bold'
            }
          }
        ] : []
      }

      myChart.setOption(option)

      // 响应式适配
      window.addEventListener('resize', () => {
        myChart.resize()
      })

      // 图表点击事件
      myChart.on('click', function(params) {
        console.log('点击了类别:', params)
        if (params.data.name !== '暂无消费数据') {
          // 可以在这里添加点击事件处理，比如查看该类别的详细账单
          console.log('点击了分类:', params.data.name, '分类ID:', params.data.categoryId)
        }
      })

    } catch (error) {
      console.error('获取类别占比数据失败:', error)

      // 降级方案：显示错误信息
      const chartDom = document.getElementById('category-chart')
      if (chartDom) {
        const oldChart = echarts.getInstanceByDom(chartDom)
        if (oldChart) {
          oldChart.dispose()
        }

        const myChart = echarts.init(chartDom)
        myChart.setOption({
          title: {
            text: '数据加载失败',
            subtext: '请检查网络连接或稍后重试',
            left: 'center',
            top: 'center',
            textStyle: {
              color: '#999',
              fontSize: 16
            }
          }
        })
      }
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
    trendDayRange,
    trendMonthRange,
    propotionTimeRange,
    showAllExpense,
    recentBills,
    isLoading,
    fetchDashboardData,
    handleAddBill,
    handleSetBudget,
    handleViewReport,
    handleDataExport,
    toggleExpenseType,
    initDayTrendChart,
    initMonthTrendChart,
    initCategoryChart,
  }
}
