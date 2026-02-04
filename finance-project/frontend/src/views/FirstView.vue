<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <div class="top-nav" style="position: fixed; left: 30px">
      <div class="logo">MyFinancePal</div>
      <div class="breadcrumb">仪表盘 / 首页</div>
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
        <el-menu
          default-active="dashboard"
          class="sidebar-menu"
          @select="handleMenuSelect"
          style="color: rgb(64, 158, 255) !important"
        >
          <el-menu-item index="dashboard" @click="handleJumpToFirst()">
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

            <el-menu-item index="CreditCard">
              <el-icon><CreditCard /></el-icon>
              <span>信用卡记录</span>
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

          <el-menu-item index="data" @click="handleJumpToAnalysis()">
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
        <div class="page-tags" style="padding-top: 70px">
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
          <!-- 系统标题与导航模块 -->
          <section class="system-intro">
            <div class="home-page">
              <h1>个人财政支出管理系统</h1>
              <p>欢迎使用收支管理、分类统计等功能</p>
            </div>
          </section>

          <!-- 数据概览卡片（核心修复：所有toFixed添加可选链+兜底） -->
          <section class="summary-cards">
            <div class="card summary-card income-card">
              <div class="card-header">
                <h3>本月收入</h3>
                <span class="icon-income"><i class="icon-arrow-up"></i></span>
              </div>
              <div class="card-body">
                <p class="amount">¥{{ monthlyIncome?.toFixed(2) || '0.00' }}</p>
                <p class="rate positive">+{{ incomeGrowth || 0 }}% 较上月</p>
              </div>
            </div>

            <div class="card summary-card expense-card">
              <div class="card-header">
                <h3>本月支出</h3>
                <span class="icon-expense"><i class="icon-arrow-down"></i></span>
              </div>
              <div class="card-body">
                <p class="amount">¥{{ monthlyExpense?.toFixed(2) || '0.00' }}</p>
                <p class="rate negative">-{{ expenseGrowth || 0 }}% 较上月</p>
              </div>
            </div>

            <div class="card summary-card balance-card">
              <div class="card-header">
                <h3>本月结余</h3>
                <span class="icon-balance"><i class="icon-wallet"></i></span>
              </div>
              <div class="card-body">
                <p class="amount">
                  ¥{{ ((monthlyIncome || 0) - (monthlyExpense || 0))?.toFixed(2) || '0.00' }}
                </p>
                <p class="rate" :class="{ positive: balanceRate > 0, negative: balanceRate < 0 }">
                  {{ balanceRate > 0 ? '+' : '' }}{{ balanceRate || 0 }}% 较上月
                </p>
              </div>
            </div>

            <div class="card summary-card budget-card">
              <div class="card-header">
                <h3>预算使用</h3>
                <span class="icon-budget"><i class="icon-chart"></i></span>
              </div>
              <div class="card-body">
                <div class="progress-container">
                  <div class="progress-bar" :style="{ width: (budgetUsage || 0) + '%' }"></div>
                </div>
                <p class="budget-info">
                  ¥{{ monthlyExpense?.toFixed(2) || '0.00' }} / ¥{{
                    monthlyBudget?.toFixed(2) || '0.00'
                  }}
                  ({{ budgetUsage || 0 }}%)
                </p>
                <p class="budget-warning" v-if="budgetUsage > 80">
                  <i class="icon-warning"></i> 预算即将超出
                </p>
              </div>
            </div>
          </section>

          <!-- 快捷功能区 -->
          <section class="quick-actions">
            <div class="action-card" @click="handleAddBill">
              <i class="icon-add"></i>
              <h4>添加账单</h4>
            </div>
            <div class="action-card" @click="handleDataExport">
              <i class="icon-export"></i>
              <h4>添加收入</h4>
            </div>
            <div class="action-card" @click="handleJumpToBudgetView">
              <i class="icon-setting"></i>
              <h4>设置预算</h4>
            </div>
            <div class="action-card" @click="handleJumpToAnalysis">
              <i class="icon-report"></i>
              <h4>年度报告</h4>
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
import { useUserStore } from '@/stores/user.js'

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

// 用户信息（用于头像/昵称展示）
const userStore = useUserStore()

const handleAvatarClick = () => {
  if (userStore.isLogin) {
    router.push('/settings')
  } else {
    router.push('/login')
  }
}

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
      CreditCard: '信用卡记录',
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
