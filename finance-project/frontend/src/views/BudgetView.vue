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
          <el-menu-item index="Goods" @click="handleJumpToRecord()">
            <template #title>
              <el-icon><Goods /></el-icon>
              <span>支出管理</span>
            </template>
          </el-menu-item>

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

        <!-- 修复：menu-management-panel 放在 content-panel 内部 -->
        <div class="menu-management-panel">
          <div class="budget-setting">
            <!-- 多月份预算管理 -->
            <el-card shadow="hover" class="multi-month-budget-card">
              <template #header>
                <div class="card-header">
                  <span>多月份预算设置</span>
                  <!-- 核心修改：添加disabled判断 -->
                  <el-button
                    type="primary"
                    size="small"
                    icon="Plus"
                    @click="addMonthBudget"
                    :disabled="isAllMonthsAdded"
                  >
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
                        <span>{{ item.month }} 月预算管理</span>
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

                    <!-- 1. 月份总预算设置 -->
                    <div class="month-budget-form">
                      <el-form :model="item" inline @submit.prevent>
                        <el-form-item label="预算月份">
                          <el-date-picker
                            v-model="item.month"
                            type="month"
                            format="YYYY-MM"
                            value-format="YYYY-MM"
                            placeholder="选择月份"
                            @change="handleMonthChange(index)"
                          />
                        </el-form-item>
                        <el-form-item label="总预算金额">
                          <el-input
                            v-model.number="item.totalBudget"
                            type="number"
                            placeholder="输入该月总预算"
                            min="0"
                            @change="calculateMonthTotal(index)"
                          />
                        </el-form-item>
                        <el-form-item>
                          <el-button type="primary" @click="saveMonthTotalBudget(index)">
                            保存总预算
                          </el-button>
                        </el-form-item>
                      </el-form>

                      <!-- 月份总预算统计 -->
                      <div v-if="item.totalBudget > 0" class="month-total-summary">
                        <div class="summary-row">
                          <span class="label">总预算：</span>
                          <span class="value total">¥{{ item.totalBudget.toFixed(2) }}</span>
                        </div>
                        <div class="summary-row">
                          <span class="label">总实际支出：</span>
                          <span class="value used">¥{{ item.totalActualExpense.toFixed(2) }}</span>
                        </div>
                        <div class="summary-row">
                          <span class="label">总可用金额：</span>
                          <span
                            class="value remaining"
                            :class="item.totalRemaining < 0 ? 'text-red' : 'text-green'"
                          >
                            ¥{{ Math.max(0, item.totalRemaining).toFixed(2) }}
                            <span v-if="item.totalRemaining < 0" class="over-limit"
                              >(超支 ¥{{ Math.abs(item.totalRemaining).toFixed(2) }})</span
                            >
                          </span>
                        </div>
                      </div>
                    </div>

                    <!-- 2. 分类预算设置 -->
                    <div v-if="item.totalBudget > 0" class="category-budget-container">
                      <div class="category-title">分类预算明细</div>

                      <!-- 分类预算表格 -->
                      <el-table
                        :data="item.categoryBudgets"
                        border
                        stripe
                        style="width: 100%; margin-top: 10px"
                        show-summary
                        :summary-method="
                          ({ columns, data }) => getSummary(columns, data, item.totalBudget)
                        "
                        :cell-class-name="summaryCellStyle"
                      >
                        <el-table-column prop="categoryName" label="预算类别" width="150" />
                        <el-table-column label="分类预算金额">
                          <template #default="scope">
                            <el-input
                              v-model.number="scope.row.budgetAmount"
                              type="number"
                              min="0"
                              size="small"
                              @input="
                                () => {
                                  handleBudgetAmountInput(scope.row)
                                  handleCategoryBudgetChange(index, scope.row.id)
                                }
                              "
                              @change="handleCategoryBudgetChange(index, scope.row.id)"
                            />
                          </template>
                        </el-table-column>
                        <el-table-column prop="actualExpense" label="分类实际支出" width="120">
                          <template #default="scope">
                            ¥{{ scope.row.actualExpense.toFixed(2) }}
                          </template>
                        </el-table-column>
                        <el-table-column label="分类剩余金额" width="120">
                          <template #default="scope">
                            <span :class="scope.row.remaining < 0 ? 'text-red' : 'text-green'">
                              ¥{{ scope.row.remaining.toFixed(2) }}
                            </span>
                          </template>
                        </el-table-column>
                        <el-table-column label="操作" width="80">
                          <template #default="scope">
                            <el-button
                              size="small"
                              type="primary"
                              @click="saveCategoryBudget(index, scope.row.id)"
                              :loading="scope.row.saving"
                            >
                              保存
                            </el-button>
                          </template>
                        </el-table-column>
                      </el-table>
                    </div>
                  </el-card>
                </div>
              </div>
            </el-card>
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

