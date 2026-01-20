<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <div class="top-nav" style="position: fixed; left: 30px">
      <div class="logo">MyFinancePal</div>
      <div class="breadcrumb" style="">仪表盘 / 支出管理-日常支出</div>
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

            <el-menu-item index="CreditCard" @click="handleJumpToRecord()">
              <el-icon><CreditCard /></el-icon>
              <span>总消费记录</span>
            </el-menu-item>

            <el-menu-item
              index="DailyExpense"
              @click="handleJumpToExpend()"
              style="color: rgb(64, 158, 255) !important"
            >
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
          <div class="search-bar"></div>

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

              <!-- 图标列（根据类型自动匹配） -->
              <el-table-column prop="icon" label="图标" width="80" align="center">
                <template #default="scope">
                  <el-icon :size="20">
                    <component :is="scope.row.iconName" />
                  </el-icon>
                </template>
              </el-table-column>

              <!-- 消费种类列（可编辑） -->
              <el-table-column prop="type" label="消费种类" width="120" align="center">
                <template #default="scope">
                  <el-select
                    v-if="scope.row.isEditing"
                    v-model="scope.row.type"
                    style="width: 100%"
                    placeholder="选择种类"
                  >
                    <el-option label="餐饮美食" value="餐饮美食" />
                    <el-option label="交通出行" value="交通出行" />
                    <el-option label="居住房租" value="居住房租" />
                    <el-option label="购物消费" value="购物消费" />
                    <el-option label="休闲娱乐" value="休闲娱乐" />
                    <el-option label="医疗健康" value="医疗健康" />
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
                  />
                  <span v-else style="color: #f44336; font-weight: 500"
                    >-{{ Number(scope.row.money).toFixed(2) }}</span
                  >
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
import { ref, onMounted, computed } from 'vue' // 新增computed导入
import { useRouter } from 'vue-router'
// 引入Element Plus消息和确认框（用于操作提示）
import { ElMessage, ElMessageBox } from 'element-plus'
// ========== 新增：导入xlsx库用于导出Excel ==========
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
  createTime: '', // 改为字符串类型，匹配日期选择器
})

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
const initExpenseData = () => {
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

  for (let i = 1; i <= 50; i++) {
    const randomTypeIdx = Math.floor(Math.random() * types.length)
    const randomType = types[randomTypeIdx]
    const randomIcon = iconMap[randomType]
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
      isEditing: false, // 新增：编辑状态标识
    })
  }

  // ========== 核心修改：初始化时按日期降序排列 ==========
  const sortedData = sortDataByDate(mockData)

  expenseList.value = sortedData
  originExpenseList.value = [...sortedData] // 保存排序后的原始数据
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

  // 新增空行数据（匹配mockData格式）
  const newRow = {
    id: getNewId(),
    time: formatDate, // 默认当前日期
    iconName: 'Food', // 默认图标
    type: '',
    name: '',
    money: '',
    extra: '',
    isEditing: true, // 新增行默认进入编辑状态
  }

  // 添加到列表头部（方便编辑）
  expenseList.value.unshift(newRow)
  originExpenseList.value.unshift(newRow) // 同步原始数据
  totalExpense.value = expenseList.value.length
  currentPage.value = 1 // 跳转到第一页
}

// 保存编辑行
const handleSaveRow = (row) => {
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

  // 根据消费种类自动匹配图标
  row.iconName = iconMap[row.type] || 'Food'
  // 格式化金额（保留2位小数）
  row.money = Number(row.money).toFixed(2)
  // 备注默认填"无"
  row.extra = row.extra || '无'
  // 退出编辑状态
  row.isEditing = false

  // ========== 核心修改：保存后重新排序 ==========
  expenseList.value = sortDataByDate([...expenseList.value])
  originExpenseList.value = sortDataByDate([...originExpenseList.value])

  ElMessage.success('支出记录保存成功！')
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
    .then(() => {
      expenseList.value = expenseList.value.filter((item) => item.id !== id)
      originExpenseList.value = originExpenseList.value.filter((item) => item.id !== id)
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

// 批量删除
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
      )
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

// ========== 核心修复：完善导出数据功能 ==========
const handleExportExpense = () => {
  // 1. 过滤掉编辑中的空行（避免导出无效数据）
  const validData = expenseList.value.filter((item) => {
    // 排除未保存的新增行、必填字段为空的行
    return item.time && item.type && item.name && item.money
  })

  if (validData.length === 0) {
    ElMessage.warning('暂无可导出的有效支出数据！')
    return
  }

  // 2. 准备导出数据：深拷贝避免修改原数据，格式化字段
  const exportData = JSON.parse(JSON.stringify(validData)).map((item) => {
    // 过滤掉不需要的字段
    const { iconName, isEditing, ...rest } = item
    // 重命名字段（让Excel表头更友好）
    return {
      序号: rest.id,
      消费日期: rest.time,
      消费种类: rest.type,
      消费名称: rest.name,
      '消费金额(¥)': Number(rest.money).toFixed(2),
      备注: rest.extra || '无',
    }
  })

  // 3. 创建工作簿和工作表
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '日常支出记录')

  // 4. 调整列宽（优化Excel显示）
  const wscols = [
    { wch: 8 }, // 序号
    { wch: 15 }, // 消费日期
    { wch: 12 }, // 消费种类
    { wch: 15 }, // 消费名称
    { wch: 15 }, // 消费金额
    { wch: 25 }, // 备注
  ]
  ws['!cols'] = wscols

  // 5. 生成文件名（带时间戳，避免重复）
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const filename = `日常支出记录_${year}${month}${day}.xlsx`

  // 6. 导出文件
  XLSX.writeFile(wb, filename)

  // 7. 提示用户
  ElMessage.success('日常支出数据导出成功！')
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

  // ========== 核心修改：搜索结果按日期降序排列 ==========
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

  // ========== 核心修改：重置后的数据按日期降序排列 ==========
  const sortedOriginData = sortDataByDate([...originExpenseList.value])

  // 恢复原始数据（排序后的）
  expenseList.value = sortedOriginData
  totalExpense.value = sortedOriginData.length
  currentPage.value = 1 // 重置页码
}

// 保留原有onSearch/onReset方法（兼容表单提交）
const onSearch = handleSearch
const onReset = resetSearch
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
  margin-top: 0px;
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

/* 表格内编辑控件样式优化 */
:deep(.el-table .el-input),
:deep(.el-table .el-select) {
  width: 100%;
}
</style>
