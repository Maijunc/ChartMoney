<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <div
      class="top-nav"
      style="position: fixed; left: 30px; display: flex; align-items: center; gap: 15px"
    >
      <div class="logo">MyFinancePal</div>
      <div class="breadcrumb">仪表盘 / 设置</div>
      <div class="tags-container"></div>
      <div class="user-info" style="display: flex; align-items: center; gap: 10px">
        <!-- 新增的登录按钮 -->
        <el-button
          type="primary"
          size="small"
          icon="User"
          @click="handleGoToLogin"
          style="padding: 6px 12px; height: 32px"
        >
          登录/注册
        </el-button>

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

          <el-menu-item
            index="tools"
            @click="handleJumpToSettings()"
            style="color: rgb(64, 158, 255) !important"
          >
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

        <!-- 补全的设置页面主要内容 -->
        <div class="menu-management-panel">
          <!-- 设置主面板 -->
          <div
            class="settings-panel"
            style="padding: 20px; background: #fff; border-radius: 8px; min-height: 600px"
          >
            <!-- 设置标签页 -->
            <el-tabs v-model="activeSettingsTab" type="card" style="margin-bottom: 20px">
              <el-tab-pane label="个人信息" name="profile">
                <div class="profile-settings">
                  <el-form :model="profileForm" label-width="120px" size="default">
                    <el-form-item label="头像" class="avatar-form-item">
                      <template #label>
                        <span class="avatar-label">头像</span>
                      </template>
                      <div class="avatar-content">
                        <div class="avatar-wrapper">
                          <!-- 关键1：添加ref用于手动触发上传，设置auto-upload为false控制上传时机 -->
                          <el-upload
                            ref="avatarUploadRef"
                            action="/api/upload/avatar"
                            :show-file-list="false"
                            :on-success="handleAvatarSuccess"
                            :on-change="handleAvatarPreview"
                            :auto-upload="false"
                            accept="image/*"
                            class="avatar-upload"
                          >
                            <el-avatar :size="80" :src="profileForm.avatar" class="avatar-img">
                              <el-icon><User /></el-icon>
                            </el-avatar>
                          </el-upload>
                        </div>
                        <!-- 关键2：按钮绑定点击事件，触发上传组件的文件选择弹窗 -->
                        <el-button
                          size="small"
                          type="primary"
                          class="avatar-btn"
                          @click="triggerAvatarUpload"
                        >
                          更换头像
                        </el-button>
                      </div>
                    </el-form-item></el-form
                  >

                  <el-form :model="profileForm" label-width="120px" size="default">
                    <el-form-item label="用户名">
                      <el-input
                        v-model="profileForm.username"
                        placeholder="请输入用户名"
                        disabled
                      />
                    </el-form-item>
                    <el-form-item label="昵称">
                      <el-input v-model="profileForm.nickname" placeholder="请输入昵称" />
                    </el-form-item>
                    <el-form-item label="邮箱">
                      <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
                    </el-form-item>
                    <el-form-item label="手机号">
                      <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
                    </el-form-item>
                    <el-form-item label="个性签名">
                      <el-input
                        v-model="profileForm.signature"
                        type="textarea"
                        :rows="3"
                        placeholder="请输入个性签名"
                      />
                    </el-form-item>

                    <el-form-item>
                      <el-button type="primary" @click="saveProfile">保存修改</el-button>
                      <el-button @click="resetProfileForm">取消</el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </el-tab-pane>

              <el-tab-pane label="账户安全" name="security">
                <div class="security-settings">
                  <el-card
                    v-for="(item, index) in securityItems"
                    :key="index"
                    style="margin-bottom: 15px"
                  >
                    <div
                      class="security-item"
                      style="display: flex; justify-content: space-between; align-items: center"
                    >
                      <div>
                        <h4 style="margin: 0">{{ item.title }}</h4>
                        <p style="margin: 5px 0 0 0; color: #999; font-size: 12px">
                          {{ item.desc }}
                        </p>
                      </div>
                      <el-button
                        type="primary"
                        size="small"
                        @click="handleSecurityOperation(item.type)"
                      >
                        {{ item.buttonText }}
                      </el-button>
                    </div>
                  </el-card>
                </div>
              </el-tab-pane>

              <el-tab-pane label="系统偏好" name="preference">
                <div class="preference-settings">
                  <el-form :model="preferenceForm" label-width="120px">
                    <el-form-item label="主题模式">
                      <el-radio-group v-model="preferenceForm.theme">
                        <el-radio value="light">浅色模式</el-radio>
                        <el-radio value="dark">深色模式</el-radio>
                        <el-radio value="auto">跟随系统</el-radio>
                      </el-radio-group>
                    </el-form-item>
                    <el-form-item label="语言设置">
                      <el-select v-model="preferenceForm.language" placeholder="请选择语言">
                        <el-option label="简体中文" value="zh-CN" />
                        <el-option label="English" value="en-US" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="数据自动备份">
                      <el-switch
                        v-model="preferenceForm.autoBackup"
                        active-text="开启"
                        inactive-text="关闭"
                      />
                    </el-form-item>
                    <el-form-item label="备份频率">
                      <el-select
                        v-model="preferenceForm.backupFrequency"
                        :disabled="!preferenceForm.autoBackup"
                      >
                        <el-option label="每天" value="daily" />
                        <el-option label="每周" value="weekly" />
                        <el-option label="每月" value="monthly" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="通知设置">
                      <el-checkbox-group v-model="preferenceForm.notifications">
                        <el-checkbox label="支出提醒" value="expense" />
                        <el-checkbox label="预算超标提醒" value="budget" />
                        <el-checkbox label="月度总结" value="monthly" />
                        <el-checkbox label="系统更新" value="system" />
                      </el-checkbox-group>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="savePreference">保存设置</el-button>
                      <el-button @click="resetPreferenceForm">恢复默认</el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </el-tab-pane>

              <el-tab-pane label="数据管理" name="data">
                <div class="data-management">
                  <el-card>
                    <h3 style="margin-top: 0">数据备份与恢复</h3>
                    <el-button
                      type="primary"
                      icon="Download"
                      @click="exportData"
                      style="margin-right: 10px"
                    >
                      导出所有数据
                    </el-button>
                    <el-upload
                      action="/api/import/data"
                      :show-file-list="false"
                      :on-success="handleImportSuccess"
                      accept=".json,.csv"
                      style="display: inline-block"
                    >
                      <el-button type="success" icon="Upload">导入数据</el-button>
                    </el-upload>
                  </el-card>

                  <el-card style="margin-top: 20px">
                    <h3 style="margin-top: 0">数据清理</h3>
                    <el-alert
                      title="警告：以下操作将永久删除数据，请谨慎操作！"
                      type="warning"
                      :closable="false"
                      style="margin-bottom: 15px"
                    />
                    <el-button
                      type="danger"
                      icon="Delete"
                      @click="handleClearData('expired')"
                      style="margin-right: 10px"
                    >
                      清理过期数据
                    </el-button>
                    <el-button
                      type="danger"
                      icon="Delete"
                      @click="handleClearData('all')"
                      :loading="clearingData"
                    >
                      清空所有数据
                    </el-button>
                  </el-card>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- 页脚 -->
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
// 修复导入顺序，先导入所有依赖
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import useDashboardLogic from '@/stores/dashboardLogic.js'
import { getUserInfo, updateUserInfo, uploadAvatar, exportUserData, clearExpiredData, clearAllData } from '@/api/user'
import { getBillList } from '@/api/bill'

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

