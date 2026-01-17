<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <div class="top-nav" style="position: fixed; left: 30px">
      <div class="logo">MyFinancePal</div>
      <div class="breadcrumb">仪表盘 / 收入管理</div>
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
          <!-- ========== 新增：收入管理主体内容 ========== -->
          <!-- 1. 搜索与筛选栏 -->
          <div class="search-bar" style="margin-bottom: 20px">
            <el-form :inline="true" :model="searchForm" class="income-search-form">
              <!-- 修复点1：日期字段绑定匹配 searchForm.date -->
              <el-form-item label="收入日期">
                <el-date-picker
                  v-model="searchForm.date"
                  type="date"
                  placeholder="选择日期"
                  style="width: 200px"
                  :locale="zhCn"
                />
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

              <!-- 修复点3：移除错误的 handleMoneyInput 调用，字段匹配 searchForm.amount -->
              <el-form-item label="收入金额">
                <el-input
                  v-model="searchForm.amount"
                  placeholder="请输入收入金额"
                  type="number"
                  min="0"
                  step="0.01"
                  style="width: 200px"
                ></el-input>
              </el-form-item>

              <el-form-item label="收入来源">
                <el-input v-model="searchForm.source" placeholder="请输入收入来源" />
              </el-form-item>

              <!-- 修复点4：备注标签规范化，移除无效的 word-limit-format 属性 -->
              <el-form-item label="备&nbsp&nbsp&nbsp注" label-width="75px">
                <el-input
                  v-model="searchForm.remark"
                  placeholder="无"
                  maxlength="80"
                  show-word-limit
                  style="width: 100%"
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

              <!-- 收入类型列（可编辑） -->
              <el-table-column prop="ctype" label="收入类型" width="120" align="center">
                <template #default="scope">
                  <el-select
                    v-if="scope.row.isEditing"
                    v-model="scope.row.ctype"
                    style="width: 100%"
                    placeholder="选择类型"
                  >
                    <el-option label="工资" value="工资"></el-option>
                    <el-option label="理财收益" value="理财收益"></el-option>
                    <el-option label="兼职收入" value="兼职收入"></el-option>
                    <el-option label="奖金" value="奖金"></el-option>
                    <el-option label="其他" value="其他"></el-option>
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
                  />
                  <span v-else style="color: #4caf50; font-weight: 500"
                    >+{{ Number(scope.row.amount).toFixed(2) }}</span
                  >
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
                    <el-button type="danger" size="small" @click="handleDeleteIncome(scope.row.id)"
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
// 导入xlsx库用于导出Excel
import * as XLSX from 'xlsx'

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

// 获取dashboard逻辑变量（移除未使用的变量，减少冗余）
const { initTrendChart, initCategoryChart } = useDashboardLogic()

