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
              <span>消费年度总结</span>
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
import { useUserStore } from '@/stores/user.js'
import useDashboardLogic from '@/stores/dashboardLogic.js'
import PageTagsNav from '@/components/PageTagsNav.vue'

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
  handleAddBill,
  handleSetBudget,
  handleViewReport,
  handleDataExport,
  toggleExpenseType,
  initDayTrendChart,
  initMonthTrendChart,
  initCategoryChart,
} = useDashboardLogic()

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


// 页面挂载初始化图表
onMounted(() => {
  // 增加DOM存在性判断，防止图表初始化失败
  setTimeout(() => {
    initDayTrendChart()
    initMonthTrendChart()
    initCategoryChart()
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
</style>
