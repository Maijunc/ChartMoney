<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <div class="top-nav" style="position: fixed; left: 30px">
      <div class="logo">MyFinancePal</div>
      <div class="breadcrumb" style="">仪表盘 / 支出管理-总消费记录</div>
      <div class="tags-container"></div>
      <div class="user-info">
        <!-- 改为直接使用User组件（全局注册后） -->
        <el-avatar>
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
          <el-sub-menu index="Goods">
            <template #title>
              <el-icon><Goods /></el-icon>
              <span>支出管理</span>
            </template>

            <el-menu-item
              index="CreditCard "
              @click="handleJumpToRecord()"
              style="color: rgb(64, 158, 255) !important"
            >
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
        <!-- 标签页导航（顶部小标签） -->
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

        <!-- 菜单管理内容 -->
        <div class="menu-management-panel">
          <!-- 搜索区域 -->
          <div class="search-bar">
            <el-form inline="false" @submit.prevent="onSearch">
              <el-form-item label="创建时间">
                <el-date-picker
                  v-model="searchForm.createTime"
                  type="date"
                  placeholder="选择日期"
                  style="width: 200px"
                />
              </el-form-item>
              <el-form-item label="消费种类">
                <el-select
                  v-model="searchForm.type"
                  placeholder="请选择消费种类"
                  style="width: 200px"
                  clearable
                >
                  <!-- 子选项列表 -->
                  <el-option label="餐饮美食" value="餐饮美食" />
                  <el-option label="交通出行" value="交通出行" />
                  <el-option label="居住房租" value="居住房租" />
                  <el-option label="购物消费" value="购物消费" />
                  <el-option label="休闲娱乐" value="休闲娱乐" />
                  <el-option label="医疗健康" value="医疗健康" />
                </el-select>
              </el-form-item>

              <el-form-item label="消费名称">
                <el-input v-model="searchForm.name" placeholder="请输入消费名称" />
              </el-form-item>

              <el-form-item label="消费金额">
                <el-input
                  v-model="searchForm.money"
                  placeholder="请输入消费金额"
                  type="number"
                  min="0"
                  step="0.01"
                  @input="handleMoneyInput"
                  style="width: 300px"
                />
              </el-form-item>

              <el-form-item label="备&nbsp&nbsp&nbsp注" label-width="68px">
                <el-input
                  v-model="searchForm.extra"
                  placeholder="无"
                  maxlength="80"
                  show-word-limit
                  :word-limit-format="(used, total) => `${used}/${total} 字`"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item>
                <!-- 修复：绑定正确的搜索方法名 handleSearch -->
                <el-button type="primary" @click="handleSearch">搜索</el-button>
                <!-- 修复：绑定正确的重置方法名 resetSearch -->
                <el-button @click="resetSearch">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- ========== 改造：操作按钮栏（和收入页面一致） ========== -->
          <div class="action-bar" style="margin: 0px 0">
            <el-button type="success" icon="Download" @click="handleExportIncome"
              >导出数据</el-button
            >
            <el-button type="warning" icon="Delete" @click="handleBatchDelete">批量删除</el-button>
          </div>

          <!-- ========== 改造：支出记录表格（带分页） ========== -->
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
              <el-table-column prop="time" label="日期" width="120" align="center" />
              <el-table-column prop="icon" label="图标" width="80" align="center">
                <template #default="scope">
                  <!-- 表格图标改为字符串匹配（全局注册后直接使用组件名） -->
                  <el-icon :size="20">
                    <component :is="scope.row.iconName" />
                  </el-icon>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="消费种类" width="120" align="center">
                <template #default="scope">
                  <el-tag :type="getTagType(scope.row.type)">{{ scope.row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="name" label="消费名称" min-width="120" align="center" />
              <el-table-column prop="money" label="消费金额(¥)" width="120" align="center">
                <template #default="scope">
                  <span style="color: #f44336; font-weight: 500"
                    >-{{ Number(scope.row.money).toFixed(2) }}</span
                  >
                </template>
              </el-table-column>
              <el-table-column prop="extra" label="备注" min-width="200" align="center" />
              <el-table-column label="操作" width="180" align="center">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="handleEditExpense(scope.row)"
                    >编辑</el-button
                  >
                  <el-button type="danger" size="small" @click="handleDeleteExpense(scope.row.id)"
                    >删除</el-button
                  >
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
import { ref, onMounted, computed } from 'vue' // 新增computed导入
import { useRouter } from 'vue-router'
// 引入Element Plus消息和确认框（用于操作提示）
import { ElMessage, ElMessageBox } from 'element-plus'
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
// 顶部标签页数据
const tagsList = ref([
  { key: 'dashboard', label: '仪表盘' },
  { key: 'user', label: '首页' },
  { key: 'coin', label: '收入管理' },
  { key: 'Goods', label: '支出管理' },
  { key: 'Tickets', label: '购物预算管理' },
  { key: 'DataAnalysis', label: '消费年度总结' },
  { key: 'Tools', label: '设置' },
])
const activePath = ref('/menu-management')

// 页面内标签页数据
const pageTagsList = ref([
  { key: 'dashboard', label: '仪表盘' },
  { key: 'user-management', label: '首页' },
  { key: 'coin-management', label: '收入管理' },
  { key: 'goods-management', label: '支出管理' },
  { key: 'budget-management', label: '购物预算管理' },
  { key: 'DataAnalysis-management', label: '消费年度总结' },
])
const activePageKey = ref('menu-management')

// 搜索表单
const searchForm = ref({
  type: '',
  name: '',
  money: '',
  extra: '',
  createTime: '', // 改为字符串类型，匹配日期选择器的返回值
})

// ========== 改造：支出列表数据（扩展为50条模拟数据，增加ID） ==========
const expenseList = ref([]) // 筛选后的数据
const originExpenseList = ref([]) // 原始数据副本（关键新增）
const totalExpense = ref(0)

// ========== 新增：日期排序方法（核心修改） ==========
const sortDataByDate = (data) => {
  // 按time字段降序排列（新日期在前）
  return data.sort((a, b) => {
    return new Date(b.time) - new Date(a.time)
  })
}

// 初始化支出数据
const initExpenseData = () => {
  // 生成50条模拟支出数据（测试分页）
  const mockData = []
  const types = ['餐饮美食', '交通出行', '居住房租', '购物消费', '休闲娱乐', '医疗健康']
  const icons = ['Food', 'Van', 'House', 'ShoppingTrolley', 'VideoPlay', 'FirstAidKit']
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

  for (let i = 1; i <= 50; i++) {
    const randomTypeIdx = Math.floor(Math.random() * types.length)
    const randomType = types[randomTypeIdx]
    const randomIcon = icons[randomTypeIdx]
    const randomName = names[Math.floor(Math.random() * names.length)]
    const randomMoney = (Math.random() * 5000 + 10).toFixed(2)
    const randomRemark = Math.random() > 0.7 ? '无' : `${randomName}消费`

    // 生成随机日期（近6个月）
    const date = new Date()
    date.setMonth(date.getMonth() - Math.floor(Math.random() * 6))
    date.setDate(Math.floor(Math.random() * 28) + 1)
    const formatDate = date.toISOString().split('T')[0]

    mockData.push({
      id: i, // 增加唯一ID
      time: formatDate,
      iconName: randomIcon,
      type: randomType,
      name: randomName,
      money: randomMoney,
      extra: randomRemark,
    })
  }

  // ========== 核心修改：初始化时就按日期降序排列 ==========
  const sortedData = sortDataByDate(mockData)
  expenseList.value = sortedData
  originExpenseList.value = [...sortedData] // 保存排序后的原始数据副本
  totalExpense.value = sortedData.length
}

// ========== 新增：分页相关逻辑 ==========
const currentPage = ref(1) // 当前页码
const pageSize = ref(15) // 每页条数（默认15条）
const selectedIds = ref([]) // 批量选择的支出ID

// 分页后的数据（计算属性）
const pagedExpenseList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return expenseList.value.slice(start, end)
})