import { ElMessage, ElMessageBox } from 'element-plus'
//导入API
//import { fetchMonthExpense, saveMonthBudget as saveMonthBudgetToAPI } from '@/api/budgetAPI.js'
// 导入独立的API和工具类
//import { fetchMonthExpense, saveMonthBudget } from '@/api/budgetAPI.js'

// 路由跳转逻辑
const router = useRouter()

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

// 1. 固定分类列表
const CATEGORY_LIST = [
  { id: 1, categoryName: '餐饮美食' },
  { id: 2, categoryName: '交通出行' },
  { id: 3, categoryName: '居住房租' },
  { id: 4, categoryName: '购物消费' },
  { id: 5, categoryName: '休闲娱乐' },
  { id: 6, categoryName: '医疗健康' },
  { id: 7, categoryName: '其他' },
]

// 2. 月份预算核心数据
const monthBudgetList = ref([])

// 3. 模拟获取分类实际支出（替代API，可替换为真实接口）
const getCategoryActualExpense = (month) => {
  // 模拟支出数据（实际项目中替换为从支出表查询）
  const mockExpense = {
    1: Math.floor(Math.random() * 1000), // 餐饮美食
    2: Math.floor(Math.random() * 500), // 交通出行
    3: Math.floor(Math.random() * 2000), // 居住房租
    4: Math.floor(Math.random() * 800), // 购物消费
    5: Math.floor(Math.random() * 600), // 休闲娱乐
    6: Math.floor(Math.random() * 300), // 医疗健康
    7: Math.floor(Math.random() * 200), // 其他
  }

  return CATEGORY_LIST.map((category) => ({
    ...category,
    actualExpense: mockExpense[category.id], // 分类实际支出
    budgetAmount: 0, // 分类预算金额
    remaining: 0, // 分类剩余金额
  }))
}

// 5. 初始化默认月份预算（修改：默认创建1月预算）
const initDefaultMonthBudget = () => {
  const currentYear = new Date().getFullYear()
  const defaultMonth = `${currentYear}-01` // 默认创建1月

  const categoryBudgets = getCategoryActualExpense(defaultMonth)
  const totalActualExpense = categoryBudgets.reduce((sum, item) => sum + item.actualExpense, 0)

  monthBudgetList.value = [
    {
      month: defaultMonth,
      totalBudget: 0,
      totalActualExpense: totalActualExpense,
      totalRemaining: 0,
      categoryBudgets: categoryBudgets,
    },
  ]
}

// 6. 改造后的新增月份预算函数
const addMonthBudget = () => {
  const currentYear = new Date().getFullYear()

  // 获取已添加的月份数字（如 [1,2,3]）
  const addedMonths = monthBudgetList.value.map((item) => {
    const [year, month] = item.month.split('-')
    return parseInt(month)
  })

  // 找到下一个未添加的月份（从1开始）
  let nextMonthNum = 1
  while (addedMonths.includes(nextMonthNum) && nextMonthNum <= 12) {
    nextMonthNum++
  }

  // 如果已经到12月，提示并返回
  if (nextMonthNum > 12) {
    ElMessage.warning('已添加1-12月所有月份的预算，无法继续新增')
    return
  }

  // 格式化月份（补零，如 2 → 02）
  const newMonth = `${currentYear}-${nextMonthNum.toString().padStart(2, '0')}`

  // 获取新月份实际支出
  const categoryBudgets = getCategoryActualExpense(newMonth)
  const totalActualExpense = categoryBudgets.reduce((sum, item) => sum + item.actualExpense, 0)

  // 添加新月份预算
  monthBudgetList.value.push({
    month: newMonth,
    totalBudget: 0,
    totalActualExpense: totalActualExpense,
    totalRemaining: 0,
    categoryBudgets: categoryBudgets,
  })

  ElMessage.success(`成功新增${newMonth}月份预算`)
}

// 5-3. 计算属性：判断是否已添加1-12月所有月份
const isAllMonthsAdded = computed(() => {
  // 获取已添加的月份（提取月份数字）
  const addedMonths = monthBudgetList.value.map((item) => {
    const [year, month] = item.month.split('-')
    return parseInt(month)
  })
  // 检查是否包含1-12所有月份
  return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].every((month) => addedMonths.includes(month))
})

