<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <div class="top-nav" style="position: fixed; left: 30px">
      <div class="logo">MyFinancePal</div>
      <div class="breadcrumb">仪表盘 / 购物预算</div>
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
        <PageTagsNav :paddingTop="10" />

        <!-- 修复：menu-management-panel 放在 content-panel 内部 -->
        <div class="menu-management-panel">
          <div class="budget-setting">
            <!-- 月份导航栏 -->
            <div style="margin-bottom: 20px; display: flex; align-items: center; gap: 10px; flex-wrap: wrap">
              <el-button
                type="default"
                size="small"
                @click="navigateToPreviousMonth"
              >
                ← 上一月
              </el-button>

              <el-select
                v-model="selectedMonth"
                placeholder="选择月份"
                @change="handleMonthSelect"
                style="width: 150px"
              >
                <el-option
                  v-for="item in monthBudgetList"
                  :key="item.month"
                  :label="item.month"
                  :value="item.month"
                />
              </el-select>

              <el-button
                type="default"
                size="small"
                @click="navigateToNextMonth"
              >
                下一月 →
              </el-button>

              <el-button
                type="primary"
                size="small"
                @click="addMonthBudget"
              >
                + 新增月份
              </el-button>
            </div>

            <!-- 当前月份预算管理 -->
            <el-card shadow="hover" class="multi-month-budget-card">
              <template #header>
                <div class="card-header">
                  <span>{{ selectedMonth }} 月预算设置</span>
                </div>
              </template>

              <!-- 仅显示当前选中月份的预算 -->
              <div class="month-budget-list">
                <div
                  class="month-budget-item"
                  v-if="currentMonthBudget"
                >
                  <el-card shadow="hover" class="single-month-card">
                    <template #header>
                      <div class="month-card-header">
                        <span>{{ currentMonthBudget.month }} 月预算管理</span>
                      </div>
                    </template>

                    <!-- 1. 月份总预算设置 -->
                    <div class="month-budget-form">
                      <el-form :model="currentMonthBudget" inline @submit.prevent>
                        <el-form-item label="预算月份">
                          <el-date-picker
                            v-model="currentMonthBudget.month"
                            type="month"
                            format="YYYY-MM"
                            value-format="YYYY-MM"
                            placeholder="选择月份"
                            @change="handleMonthChange(getCurrentMonthIndex())"
                          />
                        </el-form-item>
                        <el-form-item label="总预算金额">
                          <el-input
                            v-model.number="currentMonthBudget.totalBudget"
                            type="number"
                            placeholder="输入该月总预算"
                            min="0"
                            @change="calculateMonthTotal(getCurrentMonthIndex())"
                          />
                        </el-form-item>
                        <el-form-item>
                          <el-button
                            type="primary"
                            @click="saveMonthTotalBudget(getCurrentMonthIndex())"
                            :loading="savingBudgetIndex === getCurrentMonthIndex()"
                          >
                            保存总预算
                          </el-button>
                        </el-form-item>
                      </el-form>

                      <!-- 月份总预算统计 -->
                      <div v-if="currentMonthBudget.totalBudget > 0" class="month-total-summary">
                        <div class="summary-row">
                          <span class="label">总预算：</span>
                          <span class="value total">¥{{ currentMonthBudget.totalBudget.toFixed(2) }}</span>
                        </div>
                        <div class="summary-row">
                          <span class="label">总实际支出：</span>
                          <span class="value used">¥{{ currentMonthBudget.totalActualExpense.toFixed(2) }}</span>
                        </div>
                        <div class="summary-row">
                          <span class="label">总可用金额：</span>
                          <span
                            class="value remaining"
                            :class="currentMonthBudget.totalRemaining < 0 ? 'text-red' : 'text-green'"
                          >
                            ¥{{ Math.max(0, currentMonthBudget.totalRemaining).toFixed(2) }}
                            <span v-if="currentMonthBudget.totalRemaining < 0" class="over-limit"
                              >(超支 ¥{{ Math.abs(currentMonthBudget.totalRemaining).toFixed(2) }})</span
                            >
                          </span>
                        </div>
                      </div>
                    </div>

                    <!-- 2. 分类预算设置 -->
                    <div v-if="currentMonthBudget.totalBudget > 0" class="category-budget-container">
                      <div class="category-title">分类预算明细</div>

                      <!-- 分类预算表格 -->
                      <el-table
                        :data="currentMonthBudget.categoryBudgets"
                        border
                        stripe
                        style="width: 100%; margin-top: 10px"
                        show-summary
                        :summary-method="
                          ({ columns, data }) => getSummary(columns, data, currentMonthBudget.totalBudget)
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
                                  handleCategoryBudgetChange(getCurrentMonthIndex(), scope.row.id)
                                }
                              "
                              @change="handleCategoryBudgetChange(getCurrentMonthIndex(), scope.row.id)"
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
                              @click="saveCategoryBudget(getCurrentMonthIndex(), scope.row.id)"
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user.js'
import { getBudgetListByMonth, addBudget, updateBudget, deleteBudget } from '@/api/budget.js'
import { getCategoryList } from '@/api/category.js'
import { getBillList } from '@/api/bill.js'
import PageTagsNav from '@/components/PageTagsNav.vue'

