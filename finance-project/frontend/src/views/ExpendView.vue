<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <div class="top-nav" style="position: fixed; left: 30px">
      <div class="logo">MyFinancePal</div>
      <div class="breadcrumb" style="">仪表盘 / 支出管理-日常支出</div>
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
        <el-menu default-active="menu-management" class="sidebar-menu" @select="handleMenuSelect">
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

          <!-- 支出管理作为父级折叠菜单，包含信用卡借入记录子项 -->
          <el-menu-item index="Goods" style="color: rgb(64, 158, 255) !important"  @click="handleJumpToExpend()">
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
        <!-- 标签页导航（顶部小标签） -->
        <PageTagsNav :paddingTop="10" />

        <!-- 菜单管理内容 -->
        <div class="menu-management-panel">
          <!-- 搜索区域 -->
          <div class="search-bar" style="margin-bottom: 20px">
            <el-form :inline="true" :model="searchForm" class="expense-search-form">
              <!-- 日期筛选：动态选择器 -->
              <el-form-item label="日期筛选">
                <div class="dynamic-date-filter">
                  <!-- 筛选粒度选择 -->
                  <el-select
                    v-model="searchForm.dateType"
                    placeholder="筛选方式"
                    style="width: 100px; margin-right: 10px"
                    @change="handleDateTypeChange"
                    clearable
                  >
                    <el-option label="按日筛选" value="day"></el-option>
                    <el-option label="按月筛选" value="month"></el-option>
                    <el-option label="按年筛选" value="year"></el-option>
                  </el-select>

                  <!-- 动态日期选择器 -->
                  <template v-if="searchForm.dateType === 'day'">
                    <el-date-picker
                      v-model="searchForm.dateValue"
                      type="date"
                      placeholder="选择日期"
                      format="YYYY-MM-DD"
                      value-format="YYYY-MM-DD"
                      style="width: 150px"
                      :locale="zhCn"
                      clearable
                    />
                  </template>

                  <template v-else-if="searchForm.dateType === 'month'">
                    <el-date-picker
                      v-model="searchForm.dateValue"
                      type="month"
                      placeholder="选择月份"
                      format="YYYY-MM"
                      value-format="YYYY-MM"
                      style="width: 150px"
                      :locale="zhCn"
                      clearable
                    />
                  </template>

                  <template v-else-if="searchForm.dateType === 'year'">
                    <el-select
                      v-model="searchForm.dateValue"
                      placeholder="选择年份"
                      style="width: 150px"
                      clearable
                    >
                      <el-option
                        v-for="year in yearOptions"
                        :key="year"
                        :label="`${year}年`"
                        :value="year.toString()"
                      />
                    </el-select>
                  </template>
                </div>
              </el-form-item>

              <el-form-item label="消费种类">
                <el-select
                  v-model="searchForm.type"
                  placeholder="全部类型"
                  style="width: 200px"
                  clearable
                >
                  <el-option
                    v-for="cat in expenseCategoryList"
                    :key="cat.category_id || cat.id"
                    :label="cat.name"
                    :value="cat.name"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="支付方式">
                <el-select
                  v-model="searchForm.paymentMethod"
                  placeholder="全部方式"
                  style="width: 200px"
                  clearable
                >
                  <el-option
                    v-for="method in paymentMethodList"
                    :key="method.method_id || method.id"
                    :label="method.name"
                    :value="method.name"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="消费金额">
                <el-input
                  v-model="searchForm.amount"
                  placeholder="请输入消费金额"
                  type="number"
                  min="0"
                  step="0.01"
                  style="width: 200px"
                  clearable
                  @keydown.down.prevent
                />
              </el-form-item>

              <el-form-item label="消费名称">
                <el-input
                  v-model="searchForm.name"
                  placeholder="请输入消费名称"
                  @blur="validateSearchInput('name', '消费名称')"
                  style="width: 200px"
                  clearable
                />
              </el-form-item>

              <el-form-item label="备注">
                <el-input
                  v-model="searchForm.remark"
                  placeholder="请输入备注"
                  @blur="validateSearchInput('remark', '备注')"
                  style="width: 200px"
                  clearable
                />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="handleSearch">搜索</el-button>
                <el-button @click="resetSearch">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- ========== 改造：操作按钮栏（和收入页面一致） ========== -->
          <div class="action-bar" style="margin: 0px 0">
            <el-button type="primary" icon="Plus" @click="handleAddRow">表格快速新增</el-button>
            <el-button type="success" icon="Download" @click="handleExportExpense"
              >导出数据</el-button
            >
            <el-button type="warning" icon="Delete" @click="handleBatchDelete">批量删除</el-button>
          </div>

          <!-- ========== 改造：支出记录表格（带分页+行内新增） ========== -->
          <div
            class="expense-table-container"
            style="background: #fff; padding: 20px; border-radius: 8px"
          >
            <el-table
              :data="pagedExpenseList"
              border
              stripe
              style="width: 100%; margin-bottom: 20px"
              @selection-change="handleSelectionChange"
            >
              <!-- 多选列 -->
              <el-table-column type="selection" width="55"></el-table-column>
              <!-- 序号列 -->
              <el-table-column prop="id" label="序号" width="80" align="center">
                <template #default="scope">
                  {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
                </template>
              </el-table-column>

              <!-- 日期列（可编辑） -->
              <el-table-column prop="time" label="日期" width="120" align="center">
                <template #default="scope">
                  <el-date-picker
                    v-if="scope.row.isEditing"
                    v-model="scope.row.time"
                    type="date"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                    placeholder="选择日期"
                  />
                  <span v-else>{{ scope.row.time }}</span>
                </template>
              </el-table-column>

              <!-- 消费种类列（可编辑，动态加载分类） -->
              <el-table-column prop="type" label="消费种类" width="150" align="center">
                <template #default="scope">
                  <el-select
                    v-if="scope.row.isEditing"
                    v-model="scope.row.type"
                    style="width: 100%"
                    placeholder="选择种类"
                    @change="handleCategoryChange(scope.row)"
                  >
                    <el-option
                      v-for="cat in expenseCategoryList"
                      :key="cat.id"
                      :label="cat.name"
                      :value="cat.name"
                    />
                  </el-select>
                  <el-tag v-else :type="getTagType(scope.row.type)">{{ scope.row.type }}</el-tag>
                </template>
              </el-table-column>

              <!-- 消费名称列（可编辑） -->
              <el-table-column prop="name" label="消费名称" min-width="120" align="center">
                <template #default="scope">
                  <el-input
                    v-if="scope.row.isEditing"
                    v-model="scope.row.name"
                    placeholder="输入名称"
                    style="width: 100%"
                    @blur="trimInputValue(scope.row, 'name')"
                  />
                  <span v-else>{{ scope.row.name }}</span>
                </template>
              </el-table-column>

              <!-- 消费金额列（可编辑） -->
              <el-table-column prop="money" label="消费金额(¥)" width="120" align="center">
                <template #default="scope">
                  <el-input
                    v-if="scope.row.isEditing"
                    v-model="scope.row.money"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="输入金额"
                    style="width: 100%"
                    @keydown.down.prevent
                  />
                  <span v-else style="color: #f44336; font-weight: 500"
                    >-{{ Number(scope.row.money).toFixed(2) }}</span
                  >
                </template>
              </el-table-column>

              <!-- 支付方式列（新增，可编辑） -->
              <el-table-column prop="paymentMethod" label="支付方式" width="120" align="center">
                <template #default="scope">
                  <el-select
                    v-if="scope.row.isEditing"
                    v-model="scope.row.paymentMethod"
                    style="width: 100%"
                    placeholder="选择支付方式"
                    @change="handlePaymentChange(scope.row)"
                  >
                    <el-option
                      v-for="method in paymentMethodList"
                      :key="method.method_id || method.id"
                      :label="method.name"
                      :value="method.name"
                    />
                  </el-select>
                  <span v-else>{{ scope.row.paymentMethod || '未设置' }}</span>
                </template>
              </el-table-column>

              <!-- 备注列（可编辑） -->
              <el-table-column prop="extra" label="备注" min-width="200" align="center">
                <template #default="scope">
                  <el-input
                    v-if="scope.row.isEditing"
                    v-model="scope.row.extra"
                    placeholder="输入备注（选填）"
                    style="width: 100%"
                    @blur="trimInputValue(scope.row, 'extra')"
                  />
                  <span v-else>{{ scope.row.extra || '无' }}</span>
                </template>
              </el-table-column>

              <!-- 操作列（新增保存/取消按钮） -->
              <el-table-column label="操作" width="220" align="center">
                <template #default="scope">
                  <template v-if="scope.row.isEditing">
                    <!-- 编辑状态：保存/取消 -->
                    <el-button type="success" size="small" @click="handleSaveRow(scope.row)"
                      >保存</el-button
                    >
                    <el-button type="info" size="small" @click="handleCancelRow(scope.row)"
                      >取消</el-button
                    >
                  </template>
                  <template v-else>
                    <!-- 正常状态：编辑/删除 -->
                    <el-button type="primary" size="small" @click="handleEditExpense(scope.row)"
                      >编辑</el-button
                    >
                    <el-button type="danger" size="small" @click="handleDeleteExpense(scope.row.id)"
                      >删除</el-button
                    >
                  </template>
                </template>
              </el-table-column>
            </el-table>

            <!-- 新增：分页控件（15条/页） -->
            <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page="currentPage"
              :page-sizes="[15, 20, 30, 50]"
              :page-size="pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalExpense"
              class="expense-pagination"
            >
            </el-pagination>
          </div>

          <!-- 移除原有重复页脚，保留统一页脚 -->
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as XLSX from 'xlsx'
// 导入API和工具类
import { getBillList, addBill, updateBill, deleteBill, batchDeleteBill, BillTransformer } from '@/api/bill'
import { CategoryMapper } from '@/api/category'
import { PaymentMethodMapper } from '@/api/payment'
import { useUserStore } from '@/stores/user'
import PageTagsNav from '@/components/PageTagsNav.vue'

// 路由跳转逻辑
const router = useRouter()

// 获取用户信息
const userStore = useUserStore()

const handleAvatarClick = () => {
  if (userStore.isLogin) {
    router.push('/settings')
  } else {
    router.push('/login')
  }
}

// 初始化映射器
const categoryMapper = new CategoryMapper()
const paymentMapper = new PaymentMethodMapper()
const isDataLoading = ref(false) // 数据加载状态

// 动态加载的分类和支付方式列表
const expenseCategoryList = ref([]) // 支出分类列表（用于下拉框）
const paymentMethodList = ref([]) // 支付方式列表（用于下拉框）

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
const handleJumpToSettings = () => {
  router.push('/settings')
}

// 搜索表单
const searchForm = ref({
  dateType: '',      // 筛选方式：day/month/year
  dateValue: '',     // 筛选值：YYYY-MM-DD / YYYY-MM / YYYY
  type: '', // 消费种类
  paymentMethod: '', // 支付方式
  amount: '', // 消费金额
  name: '', // 消费名称
  remark: '', // 备注
})

// 年份选项
const yearOptions = ref([])

// 初始化年份选项
const initYearOptions = () => {
  const currentYear = new Date().getFullYear()
  const years = []
  // 生成最近10年的选项（可根据需要调整）
  for (let i = 0; i < 10; i++) {
    years.push(currentYear - i)
  }
  yearOptions.value = years
}

// 筛选方式变化时的处理
const handleDateTypeChange = (newType) => {
  // 切换筛选方式时，清空原来的值
  searchForm.value.dateValue = ''

  // 根据选择的筛选方式，设置默认值
  if (newType) {
    const now = new Date()
    switch (newType) {
      case 'day':
        searchForm.value.dateValue = formatDate(now)
        break
      case 'month':
        searchForm.value.dateValue = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
        break
      case 'year':
        searchForm.value.dateValue = now.getFullYear().toString()
        break
    }
  }
}

// 日期格式化辅助函数
const formatDate = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// ========== 改造：支出列表数据（扩展为50条模拟数据，增加ID） ==========
const expenseList = ref([]) // 筛选后的数据
const originExpenseList = ref([]) // 原始数据副本
const totalExpense = ref(0)

// 图标映射（根据消费种类自动匹配）
const iconMap = {
  餐饮美食: 'Food',
  交通出行: 'Van',
  居住房租: 'House',
  购物消费: 'ShoppingTrolley',
  休闲娱乐: 'VideoPlay',
  医疗健康: 'FirstAidKit',
}

// ========== 新增：日期排序方法（核心修改） ==========
const sortDataByDate = (data) => {
  // 按time字段降序排列（新日期在前）
  return data.sort((a, b) => {
    return new Date(b.time) - new Date(a.time)
  })
}

// 初始化支出数据
const initExpenseData = async () => {
  // 如果用户未登录，使用模拟数据
  if (!userStore.isLogin) {
    console.warn('⚠️ 用户未登录，使用模拟数据')
    loadMockExpenseData()
    return
  }

  try {
    isDataLoading.value = true

    // 调用后端API获取支出列表（type=2 表示支出）
    const res = await getBillList({
      user_id: userStore.userId,
      page: currentPage.value,
      page_size: pageSize.value,
      type: 2  // 2 = 支出
    })

    if (res.code === 200 && res.data) {
      // 转换后端数据为前端格式
      const convertedData = res.data.map(billData => {
        const categoryName = categoryMapper.getExpenseCategoryName(billData.category_id) || '其他'
        const paymentMethodName = paymentMapper.getPaymentMethodName(billData.method_id) || '未知'

        const expenseData = BillTransformer.backendToExpense(billData, categoryName)

        // 添加前端需要的额外字段
        return {
          ...expenseData,
          bill_id: billData.id,  // 保存账单ID用于修改和删除
          category_id: billData.category_id,
          method_id: billData.method_id,
          paymentMethod: paymentMethodName,
          iconName: iconMap[categoryName] || 'Food'
        }
      })

      // 按日期降序排序
      const sortedData = sortDataByDate(convertedData)

      expenseList.value = sortedData
      originExpenseList.value = [...sortedData]
      totalExpense.value = res.total || sortedData.length

      console.log('✅ 支出数据加载成功:', sortedData.length, '条')
    } else {
      throw new Error('数据格式错误')
    }
  } catch (error) {
    console.error('❌ 支出数据加载失败:', error)
    ElMessage.error('加载支出数据失败，使用模拟数据')
    loadMockExpenseData()
  } finally {
    isDataLoading.value = false
  }
}

// 加载模拟数据（兜底方案）
const loadMockExpenseData = () => {
  // 生成50条模拟支出数据（测试分页）
  const mockData = []
  const types = ['餐饮美食', '交通出行', '居住房租', '购物消费', '休闲娱乐', '医疗健康']
  const names = [
    '早餐',
    '地铁费',
    '月租',
    '衣服',
    '电影票',
    '买药',
    '打车',
    '水电费',
    '奶茶',
    '健身房',
  ]
  const paymentMethods = ['微信', '支付宝', '现金', '银行卡']

  for (let i = 1; i <= 50; i++) {
    const randomTypeIdx = Math.floor(Math.random() * types.length)
    const randomType = types[randomTypeIdx]
    const randomIcon = iconMap[randomType]
    const randomName = names[Math.floor(Math.random() * names.length)]
    const randomMoney = (Math.random() * 5000 + 10).toFixed(2)
    const randomRemark = Math.random() > 0.7 ? '无' : `${randomName}消费`
    const randomPayment = paymentMethods[Math.floor(Math.random() * paymentMethods.length)]

    // 生成随机日期（近6个月）
    const date = new Date()
    date.setMonth(date.getMonth() - Math.floor(Math.random() * 6))
    date.setDate(Math.floor(Math.random() * 28) + 1)
    const formatDate = date.toISOString().split('T')[0]

    mockData.push({
      id: i,
      time: formatDate,
      iconName: randomIcon,
      type: randomType,
      category_id: randomTypeIdx + 1,
      name: randomName,
      money: randomMoney,
      paymentMethod: randomPayment,
      method_id: Math.floor(Math.random() * 4) + 1,
      extra: randomRemark,
      isEditing: false,
    })
  }

  const sortedData = sortDataByDate(mockData)
  expenseList.value = sortedData
  originExpenseList.value = [...sortedData]
  totalExpense.value = sortedData.length
}

// ========== 新增：表格行内新增相关方法 ==========
// 生成新ID（取当前最大ID+1）
const getNewId = () => {
  if (expenseList.value.length === 0) return 1
  const maxId = Math.max(...expenseList.value.map((item) => item.id))
  return maxId + 1
}

// 表格内新增空行
const handleAddRow = () => {
  const today = new Date()
  const formatDate = today.toISOString().split('T')[0]

  // 获取默认支付方式
  const defaultPaymentMethod = paymentMethodList.value.length > 0
    ? paymentMethodList.value[0].name
    : ''
  const defaultMethodId = paymentMapper.getDefaultPaymentMethodId() || 1

  // 新增空行数据（匹配后端需要的字段）
  const newRow = {
    id: getNewId(),
    time: formatDate,
    iconName: 'Food',
    type: '',
    category_id: null,  // 后端需要的分类ID
    name: '',
    money: '',
    paymentMethod: defaultPaymentMethod,  // 显示用的支付方式名称
    method_id: defaultMethodId,  // 后端需要的支付方式ID
    extra: '',
    isEditing: true,
  }

  // 添加到列表头部（方便编辑）
  expenseList.value.unshift(newRow)
  originExpenseList.value.unshift(newRow)
  totalExpense.value = expenseList.value.length
}

// 处理分类改变
const handleCategoryChange = (row) => {
  // 当用户选择分类时，自动设置 category_id
  if (row.type) {
    console.log('🔍 正在查找分类:', row.type)
    console.log('📋 当前支出分类列表:', expenseCategoryList.value)
    console.log('🗺️ 分类映射Map大小:', categoryMapper.expenseMap.size)
    console.log('🗺️ 映射内容:', Array.from(categoryMapper.expenseMap.entries()))

    // 尝试获取 category_id
    const categoryId = categoryMapper.getExpenseCategoryId(row.type)

    if (!categoryId) {
      // 如果映射中找不到，尝试从列表中查找
      const foundCategory = expenseCategoryList.value.find(cat => cat.name === row.type)
      if (foundCategory) {
        row.category_id = foundCategory.id
        console.log('⚠️ 映射中未找到，从列表中获取:', row.type, '-> category_id:', row.category_id)

        // 更新映射
        categoryMapper.expenseMap.set(row.type, foundCategory.id)
        categoryMapper.expenseIdMap.set(foundCategory.id, row.type)
        console.log('✅ 已更新映射')
      } else {
        console.error('❌ 分类不存在:', row.type)
        ElMessage.error(`分类"${row.type}"不存在，请刷新页面重试`)
        row.category_id = null
        return
      }
    } else {
      row.category_id = categoryId
    }

    // 根据分类自动匹配图标
    row.iconName = iconMap[row.type] || 'Food'

    console.log('✅ 分类已选择:', row.type, '-> category_id:', row.category_id)
  }
}

// 处理支付方式改变
const handlePaymentChange = (row) => {
  // 当用户选择支付方式时，自动设置 method_id
  if (row.paymentMethod) {
    row.method_id = paymentMapper.getPaymentMethodId(row.paymentMethod)
    console.log('✅ 支付方式已选择:', row.paymentMethod, '-> method_id:', row.method_id)
  }
}

// 保存编辑行（调用真实API）
const handleSaveRow = async (row) => {
  // 基础校验
  if (!row.time) {
    ElMessage.warning('请选择日期！')
    return
  }
  if (!row.type) {
    ElMessage.warning('请选择消费种类！')
    return
  }
  if (!row.name) {
    ElMessage.warning('请输入消费名称！')
    return
  }
  if (!row.money || Number(row.money) <= 0) {
    ElMessage.warning('请输入有效消费金额！')
    return
  }
  if (!row.paymentMethod) {
    ElMessage.warning('请选择支付方式！')
    return
  }

  // 确保 category_id 和 method_id 已设置
  if (!row.category_id) {
    row.category_id = categoryMapper.getExpenseCategoryId(row.type)
  }
  if (!row.method_id) {
    row.method_id = paymentMapper.getPaymentMethodId(row.paymentMethod)
  }

  // 最终校验：确保 ID 不为 null
  if (!row.category_id) {
    ElMessage.error('无法��取分类ID，请重新选择消费种类')
    console.error('❌ category_id 为空:', { type: row.type, category_id: row.category_id })
    return
  }
  if (!row.method_id) {
    ElMessage.error('无法获取支付方式ID，请重新选择支付方式')
    console.error('❌ method_id 为空:', { paymentMethod: row.paymentMethod, method_id: row.method_id })
    return
  }

  // 调试日志：显示即将发送的数据
  console.log('📤 准备保存账单:', {
    user_id: userStore.userId,
    category_id: row.category_id,
    method_id: row.method_id,
    name: row.name,
    amount: Number(row.money),
    type: row.type,
    paymentMethod: row.paymentMethod
  })

  // 根据消费种类自动匹配图标
  row.iconName = iconMap[row.type] || 'Food'
  // 格式化金额（保留2位小数）
  row.money = Number(row.money).toFixed(2)
  // 备注默认填空字符串
  row.extra = row.extra || ''

  // 判断是新增还是修改（根据是否有 bill_id）
  const isNew = !row.bill_id

  try {
    if (isNew) {
      // 新增账单
      await addBill({
        user_id: userStore.userId,
        category_id: row.category_id,
        method_id: row.method_id,
        name: row.name,
        amount: Number(row.money),
        bill_time: BillTransformer.formatDateTime(row.time),
        remark: row.extra || ''
      })
      ElMessage.success('新增支出成功！')
    } else {
      // 修改账单
      await updateBill({
        user_id: userStore.userId,
        bill_id: row.bill_id,
        category_id: row.category_id,
        method_id: row.method_id,
        name: row.name,
        amount: Number(row.money),
        bill_time: BillTransformer.formatDateTime(row.time),
        remark: row.extra || ''
      })
      ElMessage.success('修改支出成功！')
    }

    // 退出编辑状态
    row.isEditing = false

    // 重新加载数据
    await initExpenseData()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请重试')
  }
}

// 取消编辑行
const handleCancelRow = (row) => {
  // 如果是新增未保存的行（判断：金额为空）
  if (!row.money) {
    // 从列表中移除
    expenseList.value = expenseList.value.filter((item) => item.id !== row.id)
    originExpenseList.value = originExpenseList.value.filter((item) => item.id !== row.id)
    totalExpense.value = expenseList.value.length
  } else {
    // 已有数据的行：退出编辑状态
    row.isEditing = false
  }
}

// 分页相关逻辑
const currentPage = ref(1) // 当前页码
const pageSize = ref(15) // 每页条数（默认15条）
const selectedIds = ref([]) // 批量选择的支出ID
const isSearching = ref(false) // 搜索状态标志（区分正常浏览和搜索筛选）

// 分页后的数据（智能分页）
const pagedExpenseList = computed(() => {
  // 如果是搜索/筛选状态，使用前端分页
  if (isSearching.value) {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return expenseList.value.slice(start, end)
  }
  // 正常情况下，直接显示后端返回的当前页数据
  return expenseList.value
})

// 分页事件处理（调用后端API重新加载数据）
const handleSizeChange = async (val) => {
  pageSize.value = val
  currentPage.value = 1 // 切换每页条数时重置页码

  // 如果不是搜索状态，重新请求后端
  if (!isSearching.value) {
    await initExpenseData()
  }
}

const handleCurrentChange = async (val) => {
  currentPage.value = val

  // 如果不是搜索状态，重新请求后端
  if (!isSearching.value) {
    await initExpenseData()
  }
}

// 表格多选事件
const handleSelectionChange = (val) => {
  selectedIds.value = val.map((item) => item.id)
}

// ========== 新增：支出操作方法 ==========
// 消费类型标签颜色映射
const getTagType = (type) => {
  const typeMap = {
    餐饮美食: 'warning',
    交通出行: 'primary',
    居住房租: 'info',
    购物消费: 'success',
    休闲娱乐: 'danger',
    医疗健康: 'default',
  }
  return typeMap[type] || 'default'
}

// 新增支出（原有弹窗式新增，保留）
const handleAddExpense = () => {
  ElMessage.info('新增支出功能待实现（推荐使用表格快速新增）')
}

// 编辑支出（改为行内编辑）
const handleEditExpense = (row) => {
  row.isEditing = true
}

// 删除支出
const handleDeleteExpense = (id) => {
  ElMessageBox.confirm('此操作将永久删除该支出记录, 是否继续?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await deleteBill({
          user_id: userStore.userId,
          bill_id: id
        })
      ElMessage.success('删除成功！')
      expenseList.value = expenseList.value.filter((item) => item.id !== id)
      originExpenseList.value = originExpenseList.value.filter((item) => item.id !== id)
      totalExpense.value = expenseList.value.length
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 批量删除
const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }

  ElMessageBox.confirm(`此操作将永久删除选中的 ${selectedIds.value.length} 条支出记录, 是否继续?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        await batchDeleteBill({
          user_id: userStore.userId,
          bill_ids: selectedIds.value
        })
        ElMessage.success(`成功删除 ${selectedIds.value.length} 条记录！`)

        // 清空选中项
        selectedIds.value = []

        // 重新加载数据
        await initExpenseData()
      } catch (error) {
        console.error('批量删除失败:', error)
        ElMessage.error('批量删除失败，请重试')
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 导出数据功能
const handleExportExpense = () => {
  // 1. 准备导出数据：深拷贝避免修改原数据
  const exportData = JSON.parse(JSON.stringify(expenseList.value)).map((item) => {
    // 过滤掉不需要的字段
    const { isEditing, iconName, bill_id, category_id, method_id, ...rest } = item
    // 重命名字段（让Excel表头更友好）
    return {
      序号: rest.id,
      支出日期: rest.time,
      消费种类: rest.type,
      消费名称: rest.name,
      '消费金额(¥)': Number(rest.money).toFixed(2),
      支付方式: rest.paymentMethod || '未设置',
      备注: rest.extra || '无',
    }
  })

  // 2. 创建工作簿和工作表
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '支出记录')

  // 3. 调整列宽（优化Excel显示）
  const wscols = [
    { wch: 8 }, // 序号
    { wch: 15 }, // 支出日期
    { wch: 12 }, // 消费种类
    { wch: 15 }, // 消费名称
    { wch: 15 }, // 消费金额
    { wch: 12 }, // 支付方式
    { wch: 25 }, // 备注
  ]
  ws['!cols'] = wscols

  // 4. 生成文件名（带时间戳，避免重复）
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const filename = `支出记录_${year}${month}${day}.xlsx`

  // 5. 导出文件
  XLSX.writeFile(wb, filename)

  // 6. 提示用户
  ElMessage.success('支出数据导出成功！')
}

// 左侧菜单选择
const handleMenuSelect = (_key) => {
  // no-op
}
</script>

<style scoped>
@import '../styles/framework.css';
@import '../styles/finance-dashboard.css';

/* 支出管理页面专属样式 */
.expense-search-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.expense-table-container {
  margin-top: 20px;
}

/* 表格内编辑控件样式优化 */
:deep(.el-table .el-input),
:deep(.el-table .el-select),
:deep(.el-table .el-date-picker) {
  width: 100%;
}
</style>
