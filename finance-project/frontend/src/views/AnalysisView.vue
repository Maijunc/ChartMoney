<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <div class="top-nav" style="position: fixed; left: 30px">
      <div class="logo">MyFinancePal</div>
      <div class="breadcrumb">仪表盘 / 消费年度总结</div>
      <div class="tags-container"></div>
      <div class="user-info">
        <el-avatar>
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
          <el-sub-menu index="Goods">
            <template #title>
              <el-icon><Goods /></el-icon>
              <span>支出管理</span>
            </template>

            <el-menu-item index="CreditCard" @click="handleJumpToRecord()">
              <el-icon><CreditCard /></el-icon>
              <span>总消费记录</span>
            </el-menu-item>

            <el-menu-item index="DailyExpense" @click="handleJumpToExpend()">
              <el-icon><Wallet /></el-icon>
              <span>日常支出</span>
            </el-menu-item>
          </el-sub-menu>

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
        <div class="page-tags" style="padding-top: 10px">
          <el-tag
            v-for="(tag, index) in pageTagsList"
            :key="tag.key"
            :closable="tag.key !== 'dashboard'"
            @close="handleClosePageTag(index)"
            @click="handlePageTagClick(tag.key)"
            :effect="activePageKey === tag.key ? 'dark' : 'light'"
            class="page-tag-item"
          >
            {{ tag.label }}
          </el-tag>
        </div>

        <div class="menu-management-panel">
          <!-- 可视化图表区域 -->
          <section class="charts-container">
            <div class="card chart-card">
              <div class="card-header">
                <h3>消费趋势分析</h3>
                <select class="time-selector" v-model="trendTimeRange">
                  <option value="week">近7天</option>
                  <option value="month">近30天</option>
                  <option value="quarter">近3个月</option>
                </select>
              </div>
              <div class="card-body">
                <div id="trend-chart" class="chart"></div>
              </div>
            </div>

            <div class="card chart-card">
              <div class="card-header">
                <h3>消费类别占比</h3>
                <button class="btn btn-outline" @click="toggleExpenseType">
                  {{ showAllExpense ? '显示主要类别' : '显示全部类别' }}
                </button>
              </div>
              <div class="card-body">
                <div id="category-chart" class="chart"></div>
              </div>
            </div>
          </section>

          <!-- 近期账单列表（修复bill.amount的toFixed） -->
          <section class="recent-bills">
            <div class="section-header">
              <h3>近期账单</h3>
              <button class="btn btn-outline">查看全部</button>
            </div>
            <div class="bills-table">
              <table>
                <thead>
                  <tr>
                    <th>日期</th>
                    <th>类别</th>
                    <th>金额</th>
                    <th>类型</th>
                    <th>备注</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(bill, index) in recentBills" :key="index">
                    <td>{{ bill.date }}</td>
                    <td>
                      <span :class="`category-tag ${bill.category}`">{{ bill.category }}</span>
                    </td>
                    <td :class="bill.type === 'income' ? 'text-green' : 'text-red'">
                      {{ bill.type === 'income' ? '+' : '-' }}¥{{
                        bill.amount?.toFixed(2) || '0.00'
                      }}
                    </td>
                    <td>{{ bill.type === 'income' ? '收入' : '支出' }}</td>
                    <td>{{ bill.remark || '-' }}</td>
                  </tr>
                </tbody>
              </table>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import useDashboardLogic from '@/stores/dashboardLogic.js'

// 路由跳转逻辑
const router = useRouter()
const handleJumpToExpend = () => {
  router.push('/expend')
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
const handleJumpToRecord = () => {
  router.push('/record')
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
} = useDashboardLogic()

// 页面挂载初始化图表
onMounted(() => {
  // 增加DOM存在性判断，防止图表初始化失败
  setTimeout(() => {
    initTrendChart()
    initCategoryChart()
  }, 100)
})

// 顶部标签页数据（修复activePath初始值匹配）
const tagsList = ref([
  { key: 'dashboard', label: '仪表盘' },
  { key: 'user', label: '首页' },
  { key: 'coin', label: '收入管理' },
  { key: 'Goods', label: '支出管理' },
  { key: 'Tickets', label: '购物预算管理' },
  { key: 'DataAnalysis', label: '消费年度总结' },
  { key: 'Tools', label: '设置' },
])
const activePath = ref('dashboard') // 修复：匹配标签页key，而非path

// 页面内标签页数据（修复key匹配）
const pageTagsList = ref([
  { key: 'dashboard', label: '仪表盘' },
  { key: 'user', label: '首页' },
  { key: 'coin', label: '收入管理' },
  { key: 'Goods', label: '支出管理' },
  { key: 'Tickets', label: '购物预算管理' },
  { key: 'DataAnalysis', label: '消费年度总结' },
])
const activePageKey = ref('dashboard') // 修复：初始值匹配标签页key

// 顶部标签页-关闭（修复判断key而非path）
const handleCloseTag = (index) => {
  const closedTag = tagsList.value[index]
  tagsList.value.splice(index, 1)
  if (closedTag?.key === activePath.value) {
    activePath.value = tagsList.value[tagsList.value.length - 1]?.key || 'dashboard'
  }
}

// 顶部标签页-点击切换
const handleTagClick = (key) => {
  activePath.value = key
}

// 页面内标签页-关闭
const handleClosePageTag = (index) => {
  const closedTag = pageTagsList.value[index]
  pageTagsList.value.splice(index, 1)
  if (closedTag?.key === activePageKey.value) {
    activePageKey.value = pageTagsList.value[pageTagsList.value.length - 1]?.key || 'dashboard'
  }
}

// 页面内标签页-点击切换
const handlePageTagClick = (key) => {
  activePageKey.value = key
}

// 左侧菜单选择（修复labelMap匹配）
const handleMenuSelect = (key) => {
  const tagExists = pageTagsList.value.some((item) => item.key === key)
  if (!tagExists) {
    const labelMap = {
      dashboard: '仪表盘',
      user: '首页',
      coin: '收入管理',
      Goods: '支出管理',
      Tickets: '购物预算管理',
      data: '消费年度总结',
      tools: '设置',
      CreditCard: '总消费记录',
      DailyExpense: '日常支出',
    }
    pageTagsList.value.push({ key, label: labelMap[key] || key })
  }
  activePageKey.value = key
}
</script>

<style scoped>
@import '../styles/framework.css';
@import '../styles/finance-dashboard.css';
</style>