// 路由跳转逻辑
const router = useRouter()

// 用户状态管理
const userStore = useUserStore()

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

const handleAvatarClick = () => {
  if (userStore.isLogin) {
    router.push('/settings')
  } else {
    router.push('/login')
  }
}


// 1. 分类列表（从API加载）
const CATEGORY_LIST = ref([])

// 1-1. 月份选择状态（新增）
const selectedMonth = ref('')  // 当前选中的月份

// 加载分类列表
const loadCategories = async () => {
  try {
    const response = await getCategoryList(2) // 2=支出分类
    if (response.code === 200 && response.data) {
      CATEGORY_LIST.value = response.data.map((item) => ({
        id: item.category_id,
        categoryName: item.name,
      }))
      console.log('✅ 分类列表加载成功:', CATEGORY_LIST.value)
    } else {
      ElMessage.error('加载分类列表失败')
    }
  } catch (error) {
    console.error('加载分类列表错误:', error)
    ElMessage.error('加载分类列表失败，请稍后重试')
  }
}

// 2. 月份预算核心数据
const monthBudgetList = ref([])

// 2-1. 保存状态标志
const savingBudgetIndex = ref(-1)  // 标记哪个索引的预算正在保存

// 3. 获取分类实际支出（从API获取真实数据）
const getCategoryActualExpense = async (month) => {
  try {
    const response = await getBillList({
      user_id: userStore.userId,
      the_time: month,
      page: 1,
      page_size: 999, // 获取所有账单
      type: 2, // 2=支出
    })

    // 按分类汇总支出金额
    const expenseByCategory = {}
    if (response.data) {
      response.data.forEach((bill) => {
        const catId = bill.category_id
        expenseByCategory[catId] = (expenseByCategory[catId] || 0) + parseFloat(bill.amount)
      })
    }

    // 返回带实际支出的分类列表
    return CATEGORY_LIST.value.map((category) => ({
      ...category,
      actualExpense: expenseByCategory[category.id] || 0, // 分类实际支出
      budgetAmount: 0, // 分类预算金额
      budgetId: null, // 预算ID（用于更新）
      remaining: 0, // 分类剩余金额
      saving: false, // loading状态
    }))
  } catch (error) {
    console.error('获取分类实际支出失败:', error)
    ElMessage.error('加载实际支出数据失败')
    // 返回空实际支出作为兜底
    return CATEGORY_LIST.value.map((category) => ({
      ...category,
      actualExpense: 0,
      budgetAmount: 0,
      budgetId: null,
      remaining: 0,
      saving: false,
    }))
  }
}

// 4. 加载某月已保存的预算（从API获取）
const loadMonthBudget = async (month) => {
  try {
    const response = await getBudgetListByMonth({
      user_id: userStore.userId,
      month: month,
    })

    if (response.code === 200 && response.data) {
      const budgets = response.data

      // 1. 提取总预算
      const totalBudgetItem = budgets.find((item) => item.is_total === true)
      const totalBudget = totalBudgetItem ? totalBudgetItem.amount : 0
      const totalBudgetId = totalBudgetItem ? totalBudgetItem.id : null

      // 2. 提取分类预算并填充到 categoryBudgets
      const categoryBudgets = await getCategoryActualExpense(month)

      budgets.forEach((budget) => {
        if (!budget.is_total) {
          const category = categoryBudgets.find((c) => c.id === budget.category_id)
          if (category) {
            category.budgetAmount = budget.amount
            category.budgetId = budget.id // 保存budget_id，用于更新
            category.remaining = category.budgetAmount - category.actualExpense
          }
        }
      })

      const totalActualExpense = categoryBudgets.reduce((sum, c) => sum + c.actualExpense, 0)
      const totalRemaining = totalBudget - totalActualExpense

      return {
        month,
        totalBudget,
        totalBudgetId,
        totalActualExpense,
        totalRemaining,
        categoryBudgets,
      }
    }

    return null
  } catch (error) {
    console.error('加载月份预算失败:', error)
    return null
  }
}

