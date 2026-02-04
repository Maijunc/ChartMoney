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
        <!-- 未登录状态：显示登录按钮 -->
        <template v-if="!userStore.isLogin">
          <el-button
            type="primary"
            size="small"
            icon="User"
            @click="handleGoToLogin"
            style="padding: 6px 12px; height: 32px"
          >
            登录/注册
          </el-button>
        </template>

        <!-- 已登录状态：显示用户名、头像和退出按钮 -->
        <template v-else>
          <span style="font-size: 14px; color: #606266">{{ userStore.username }}</span>
          <el-avatar :size="32" :src="userStore.avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <el-button
            type="danger"
            size="small"
            icon="SwitchButton"
            @click="handleLogout"
            style="padding: 6px 12px; height: 32px"
          >
            退出登录
          </el-button>
        </template>
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
        <PageTagsNav :paddingTop="10" />

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
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px">
                      <span>导出格式：</span>
                      <el-select v-model="exportFormat" style="width: 140px">
                        <el-option label="CSV" value="csv" />
                        <el-option label="Excel (.xlsx)" value="xlsx" />
                      </el-select>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px">
                      <span>导入策略：</span>
                      <el-select v-model="importStrategy" style="width: 160px">
                        <el-option label="合并（追加导入）" value="merge" />
                        <el-option label="覆盖（清空后导入）" value="replace" />
                      </el-select>
                    </div>
                    <el-button
                      type="primary"
                      icon="Download"
                      @click="exportData"
                      style="margin-right: 10px"
                    >
                      导出所有数据
                    </el-button>
                    <el-upload
                      :show-file-list="false"
                      :http-request="handleImportRequest"
                      :before-upload="beforeImportUpload"
                      accept=".csv,.xlsx"
                      style="display: inline-block"
                    >
                      <el-button type="success" icon="Upload">导入数据</el-button>
                    </el-upload>
                  </el-card>

                  <el-card style="margin-top: 20px">
                    <h3 style="margin-top: 0">数据清理</h3>
                    <el-alert
                      title="警告：此操作将永久删除所有数据，请谨慎操作！"
                      type="warning"
                      :closable="false"
                      style="margin-bottom: 15px"
                    />
                    <el-button
                      type="danger"
                      icon="Delete"
                      @click="handleClearData"
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
import { useUserStore } from '@/stores/user.js'
import useDashboardLogic from '@/stores/dashboardLogic.js'
import { getUserInfo, updateUserInfo, uploadAvatar, exportUserData, importUserData, clearAllData } from '@/api/user'
import {
  User,
  House,
  Coin,
  Goods,
  Tickets,
  DataAnalysis,
  Tools,
  Download,
  Upload,
  Delete,
  SwitchButton
} from '@element-plus/icons-vue'
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

const handleGoToLogin = () => {
  router.push('/login')
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 用户取消退出
  }
}

// 获取dashboard逻辑变量
const { initTrendChart, initCategoryChart } = useDashboardLogic()

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

// 左侧菜单选择：不再维护页面内标签数组，标签页由全局 store 自动维护
const handleMenuSelect = (_key) => {
  // no-op
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
    // 检查用户是否登录
    if (!userStore.isLogin) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }

    currentUserId.value = userStore.userId

    // 直接从userStore读取用户数据（已在App.vue初始化时加载）
    profileForm.username = userStore.username || ''
    profileForm.phone = userStore.phone || ''
    profileForm.avatar = userStore.avatar || ''
    // 昵称、邮箱、签名暂时使用默认值（后端schema需要扩展）
    profileForm.nickname = userStore.username || ''
    profileForm.email = ''
    profileForm.signature = '合理规划，智慧消费'

    // 如果需要最新数据，可以调用API刷新
    try {
      const response = await getUserInfo()
      if (response.code === 200 && response.data) {
        const userData = response.data
        profileForm.username = userData.username || profileForm.username
        profileForm.phone = userData.phone || profileForm.phone
        profileForm.avatar = userData.avatar || profileForm.avatar

        // 同步更新userStore
        userStore.setUserInfo({
          username: userData.username,
          phone: userData.phone,
          avatar: userData.avatar
        })
      }
    } catch (apiError) {
      console.warn('API获取用户信息失败，使用缓存数据:', apiError)
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

      // 同步更新userStore（关键：确保整个应用中的头像一致）
      userStore.setUserInfo({
        phone: profileForm.phone,
        avatar: profileForm.avatar
      })
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
const exportFormat = ref('csv')
const importStrategy = ref('merge')

const getDownloadFilename = (disposition, fallbackName) => {
  if (!disposition) return fallbackName
  const match = /filename=([^;]+)/i.exec(disposition)
  if (!match) return fallbackName
  return match[1].replace(/"/g, '').trim() || fallbackName
}

// 导出数据
const exportData = async () => {
  try {
    ElMessage.info('开始导出数据，请稍候...')

    if (!userStore.isLogin) {
      ElMessage.warning('请先登录')
      return
    }

    const response = await exportUserData(exportFormat.value)
    const blob = response.data

    const fallbackName = `finance_export_${new Date().toISOString().split('T')[0]}.${exportFormat.value}`
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

const beforeImportUpload = (file) => {
  const name = (file.name || '').toLowerCase()
  if (!name.endsWith('.csv') && !name.endsWith('.xlsx')) {
    ElMessage.error('仅支持 CSV 或 XLSX 文件')
    return false
  }
  return true
}

const handleImportRequest = async (options) => {
  try {
    if (!userStore.isLogin) {
      ElMessage.warning('请先登录')
      return
    }

    const response = await importUserData(options.file, importStrategy.value)
    handleImportSuccess(response)
  } catch (error) {
    console.error('导入数据失败:', error)
    ElMessage.error(error.response?.data?.detail || '数据导入失败，请稍后重试')
  }
}

// 导入数据成功处理
const handleImportSuccess = (response) => {
  if (response.code === 200) {
    ElMessage.success(`数据导入成功！账单 ${response.data?.bills_imported ?? 0} 条，预算 ${response.data?.budgets_imported ?? 0} 条`)
  } else {
    ElMessage.error('数据导入失败：' + (response.message || response.msg || '未知错误'))
  }
}

// 清理数据
const handleClearData = async () => {
  const message = '确定要清空所有数据吗？此操作将删除您的所有财务记录，且不可恢复！'

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
      await clearAllData(userId)
      ElMessage.success('所有数据已清空！')
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

        // 自动保存用户信息到后端
        await updateUserInfo({
          phone: profileForm.phone,
          avatar: profileForm.avatar
        })

        // 同步更新userStore（关键：确保顶部导航头像立即更新）
        userStore.setUserInfo({
          avatar: profileForm.avatar
        })
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
