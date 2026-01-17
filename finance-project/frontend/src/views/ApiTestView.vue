<template>
  <div class="api-test-container">
    <h1>🚀 API 服务层测试页面</h1>
    <p class="subtitle">这个页面使用了封装的 API 服务层（src/api/）</p>

    <!-- 配置区 -->
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>⚙️ 配置信息</span>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="后端地址">http://localhost:8000</el-descriptions-item>
        <el-descriptions-item label="当前用户ID">{{ userStore.userId || '未登录' }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ userStore.username || '未登录' }}</el-descriptions-item>
        <el-descriptions-item label="登录状态">
          <el-tag :type="userStore.isLogin ? 'success' : 'danger'">
            {{ userStore.isLogin ? '已登录' : '未登录' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 用户认证测试 -->
    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <span>👤 用户认证测试（使用 useUserStore）</span>
        </div>
      </template>

      <el-form :model="loginForm" label-width="80px">
        <h3>注册</h3>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="用户名">
              <el-input v-model="registerForm.username" placeholder="testuser2" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="手机号">
              <el-input v-model="registerForm.phone" placeholder="13900139000" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="密码">
              <el-input v-model="registerForm.password" type="password" placeholder="123456" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-button type="primary" @click="handleRegister" :loading="loading.register">
              测试注册
            </el-button>
          </el-col>
        </el-row>

        <h3 style="margin-top: 20px">登录</h3>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="用户名">
              <el-input v-model="loginForm.username" placeholder="testuser" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="密码">
              <el-input v-model="loginForm.password" type="password" placeholder="123456" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-button type="success" @click="handleLogin" :loading="loading.login">
              测试登录
            </el-button>
            <el-button @click="handleLogout" v-if="userStore.isLogin">
              退出登录
            </el-button>
          </el-col>
        </el-row>
      </el-form>

      <div v-if="results.auth" class="result-box">
        <pre>{{ results.auth }}</pre>
      </div>
    </el-card>

    <!-- 分类管理测试 -->
    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <span>📋 分类管理测试（使用 categoryMapper）</span>
        </div>
      </template>

      <el-space wrap>
        <el-button type="primary" @click="handleInitCategory" :loading="loading.category">
          初始化分类映射
        </el-button>
        <el-button @click="handleGetExpenseCategory">获取支出分类</el-button>
        <el-button @click="handleGetIncomeCategory">获取收入分类</el-button>
        <el-button type="warning" @click="handleTestCategoryMapping">
          测试分类映射转换
        </el-button>
      </el-space>

      <div v-if="results.category" class="result-box">
        <pre>{{ results.category }}</pre>
      </div>
    </el-card>

    <!-- 账单管理测试 -->
    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <span>💰 账单管理测试（使用 bill.js + BillTransformer）</span>
        </div>
      </template>

      <el-alert
        v-if="!userStore.isLogin"
        title="请先登录"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      />

      <el-space wrap>
        <el-button
          type="primary"
          @click="handleAddBill"
          :loading="loading.bill"
          :disabled="!userStore.isLogin"
        >
          添加账单
        </el-button>
        <el-button
          @click="handleGetBillList"
          :disabled="!userStore.isLogin"
        >
          获取账单列表
        </el-button>
        <el-button
          type="warning"
          @click="handleTestBillTransform"
          :disabled="!userStore.isLogin"
        >
          测试数据转换
        </el-button>
        <el-button
          type="danger"
          @click="handleDeleteBill"
          :disabled="!userStore.isLogin"
        >
          删除账单
        </el-button>
      </el-space>

      <div v-if="results.bill" class="result-box">
        <pre>{{ results.bill }}</pre>
      </div>
    </el-card>

    <!-- 预算管理测试 -->
    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <span>📊 预算管理测试（使用 budget.js）</span>
        </div>
      </template>

      <el-alert
        v-if="!userStore.isLogin"
        title="请先登录"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      />

      <el-space wrap>
        <el-button
          type="primary"
          @click="handleAddBudget"
          :loading="loading.budget"
          :disabled="!userStore.isLogin"
        >
          添加总预算
        </el-button>
        <el-button
          @click="handleGetBudgetList"
          :disabled="!userStore.isLogin"
        >
          获取预算列表
        </el-button>
        <el-button
          type="warning"
          @click="handleUpdateBudget"
          :disabled="!userStore.isLogin"
        >
          修改预算
        </el-button>
        <el-button
          type="danger"
          @click="handleDeleteBudget"
          :disabled="!userStore.isLogin"
        >
          删除预算
        </el-button>
      </el-space>

      <div v-if="results.budget" class="result-box">
        <pre>{{ results.budget }}</pre>
      </div>
    </el-card>

    <!-- 说明卡片 -->
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <span>💡 功能说明</span>
        </div>
      </template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="自动错误处理">
          所有请求失败会自动弹出 ElMessage 提示，无需手动处理
        </el-descriptions-item>
        <el-descriptions-item label="请求日志">
          打开浏览器控制台，可以看到 🚀 Request 和 ✅ Response 日志
        </el-descriptions-item>
        <el-descriptions-item label="分类映射">
          自动处理中文类型（如"餐饮美食"）与后端 category_id 的转换
        </el-descriptions-item>
        <el-descriptions-item label="数据转换">
          BillTransformer 自动处理前端字段（money, time）与后端字段（amount, bill_time）的转换
        </el-descriptions-item>
        <el-descriptions-item label="用户状态">
          使用 Pinia Store 管理用户登录状态，localStorage 自动持久化
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  getCategoryList,
  categoryMapper,
  addBill,
  getBillList,
  deleteBill,
  BillTransformer,
  addBudget,
  getBudgetListByMonth,
  updateBudget,
  deleteBudget
} from '@/api'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()

// 表单数据
const loginForm = reactive({
  username: 'testuser',
  password: '123456'
})

const registerForm = reactive({
  username: 'testuser2',
  phone: '13900139000',
  password: '123456'
})

// 加载状态
const loading = reactive({
  register: false,
  login: false,
  category: false,
  bill: false,
  budget: false
})

// 结果显示
const results = reactive({
  auth: '',
  category: '',
  bill: '',
  budget: ''
})

// 用户认证
async function handleRegister() {
  loading.register = true
  try {
    const success = await userStore.register(registerForm)
    results.auth = success
      ? '✅ 注册成功！\n' + JSON.stringify(registerForm, null, 2)
      : '❌ 注册失败'
  } finally {
    loading.register = false
  }
}

async function handleLogin() {
  loading.login = true
  try {
    const success = await userStore.login(loginForm)
    results.auth = success
      ? `✅ 登录成功！\n用户ID: ${userStore.userId}\n用户名: ${userStore.username}`
      : '❌ 登录失败'
  } finally {
    loading.login = false
  }
}

function handleLogout() {
  userStore.logout()
  results.auth = '✅ 已退出登录'
}

// 分类管理
async function handleInitCategory() {
  loading.category = true
  try {
    await categoryMapper.init()
    results.category = '✅ 分类映射初始化成功！\n\n支出分类：\n' +
      JSON.stringify(categoryMapper.getExpenseCategories(), null, 2) +
      '\n\n收入分类：\n' +
      JSON.stringify(categoryMapper.getIncomeCategories(), null, 2)
  } catch (error) {
    results.category = '❌ 初始化失败: ' + error.message
  } finally {
    loading.category = false
  }
}

async function handleGetExpenseCategory() {
  try {
    const res = await getCategoryList(2)
    results.category = '✅ 支出分类列表：\n' + JSON.stringify(res, null, 2)
  } catch (error) {
    results.category = '❌ 获取失败: ' + error.message
  }
}

async function handleGetIncomeCategory() {
  try {
    const res = await getCategoryList(1)
    results.category = '✅ 收入分类列表：\n' + JSON.stringify(res, null, 2)
  } catch (error) {
    results.category = '❌ 获取失败: ' + error.message
  }
}

function handleTestCategoryMapping() {
  // 测试分类映射功能
  const testResults = []

  // 测试支出分类映射
  const expenseTypes = ['餐饮美食', '交通出行', '居住房租']
  testResults.push('🔍 支出分类映射测试：')
  expenseTypes.forEach(type => {
    const id = categoryMapper.getExpenseCategoryId(type)
    const nameBack = categoryMapper.getExpenseCategoryName(id)
    testResults.push(`  "${type}" → ID: ${id} → "${nameBack}"`)
  })

  // 测试收入分类映射
  testResults.push('\n🔍 收入分类映射测试：')
  const incomeTypes = ['工资', '理财收益', '兼职收入']
  incomeTypes.forEach(type => {
    const id = categoryMapper.getIncomeCategoryId(type)
    const nameBack = categoryMapper.getIncomeCategoryName(id)
    testResults.push(`  "${type}" → ID: ${id} → "${nameBack}"`)
  })

  results.category = testResults.join('\n')
}

// 账单管理
async function handleAddBill() {
  loading.bill = true
  try {
    // 获取分类ID
    const categoryId = categoryMapper.getExpenseCategoryId('餐饮美食') || 1

    const res = await addBill({
      user_id: userStore.userId,
      category_id: categoryId,
      amount: 88.50,
      bill_time: '2026-01-17T12:00:00',
      remark: '测试账单 - 使用API服务层'
    })

    results.bill = '✅ 添加账单成功！\n' + JSON.stringify(res, null, 2)
  } catch (error) {
    results.bill = '❌ 添加失败: ' + error.message
  } finally {
    loading.bill = false
  }
}

async function handleGetBillList() {
  try {
    const res = await getBillList({
      user_id: userStore.userId,
      the_time: '2026-01',
      page: 1,
      page_size: 15,
      type: 2
    })

    results.bill = '✅ 获取账单列表成功！\n' +
      `总数: ${res.total}\n` +
      `页数: ${res.page_num}\n\n` +
      JSON.stringify(res.data, null, 2)
  } catch (error) {
    results.bill = '❌ 获取失败: ' + error.message
  }
}

function handleTestBillTransform() {
  // 测试数据转换功能
  const testResults = []

  testResults.push('🔄 数据转换测试：\n')

  // 1. 前端支出数据 -> 后端
  const frontendExpense = {
    time: '2026-01-17',
    money: 88.5,
    type: '餐饮美食',
    extra: '午餐'
  }
  const categoryId = categoryMapper.getExpenseCategoryId('餐饮美食')
  const backendData = BillTransformer.expenseToBackend(
    frontendExpense,
    userStore.userId,
    categoryId
  )

  testResults.push('1️⃣ 前端支出数据 → 后端账单数据：')
  testResults.push('前端数据：')
  testResults.push(JSON.stringify(frontendExpense, null, 2))
  testResults.push('\n转换后（后端格式）：')
  testResults.push(JSON.stringify(backendData, null, 2))

  // 2. 后端数据 -> 前端支出
  testResults.push('\n\n2️⃣ 后端账单数据 → 前端支出数据：')
  const mockBackendData = {
    id: 1,
    name: '午餐',
    amount: 88.5,
    bill_time: '2026-01-17T12:00:00',
    remark: '测试'
  }
  const frontendData = BillTransformer.backendToExpense(
    mockBackendData,
    '餐饮美食'
  )
  testResults.push('后端数据：')
  testResults.push(JSON.stringify(mockBackendData, null, 2))
  testResults.push('\n转换后（前端格式）：')
  testResults.push(JSON.stringify(frontendData, null, 2))

  results.bill = testResults.join('\n')
}

async function handleDeleteBill() {
  try {
    const res = await deleteBill({
      user_id: userStore.userId,
      bill_id: 1
    })

    results.bill = '✅ 删除账单成功！\n' + JSON.stringify(res, null, 2)
  } catch (error) {
    results.bill = '❌ 删除失败: ' + error.message
  }
}

// 预算管理
async function handleAddBudget() {
  loading.budget = true
  try {
    const res = await addBudget({
      user_id: userStore.userId,
      category_id: null,
      is_total: true,
      amount: 5000,
      month: '2026-01'
    })

    results.budget = '✅ 添加预算成功！\n' + JSON.stringify(res, null, 2)
  } catch (error) {
    results.budget = '❌ 添加失败: ' + error.message
  } finally {
    loading.budget = false
  }
}

async function handleGetBudgetList() {
  try {
    const res = await getBudgetListByMonth({
      user_id: userStore.userId,
      month: '2026-01'
    })

    results.budget = '✅ 获取预算列表成功！\n' + JSON.stringify(res, null, 2)
  } catch (error) {
    results.budget = '❌ 获取失败: ' + error.message
  }
}

async function handleUpdateBudget() {
  try {
    const res = await updateBudget({
      user_id: userStore.userId,
      budget_id: 1,
      amount: 6000
    })

    results.budget = '✅ 修改预算成功！\n' + JSON.stringify(res, null, 2)
  } catch (error) {
    results.budget = '❌ 修改失败: ' + error.message
  }
}

async function handleDeleteBudget() {
  try {
    const res = await deleteBudget({
      user_id: userStore.userId,
      budget_id: 1
    })

    results.budget = '✅ 删除预算成功！\n' + JSON.stringify(res, null, 2)
  } catch (error) {
    results.budget = '❌ 删除失败: ' + error.message
  }
}

// 页面加载时初始化
onMounted(() => {
  ElMessage.info('页面已加载，请先登录后再测试其他功能')

  // 提示用户查看控制台
  console.log('💡 提示：所有 API 请求和响应都会在控制台打印')
  console.log('💡 查看 🚀 Request 和 ✅ Response 日志')
})
</script>

<style scoped>
.api-test-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

h1 {
  color: #409eff;
  margin-bottom: 10px;
}

.subtitle {
  color: #909399;
  margin-bottom: 20px;
}

.config-card,
.test-card,
.info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.result-box {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
}

.result-box pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

h3 {
  color: #606266;
  margin-bottom: 15px;
}
</style>