// 5. 初始化预算页面（改为加载所有已保存的月份预算）
const initDefaultMonthBudget = async () => {
  if (!userStore.isLogin) {
    ElMessage.warning('请先登录')
    return
  }

  // 修复：改为加载用户所有已保存的预算月份
  // 获取当前年月
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = String(now.getMonth() + 1).padStart(2, '0')
  const defaultMonth = `${currentYear}-${currentMonth}`

  // 策略：先尝试加载当前月份，如果有的话也加载前后2个月的预算
  const monthsToLoad = []

  // 生成要加载的月份列表（当前月前后各2个月）
  for (let i = -2; i <= 2; i++) {
    const date = new Date(currentYear, parseInt(currentMonth) - 1 + i, 1)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    monthsToLoad.push(`${year}-${month}`)
  }

  // 并行加载所有月份的预算
  const monthsData = await Promise.all(
    monthsToLoad.map(month => loadMonthBudget(month))
  )

  // 过滤出有预算的月份，以及当前月
  monthBudgetList.value = []

  for (let i = 0; i < monthsToLoad.length; i++) {
    const month = monthsToLoad[i]
    let monthData = monthsData[i]

    // 如果该月没有预算，创建空预算对象
    if (!monthData) {
      const categoryBudgets = await getCategoryActualExpense(month)
      const totalActualExpense = categoryBudgets.reduce((sum, item) => sum + item.actualExpense, 0)

      monthData = {
        month: month,
        totalBudget: 0,
        totalBudgetId: null,
        totalActualExpense: totalActualExpense,
        totalRemaining: 0,
        categoryBudgets: categoryBudgets,
      }
    }

    monthBudgetList.value.push(monthData)
  }

  // 按月份倒序排列（最新的月份在前）
  monthBudgetList.value.sort((a, b) => b.month.localeCompare(a.month))
}

// 6. 新增月份预算函数（改为提供快速选择或手动输入）
const addMonthBudget = async () => {
  // 获取当前已添加的最后一个月份
  const lastMonth = monthBudgetList.value[0]?.month ||
    new Date().toISOString().slice(0, 7)

  // 计算下一个月份
  const [year, month] = lastMonth.split('-').map(Number)
  let nextMonth = month + 1
  let nextYear = year

  if (nextMonth > 12) {
    nextMonth = 1
    nextYear++
  }

  const suggestedMonth = `${nextYear}-${String(nextMonth).padStart(2, '0')}`

  // 弹出对话框让用户确认或修改
  try {
    const newMonthStr = await ElMessageBox.prompt(
      `建议添加 ${suggestedMonth} 月份预算，您也可以输入其他月份（格式：YYYY-MM）`,
      '新增月份预算',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /^\d{4}-\d{2}$/,
        inputErrorMessage: '月份格式错误，请输入 YYYY-MM 格式',
        inputValue: suggestedMonth,
      }
    )

    // 验证年月格式和有效性
    try {
      const [yearStr, monthStr] = newMonthStr.split('-')
      const yearNum = parseInt(yearStr)
      const monthNum = parseInt(monthStr)

      if (isNaN(yearNum) || isNaN(monthNum) || monthNum < 1 || monthNum > 12) {
        ElMessage.error('请输入有效的年月（月份应在 01-12 之间）')
        return
      }
    } catch {
      ElMessage.error('月份格式错误')
      return
    }

    // 检查是否已添加相同月份的预算
    const duplicateIndex = monthBudgetList.value.findIndex((item) => item.month === newMonthStr)
    if (duplicateIndex !== -1) {
      ElMessage.warning(`已存在 ${newMonthStr} 的预算，请勿重复添加`)
      return
    }

    // 获取该月份实际支出
    const categoryBudgets = await getCategoryActualExpense(newMonthStr)
    const totalActualExpense = categoryBudgets.reduce((sum, item) => sum + item.actualExpense, 0)

    // 尝试从API加载该月已保存的预算
    let monthData = await loadMonthBudget(newMonthStr)

    if (!monthData) {
      // 创建新月份预算对象
      monthData = {
        month: newMonthStr,
        totalBudget: 0,
        totalBudgetId: null,
        totalActualExpense: totalActualExpense,
        totalRemaining: 0,
        categoryBudgets: categoryBudgets,
      }
    }

    // 添加到列表并排序
    monthBudgetList.value.push(monthData)
    monthBudgetList.value.sort((a, b) => b.month.localeCompare(a.month))

    ElMessage.success(`成功新增 ${newMonthStr} 月份预算`)
  } catch {
    // 用户取消操作
    return
  }
}