// 页面挂载初始化图表
onMounted(() => {
  // 增加DOM存在性判断，防止图表初始化失败
  setTimeout(() => {
    initTrendChart()
    initCategoryChart()
  }, 100)
  // 初始化收入数据
  initIncomeData()
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

// 修复点8：搜索表单字段与模板匹配（删除冗余的min/maxAmount，新增date/source/remark）
const searchForm = ref({
  date: '', // 收入日期
  type: '', // 收入类型
  amount: '', // 收入金额
  source: '', // 收入来源
  remark: '', // 备注
})

// 2. 分页相关
const currentPage = ref(1) // 当前页码
const pageSize = ref(15) // 每页条数（默认15条）
const selectedIds = ref([]) // 批量选择的ID

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

// 初始化收入数据
const initIncomeData = () => {
  // 生成模拟数据（50条，用于测试分页）
  const mockData = []
  const types = ['工资', '理财收益', '兼职收入', '奖金', '其他']
  const sources = ['公司打卡', '支付宝理财', '副业接单', '年终奖金', '亲友转账', '稿费', '投资分红']
  const remarks = ['', '本月绩效奖金', '加班补贴', '理财到期收益', '兼职设计费用', '无备注']

  for (let i = 1; i <= 50; i++) {
    const randomType = types[Math.floor(Math.random() * types.length)]
    const randomSource = sources[Math.floor(Math.random() * sources.length)]
    const randomRemark = remarks[Math.floor(Math.random() * remarks.length)]
    const randomAmount = (Math.random() * 10000 + 100).toFixed(2)

    // 生成随机日期（近6个月）
    const date = new Date()
    date.setMonth(date.getMonth() - Math.floor(Math.random() * 6))
    date.setDate(Math.floor(Math.random() * 28) + 1)
    const formatDate = date.toISOString().split('T')[0]

    mockData.push({
      id: i,
      date: formatDate,
      ctype: randomType, // 保持与表格匹配的 ctype 字段
      amount: Number(randomAmount),
      source: randomSource,
      remark: randomRemark,
      isEditing: false, // 新增：编辑状态标识
    })
  }

  // ========== 核心修改：初始化时按日期降序排列 ==========
  const sortedData = sortDataByDate(mockData)

  incomeList.value = sortedData
  originIncomeList.value = [...sortedData] // 保存排序后的原始数据
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

  // 新增空行数据（匹配收入数据格式）
  const newRow = {
    id: getNewId(),
    date: formatDate, // 默认当前日期
    ctype: '',
    amount: '',
    source: '',
    remark: '',
    isEditing: true, // 新增行默认进入编辑状态
  }

  // 添加到列表头部（方便编辑）
  incomeList.value.unshift(newRow)
  originIncomeList.value.unshift(newRow) // 同步原始数据
  totalIncome.value = incomeList.value.length
  currentPage.value = 1 // 跳转到第一页
}

// 保存编辑行
const handleSaveRow = (row) => {
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

  // 格式化金额（保留2位小数）
  row.amount = Number(row.amount).toFixed(2)
  // 备注默认填"无"
  row.remark = row.remark || '无'
  // 退出编辑状态
  row.isEditing = false

  // ========== 核心修改：保存后重新排序 ==========
  incomeList.value = sortDataByDate([...incomeList.value])
  originIncomeList.value = sortDataByDate([...originIncomeList.value])

  ElMessage.success('收入记录保存成功！')
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

// 4. 分页后的数据（计算属性）
const pagedIncomeList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return incomeList.value.slice(start, end)
})

// 5. 分页事件处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1 // 切换每页条数时重置页码
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 修复点9：完善搜索逻辑（关键修复：使用 originIncomeList 作为数据源 + 排序）
const handleSearch = () => {
  console.log('搜索条件：', searchForm.value)
  // 重置页码
  currentPage.value = 1

  // 关键修复：从原始数据拷贝，而非筛选后的数据
  let filteredData = JSON.parse(JSON.stringify(originIncomeList.value))

  // 1. 日期筛选
  if (searchForm.value.date) {
    filteredData = filteredData.filter((item) => item.date === searchForm.value.date)
  }

  // 2. 收入类型筛选
  if (searchForm.value.type) {
    filteredData = filteredData.filter((item) => item.ctype === searchForm.value.type)
  }

  // 3. 收入金额筛选（精确匹配）
  if (searchForm.value.amount) {
    const targetAmount = Number(searchForm.value.amount)
    filteredData = filteredData.filter(
      (item) => Math.abs(Number(item.amount) - targetAmount) < 0.01,
    )
  }

  // 4. 收入来源筛选（模糊匹配）
  if (searchForm.value.source) {
    const keyword = searchForm.value.source.trim()
    filteredData = filteredData.filter((item) => item.source.includes(keyword))
  }

  // 5. 备注筛选（模糊匹配）
  if (searchForm.value.remark && searchForm.value.remark !== '无') {
    const keyword = searchForm.value.remark.trim()
    filteredData = filteredData.filter((item) => item.remark.includes(keyword))
  }

  // ========== 核心修改：搜索结果按日期降序排列 ==========
  const sortedFilteredData = sortDataByDate(filteredData)

  // 更新筛选后的数据
  incomeList.value = sortedFilteredData
  totalIncome.value = sortedFilteredData.length
}

// 修复点10：重置搜索表单（关键修复：恢复原始数据 + 排序）
const resetSearch = () => {
  searchForm.value = {
    date: '',
    type: '',
    amount: '',
    source: '',
    remark: '',
  }

  // ========== 核心修改：重置后的数据按日期降序排列 ==========
  const sortedOriginData = sortDataByDate([...originIncomeList.value])

  // 恢复原始数据（排序后的）
  incomeList.value = sortedOriginData
  totalIncome.value = sortedOriginData.length
  currentPage.value = 1
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

// 9. 收入操作方法（实际项目中替换为接口请求）
const handleAddIncome = () => {
  // 新增收入逻辑，可弹出表单弹窗
  ElMessage.info('新增收入功能待实现（推荐使用表格快速新增）')
}

// 编辑收入（改为行内编辑）
const handleEditIncome = (row) => {
  row.isEditing = true
}

const handleDeleteIncome = (id) => {
  // 删除收入逻辑
  ElMessageBox.confirm('此操作将永久删除该收入记录, 是否继续?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      incomeList.value = incomeList.value.filter((item) => item.id !== id)
      totalIncome.value = incomeList.value.length
      // 同步更新原始数据（删除操作后原始数据也需要更新）
      originIncomeList.value = originIncomeList.value.filter((item) => item.id !== id)
      ElMessage({
        type: 'success',
        message: '删除成功!',
      })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消删除',
      })
    })
}

const handleBatchDelete = () => {
  // 批量删除逻辑
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }

  ElMessageBox.confirm('此操作将永久删除选中的收入记录, 是否继续?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      incomeList.value = incomeList.value.filter((item) => !selectedIds.value.includes(item.id))
      totalIncome.value = incomeList.value.length
      // 同步更新原始数据
      originIncomeList.value = originIncomeList.value.filter(
        (item) => !selectedIds.value.includes(item.id),
      )
      selectedIds.value = []
      ElMessage({
        type: 'success',
        message: '批量删除成功!',
      })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消删除',
      })
    })
}

// ========== 完善导出数据功能 ==========
const handleExportIncome = () => {
  // 1. 准备导出数据：深拷贝避免修改原数据
  const exportData = JSON.parse(JSON.stringify(incomeList.value)).map((item) => {
    // 过滤掉不需要的字段
    const { isEditing, ...rest } = item
    // 重命名字段（让Excel表头更友好）
    return {
      序号: rest.id,
      收入日期: rest.date,
      收入类型: rest.ctype,
      '收入金额(¥)': Number(rest.amount).toFixed(2),
      收入来源: rest.source,
      备注: rest.remark || '无',
    }
  })

  // 2. 创建工作簿和工作表
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '收入记录')

  // 3. 调整列宽（可选，优化Excel显示）
  const wscols = [
    { wch: 8 }, // 序号
    { wch: 15 }, // 收入日期
    { wch: 12 }, // 收入类型
    { wch: 15 }, // 收入金额
    { wch: 20 }, // 收入来源
    { wch: 25 }, // 备注
  ]
  ws['!cols'] = wscols

  // 4. 生成文件名（带时间戳，避免重复）
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const filename = `收入记录_${year}${month}${day}.xlsx`

  // 5. 导出文件
  XLSX.writeFile(wb, filename)

  // 6. 提示用户
  ElMessage.success('收入数据导出成功！')
}
// ========== 导出功能结束 ==========
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
