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
                    <el-button type="danger" size="small" @click="handleDeleteExpense(scope.row.bill_id)"
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
// 统一走后端导出
import { exportUserData } from '@/api/user'
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

// ✅ 补上挂载初始化：ExpendView 之前缺少 onMounted，导致分类/支付方式/账单数据都不会初始化
onMounted(async () => {
  // 检查用户是否登录
  if (!userStore.isLogin) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  initYearOptions()
  console.log('🔄 开始初始化支出页面数据...')

  try {
    await Promise.all([categoryMapper.init(), paymentMapper.init()])

    // 下拉数据
    expenseCategoryList.value = categoryMapper.expenseCategories
    paymentMethodList.value = paymentMapper.getPaymentMethodList()

    await initExpenseData()

    console.log('✅ 支出页面数据初始化完成')
  } catch (error) {
    console.error('❌ 支出页面数据初始化失败:', error)
    ElMessage.error('数据加载失败，请刷新页面重试')
  }
})

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

// 支出种类对应的 tag 样式
const getTagType = (type) => {
  const typeMap = {
    '餐饮美食': 'danger',
    '交通出行': 'warning',
    '居住房租': 'info',
    '购物消费': 'success',
    '休闲娱乐': 'primary',
    '医疗健康': 'danger',
    '其他': 'info',
  }
  return typeMap[type] || 'info'
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

  // 登录态刚恢复时可能 userId 还没就绪，下一拍重试
  if (!userStore.userId) {
    console.warn('⚠️ userId 为空，稍后重试初始化支出数据')
    setTimeout(() => initExpenseData().catch(() => {}), 0)
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

    if (res.code === 200 && Array.isArray(res.data)) {
      // 转换后端数据为前端格式
      const convertedData = res.data.map((billData, index) => {
        const categoryName = categoryMapper.getExpenseCategoryName(billData.category_id) || '其他'
        const paymentMethodName = paymentMapper.getPaymentMethodName(billData.method_id) || '未知'

        const expenseData = BillTransformer.backendToExpense(billData, categoryName)

        // ✅ 关键：row_id（前端行）与 bill_id（后端账单）分离
        return {
          ...expenseData,
          row_id: expenseData.id ?? index + 1,
          bill_id: billData.id,
          category_id: billData.category_id,
          method_id: billData.method_id,
          paymentMethod: paymentMethodName,
          iconName: iconMap[categoryName] || 'Food'
        }
      })

      // 按日期降序排序
      const sortedData = sortDataByDate(convertedData)

      // 分页越界处理
      const total = Number(res.total ?? sortedData.length)
      const maxPage = Math.max(1, Math.ceil(total / pageSize.value))
      if (currentPage.value > maxPage) {
        currentPage.value = 1
        await initExpenseData()
        return
      }

      expenseList.value = sortedData
      originExpenseList.value = [...sortedData]
      totalExpense.value = total

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
      row_id: i,
      id: i,
      bill_id: null,
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

// 2. 分页相关（✅ ExpendView 之前缺失这组状态，模板和 initExpenseData 会直接 ReferenceError 导致页面无法加载）
const currentPage = ref(1) // 当前页码
const pageSize = ref(15) // 每页条数（默认15条）
const selectedIds = ref([]) // 批量选择的后端 bill_id 数组
const isSearching = ref(false) // 搜索状态标志（区分正常浏览和搜索筛选）

// 4. 分页后的数据（后端已返回当前页时直接用 expenseList；搜索时前端 slice）
const pagedExpenseList = computed(() => {
  if (isSearching.value) {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return expenseList.value.slice(start, end)
  }
  return expenseList.value
})

// 5. 分页事件处理（非搜索时请求后端重新加载）
const handleSizeChange = async (val) => {
  pageSize.value = val
  currentPage.value = 1
  if (!isSearching.value) {
    await initExpenseData()
  }
}

const handleCurrentChange = async (val) => {
  currentPage.value = val
  if (!isSearching.value) {
    await initExpenseData()
  }
}

// 表格多选事件
const handleSelectionChange = (val) => {
  // ✅ 批量删除使用 bill_id；未保存的行没有 bill_id，过滤掉
  selectedIds.value = val.map((item) => item.bill_id).filter((v) => !!v)
}

// ========== 新增：行内新增/保存/删除相关 ==========

const getNewRowId = () => {
  const ids = expenseList.value.map((x) => Number(x.row_id || x.id || 0)).filter((n) => !Number.isNaN(n))
  return (ids.length ? Math.max(...ids) : 0) + 1
}

const handleAddRow = () => {
  const today = new Date().toISOString().split('T')[0]

  const defaultPaymentMethod = paymentMethodList.value.length > 0 ? paymentMethodList.value[0].name : ''
  const defaultMethodId = defaultPaymentMethod ? paymentMapper.getPaymentMethodId(defaultPaymentMethod) : (paymentMapper.getDefaultPaymentMethodId?.() || 1)

  const newRow = {
    row_id: getNewRowId(),
    id: getNewRowId(),
    bill_id: null,
    time: today,
    type: '',
    category_id: null,
    name: '',
    money: '',
    paymentMethod: defaultPaymentMethod,
    method_id: defaultMethodId,
    extra: '',
    iconName: 'Food',
    isEditing: true,
  }

  expenseList.value.unshift(newRow)
  originExpenseList.value.unshift(newRow)
  totalExpense.value = expenseList.value.length
  currentPage.value = 1
}

const handleCategoryChange = (row) => {
  if (!row?.type) return
  row.category_id = categoryMapper.getExpenseCategoryId(row.type)
  row.iconName = iconMap[row.type] || row.iconName || 'Food'
}

const handlePaymentChange = (row) => {
  if (!row?.paymentMethod) return
  row.method_id = paymentMapper.getPaymentMethodId(row.paymentMethod)
}

const handleSaveRow = async (row) => {
  if (!userStore.isLogin) {
    ElMessage.warning('请先登录')
    return
  }

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

  // 确保 id 已同步
  if (!row.category_id) row.category_id = categoryMapper.getExpenseCategoryId(row.type)
  if (!row.method_id) row.method_id = paymentMapper.getPaymentMethodId(row.paymentMethod)

  try {
    const isNew = !row.bill_id
    const payload = {
      user_id: userStore.userId,
      category_id: row.category_id,
      method_id: row.method_id,
      name: row.name,
      amount: Number(Number(row.money).toFixed(2)),
      bill_time: BillTransformer.formatDateTime(row.time),
      remark: row.extra || ''
    }

    if (isNew) {
      await addBill(payload)
      ElMessage.success('新增支出成功！')
    } else {
      await updateBill({
        ...payload,
        bill_id: row.bill_id,
      })
      ElMessage.success('修改支出成功！')
    }

    row.isEditing = false
    await initExpenseData()
  } catch (error) {
    console.error('保存支出失败:', error)
    ElMessage.error('保存失败，请重试')
  }
}

// 编辑支出（行内编辑）
const handleEditExpense = (row) => {
  // 保存原始数据用于取消编辑
  row._originalData = { ...row }
  row.isEditing = true
}

const handleDeleteExpense = async (billId) => {
  if (!billId) {
    ElMessage.warning('该行尚未保存，无法删除')
    return
  }

  try {
    await ElMessageBox.confirm('此操作将永久删除该支出记录, 是否继续?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await deleteBill({
      user_id: userStore.userId,
      bill_id: billId,
    })

    ElMessage.success('删除成功！')
    await initExpenseData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

// 取消编辑（恢复原始数据）
const handleCancelRow = (row) => {
  if (row._originalData) {
    // 恢复原始数据
    Object.assign(row, row._originalData)
    // 清除保存的原始数据
    delete row._originalData
  }
  row.isEditing = false
}

const handleBatchDelete = async () => {
  if (!selectedIds.value.length) {
    ElMessage.warning('请选择要删除的记录')
    return
  }

  try {
    await ElMessageBox.confirm(`此操作将永久删除选中的 ${selectedIds.value.length} 条支出记录, 是否继续?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await batchDeleteBill({
      user_id: userStore.userId,
      bill_ids: selectedIds.value,
    })

    ElMessage.success(`成功删除 ${selectedIds.value.length} 条记录！`)
    selectedIds.value = []
    await initExpenseData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败，请重试')
    }
  }
}

// 搜索表单验证函数
const validateSearchInput = (field, fieldName) => {
  const value = searchForm.value[field]
  if (typeof value === 'string' && value.trim() === '') {
    ElMessage.warning({
      message: `${fieldName}不能只输入空格，已自动清空`,
      duration: 2000,
      showClose: true
    })
    searchForm.value[field] = ''
  }
}

// 自动修剪首尾空格（当输入框失去焦点时）
const trimInputValue = (row, field) => {
  if (!row[field]) return
  if (typeof row[field] !== 'string') return

  const originalValue = row[field]
  const trimmedValue = originalValue.trim()
  if (originalValue !== trimmedValue) {
    row[field] = trimmedValue
  }
}

// 搜索/筛选（前端筛选 originExpenseList）
const handleSearch = () => {
  currentPage.value = 1
  isSearching.value = true

  let filteredData = JSON.parse(JSON.stringify(originExpenseList.value))

  // 1) 动态日期筛选
  if (searchForm.value.dateType && searchForm.value.dateValue) {
    const { dateType, dateValue } = searchForm.value

    if (dateType === 'day') {
      filteredData = filteredData.filter((item) => item.time === dateValue)
    } else if (dateType === 'month') {
      filteredData = filteredData.filter((item) => (item.time || '').startsWith(dateValue))
    } else if (dateType === 'year') {
      filteredData = filteredData.filter((item) => (item.time || '').startsWith(dateValue))
    }
  }

  // 2) 消费种类
  if (searchForm.value.type) {
    filteredData = filteredData.filter((item) => item.type === searchForm.value.type)
  }

  // 3) 支付方式
  if (searchForm.value.paymentMethod) {
    filteredData = filteredData.filter((item) => item.paymentMethod === searchForm.value.paymentMethod)
  }

  // 4) 金额（允许 money 为 string/number）
  if (searchForm.value.amount) {
    const target = Number(searchForm.value.amount)
    filteredData = filteredData.filter((item) => Math.abs(Number(item.money) - target) < 0.01)
  }

  // 5) 消费名称（模糊）
  if (searchForm.value.name) {
    const keyword = searchForm.value.name.trim()
    filteredData = filteredData.filter((item) => (item.name || '').includes(keyword))
  }

  // 6) 备注（模糊；"无" 特判）
  if (searchForm.value.remark) {
    const keyword = searchForm.value.remark.trim().toLowerCase()
    if (keyword === '无') {
      filteredData = filteredData.filter((item) => {
        const v = item.extra || ''
        return v === '' || v === '无'
      })
    } else {
      filteredData = filteredData.filter((item) => ((item.extra || '').toLowerCase()).includes(keyword))
    }
  }

  const sorted = sortDataByDate(filteredData)
  expenseList.value = sorted
  totalExpense.value = sorted.length
}

// 重置搜索
const resetSearch = async () => {
  searchForm.value = {
    dateType: '',
    dateValue: '',
    type: '',
    paymentMethod: '',
    amount: '',
    name: '',
    remark: '',
  }

  isSearching.value = false
  currentPage.value = 1

  await initExpenseData()
}

// 统一下载文件名解析（与设置页一致）
const getDownloadFilename = (disposition, fallbackName) => {
  if (!disposition) return fallbackName
  const match = /filename=([^;]+)/i.exec(disposition)
  if (!match) return fallbackName
  return match[1].replace(/\"/g, '').trim() || fallbackName
}

// 支出页：导出数据（统一导出全量用户数据，字段由后端控制，包含支付方式等）
const handleExportExpense = async () => {
  try {
    if (!userStore.isLogin) {
      ElMessage.warning('请先登录')
      return
    }

    ElMessage.info('开始导出数据，请稍候...')

    const response = await exportUserData('xlsx')
    const blob = response.data

    const fallbackName = `finance_export_${new Date().toISOString().split('T')[0]}.xlsx`
    const filename = getDownloadFilename(response.headers['content-disposition'], fallbackName)

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('数据导出成功！文件已下载')
  } catch (error) {
    console.error('导出数据失败:', error)
    ElMessage.error('数据导出失败，请稍后重试')
  }
}

// 左侧菜单选择：不再维护页面内标签数组，标签页由全局 store 自动维护
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
