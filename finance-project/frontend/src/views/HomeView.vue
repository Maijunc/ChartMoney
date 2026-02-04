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
          <el-icon><UserIcon /></el-icon>
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
              <el-icon><HouseIcon /></el-icon>
              <span>首页</span>
            </template>
          </el-menu-item>

          <el-menu-item index="Coin" @click="handleJumpToCoin()">
            <template #title>
              <el-icon><CoinIcon /></el-icon>
              <span>收入管理</span>
            </template>
          </el-menu-item>

          <!-- 支出管理折叠菜单 -->
          <el-menu-item index="Goods" @click="handleJumpToExpend()">
            <template #title>
              <el-icon><GoodsIcon /></el-icon>
              <span>支出管理</span>
            </template>
          </el-menu-item>

          <el-menu-item index="Tickets" @click="handleJumpToBudgetView()">
            <template #title>
              <el-icon><TicketsIcon /></el-icon>
              <span>购物预算管理</span>
            </template>
          </el-menu-item>

          <el-menu-item index="data" @click="handleJumpToAnalysis()">
            <template #title>
              <el-icon><DataAnalysisIcon /></el-icon>
              <span>消费年度总结</span>
            </template>
          </el-menu-item>

          <el-menu-item index="tools" @click="handleJumpToSettings()">
            <template #title>
              <el-icon><ToolsIcon /></el-icon>
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
                <!-- 修复：expenseGrowth 本身可能为负数，不能再写死 '-'，否则会出现 --28.3% -->
                <p class="rate negative">
                  {{ (expenseGrowth ?? 0) > 0 ? '+' : (expenseGrowth ?? 0) < 0 ? '-' : '' }}{{
                    Math.abs(expenseGrowth ?? 0)
                  }}% 较上月
                </p>
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
                  <div class="progress-bar" :style="{ width: Math.min((budgetUsage || 0), 100) + '%' }"></div>
                </div>
                <p class="budget-info">
                  ¥{{ monthlyExpense?.toFixed(2) || '0.00' }} / ¥{{
                    monthlyBudget?.toFixed(2) || '0.00'
                  }}
                  ({{ budgetUsage || 0 }}%)
                </p>
                <p class="budget-warning warning-exceeded" v-if="budgetUsage > 100">
                  <i class="icon-warning"></i> 预算已超出 ¥{{ (monthlyExpense - monthlyBudget).toFixed(2) }}
                </p>
                <p class="budget-warning warning-approaching" v-else-if="budgetUsage > 80">
                  <i class="icon-warning"></i> 预算即将超出，仅剩 ¥{{ (monthlyBudget - monthlyExpense).toFixed(2) }}
                </p>
              </div>
            </div>
          </section>

          <!-- 快捷功能区 -->
          <section class="quick-actions">
            <div class="action-card" @click="handleJumpToExpend()">
              <i class="icon-add"></i>
              <h4>添加账单</h4>
            </div>
            <div class="action-card" @click="handleJumpToCoin()">
              <i class="icon-export"></i>
              <h4>添加收入</h4>
            </div>
            <div class="action-card" @click="handleJumpToBudgetView()">
              <i class="icon-setting"></i>
              <h4>设置预算</h4>
            </div>
            <div class="action-card" @click="handleJumpToAnalysis()">
              <i class="icon-report"></i>
              <h4>年度报告</h4>
            </div>
          </section>

          <!-- 近期账单列表（修复bill.amount的toFixed） -->
          <section class="recent-bills">
            <div class="section-header">
              <h3>近期账单</h3>
              <button class="btn btn-outline" @click="handleViewAllBills">查看全部</button>
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
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Coin, DataAnalysis, Goods, House, Tickets, Tools, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user.js'
import useDashboardLogic from '@/stores/dashboardLogic.js'
import PageTagsNav from '@/components/PageTagsNav.vue'

// 给图标组件起别名，避免 IDE/模板检查误判“未导入组件”
const UserIcon = User
const HouseIcon = House
const CoinIcon = Coin
const GoodsIcon = Goods
const TicketsIcon = Tickets
const DataAnalysisIcon = DataAnalysis
const ToolsIcon = Tools

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

// 查看全部账单
const handleViewAllBills = () => {
  router.push('/expend')
}

// 获取dashboard逻辑变量（只保留本页面用到的，避免未使用变量 lint）
const {
  monthlyIncome,
  monthlyExpense,
  monthlyBudget,
  incomeGrowth,
  expenseGrowth,
  balanceRate,
  budgetUsage,
  recentBills,
  fetchDashboardData,
  initTrendChart,
  initCategoryChart,
} = useDashboardLogic()

// 页面挂载初始化
onMounted(async () => {
  // 先加载实际数据
  await fetchDashboardData()

  // 增加DOM存在性判断，防止图表初始化失败
  setTimeout(() => {
    initTrendChart()
    initCategoryChart()
  }, 100)
})

// 左侧菜单选择：只保持当前高亮，不再维护标签数组
const handleMenuSelect = () => {
  // 标签页导航由全局 store 自动维护
}
</script>

<style scoped>
@import '../styles/framework.css';
@import '../styles/finance-dashboard.css';
</style>
