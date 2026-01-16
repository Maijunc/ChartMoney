<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <div class="top-nav" style="position: fixed; left: 30px">
      <div class="logo">MyFinancePal</div>
      <div class="breadcrumb">仪表盘 / 购物预算</div>
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

          <el-menu-item
            index="Tickets"
            @click="handleJumpToBudgetView()"
            style="color: rgb(64, 158, 255) !important"
          >
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
          <!-- 预算设置区域 -->
          <div class="budget-setting">
            <!-- 多月份预算管理 -->
            <el-card shadow="hover" class="multi-month-budget-card">
              <template #header>
                <div class="card-header">
                  <span>多月份预算设置</span>
                  <el-button type="primary" size="small" icon="Plus" @click="addMonthBudget">
                    新增月份预算
                  </el-button>
                </div>
              </template>

              <!-- 月份预算列表 -->
              <div class="month-budget-list">
                <div
                  class="month-budget-item"
                  v-for="(item, index) in monthBudgetList"
                  :key="item.month"
                >
                  <el-card shadow="hover" class="single-month-card">
                    <template #header>
                      <div class="month-card-header">
                        <span>{{ item.month }} 月预算设置</span>
                        <el-button
                          type="danger"
                          size="small"
                          icon="Delete"
                          @click="deleteMonthBudget(index)"
                          :disabled="monthBudgetList.length <= 1"
                        >
                          删除
                        </el-button>
                      </div>
                    </template>

                    <div class="month-budget-form">
                      <el-form :model="item" inline @submit.prevent>
                        <el-form-item label="预算月份">
                          <el-date-picker
                            v-model="item.month"
                            type="month"
                            format="YYYY-MM"
                            value-format="YYYY-MM"
                            placeholder="选择月份"
                            @change="updateMonthBudget(index)"
                          />
                        </el-form-item>
                        <el-form-item label="总预算金额">
                          <el-input
                            v-model.number="item.totalAmount"
                            type="number"
                            placeholder="输入该月总预算"
                            min="0"
                            @change="calculateMonthUsedAmount(index)"
                          />
                        </el-form-item>
                        <el-form-item>
                          <el-button type="primary" @click="saveMonthBudget(index)">
                            保存该月预算
                          </el-button>
                        </el-form-item>
                      </el-form>

                      <!-- 该月预算信息 -->
                      <div v-if="item.isSaved" class="month-budget-info">
                        <p>
                          {{ item.month }} 总预算：<span class="total-amount"
                            >¥{{ item.totalAmount }}</span
                          >
                        </p>
                        <p>
                          已分配金额：<span
                            :class="item.usedAmount > item.totalAmount ? 'text-red' : 'text-green'"
                          >
                            ¥{{ item.usedAmount }}
                          </span>
                        </p>
                        <p>
                          剩余可分配金额：<span
                            :class="item.remainingAmount < 0 ? 'text-red' : 'text-green'"
                          >
                            ¥{{ item.remainingAmount }}
                          </span>
                        </p>
                      </div>
                    </div>

                    <!-- 该月分类预算分配 -->
                    <div v-if="item.isSaved" class="month-category-budget">
                      <el-table
                        :data="item.categoryBudgets"
                        border
                        style="width: 100%; margin-top: 10px"
                      >
                        <el-table-column prop="categoryName" label="预算类别" width="200" />
                        <el-table-column prop="amount" label="预算金额">
                          <template #default="scope">
                            <el-input
                              v-model.number="scope.row.amount"
                              type="number"
                              min="0"
                              @change="updateMonthCategoryBudget(index, scope.row)"
                            />
                          </template>
                        </el-table-column>
                        <el-table-column label="状态" width="120">
                          <template #default="scope">
                            <span
                              :class="
                                scope.row.amount > item.totalAmount ? 'text-red' : 'text-green'
                              "
                            >
                              {{ scope.row.amount > item.totalAmount ? '已超限' : '正常' }}
                            </span>
                          </template>
                        </el-table-column>
                      </el-table>
                    </div>
                  </el-card>
                </div>
              </div>
            </el-card>

            <!-- 页脚 -->
            <footer class="dashboard-footer">
              <p>© 2026 财智管家 - 个人财务管理系统 | 数据安全加密存储</p>
            </footer>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 修复导入顺序，先导入所有依赖
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import useDashboardLogic from '@/stores/dashboardLogic.js'
// 导入Element Plus图标
import {
  User,
  House,
  Coin,
  Goods,
  CreditCard,
  Wallet,
  Tickets,
  DataAnalysis,
  Tools,
  Plus,
  Delete,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

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

// 预算类别列表（不变）
const categoryList = ref([
  { id: 1, categoryName: '餐饮美食' },
  { id: 2, categoryName: '交通出行' },
  { id: 3, categoryName: '居住房租' },
  { id: 4, categoryName: '购物消费' },
  { id: 5, categoryName: '休闲娱乐' },
  { id: 6, categoryName: '医疗健康' },
  { id: 7, categoryName: '其他' },
])

// 多月份预算核心数据
const monthBudgetList = ref([])

// 初始化默认月份预算（当前月）
const initDefaultMonthBudget = () => {
  const now = new Date()
  const defaultMonth = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}`

  // 初始化默认月份预算项
  monthBudgetList.value = [
    {
      month: defaultMonth, // 预算月份
      totalAmount: 0, // 该月总预算
      isSaved: false, // 是否已保存
      usedAmount: 0, // 已分配金额
      remainingAmount: 0, // 剩余金额
      categoryBudgets: categoryList.value.map((item) => ({ ...item, amount: 0 })), // 分类预算
    },
  ]
}

// 新增月份预算
const addMonthBudget = () => {
  const now = new Date()
  // 新增月份默认是下一个月
  const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1)
  const newMonth = `${nextMonth.getFullYear()}-${(nextMonth.getMonth() + 1).toString().padStart(2, '0')}`

  // 检查是否已存在该月份
  const isExist = monthBudgetList.value.some((item) => item.month === newMonth)
  if (isExist) {
    ElMessage.warning(`已存在${newMonth}的预算设置，请选择其他月份`)
    return
  }

  monthBudgetList.value.push({
    month: newMonth,
    totalAmount: 0,
    isSaved: false,
    usedAmount: 0,
    remainingAmount: 0,
    categoryBudgets: categoryList.value.map((item) => ({ ...item, amount: 0 })),
  })
}

// 删除月份预算（至少保留1个）
const deleteMonthBudget = (index) => {
  if (monthBudgetList.value.length <= 1) {
    ElMessage.warning('至少需要保留一个月份的预算设置')
    return
  }
  monthBudgetList.value.splice(index, 1)
  ElMessage.success('月份预算删除成功')
}

// 更新月份（防止重复）
const updateMonthBudget = (index) => {
  const currentItem = monthBudgetList.value[index]
  // 检查是否与其他月份重复
  const duplicateIndex = monthBudgetList.value.findIndex((item, i) => {
    return i !== index && item.month === currentItem.month
  })

  if (duplicateIndex !== -1) {
    ElMessage.warning(`已存在${currentItem.month}的预算设置，请选择其他月份`)
    // 恢复原月份
    const now = new Date()
    monthBudgetList.value[index].month =
      `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}`
  }
}

// 保存该月预算
const saveMonthBudget = (index) => {
  const currentItem = monthBudgetList.value[index]
  if (!currentItem.month || currentItem.totalAmount <= 0) {
    ElMessage.warning('请填写有效的月份和预算金额')
    return
  }

  // 计算已分配和剩余金额
  calculateMonthUsedAmount(index)

  currentItem.isSaved = true
  ElMessage.success(`${currentItem.month}预算设置成功`)
}

// 计算该月已使用金额和剩余金额
const calculateMonthUsedAmount = (index) => {
  const currentItem = monthBudgetList.value[index]
  // 计算已分配金额
  const used = currentItem.categoryBudgets.reduce((sum, item) => sum + item.amount, 0)
  currentItem.usedAmount = used
  // 计算剩余金额
  currentItem.remainingAmount = currentItem.totalAmount - used
}

// 更新该月分类预算
const updateMonthCategoryBudget = (monthIndex, row) => {
  const currentItem = monthBudgetList.value[monthIndex]
  if (!currentItem.isSaved) {
    ElMessage.warning('请先保存该月总预算后再设置分类预算')
    row.amount = 0
    return
  }

  // 计算最新的已分配金额
  calculateMonthUsedAmount(monthIndex)

  if (row.amount > currentItem.totalAmount) {
    ElMessage.warning(`${currentItem.month}的该分类预算不能超过总预算¥${currentItem.totalAmount}`)
  }
}

// 页面挂载初始化
onMounted(() => {
  // 初始化默认月份预算
  initDefaultMonthBudget()
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
@import '../styles/budget.css';
</style>