// 6. 删除月份预算
const deleteMonthBudget = (index) => {
  if (monthBudgetList.value.length <= 1) {
    ElMessage.warning('至少保留一个月份的预算设置')
    return
  }
  monthBudgetList.value.splice(index, 1)
  ElMessage.success('月份预算删除成功')
}

// 7. 月份变更处理
const handleMonthChange = async (index) => {
  const currentItem = monthBudgetList.value[index]
  // 检查重复
  const duplicateIndex = monthBudgetList.value.findIndex(
    (item, i) => i !== index && item.month === currentItem.month,
  )
  if (duplicateIndex !== -1) {
    ElMessage.warning(`已存在${currentItem.month}的预算，请选择其他月份`)
    const now = new Date()
    currentItem.month = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}`
    return
  }

  // 更新该月实际支出数据
  currentItem.categoryBudgets = getCategoryActualExpense(currentItem.month)
  currentItem.totalActualExpense = currentItem.categoryBudgets.reduce(
    (sum, item) => sum + item.actualExpense,
    0,
  )
  // 重新计算总剩余
  calculateMonthTotal(index)
}

// 8. 计算月份总剩余金额
const calculateMonthTotal = (index) => {
  const currentItem = monthBudgetList.value[index]
  // 总剩余 = 总预算 - 总实际支出
  currentItem.totalRemaining = currentItem.totalBudget - currentItem.totalActualExpense

  // 同步更新分类剩余（如果分类预算已设置）
  currentItem.categoryBudgets.forEach((category) => {
    if (category.budgetAmount > 0) {
      category.remaining = category.budgetAmount - category.actualExpense
    }
  })
}

// 9. 计算分类剩余金额
const calculateCategoryRemaining = (monthIndex, categoryId) => {
  const currentItem = monthBudgetList.value[monthIndex]
  const category = currentItem.categoryBudgets.find((item) => item.id === categoryId)

  if (category) {
    // 分类剩余 = 分类预算 - 分类实际支出
    category.remaining = category.budgetAmount - category.actualExpense
  }

  // 重新计算总剩余（可选）
  calculateMonthTotal(monthIndex)
}

// 10. 保存月份总预算
const saveMonthTotalBudget = (index) => {
  const currentItem = monthBudgetList.value[index]
  if (currentItem.totalBudget <= 0) {
    ElMessage.warning('请输入有效的总预算金额（大于0）')
    return
  }

  // 计算总剩余
  calculateMonthTotal(index)
  ElMessage.success(`${currentItem.month} 总预算保存成功`)
}

// 实时校验单个分类预算是否超限（必须存在）
const checkSingleCategoryOverTotal = (
  totalBudget,
  categoryBudgets,
  currentCategoryId,
  newBudgetAmount,
) => {
  // 计算除当前分类外的其他分类预算总和
  const otherCategoriesTotal = categoryBudgets.reduce((sum, item) => {
    if (item.id === currentCategoryId) return sum
    return sum + (item.budgetAmount || 0)
  }, 0)

  // 计算加上当前分类新预算后的总分类预算
  const newTotal = otherCategoriesTotal + newBudgetAmount

  return {
    isOver: newTotal > totalBudget,
    newTotal,
    overAmount: newTotal - totalBudget,
    totalBudget,
  }
}

// 11. 保存分类预算
// BudgetView.vue 中的 saveCategoryBudget 函数
const saveCategoryBudget = (monthIndex, categoryId) => {
  const currentItem = monthBudgetList.value[monthIndex]
  const category = currentItem.categoryBudgets.find((item) => item.id === categoryId)

  // 1. 前置校验：分类不存在则返回
  if (!category) return

  // 2. 添加loading状态（防止重复点击）
  category.saving = true

  try {
    // 3. 负数校验（和实时校验一致，双重保障）
    if (category.budgetAmount < 0 || isNaN(category.budgetAmount)) {
      ElMessage.warning('分类预算金额不能为负数，请输入大于等于0的数值！')
      category.budgetAmount = 0
      calculateCategoryRemaining(monthIndex, categoryId) // 强制刷新剩余金额
      return
    }

    // 4. 总预算为0的校验
    if (currentItem.totalBudget <= 0) {
      ElMessage.warning('请先设置并保存该月份的总预算！')
      return
    }

    // 5. 最终超限校验（更严格的校验）
    const checkResult = checkSingleCategoryOverTotal(
      currentItem.totalBudget,
      currentItem.categoryBudgets,
      categoryId,
      category.budgetAmount,
    )

    if (checkResult.isOver) {
      ElMessageBox.alert(
        `已超出预算！当前分类预算设置后，所有分类预算总和（¥${checkResult.newTotal.toFixed(2)}）将超出总预算（¥${checkResult.totalBudget.toFixed(2)}）¥${checkResult.overAmount.toFixed(2)}`,
        '保存失败',
        { type: 'error' },
      )
      category.budgetAmount = 0
      calculateCategoryRemaining(monthIndex, categoryId) // 刷新剩余金额
      return
    }

    // 6. 模拟API保存（核心价值：持久化操作）
    // 实际项目中替换为真实的接口调用
    setTimeout(() => {
      // 强制刷新剩余金额（确保100%同步）
      calculateCategoryRemaining(monthIndex, categoryId)

      // 成功提示（更友好）
      ElMessage.success(
        `${category.categoryName} 预算已成功保存！剩余金额：¥${category.remaining.toFixed(2)}`,
      )

      // 可在这里添加本地存储/缓存逻辑
      // localStorage.setItem(`budget_${currentItem.month}_${categoryId}`, category.budgetAmount)
    }, 500)
  } catch (error) {
    ElMessage.error(`${category.categoryName} 预算保存失败：${error.message}`)
  } finally {
    // 移除loading状态
    category.saving = false
  }
}
// 12. 页面挂载初始化
onMounted(() => {
  initDefaultMonthBudget()
})
// ========== 核心业务逻辑结束 ==========

// 原有标签页逻辑（完全不变）
const tagsList = ref([
  { key: 'dashboard', label: '仪表盘' },
  { key: 'user', label: '首页' },
  { key: 'coin', label: '收入管理' },
  { key: 'Goods', label: '支出管理' },
  { key: 'Tickets', label: '购物预算管理' },
  { key: 'DataAnalysis', label: '消费年度总结' },
  { key: 'Tools', label: '设置' },
])
const activePath = ref('dashboard')

const pageTagsList = ref([
  { key: 'dashboard', label: '仪表盘' },
  { key: 'user', label: '首页' },
  { key: 'coin', label: '收入管理' },
  { key: 'Goods', label: '支出管理' },
  { key: 'Tickets', label: '购物预算管理' },
  { key: 'DataAnalysis', label: '消费年度总结' },
])
const activePageKey = ref('dashboard')

const handleCloseTag = (index) => {
  const closedTag = tagsList.value[index]
  tagsList.value.splice(index, 1)
  if (closedTag?.key === activePath.value) {
    activePath.value = tagsList.value[tagsList.value.length - 1]?.key || 'dashboard'
  }
}

const handleTagClick = (key) => {
  activePath.value = key
}

const handleClosePageTag = (index) => {
  const closedTag = pageTagsList.value[index]
  pageTagsList.value.splice(index, 1)
  if (closedTag?.key === activePageKey.value) {
    activePageKey.value = pageTagsList.value[pageTagsList.value.length - 1]?.key || 'dashboard'
  }
}

const handlePageTagClick = (key) => {
  activePageKey.value = key
}

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

// 计算分类预算总和（隐藏算法）
const _calculateCategoryBudgetTotal = (categoryBudgets) => {
  return categoryBudgets.reduce((sum, item) => sum + (item.budgetAmount || 0), 0)
}

// 校验是否超出总预算（隐藏算法）
const _checkCategoryBudgetOverTotal = (totalBudget, categoryBudgets) => {
  const categoryTotal = _calculateCategoryBudgetTotal(categoryBudgets)
  return categoryTotal > totalBudget
}

const handleCategoryBudgetChange = (monthIndex, categoryId) => {
  const currentItem = monthBudgetList.value[monthIndex]
  const category = currentItem.categoryBudgets.find((item) => item.id === categoryId)

  if (currentItem.totalBudget <= 0) {
    ElMessage.warning('请先设置并保存该月份的总预算！')
    category.budgetAmount = 0
    calculateCategoryRemaining(monthIndex, categoryId) // 实时刷新剩余金额
    return
  }

  // 实时校验当前分类是否导致总分类预算超出总预算
  const checkResult = checkSingleCategoryOverTotal(
    currentItem.totalBudget,
    currentItem.categoryBudgets,
    categoryId,
    category.budgetAmount,
  )

  if (checkResult.isOver) {
    // 红色提示：当前分类预算导致总分类预算超出
    ElMessage.error(
      `已超出预算！当前分类预算设置后，所有分类预算总和（¥${checkResult.newTotal.toFixed(2)}）将超出总预算（¥${checkResult.totalBudget.toFixed(2)}）¥${checkResult.overAmount.toFixed(2)}`,
    )
    // 重置当前分类预算
    category.budgetAmount = 0
    // 实时计算剩余金额
    calculateCategoryRemaining(monthIndex, categoryId)
    return
  }

  // 未超出时实时计算剩余金额（核心修复：直接调用函数，不赋值）
  calculateCategoryRemaining(monthIndex, categoryId)
}

// 监听分类预算金额输入，禁止负数并提示
const handleBudgetAmountInput = (row) => {
  // 如果输入负数，强制重置为0并提示
  if (row.budgetAmount < 0) {
    ElMessage.warning('分类预算金额不能为负数，请输入大于等于0的数值！')
    row.budgetAmount = 0 // 强制重置为0
  }
}

// ========== 表格合计行功能 ==========
// 计算合计行内容
/*const getSummary = (columns, data, totalBudget) => {
  const sums = []
  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = '分类预算总和'
    } else if (column.label === '分类预算金额') {
      // 计算所有分类预算的总和
      const total = data.reduce((sum, item) => sum + (item.budgetAmount || 0), 0)
      // 返回包含状态的对象，用于样式控制
      sums[index] = {
        value:
          total > totalBudget
            ? `¥${total.toFixed(2)} (超出 ¥${(total - totalBudget).toFixed(2)})`
            : `¥${total.toFixed(2)}`,
        isOver: total > totalBudget,
        overAmount: total > totalBudget ? total - totalBudget : 0,
      }
    } else {
      sums[index] = '' // 其他列合计行留空
    }
  })
  return sums
}*/
// 计算合计行内容（修复 [object Object] 问题）
const getSummary = (columns, data, totalBudget) => {
  const sums = []
  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = '分类预算总和'
    } else if (column.label === '分类预算金额') {
      // 计算所有分类预算的总和
      const total = data.reduce((sum, item) => sum + (item.budgetAmount || 0), 0)
      // 直接返回纯字符串（关键修复）
      if (total > totalBudget) {
        sums[index] = `¥${total.toFixed(2)} (超出 ¥${(total - totalBudget).toFixed(2)})`
      } else {
        sums[index] = `¥${total.toFixed(2)}`
      }
    } else {
      sums[index] = '' // 其他列合计行留空
    }
  })
  return sums
}

// 控制合计行单元格样式（适配纯字符串）
const summaryCellStyle = ({ row, column, rowIndex, columnIndex, tableData }) => {
  // 仅对合计行（rowIndex=-1）生效
  if (rowIndex === -1) {
    // 仅对分类预算金额列（columnIndex=1）生效
    if (columnIndex === 1) {
      // 重新计算总和判断是否超限
      const totalBudget = row[0] === '分类预算总和' ? tableData[0]?.totalBudget : 0
      const total = tableData.reduce((sum, item) => sum + (item.budgetAmount || 0), 0)
      if (total > totalBudget && totalBudget > 0) {
        return 'summary-over' // 超出预算的样式类
      }
    }
  }
}
// ========== 表格合计行功能结束 ==========
</script>

<style scoped>
@import '../styles/framework.css';
@import '../styles/finance-dashboard.css';
@import '../styles/budget.css';

/* 新增必要的样式 */
.month-budget-summary-card {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}
.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.summary-item label {
  color: #666;
  font-size: 14px;
}
.total-amount {
  color: #1989fa;
  font-weight: bold;
  font-size: 16px;
}
.actual-expense {
  color: #f56c6c;
  font-weight: bold;
  font-size: 16px;
}
.text-red {
  color: #f56c6c !important;
}
.text-green {
  color: #67c23a !important;
}
.over-limit {
  font-size: 12px;
  color: #f56c6c;
  margin-left: 4px;
}
.category-budget-cards {
  margin-top: 20px;
}
.card-title {
  font-size: 15px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #333;
}
.category-card {
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.category-header {
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 8px;
}
.category-name {
  font-weight: 500;
  color: #333;
}
.category-stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  padding: 8px 0;
}
.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}
.stat-item label {
  color: #666;
}
.category-edit {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}
.category-edit .el-input {
  width: 120px;
}
</style>
