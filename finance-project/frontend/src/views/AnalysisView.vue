<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <div class="top-nav" style="position: fixed; left: 30px">
      <div class="logo">MyFinancePal</div>
      <div class="breadcrumb">仪表盘 / 消费年度总结</div>
      <div class="tags-container"></div>
      <div class="user-info" style="display: flex; align-items: center; gap: 10px">
        <template v-if="userStore?.isLogin">
          <span style="font-size: 14px; color: #606266">{{ userStore.username }}</span>
        </template>
        <el-avatar
          :size="32"
          :src="userStore?.avatar || ''"
          style="cursor: pointer"
          @click="handleAvatarClick"
        >
          <el-icon><User /></el-icon>
        </el-avatar>
      </div>
    </div>

    <!-- 主体区域 -->
    <div class="main-content">
      <!-- 左侧菜单 -->
      <div class="sidebar">
        <el-menu default-active="dashboard" class="sidebar-menu" @select="handleMenuSelect">
          <el-menu-item
            index="dashboard"
            @click="handleJumpToFirst()"
            style="color: black !important"
          >
            <template #title>
              <el-icon><House /></el-icon>
              <span>首页</span>
            </template>
          </el-menu-item>

          <el-menu-item index="Coin" @click="handleJumpToCoin()">
            <template #title>
              <el-icon><Coin /></el-icon>
              <span>收入管理</span>
            </template>
          </el-menu-item>

          <!-- 支出管理折叠菜单 -->
          <el-menu-item index="Goods" @click="handleJumpToExpend()">
            <template #title>
              <el-icon><Goods /></el-icon>
              <span>支出管理</span>
            </template>
          </el-menu-item>

          <el-menu-item index="Tickets" @click="handleJumpToBudgetView()">
            <template #title>
              <el-icon><Tickets /></el-icon>
              <span>购物预算管理</span>
            </template>
          </el-menu-item>

          <el-menu-item
            index="data"
            @click="handleJumpToAnalysis()"
            style="color: rgb(64, 158, 255) !important"
          >
            <template #title>
              <el-icon><DataAnalysis /></el-icon>
              <span>消费趋势</span>
            </template>
          </el-menu-item>

          <el-menu-item index="tools" @click="handleJumpToSettings()">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>设置</span>
            </template>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 右侧内容区 -->
      <div class="content-panel">
        <!-- 标签页导航 -->
        <PageTagsNav :paddingTop="10" />

        <div class="menu-management-panel">
          <!-- 可视化图表区域 -->
          <section class="charts-container">
            <div class="card chart-card">
              <div class="card-header">
                <h3>消费趋势分析（天）</h3>
                <select class="time-selector" v-model="trendDayRange">
                  <option value="7">近7天</option>
                  <option value="30">近30天</option>
                  <option value="90">近90天</option>
                </select>
              </div>
              <div class="card-body">
                <div id="day-trend-chart" class="chart"></div>
              </div>
            </div>

            <div class="card chart-card">
              <div class="card-header">
                <h3>消费趋势分析（月）</h3>
                <select class="time-selector" v-model="trendMonthRange">
                  <option value="3">近3个月</option>
                  <option value="6">近6个月</option>
                  <option value="9">近9个月</option>
                  <option value="12">近12个月</option>
                </select>
              </div>
              <div class="card-body">
                <div id="month-trend-chart" class="chart"></div>
              </div>
            </div>

            <div class="card chart-card">
              <div class="card-header">
                <h3>消费类别占比</h3>
                <select class="time-selector" v-model="propotionTimeRange">
                  <option value="0">近1个月</option>
                  <option value="2">近3个月</option>
                  <option value="5">近6个月</option>
                  <option value="8">近9个月</option>
                  <option value="11">近12个月</option>
                  <option value="-1">全部</option>
                </select>
              </div>
              <div class="card-body">
                <div id="category-chart" class="chart"></div>
              </div>
            </div>

            <div class="card chart-card">
              <div class="card-header">
                <h3>预算使用情况分析</h3>
                <select class="time-selector" v-model="budgetMonth" @change="fetchBudgetUsage">
                  <option value="" disabled>选择月份</option>
                  <option v-for="month in monthOptions" :key="month" :value="month">
                    {{ month }}
                  </option>
                </select>
              </div>
              <div class="card-body">
                <div v-if="budgetData.has_budget" style="margin-bottom: 20px">
                  <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px">
                    <div class="budget-stat-card" :class="{ 'over-budget': budgetData.total_status === 'over' }">
                      <div class="stat-label">总预算</div>
                      <div class="stat-value">¥{{ budgetData.total_budget?.toFixed(2) }}</div>
                    </div>
                    <div class="budget-stat-card">
                      <div class="stat-label">已使用</div>
                      <div class="stat-value">¥{{ budgetData.total_used?.toFixed(2) }}</div>
                    </div>
                    <div class="budget-stat-card">
                      <div class="stat-label">剩余</div>
                      <div class="stat-value" :style="{ color: budgetData.total_remaining < 0 ? '#F56C6C' : '#67C23A' }">
                        ¥{{ budgetData.total_remaining?.toFixed(2) }}
                      </div>
                    </div>
                    <div class="budget-stat-card" :class="{ 'over-budget': budgetData.total_usage_rate > 100 }">
                      <div class="stat-label">使用率</div>
                      <div class="stat-value" :style="{ color: budgetData.total_usage_rate > 100 ? '#F56C6C' : '#409EFF' }">
                        {{ budgetData.total_usage_rate?.toFixed(1) }}%
                      </div>
                    </div>
                  </div>

                  <div id="budget-usage-chart" class="chart"></div>

                  <div v-if="budgetData.budget_list && budgetData.budget_list.length > 0" style="margin-top: 20px">
                    <h4 style="margin-bottom: 15px">分类预算详情</h4>
                    <div
                      v-for="item in budgetData.budget_list"
                      :key="item.id"
                      class="budget-item"
                      :class="{ 'over-budget': item.status === 'over' }"
                    >
                      <div class="budget-item-header">
                        <span class="budget-item-name">{{ item.name }}</span>
                        <span class="budget-item-rate" :style="{ color: item.usage_rate > 100 ? '#F56C6C' : '#67C23A' }">
                          {{ item.usage_rate.toFixed(1) }}%
                        </span>
                      </div>
                      <el-progress
                        :percentage="Math.min(item.usage_rate, 100)"
                        :stroke-width="8"
                        :color="item.usage_rate > 100 ? '#F56C6C' : item.usage_rate > 80 ? '#E6A23C' : '#67C23A'"
                      />
                      <div class="budget-item-detail">
                        <span>预算: ¥{{ item.budget_amount.toFixed(2) }}</span>
                        <span>已用: ¥{{ item.used_amount.toFixed(2) }}</span>
                        <span :style="{ color: item.remaining_amount < 0 ? '#F56C6C' : '#67C23A' }">
                          剩余: ¥{{ item.remaining_amount.toFixed(2) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="no-budget">
                  <el-empty description="该月份未设置预算">
                    <el-button type="primary" @click="goToBudgetPage">前往设置预算</el-button>
                  </el-empty>
                </div>
              </div>
            </div>
          </section>

          <!-- 页脚 -->
          <footer class="dashboard-footer">
            <p>© 2026 财智管家 - 个人财务管理系统 | 数据安全加密存储</p>
          </footer>
          <div class="search-bar"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 修复导入顺序，先导入所有依赖
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user.js'
import useDashboardLogic from '@/stores/dashboardLogic.js'
import PageTagsNav from '@/components/PageTagsNav.vue'
import { getBudgetUsage } from '@/api/budget'
import * as echarts from 'echarts'

// 路由跳转逻辑
const router = useRouter()

// 用户信息（用于头像/昵称展示）
const userStore = useUserStore()

const handleAvatarClick = () => {
  if (userStore.isLogin) {
    router.push('/settings')
  } else {
    router.push('/login')
  }
}

const handleJumpToFirst = () => {
  router.push('/')
}
const handleJumpToAnalysis = () => {
  router.push('/analysis')
}
const handleJumpToBudgetView = () => {
  router.push('/budget')
}
const handleJumpToCoin = () => {
  router.push('/coin')
}
const handleJumpToExpend = () => {
  router.push('/expend')
}
const handleJumpToSettings = () => {
  router.push('/settings')
}

// 获取dashboard逻辑变量
const {
  trendDayRange,
  trendMonthRange,
  propotionTimeRange,
  initDayTrendChart,
  initMonthTrendChart,
  initCategoryChart,
} = useDashboardLogic()

// ========== 预算使用情况分析 ==========
const budgetMonth = ref('')
const monthOptions = ref([])
const budgetData = ref({
  has_budget: false,
  total_budget: 0,
  total_used: 0,
  total_remaining: 0,
  total_usage_rate: 0,
  total_status: 'normal',
  total_info: null,
  budget_list: []
})
let budgetChart = null

// 生成最近12个月的选项
const generateMonthOptions = () => {
  const options = []
  const now = new Date()
  for (let i = 0; i < 12; i++) {
    const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const monthStr = `${year}-${month}`
    options.push(monthStr)
  }
  return options
}

// 获取预算使用情况
const fetchBudgetUsage = async () => {
  if (!budgetMonth.value) return

  try {
    const res = await getBudgetUsage({
      user_id: userStore.userId,
      month: budgetMonth.value
    })

    if (res.code === 200) {
      budgetData.value = res.data
      if (res.data.has_budget) {
        initBudgetUsageChart()
      }
    }
  } catch (e) {
    console.error('获取预算使用情况失败:', e)
  }
}

// 初始化预算使用情况图表
const initBudgetUsageChart = () => {
  const chartDom = document.getElementById('budget-usage-chart')
  if (!chartDom) return

  if (budgetChart) {
    budgetChart.dispose()
  }

  budgetChart = echarts.init(chartDom)

  const categories = budgetData.value.budget_list.map(item => item.name)
  const budgetAmounts = budgetData.value.budget_list.map(item => item.budget_amount)
  const usedAmounts = budgetData.value.budget_list.map(item => item.used_amount)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['预算金额', '已使用金额']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        rotate: 45,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      name: '金额（元）'
    },
    series: [
      {
        name: '预算金额',
        type: 'bar',
        data: budgetAmounts,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '已使用金额',
        type: 'bar',
        data: usedAmounts,
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }

  budgetChart.setOption(option)
}

// 跳转到预算设置页面
const goToBudgetPage = () => {
  router.push('/budget')
}

// 监听预算月份变化
watch(budgetMonth, (newValue) => {
  console.log('预算月份变化:', newValue)
  fetchBudgetUsage()
})

// 监听日趋势时间范围变化
watch(trendDayRange, (newValue) => {
  console.log('日趋势时间范围变化:', newValue)
  initDayTrendChart()
})

// 监听月趋势时间范围变化
watch(trendMonthRange, (newValue) => {
  console.log('月趋势时间范围变化:', newValue)
  initMonthTrendChart()
})

// 监听消费类别占比时间范围变化
watch(propotionTimeRange, (newValue) => {
  console.log('消费类别占比时间范围变化:', newValue)
  initCategoryChart()
})

// 监听预算月份变化
watch(budgetMonth, (newValue) => {
  console.log('预算月份变化:', newValue)
  if (newValue) {
    fetchBudgetUsage()
  }
})


// 页面挂载初始化图表
onMounted(() => {
  // 检查用户是否登录
  if (!userStore.isLogin) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  // 生成月份选项并设置默认值
  monthOptions.value = generateMonthOptions()
  budgetMonth.value = monthOptions.value[0]

  // 增加DOM存在性判断，防止图表初始化失败
  setTimeout(() => {
    initDayTrendChart()
    initMonthTrendChart()
    initCategoryChart()
    fetchBudgetUsage()
  }, 100)
})

// 左侧菜单选择：不再维护页面内标签数组，标签页由全局 store 自动维护
const handleMenuSelect = (_key) => {
  // no-op
}
</script>

<style scoped>
@import '../styles/framework.css';
@import '../styles/finance-dashboard.css';

.budget-stat-card {
  background: #F5F7FA;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.budget-stat-card .stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.budget-stat-card .stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.budget-stat-card.over-budget {
  background: #FEF0F0;
  border: 1px solid #FDE2E2;
}

.budget-stat-card.over-budget .stat-value {
  color: #F56C6C;
}

.budget-item {
  background: #F5F7FA;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.budget-item.over-budget {
  background: #FEF0F0;
  border: 1px solid #FDE2E2;
}

.budget-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.budget-item-name {
  font-weight: 500;
  color: #303133;
}

.budget-item-rate {
  font-size: 14px;
  font-weight: bold;
}

.budget-item-detail {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
}

.no-budget {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
</style>
