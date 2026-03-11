<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <div class="top-nav" style="position: fixed; left: 30px">
      <div class="logo">MyFinancePal</div>
      <div class="breadcrumb">仪表盘 / 收入管理</div>
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

          <el-menu-item
            index="Coin"
            @click="handleJumpToCoin()"
            style="color: rgb(64, 158, 255) !important"
          >
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

        <div class="menu-management-panel">
          <!-- ========== 新增：收入管理主体内容 ========== -->
          <!-- 1. 搜索与筛选栏 -->
          <div class="search-bar" style="margin-bottom: 20px">
            <el-form :inline="true" :model="searchForm" class="income-search-form">
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

              <!-- 修复点2：收入类型字段绑定匹配 searchForm.type -->
              <el-form-item label="收入类型">
                <el-select
                  v-model="searchForm.type"
                  placeholder="全部类型"
                  style="width: 200px"
                  clearable
                >
                  <el-option label="工资" value="工资"></el-option>
                  <el-option label="理财收益" value="理财收益"></el-option>
                  <el-option label="兼职收入" value="兼职收入"></el-option>
                  <el-option label="奖金" value="奖金"></el-option>
                  <el-option label="其他" value="其他"></el-option>
                </el-select>
              </el-form-item>

              <!-- 支付方式筛选（新增） -->
              <el-form-item label="支付方式">
                <el-select
                  v-model="searchForm.paymentMethod"
                  placeholder="全部方式"
                  style="width: 200px"
                  clearable
                >
                  <el-option
                    v-for="method in paymentMethodList"
                    :key="method.method_id"
                    :label="method.name"
                    :value="method.name"
                  />
                </el-select>
              </el-form-item>

              <!-- 修复点3：移除错误的 handleMoneyInput 调用，字段匹配 searchForm.amount -->
              <el-form-item label="收入金额">
                <el-input
                  v-model="searchForm.amount"
                  placeholder="请输入收入金额"
                  type="number"
                  min="0"
                  step="0.01"
                  style="width: 200px"
                  @keydown.down.prevent
                ></el-input>
              </el-form-item>

              <el-form-item label="收入来源">
                <el-input
                  v-model="searchForm.source"
                  placeholder="请输入收入来源"
                  @blur="validateSearchInput('source', '收入来源')"
                />
              </el-form-item>

              <!-- 修复点4：备注标签规范化，移除无效的 word-limit-format 属性 -->
              <el-form-item label="备&nbsp&nbsp&nbsp注" label-width="75px">
                <el-input
                  v-model="searchForm.remark"
                  placeholder="无"
                  maxlength="80"
                  show-word-limit
                  style="width: 100%"
                  @blur="validateSearchInput('remark', '备注')"
                />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="handleSearch">搜索</el-button>
                <el-button @click="resetSearch">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 2. 操作按钮栏 -->
          <div class="action-bar" style="margin-bottom: 0px">
            <el-button type="primary" icon="Plus" @click="handleAddRow">表格快速新增</el-button>
            <el-button type="success" icon="Download" @click="handleExportIncome"
              >导出数据</el-button
            >
            <el-button type="warning" icon="Delete" @click="handleBatchDelete">批量删除</el-button>
          </div>

          <!-- 3. 收入记录表格 -->
          <div
            class="income-table-container"
            style="background: #fff; padding: 20px; border-radius: 8px"
          >
            <!-- 表格 -->
            <el-table
              :data="pagedIncomeList"
              border
              stripe
              style="width: 100%; margin-bottom: 20px"
              @selection-change="handleSelectionChange"
            >
              <el-table-column type="selection" width="55"></el-table-column>
              <el-table-column prop="id" label="序号" width="80" align="center">
                <template #default="scope">
                  {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
                </template>
              </el-table-column>

              <!-- 收入日期列（可编辑） -->
              <el-table-column prop="date" label="收入日期" width="120" align="center">
                <template #default="scope">
                  <el-date-picker
                    v-if="scope.row.isEditing"
                    v-model="scope.row.date"
                    type="date"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                    placeholder="选择日期"
                    :locale="zhCn"
                  />
                  <span v-else>{{ scope.row.date }}</span>
                </template>
              </el-table-column>

              <!-- 收入类型列（可编辑，动态加载分类） -->
              <el-table-column prop="ctype" label="收入类型" width="150" align="center">
                <template #default="scope">
                  <el-select
                    v-if="scope.row.isEditing"
                    v-model="scope.row.ctype"
                    style="width: 100%"
                    placeholder="选择类型"
                    @change="handleCategoryChange(scope.row)"
                  >
                    <el-option
                      v-for="cat in incomeCategoryList"
                      :key="cat.category_id"
                      :label="cat.name"
                      :value="cat.name"
                    />
                  </el-select>
                  <el-tag v-else :type="getTagType(scope.row.ctype)">{{ scope.row.ctype }}</el-tag>
                </template>
              </el-table-column>

              <!-- 收入金额列（可编辑） -->
              <el-table-column prop="amount" label="收入金额(¥)" width="120" align="center">
                <template #default="scope">
                  <el-input
                    v-if="scope.row.isEditing"
                    v-model="scope.row.amount"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="输入金额"
                    style="width: 100%"
                    @keydown.down.prevent
                  />
                  <span v-else style="color: #4caf50; font-weight: 500"
                    >+{{ Number(scope.row.amount).toFixed(2) }}</span
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
                      :key="method.method_id"
                      :label="method.name"
                      :value="method.name"
                    />
                  </el-select>
                  <span v-else>{{ scope.row.paymentMethod || '未设置' }}</span>
                </template>
              </el-table-column>

              <!-- 收入来源列（可编辑） -->
              <el-table-column prop="source" label="收入来源" min-width="150">
                <template #default="scope">
                  <el-input
                    v-if="scope.row.isEditing"
                    v-model="scope.row.source"
                    placeholder="输入来源"
                    style="width: 100%"
                    @blur="trimInputValue(scope.row, 'source')"
                  />
                  <span v-else>{{ scope.row.source }}</span>
                </template>
              </el-table-column>

              <!-- 备注列（可编辑） -->
              <el-table-column prop="remark" label="备注" min-width="200">
                <template #default="scope">
                  <el-input
                    v-if="scope.row.isEditing"
                    v-model="scope.row.remark"
                    placeholder="输入备注（选填）"
                    style="width: 100%"
                    @blur="trimInputValue(scope.row, 'remark')"
                  />
                  <span v-else>{{ scope.row.remark || '无' }}</span>
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
                    <el-button type="primary" size="small" @click="handleEditIncome(scope.row)"
                      >编辑</el-button
                    >
                    <el-button type="danger" size="small" @click="handleDeleteIncome(scope.row.bill_id)"
                      >删除</el-button
                    >
                  </template>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页控件 -->
            <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page="currentPage"
              :page-sizes="[15, 20, 30, 50]"
              :page-size="pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalIncome"
              style="text-align: right"
            >
            </el-pagination>
          </div>
          <!-- ========== 新增结束 ========== -->

          <!-- 页脚 -->
          <footer class="dashboard-footer">
            <p>© 2026 财智管家 - 个人财务管理系统 | 数据安全加密存储</p>
          </footer>
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
// 修复点6：导入 ElMessage/ElMessageBox 组件
import { ElMessage, ElMessageBox } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
// 移除前端本地 xlsx 导出，统一走后端 /user/export
import { exportUserData } from '@/api/user'
// ========== 导入API和工具类 ==========
import { getBillList, addBill, updateBill, deleteBill, batchDeleteBill, BillTransformer } from '@/api/bill'
import { CategoryMapper } from '@/api/category'
import { PaymentMethodMapper } from '@/api/payment'
import { useUserStore } from '@/stores/user'
import PageTagsNav from '@/components/PageTagsNav.vue'

// 路由跳转逻辑
const router = useRouter()

// ==========  获取用户信息 ==========
const userStore = useUserStore()

const handleAvatarClick = () => {
  if (userStore.isLogin) {
    router.push('/settings')
  } else {
    router.push('/login')
  }
}

// ========== 初始化映射器 ==========
const categoryMapper = new CategoryMapper()
const paymentMapper = new PaymentMethodMapper()
const isDataLoading = ref(false) // 数据加载状态

// ========== 动态加载的分类和支付方式列表 ==========
const incomeCategoryList = ref([]) // 收入分类列表（用于下拉框）
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

// ========== 页面挂载初始化 ==========
onMounted(async () => {
  // 检查用户是否登录
  if (!userStore.isLogin) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  initYearOptions() // 初始化年份选择器

  // 初始化分类和支付方式映射
  console.log('🔄 开始初始化收入页面数据...')

  try {
    // 并行初始化分类和支付方式映射
    await Promise.all([
      categoryMapper.init(),
      paymentMapper.init()
    ])

    console.log('✅ 分类和支付方式映射初始化成功')

    // 获取分类和支付方式列表（用于下拉框）
    incomeCategoryList.value = categoryMapper.incomeCategories
    paymentMethodList.value = paymentMapper.getPaymentMethodList()

    // 初始化收入数据（从后端加载）
    await initIncomeData()

    console.log('✅ 收入页面数据初始化完成')
  } catch (error) {
    console.error('❌ 收入数据初始化失败:', error)
    ElMessage.error('数据加载失败，请刷新页面重试')
  }
})


// 左侧菜单选择：不再维护页面内标签数组，标签页由全局 store 自动维护
const handleMenuSelect = (_key) => {
  // no-op
}

// 修复点8：搜索表单字段与模板匹配（删除冗余的min/maxAmount，新增date/source/remark/paymentMethod）
const searchForm = ref({
  dateType: '',      // 筛选方式：day/month/year
  dateValue: '',     // 筛选值：YYYY-MM-DD / YYYY-MM / YYYY
  type: '', // 收入类型
  paymentMethod: '', // 支付方式（新增）
  amount: '', // 收入金额
  source: '', // 收入来源
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

// 2. 分页相关
const currentPage = ref(1) // 当前页码
const pageSize = ref(15) // 每页条数（默认15条）
const selectedIds = ref([]) // 批量选择的ID
const isSearching = ref(false) // 搜索状态标志（区分正常浏览和搜索筛选）

// 3. 模拟收入数据（关键修复：提前声明 originIncomeList）
const incomeList = ref([]) // 筛选后的数据
const originIncomeList = ref([]) // 原始数据（永久保存）
const totalIncome = ref(0)

// ========== 新增：日期排序方法（核心修改） ==========
const sortDataByDate = (data) => {
  // 按date字段降序排列（新日期在前）
  return data.sort((a, b) => {
    return new Date(b.date) - new Date(a.date)
  })
}

// ==========  修改为从后端加载真实数据 ==========
// 初始化收入数据
const initIncomeData = async () => {
  // 如果用户未登录，使用模拟数据
  if (!userStore.isLogin) {
    console.warn('⚠️ 用户未登录，使用模拟数据')
    loadMockIncomeData()
    return
  }

  try {
    isDataLoading.value = true

    // 调用后端API获取收入列表（type=1 表示收入）
    // 不传递 the_time 参数，获取所有数据
    const res = await getBillList({
      user_id: userStore.userId,
      page: currentPage.value,
      page_size: pageSize.value,
      type: 1  // 1 = 收入
    })

    if (res.code === 200 && res.data) {
      // 转换后端数据为前端格式
      const convertedData = res.data.map(billData => {
        const categoryName = categoryMapper.getIncomeCategoryName(billData.category_id) || '其他'
        const paymentMethodName = paymentMapper.getPaymentMethodName(billData.method_id) || '未知'

        const incomeData = BillTransformer.backendToIncome(billData, categoryName)

        // 添加前端需要的额外字段
        return {
          ...incomeData,
          bill_id: billData.id,  // 保存账单ID用于修改和删除
          category_id: billData.category_id,
          method_id: billData.method_id,
          paymentMethod: paymentMethodName
        }
      })

      // 按日期降序排序
      const sortedData = sortDataByDate(convertedData)

      incomeList.value = sortedData
      originIncomeList.value = [...sortedData]
      totalIncome.value = res.total || sortedData.length

      console.log('✅ 收入数据加载成功:', sortedData.length, '条')
    } else {
      throw new Error('数据格式错误')
    }
  } catch (error) {
    console.error('❌ 收入数据加载失败:', error)
    ElMessage.error('加载收入数据失败，使用模拟数据')
    loadMockIncomeData()
  } finally {
    isDataLoading.value = false
  }
}

// 加载模拟数据（兜底方案）
const loadMockIncomeData = () => {
  // 生成模拟数据（50条，用于测试分页）
  const mockData = []
  const types = ['工资', '理财收益', '兼职收入', '奖金', '其他']
  const sources = ['公司打卡', '支付宝理财', '副业接单', '年终奖金', '亲友转账', '稿费', '投资分红']
  const remarks = ['', '本月绩效奖金', '加班补贴', '理财到期收益', '兼职设计费用', '无备注']
  const paymentMethods = ['微信', '支付宝', '现金', '银行卡']

  for (let i = 1; i <= 50; i++) {
    const randomTypeIdx = Math.floor(Math.random() * types.length)
    const randomType = types[randomTypeIdx]
    const randomSource = sources[Math.floor(Math.random() * sources.length)]
    const randomRemark = remarks[Math.floor(Math.random() * remarks.length)]
    const randomAmount = (Math.random() * 10000 + 100).toFixed(2)
    const randomPayment = paymentMethods[Math.floor(Math.random() * paymentMethods.length)]

    // 生成随机日期（近6个月）
    const date = new Date()
    date.setMonth(date.getMonth() - Math.floor(Math.random() * 6))
    date.setDate(Math.floor(Math.random() * 28) + 1)
    const formatDate = date.toISOString().split('T')[0]

    mockData.push({
      id: i,
      date: formatDate,
      ctype: randomType,
      category_id: randomTypeIdx + 1,
      amount: Number(randomAmount),
      source: randomSource,
      paymentMethod: randomPayment,
      method_id: Math.floor(Math.random() * 4) + 1,
      remark: randomRemark,
      isEditing: false,
    })
  }

  const sortedData = sortDataByDate(mockData)
  incomeList.value = sortedData
  originIncomeList.value = [...sortedData]
  totalIncome.value = sortedData.length
}

// ========== 新增：表格行内新增相关方法 ==========
// 生成新ID（取当前最大ID+1）
const getNewId = () => {
  if (incomeList.value.length === 0) return 1
  const maxId = Math.max(...incomeList.value.map((item) => item.id))
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
    date: formatDate,
    ctype: '',
    category_id: null,  // 后端需要的分类ID
    amount: '',
    source: '',
    paymentMethod: defaultPaymentMethod,  // 显示用的支付方式名称
    method_id: defaultMethodId,  // 后端需要的支付方式ID
    remark: '',
    isEditing: true,
  }

  // 添加到列表头部（方便编辑）
  incomeList.value.unshift(newRow)
  originIncomeList.value.unshift(newRow)
  totalIncome.value = incomeList.value.length
  currentPage.value = 1
}

// ========== 处理分类改变 ==========
const handleCategoryChange = (row) => {
  // 当用户选择分类时，自动设置 category_id
  if (row.ctype) {
    row.category_id = categoryMapper.getIncomeCategoryId(row.ctype)
  }
}

// ========== 处理支付方式改变 ==========
const handlePaymentChange = (row) => {
  // 当用户选择支付方式时，自动设置 method_id
  if (row.paymentMethod) {
    row.method_id = paymentMapper.getPaymentMethodId(row.paymentMethod)
  }
}

// 保存编辑行（调用真实API）
const handleSaveRow = async (row) => {
  // 基础校验
  if (!row.date) {
    ElMessage.warning('请选择收入日期！')
    return
  }
  if (!row.ctype) {
    ElMessage.warning('请选择收入类型！')
    return
  }
  if (!row.amount || Number(row.amount) <= 0) {
    ElMessage.warning('请输入有效收入金额！')
    return
  }
  if (!row.source) {
    ElMessage.warning('请输入收入来源！')
    return
  }
  if (!row.paymentMethod) {
    ElMessage.warning('请选择支付方式！')
    return
  }

  // 确保 category_id 和 method_id 已设置
  if (!row.category_id) {
    row.category_id = categoryMapper.getIncomeCategoryId(row.ctype)
  }
  if (!row.method_id) {
    row.method_id = paymentMapper.getPaymentMethodId(row.paymentMethod)
  }

  // 格式化金额（保留2位小数）
  row.amount = Number(row.amount).toFixed(2)
  // 备注默认填空字符串
  row.remark = row.remark || ''

  // 判断是新增还是修改（根据是否有 bill_id）
  const isNew = !row.bill_id

  try {
    if (isNew) {
      // 新增账单
      await addBill({
        user_id: userStore.userId,
        category_id: row.category_id,
        method_id: row.method_id,
        name: row.source,  // 收入来源作为账单名称
        amount: Number(row.amount),
        bill_time: BillTransformer.formatDateTime(row.date),
        remark: row.remark || ''
      })
      ElMessage.success('新增收入成功！')
    } else {
      // 修改账单
      await updateBill({
        user_id: userStore.userId,
        bill_id: row.bill_id,
        category_id: row.category_id,
        method_id: row.method_id,
        name: row.source,
        amount: Number(row.amount),
        bill_time: BillTransformer.formatDateTime(row.date),
        remark: row.remark || ''
      })
      ElMessage.success('修改收入成功！')
    }

    // 退出编辑状态
    row.isEditing = false

    // 重新加载数据
    await initIncomeData()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请重试')
  }
}

// 取消编辑行
const handleCancelRow = (row) => {
  // 如果是新增未保存的行（判断：金额为空）
  if (!row.amount) {
    // 从列表中移除
    incomeList.value = incomeList.value.filter((item) => item.id !== row.id)
    originIncomeList.value = originIncomeList.value.filter((item) => item.id !== row.id)
    totalIncome.value = incomeList.value.length
  } else {
    // 已有数据的行：退出编辑状态
    row.isEditing = false
  }
}

// 4. 分页后的数据（直接显示 incomeList，因为后端已返回当前页数据）
const pagedIncomeList = computed(() => {
  // 如果是搜索/筛选状态，使用前端分页
  if (isSearching.value) {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return incomeList.value.slice(start, end)
  }
  // 正常情况下，直接显示后端返回的当前页数据
  return incomeList.value
})

// 5. 分页事件处理（调用后端API重新加载数据）
const handleSizeChange = async (val) => {
  pageSize.value = val
  currentPage.value = 1 // 切换每页条数时重置页码

  // 如果是搜索状态，不重新请求后端
  if (!isSearching.value) {
    await initIncomeData()
  }
}

const handleCurrentChange = async (val) => {
  currentPage.value = val

  // 如果是搜索状态，不重新请求后端
  if (!isSearching.value) {
    await initIncomeData()
  }
}

// 修复点9：完善搜索逻辑（关键修复：使用 originIncomeList 作为数据源 + 排序）
const handleSearch = () => {
  console.log('搜索条件：', searchForm.value)
  // 重置页码
  currentPage.value = 1
  // 设置为搜索状态
  isSearching.value = true

  // 关键修复：从原始数据拷贝，而非筛选后的数据
  let filteredData = JSON.parse(JSON.stringify(originIncomeList.value))

  // 1.  ========== 动态日期筛选逻辑 ==========
  if (searchForm.value.dateType && searchForm.value.dateValue) {
    const dateType = searchForm.value.dateType
    const dateValue = searchForm.value.dateValue

    switch (dateType) {
      case 'day':
        // 按日筛选
        filteredData = filteredData.filter((item) => item.date === dateValue)
        break

      case 'month':
        // 按月筛选
        filteredData = filteredData.filter((item) => {
          return item.date.startsWith(dateValue) // YYYY-MM 开头
        })
        break

      case 'year':
        // 按年筛选
        filteredData = filteredData.filter((item) => {
          return item.date.startsWith(dateValue) // YYYY 开头
        })
        break
    }
  }

  // 2. 收入类型筛选
  if (searchForm.value.type) {
    filteredData = filteredData.filter((item) => item.ctype === searchForm.value.type)
  }

  // 3. 支付方式筛选（新增）
  if (searchForm.value.paymentMethod) {
    filteredData = filteredData.filter((item) => item.paymentMethod === searchForm.value.paymentMethod)
  }

  // 4. 收入金额筛选（精确匹配）
  if (searchForm.value.amount) {
    const targetAmount = Number(searchForm.value.amount)
    filteredData = filteredData.filter(
      (item) => Math.abs(Number(item.amount) - targetAmount) < 0.01,
    )
  }

  // 5. 收入来源筛选（模糊匹配）
  if (searchForm.value.source) {
    const keyword = searchForm.value.source.trim()
    filteredData = filteredData.filter((item) => item.source.includes(keyword))
  }

  // 6. 备注筛选（模糊匹配 - 优化版）
  if (searchForm.value.remark) {
    const keyword = searchForm.value.remark.trim().toLowerCase()

    // 如果用户搜索"无"，则查找备注为空或为"无"的记录
    if (keyword === '无') {
      filteredData = filteredData.filter((item) => {
        const remarkValue = item.remark || ''
        return remarkValue === '' || remarkValue === '无'
      })
    } else {
      // 普通模糊匹配（大小写不敏感）
      filteredData = filteredData.filter((item) => {
        const remarkValue = (item.remark || '').toLowerCase()
        return remarkValue.includes(keyword)
      })
    }
  }

  // ========== 核心修改：搜索结果按日期降序排列 ==========
  const sortedFilteredData = sortDataByDate(filteredData)

  // 更新筛选后的数据
  incomeList.value = sortedFilteredData
  totalIncome.value = sortedFilteredData.length
}

// 修复点10：重置搜索表单（关键修复：恢复原始数据 + 排序）
const resetSearch = async () => {
  searchForm.value = {
    dateType: '',
    dateValue: '',
    type: '',
    paymentMethod: '',
    amount: '',
    source: '',
    remark: '',
  }

  // 清除搜索状态
  isSearching.value = false
  currentPage.value = 1

  // 重新从后端加载数据
  await initIncomeData()
}

// 7. 表格选择事件
const handleSelectionChange = (val) => {
  selectedIds.value = val.map((item) => item.id)
}

// 8. 标签类型映射（用于表格中收入类型的标签颜色）
const getTagType = (type) => {
  const typeMap = {
    工资: 'primary',
    理财收益: 'success',
    兼职收入: 'warning',
    奖金: 'info',
    其他: 'default',
  }
  return typeMap[type] || 'default'
}

// 编辑收入（改为行内编辑）
const handleEditIncome = (row) => {
  // 保存原始数据用于取消编辑
  row._originalData = { ...row }
  row.isEditing = true
}

const handleDeleteIncome = (billId) => {
  // 删除收入逻辑（调用真实API）
  ElMessageBox.confirm('此操作将永久删除该收入记录, 是否继续?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        await deleteBill({
          user_id: userStore.userId,
          bill_id: billId
        })
        ElMessage.success('删除成功！')
        incomeList.value = incomeList.value.filter((item) => item.id !== billId)
        originIncomeList.value = originIncomeList.value.filter((item) => item.id !== billId)
        totalIncome.value = incomeList.value.length
      } catch (error) {
        console.error('删除失败:', error)
        ElMessage.error('删除失败，请重试')
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

const handleBatchDelete = () => {
  // 批量删除逻辑（调用真实API）
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }

  ElMessageBox.confirm(`此操作将永久删除选中的 ${selectedIds.value.length} 条收入记录, 是否继续?`, '提示', {
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
        await initIncomeData()
      } catch (error) {
        console.error('批量删除失败:', error)
        ElMessage.error('批量删除失败，请重试')
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 统一下载文件名解析（与设置页一致）
const getDownloadFilename = (disposition, fallbackName) => {
  if (!disposition) return fallbackName
  const match = /filename=([^;]+)/i.exec(disposition)
  if (!match) return fallbackName
  return match[1].replace(/\"/g, '').trim() || fallbackName
}

// 收入页：导出数据（统一导出全量用户数据，字段由后端控制，包含支付方式等）
const handleExportIncome = async () => {
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

// 搜索表单验证函数
const validateSearchInput = (field, fieldName) => {
  console.log(`验证搜索字段: ${fieldName}(${field}) = "${searchForm.value[field]}"`)

  const value = searchForm.value[field]

  // 如果是字符串且只包含空格
  if (typeof value === 'string' && value.trim() === '') {
    ElMessage.warning({
      message: `${fieldName}不能只输入空格，已自动清空`,
      duration: 2000,
      showClose: true
    })
    searchForm.value[field] = ''  // 清空搜索表单的字段
  }
}

// 自动修剪首尾空格（当输入框失去焦点时）
const trimInputValue = (row, field) => {
  if (!row[field]) return;

  const originalValue = row[field];
  const trimmedValue = originalValue.trim();

  // 如果修剪前后不同（说明有首尾空格）
  if (originalValue !== trimmedValue) {
    row[field] = trimmedValue;

    // 轻微提示（可选）
    if (trimmedValue === '') {
      ElMessage.warning(`${field === 'source' ? '收入来源' : '备注'}已清除多余空格`);
    }
  }
}
</script>

<style scoped>
@import '../styles/framework.css';
@import '../styles/finance-dashboard.css';

/* 收入管理页面专属样式 */
.income-search-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.income-table-container {
  margin-top: 20px;
}

/* 表格内编辑控件样式优化 */
:deep(.el-table .el-input),
:deep(.el-table .el-select),
:deep(.el-table .el-date-picker) {
  width: 100%;
}
</style>