// 5-3. 计算属性：判断是否允许新增月份（改为始终允许）
const isAllMonthsAdded = computed(() => {
  // 修复：支持跨年份月份选择，所以始终允许新增
  // 用户可以手动选择任意年月，无需限制
  return false
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

// 5-4. 计算属性：获取当前选中的月份预算对象
const currentMonthBudget = computed(() => {
  return monthBudgetList.value.find((item) => item.month === selectedMonth.value) || null
})

// 5-5. 辅助函数：获取当前月份在列表中的索引
const getCurrentMonthIndex = () => {
  return monthBudgetList.value.findIndex((item) => item.month === selectedMonth.value)
}

// 6-1. 上一月导航（新增）
const navigateToPreviousMonth = () => {
  if (!selectedMonth.value) return

  const [year, month] = selectedMonth.value.split('-').map(Number)
  let prevMonth = month - 1
  let prevYear = year

  if (prevMonth < 1) {
    prevMonth = 12
    prevYear--
  }

  const prevMonthStr = `${prevYear}-${String(prevMonth).padStart(2, '0')}`

  // 检查该月是否存在
  const exists = monthBudgetList.value.some(item => item.month === prevMonthStr)
  if (exists) {
    selectedMonth.value = prevMonthStr
    handleMonthSelect(prevMonthStr)
  } else {
    ElMessage.warning(`${prevMonthStr} 月份暂无预算数据`)
  }
}

// 6-2. 下一月导航（新增）
const navigateToNextMonth = () => {
  if (!selectedMonth.value) return

  const [year, month] = selectedMonth.value.split('-').map(Number)
  let nextMonth = month + 1
  let nextYear = year

  if (nextMonth > 12) {
    nextMonth = 1
    nextYear++
  }

  const nextMonthStr = `${nextYear}-${String(nextMonth).padStart(2, '0')}`

  // 检查该月是否存在
  const exists = monthBudgetList.value.some(item => item.month === nextMonthStr)
  if (exists) {
    selectedMonth.value = nextMonthStr
    handleMonthSelect(nextMonthStr)
  } else {
    ElMessage.warning(`${nextMonthStr} 月份暂无预算数据`)
  }
}

// 6-3. 月份选择处理（新增）
const handleMonthSelect = async (month) => {
  selectedMonth.value = month
  // 找到对应的月份数据，重新加载
  const monthData = monthBudgetList.value.find(item => item.month === month)
  if (monthData) {
    // 重新加载该月的完整数据，确保显示最新信息
    const reloadedData = await loadMonthBudget(month)
    if (reloadedData) {
      const index = monthBudgetList.value.findIndex(item => item.month === month)
      monthBudgetList.value[index] = reloadedData
    }
  }
}

// 7. 月份变更处理（修复：加载该月完整预算数据）
const handleMonthChange = async (index) => {
  const currentItem = monthBudgetList.value[index]

  // 检查重复
  const duplicateIndex = monthBudgetList.value.findIndex(
    (item, i) => i !== index && item.month === currentItem.month,
  )
  if (duplicateIndex !== -1) {
    ElMessage.error(
      `月份 ${currentItem.month} 已被其他预算项占用！请选择其他月份或删除其他项的相同月份。`,
    )
    return
  }

  // 修复：加载该月的完整预算数据（包括已保存的总预算和分类预算）
  try {
    const monthData = await loadMonthBudget(currentItem.month)

    if (monthData) {
      // 该月已有保存的预算，加载完整数据
      monthBudgetList.value[index] = monthData
      ElMessage.success(`成功切换到 ${currentItem.month}，已加载该月预算数据`)
    } else {
      // 该月没有保存的预算，只加载实际支出
      currentItem.categoryBudgets = await getCategoryActualExpense(currentItem.month)
      currentItem.totalActualExpense = currentItem.categoryBudgets.reduce(
        (sum, item) => sum + item.actualExpense,
        0,
      )
      // 重置预算数据
      currentItem.totalBudget = 0
      currentItem.totalBudgetId = null
      currentItem.totalRemaining = 0

      ElMessage.success(`成功切换到 ${currentItem.month}，该月暂无预算`)
    }
  } catch (error) {
    console.error('切换月份失败:', error)
    ElMessage.error('切换月份失败，请稍后重试')
  }
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

// 10. 保存月份总预算（改为异步，调用真实API）
const saveMonthTotalBudget = async (index) => {
  const currentItem = monthBudgetList.value[index]

  // 1. 验证总预算金额
  if (currentItem.totalBudget <= 0) {
    ElMessage.warning('请输入有效的总预算金额（大于0）')
    return
  }

  // 2. 再次检查是否重复（保存前再验证一次）
  const duplicateIndex = monthBudgetList.value.findIndex(
    (item, i) => i !== index && item.month === currentItem.month,
  )
  if (duplicateIndex !== -1) {
    ElMessage.error(`已存在 ${currentItem.month} 的预算，请选择其他月份或删除重复项`)
    return
  }

  // 3. 设置 loading 状态
  savingBudgetIndex.value = index

  try {
    if (currentItem.totalBudgetId) {
      // 更新已存在的总预算
      await updateBudget({
        user_id: userStore.userId,
        budget_id: currentItem.totalBudgetId,
        amount: currentItem.totalBudget,
      })
      ElMessage.success(`${currentItem.month} 总预算更新成功`)
    } else {
      // 添加新的总预算
      const response = await addBudget({
        user_id: userStore.userId,
        category_id: null, // 总预算没有分类
        is_total: true,
        amount: currentItem.totalBudget,
        month: currentItem.month,
      })

      // 保存返回的budget_id
      if (response.data && response.data.id) {
        currentItem.totalBudgetId = response.data.id
      }
      ElMessage.success(`${currentItem.month} 总预算保存成功`)
    }

    // 重新计算总剩余
    calculateMonthTotal(index)
  } catch (error) {
    console.error('保存总预算失败:', error)
    ElMessage.error('保存失败：' + (error.response?.data?.detail || error.message))
  } finally {
    // 4. 清除 loading 状态
    savingBudgetIndex.value = -1
  }
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

// 11. 保存分类预算（改为异步，调用真实API）
const saveCategoryBudget = async (monthIndex, categoryId) => {
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

    // 6. 调用真实API保存
    if (category.budgetId) {
      // 更新已存在的分类预算
      await updateBudget({
        user_id: userStore.userId,
        budget_id: category.budgetId,
        amount: category.budgetAmount,
      })
    } else {
      // 添加新的分类预算
      const response = await addBudget({
        user_id: userStore.userId,
        category_id: categoryId,
        is_total: false,
        amount: category.budgetAmount,
        month: currentItem.month,
      })

      // 保存返回的budget_id
      if (response.data && response.data.id) {
        category.budgetId = response.data.id
      }
    }

    // 7. 强制刷新剩余金额（确保100%同步）
    calculateCategoryRemaining(monthIndex, categoryId)

    // 8. 成功提示（更友好）
    ElMessage.success(
      `${category.categoryName} 预算已成功保存！剩余金额：¥${category.remaining.toFixed(2)}`,
    )
  } catch (error) {
    console.error('保存分类预算失败:', error)
    ElMessage.error(`${category.categoryName} 预算保存失败：${error.response?.data?.detail || error.message}`)
  } finally {
    // 移除loading状态
    category.saving = false
  }
}
// 12. 页面挂载初始化
onMounted(async () => {
  // 1. 加载分类列表
  await loadCategories()

  // 2. 初始化默认月份（使用真实数据）
  await initDefaultMonthBudget()

  // 3. 初始化选中的月份（选择第一个，通常是最新的月份）
  if (monthBudgetList.value.length > 0) {
    selectedMonth.value = monthBudgetList.value[0].month
  }
})
// ========== 核心业务逻辑结束 ==========


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