// 分页事件处理
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1 // 切换每页条数时重置页码
}

const handleCurrentChange = (val) => {
  currentPage.value = val
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

// 新增支出
const handleAddExpense = () => {
  ElMessage.info('新增支出功能待实现')
}

// 编辑支出
const handleEditExpense = (row) => {
  ElMessage.info(`编辑ID为${row.id}的支出记录`)
}

// 删除支出（同步更新原始数据）
const handleDeleteExpense = (id) => {
  ElMessageBox.confirm('此操作将永久删除该支出记录, 是否继续?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      expenseList.value = expenseList.value.filter((item) => item.id !== id)
      originExpenseList.value = originExpenseList.value.filter((item) => item.id !== id) // 同步原始数据
      totalExpense.value = expenseList.value.length
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

// 批量删除（同步更新原始数据）
const handleBatchDelete = () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要删除的记录')
    return
  }

  ElMessageBox.confirm('此操作将永久删除选中的支出记录, 是否继续?', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      expenseList.value = expenseList.value.filter((item) => !selectedIds.value.includes(item.id))
      originExpenseList.value = originExpenseList.value.filter(
        (item) => !selectedIds.value.includes(item.id),
      ) // 同步原始数据
      totalExpense.value = expenseList.value.length
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

// 顶部标签页-关闭
const handleCloseTag = (index) => {
  tagsList.value.splice(index, 1)
  // 如果关闭的是当前激活的标签，切换到最后一个标签
  if (tagsList.value[index]?.path === activePath.value) {
    activePath.value = tagsList.value[tagsList.value.length - 1]?.path || '/dashboard'
  }
}

// 顶部标签页-点击切换
const handleTagClick = (path) => {
  activePath.value = path
}

// 页面内标签页-关闭
const handleClosePageTag = (index) => {
  pageTagsList.value.splice(index, 1)
  if (pageTagsList.value[index]?.key === activePageKey.value) {
    activePageKey.value = pageTagsList.value[pageTagsList.value.length - 1]?.key || 'dashboard'
  }
}

// 页面内标签页-点击切换
const handlePageTagClick = (key) => {
  activePageKey.value = key
}

// 左侧菜单选择
const handleMenuSelect = (key) => {
  // 点击菜单时，自动添加到标签页（如果不存在）
  const tagExists = pageTagsList.value.some((item) => item.key === key)
  if (!tagExists) {
    const labelMap = {
      dashboard: '仪表盘',
      'user-management': '首页',
      'coin-management': '收入管理',
      'goods-management': '支出管理',
      'budget-management': '购物预算管理',
      'DataAnalysis-management': '消费年度总结',
    }
    pageTagsList.value.push({ key, label: labelMap[key] })
  }
  activePageKey.value = key
}

// 过滤消费金额：只保留非负的数字和一个小数点
const handleMoneyInput = () => {
  searchForm.value.money = searchForm.value.money
    ?.replace(/[^0-9.]/g, '') // 移除所有非数字、非小数点的字符
    .replace(/^\./, '') // 移除开头的小数点（避免.123这种格式）
    .replace(/\.{2,}/g, '.') // 多个小数点只保留第一个
    .replace(/^0+(\d)/, '$1') // 移除开头多余的0（避免00123这种格式）
    .replace(/(\.\d{2}).*/g, '$1') // 可选：限制小数点后最多2位（金额精确到分）
}

// 页面挂载时初始化
onMounted(() => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  searchForm.value.createTime = `${year}-${month}-${day}`

  // 初始化支出数据
  initExpenseData()
})

// ========== 核心修改：搜索逻辑（添加日期排序） ==========
const handleSearch = () => {
  console.log('搜索参数：', searchForm.value)
  // 重置页码
  currentPage.value = 1

  // 关键：从原始数据拷贝，而非筛选后的数据
  let filteredData = JSON.parse(JSON.stringify(originExpenseList.value))

  // 1. 日期筛选
  if (searchForm.value.createTime) {
    filteredData = filteredData.filter((item) => item.time === searchForm.value.createTime)
  }

  // 2. 消费种类筛选
  if (searchForm.value.type) {
    filteredData = filteredData.filter((item) => item.type === searchForm.value.type)
  }

  // 3. 消费名称筛选（模糊匹配）
  if (searchForm.value.name) {
    const keyword = searchForm.value.name.trim()
    filteredData = filteredData.filter((item) => item.name.includes(keyword))
  }

  // 4. 消费金额筛选（精确匹配，兼容浮点数精度）
  if (searchForm.value.money) {
    const targetMoney = Number(searchForm.value.money)
    filteredData = filteredData.filter((item) => Math.abs(Number(item.money) - targetMoney) < 0.01)
  }

  // 5. 备注筛选（模糊匹配，排除"无"的情况）
  if (searchForm.value.extra && searchForm.value.extra !== '无') {
    const keyword = searchForm.value.extra.trim()
    filteredData = filteredData.filter((item) => item.extra.includes(keyword))
  }

  // ========== 核心修改：搜索结果也按日期降序排列 ==========
  const sortedFilteredData = sortDataByDate(filteredData)

  // 更新筛选后的数据
  expenseList.value = sortedFilteredData
  totalExpense.value = sortedFilteredData.length
}

// ========== 核心修改：重置逻辑（添加日期排序） ==========
const resetSearch = () => {
  // 清空搜索表单
  searchForm.value = {
    type: '',
    name: '',
    money: '',
    extra: '',
    createTime: '',
  }

  // ========== 核心修改：重置后的数据也按日期降序排列 ==========
  const sortedOriginData = sortDataByDate([...originExpenseList.value])

  // 恢复原始数据（排序后的）
  expenseList.value = sortedOriginData
  totalExpense.value = sortedOriginData.length
  currentPage.value = 1 // 重置页码
}

// 保留原有onSearch方法（兼容表单提交）
const onSearch = handleSearch
// 保留原有onReset方法（兼容备用调用）
const onReset = resetSearch

// ========== 修复核心：支出数据导出功能 ==========
const handleExportIncome = () => {
  // 1. 修复：使用支出数据源expenseList，而非incomeList
  const exportData = JSON.parse(JSON.stringify(expenseList.value)).map((item) => {
    // 过滤掉不需要的字段
    const { iconName, ...rest } = item
    // 修复：使用支出的字段名（time/type/name/money/extra）
    return {
      序号: rest.id,
      消费日期: rest.time,
      消费种类: rest.type,
      消费名称: rest.name,
      '消费金额(¥)': Number(rest.money).toFixed(2),
      备注: rest.extra || '无',
    }
  })

  // 2. 修复列宽配置（匹配支出字段数量）
  const wscols = [
    { wch: 8 }, // 序号
    { wch: 15 }, // 消费日期
    { wch: 12 }, // 消费种类
    { wch: 15 }, // 消费名称
    { wch: 15 }, // 消费金额
    { wch: 25 }, // 备注
  ]

  // 3. 创建工作簿和工作表
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '支出记录')
  ws['!cols'] = wscols

  // 4. 生成文件名（支出专属）
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const filename = `支出记录_${year}${month}${day}.xlsx`

  // 5. 导出文件
  XLSX.writeFile(wb, filename)

  // 6. 修复提示语
  ElMessage.success('支出数据导出成功！')
}
</script>

<style scoped>
@import '../styles/framework.css'; /* 导入外部CSS文件，通过@import方式并保留scoped */
@import '../styles/finance-dashboard.css';

/* 支出管理页面专属样式 */
.action-bar {
  display: flex;
  gap: 10px;
}

.expense-table-container {
  margin-top: 10px;
}

.expense-pagination {
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中（可选） */
  margin: 20px 0; /* 上下间距，优化视觉 */
  text-align: center; /* 兜底兼容 */
}

/* 穿透样式：确保Element Plus分页组件内部也居中（如果需要） */
:deep(.expense-pagination .el-pagination) {
  justify-content: center;
}
</style>