const handleGoToLogin = () => {
  router.push('/login')
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

// 页面挂载初始化图表
onMounted(() => {
  // 增加DOM存在性判断，防止图表初始化失败
  setTimeout(() => {
    initTrendChart()
    initCategoryChart()
  }, 100)

  // 加载用户信息
  loadUserInfo()
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

// ========== 新增的设置页面逻辑 ==========
// 激活的设置标签页
const activeSettingsTab = ref('profile')

// 当前用户ID（从localStorage获取）
const currentUserId = ref(null)

// 个人信息表单
const profileForm = reactive({
  username: '', // 用户名（不可修改）
  nickname: '',
  email: '',
  phone: '',
  signature: '',
  avatar: '',
})

// 加载用户信息
const loadUserInfo = async () => {
  try {
    // 从localStorage获取用户ID
    const userId = localStorage.getItem('userId')
    if (!userId) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }
    currentUserId.value = parseInt(userId)

    const response = await getUserInfo()
    if (response.code === 200 && response.data) {
      const userData = response.data
      profileForm.username = userData.username || ''
      profileForm.phone = userData.phone || ''
      profileForm.avatar = userData.avatar || ''
      // 昵称、邮箱、签名暂时使用默认值（后端schema需要扩展）
      profileForm.nickname = userData.nickname || userData.username
      profileForm.email = userData.email || ''
      profileForm.signature = userData.signature || '合理规划，智慧消费'
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败')
  }
}

// 保存个人信息
const saveProfile = async () => {
  try {
    // 验证必填字段
    if (!profileForm.phone || profileForm.phone.length !== 11) {
      ElMessage.warning('请输入正确的手机号')
      return
    }

    const response = await updateUserInfo({
      phone: profileForm.phone,
      avatar: profileForm.avatar
    })

    if (response.code === 200) {
      ElMessage.success('个人信息保存成功！')
      // 更新localStorage中的用户信息
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
      userInfo.phone = profileForm.phone
      userInfo.avatar = profileForm.avatar
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
    } else {
      ElMessage.error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存用户信息失败:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败，请稍后重试')
  }
}

// 重置个人信息表单
const resetProfileForm = () => {
  loadUserInfo()
  ElMessage.info('已重置为原始数据')
}

// 账户安全设置项
const securityItems = ref([
  {
    title: '修改密码',
    desc: '当前密码强度：中，建议定期更换密码',
    buttonText: '修改',
    type: 'password',
  },
  {
    title: '绑定手机号',
    desc: '已绑定：138****8888',
    buttonText: '更换',
    type: 'phone',
  },
  {
    title: '邮箱验证',
    desc: '已验证：user@example.com',
    buttonText: '重新验证',
    type: 'email',
  },
  {
    title: '登录设备管理',
    desc: '当前登录设备：Chrome浏览器（Windows 10）',
    buttonText: '查看',
    type: 'devices',
  },
  {
    title: '登录保护',
    desc: '未开启，开启后异地登录需要验证',
    buttonText: '开启',
    type: 'loginProtect',
  },
])

// 账户安全操作处理
const handleSecurityOperation = (type) => {
  switch (type) {
    case 'password':
      ElMessage.info('跳转到修改密码页面')
      break
    case 'phone':
      ElMessage.info('跳转到更换手机号页面')
      break
    case 'email':
      ElMessage.info('已发送验证邮件，请查收')
      break
    case 'devices':
      ElMessage.info('查看登录设备列表')
      break
    case 'loginProtect':
      ElMessage.success('登录保护已开启')
      securityItems.value[4].desc = '已开启，异地登录需要验证'
      securityItems.value[4].buttonText = '关闭'
      break
    default:
      break
  }
}

// 系统偏好设置
const preferenceForm = reactive({
  theme: 'light',
  language: 'zh-CN',
  autoBackup: true,
  backupFrequency: 'weekly',
  notifications: ['expense', 'budget', 'monthly'],
})

// 保存系统偏好设置
const savePreference = () => {
  ElMessage.success('系统偏好设置保存成功！')
  // 可以在这里添加主题切换、语言切换等逻辑
}

// 重置系统偏好设置为默认值
const resetPreferenceForm = () => {
  preferenceForm.theme = 'light'
  preferenceForm.language = 'zh-CN'
  preferenceForm.autoBackup = true
  preferenceForm.backupFrequency = 'weekly'
  preferenceForm.notifications = ['expense', 'budget', 'monthly']
  ElMessage.info('已恢复默认设置')
}

// 数据管理相关
const clearingData = ref(false)

// 导出数据
const exportData = async () => {
  try {
    ElMessage.info('开始导出数据，请稍候...')

    const userId = currentUserId.value
    if (!userId) {
      ElMessage.warning('请先登录')
      return
    }

    // 调用导出API
    const response = await exportUserData(userId)

    // 创建下载链接
    const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `财务数据导出_${new Date().toISOString().split('T')[0]}.json`
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

// 导入数据成功处理
const handleImportSuccess = (response) => {
  if (response.code === 200) {
    ElMessage.success('数据导入成功！')
  } else {
    ElMessage.error('数据导入失败：' + response.msg)
  }
}

// 清理数据
const handleClearData = async (type) => {
  const message =
    type === 'expired'
      ? '确定要清理过期数据吗？此操作不可恢复！'
      : '确定要清空所有数据吗？此操作将删除您的所有财务记录，且不可恢复！'

  try {
    await ElMessageBox.confirm(message, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'error',
    })

    clearingData.value = true
    const userId = currentUserId.value

    if (!userId) {
      ElMessage.warning('请先登录')
      clearingData.value = false
      return
    }

    try {
      if (type === 'expired') {
        await clearExpiredData(userId, 365) // 清理一年前的数据
        ElMessage.success('过期数据清理完成！')
      } else {
        await clearAllData(userId)
        ElMessage.success('所有数据已清空！')
      }
    } catch (error) {
      console.error('清理数据失败:', error)
      ElMessage.error(error.response?.data?.detail || '清理数据失败，请稍后重试')
    } finally {
      clearingData.value = false
    }
  } catch {
    ElMessage.info('已取消数据清理操作')
  }
}
// 新增：获取上传组件的ref
const avatarUploadRef = ref(null)

// 关键3：触发上传组件的文件选择弹窗

const triggerAvatarUpload = () => {
  if (avatarUploadRef.value) {
    // 方案1：兼容Element Plus 2.x版本
    const uploadInput = avatarUploadRef.value.$el.querySelector('input[type="file"]')
    // 方案2：兼容Element Plus 3.x版本（备用）
    // const uploadInput = avatarUploadRef.value.$refs.upload?.querySelector('input[type="file"]')

    if (uploadInput) {
      // 清空原有值，避免重复选择同一张图片不触发change事件
      uploadInput.value = ''
      // 手动触发文件选择框
      uploadInput.click()
    } else {
      ElMessage.warning('上传组件初始化失败，请刷新页面重试')
    }
  }
}

// 关键4：新增本地预览逻辑（选择文件后立即显示，无需等上传成功）
const handleAvatarPreview = async (uploadFile) => {
  if (uploadFile.raw) {
    // 生成本地临时URL，实现即时预览
    profileForm.avatar = URL.createObjectURL(uploadFile.raw)

    // 自动上传到后端
    try {
      ElMessage.info('正在上传头像...')
      const response = await uploadAvatar(uploadFile.raw)

      if (response.code === 200 && response.data?.url) {
        profileForm.avatar = response.data.url
        ElMessage.success('头像上传成功！')

        // 自动保存用户信息
        await updateUserInfo({
          phone: profileForm.phone,
          avatar: profileForm.avatar
        })

        // 更新localStorage
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
        userInfo.avatar = profileForm.avatar
        localStorage.setItem('userInfo', JSON.stringify(userInfo))
      }
    } catch (error) {
      console.error('头像上传失败:', error)
      ElMessage.error('头像上传失败，请稍后重试')
      // 保留本地预览
    }
  }
}

// 优化：原有上传成功处理函数（兼容本地预览和后端返回）
const handleAvatarSuccess = (response, uploadFile) => {
  // 1. 优先处理后端返回的URL（正式环境）
  if (response.code === 200 && response.data?.url) {
    profileForm.avatar = response.data.url
    ElMessage.success('头像上传成功！')
  }
  // 2. 兼容后端直接返回URL的情况
  else if (typeof response === 'string') {
    profileForm.avatar = response
    ElMessage.success('头像上传成功！')
  }
  // 3. 保留本地预览兜底（即使后端接口未通，也能看到图片）
  else if (uploadFile.raw) {
    profileForm.avatar = URL.createObjectURL(uploadFile.raw)
    ElMessage.info('头像预览成功（需要保存后生效）')
  }
}
</script>

<style scoped>
@import '../styles/framework.css';
@import '../styles/finance-dashboard.css';

/* 设置页面样式补充 */
.settings-panel {
  margin-top: 20px;
}

.security-item {
  padding: 10px 0;
}

.page-tag-item {
  margin-right: 8px;
  cursor: pointer;
}

.avatar-label {
  display: inline-block;
  width: 120px; /* 与label-width="120px"匹配 */
  text-align: right;
  padding-right: 12px;
  line-height: 32px; /* 与其他表单项标签行高一致（关键！） */
  box-sizing: border-box;
  padding-top: 20px;
  font-size: 14px;
}

/* 头像内容容器 - 模拟输入框的margin和对齐 */
.avatar-content {
  display: inline-flex; /* 关键：用inline-flex而非flex，匹配输入框的行内特性 */
  align-items: center;
  gap: 12px;
  margin-left: 0; /* 清除额外间距 */
  vertical-align: middle;
}

.avatar-wrapper {
  display: inline-block;
  vertical-align: middle;
}

.avatar-img {
  width: 80px;
  height: 80px;
  display: inline-block;
  vertical-align: middle;
}

.avatar-btn {
  margin: 0; /* 清除默认margin */
  vertical-align: middle;
  height: 32px; /* 与其他表单项的输入框高度一致 */
  line-height: 32px;
}

/* 修复Element Plus默认样式的干扰 */
:deep(.avatar-form-item .el-form-item__content) {
  margin-left: 0 !important; /* 取消默认的margin-left，完全手动控制 */
  display: inline-block;
  vertical-align: middle;
}

:deep(.avatar-form-item .el-form-item__label) {
  float: none !important; /* 取消标签浮动 */
  display: inline-block;
  vertical-align: middle;
  line-height: 32px !important; /* 强制和其他标签行高一致 */
  height: auto !important;
}
.avatar-upload {
  cursor: pointer; /* 提示可点击 */
  position: relative;
  z-index: 1;
}
</style>
