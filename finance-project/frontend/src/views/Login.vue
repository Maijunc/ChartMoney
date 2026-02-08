<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="background-decoration"></div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- Logo区域 -->
      <div class="login-logo">
        <h1>MyFinancePal</h1>
        <p>个人财务管理系统</p>
      </div>

      <!-- 登录方式切换 -->
      <div class="login-type-switch">
        <el-radio-group v-model="loginType" size="large">
          <el-radio-button label="password">密码登录</el-radio-button>
          <el-radio-button label="sms">手机号登录</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 密码登录表单 -->
      <el-form
        v-if="loginType === 'password'"
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="0px"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="passwordForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="passwordForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            @keyup.enter="handlePasswordLogin"
          />
        </el-form-item>

        <!-- 记住我 -->
        <el-form-item class="login-form-actions">
          <el-checkbox v-model="passwordForm.remember">记住我</el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loginLoading"
            @click="handlePasswordLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 手机号登录表单 -->
      <el-form
        v-else
        ref="smsFormRef"
        :model="smsForm"
        :rules="smsRules"
        label-width="0px"
        class="login-form"
      >
        <el-form-item prop="phone">
          <el-input
            v-model="smsForm.phone"
            placeholder="请输入手机号"
            prefix-icon="Iphone"
            size="large"
            maxlength="11"
          >
            <template #prefix>
              <div class="phone-prefix">
                <el-icon><Iphone /></el-icon>
                <span class="country-code">+86</span>
              </div>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="code" class="sms-code-item">
          <el-input
            v-model="smsForm.code"
            placeholder="请输入验证码"
            prefix-icon="Message"
            size="large"
            maxlength="4"
            @keyup.enter="handleSmsLogin"
          />
          <el-button
            :disabled="countdown > 0 || !smsForm.phone"
            @click="sendSmsCode"
            class="sms-btn"
          >
            {{ countdown > 0 ? `${countdown}秒后重发` : '获取验证码' }}
          </el-button>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loginLoading"
            @click="handleSmsLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 注册链接 -->
      <div class="register-link">
        <span>还没有账号？</span>
        <el-link type="primary" @click="handleGoToRegister">立即注册</el-link>
      </div>

      <!-- 快速切换 -->
      <div v-if="loginType === 'sms'" class="quick-switch">
        <el-link type="info" @click="loginType = 'password'">
          使用密码登录
        </el-link>
      </div>
      <div v-else class="quick-switch">
        <el-link type="info" @click="loginType = 'sms'">
          使用手机号登录
        </el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Iphone, Message } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { sendVerifyCode, verifyCode } from '@/api/verification'
// import { getUserByPhone } from '@/api/auth' // 假设有这个API

const router = useRouter()
const userStore = useUserStore()

// 登录类型：password-密码登录，sms-手机号登录
const loginType = ref('password')

// 密码登录表单
const passwordFormRef = ref(null)
const passwordForm = reactive({
  username: '',
  password: '',
  remember: false,
})

// 手机号登录表单
const smsFormRef = ref(null)
const smsForm = reactive({
  phone: '',
  code: '',
})

// 验证码倒计时
const countdown = ref(0)
let countdownTimer = null

// 密码登录验证规则
const passwordRules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
})

// 手机号登录验证规则
const smsRules = reactive({
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'change' },
    { pattern: /^\d{4}$/, message: '验证码为4位数字', trigger: 'blur' }
  ]
})

// 登录状态
const loginLoading = ref(false)

// 发送短信验证码
const sendSmsCode = async () => {
  try {
    // 1. 先验证手机号字段
    try {
      await smsFormRef.value.validateField('phone')
    } catch {
      return
    }

    // 2. 调用发送验证码的API
    const response = await sendVerifyCode({
      phone: smsForm.phone,
      type: 1
    })

    // 3. 根据后端返回的实际情况调整判断逻辑
    if (response.success === false) {
      ElMessage.error(response.message || '发送验证码失败')
      return
    }

    // 4. 发送成功
    ElMessage.success('验证码已发送，请注意查收')

    // 5. 开始倒计时
    countdown.value = 60
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownTimer)
      }
    }, 1000)

  } catch (error) {
    console.error('发送验证码失败:', error)
    ElMessage.error('发送验证码失败，请重试')
  }
}

// 处理密码登录
const handlePasswordLogin = async () => {
  try {
    await passwordFormRef.value.validate()

    loginLoading.value = true

    // 调用真实的登录 API
    const success = await userStore.login({
      username: passwordForm.username,
      password: passwordForm.password
    })

    if (success) {
      // 记住用户名逻辑
      if (passwordForm.remember) {
        localStorage.setItem('rememberUsername', passwordForm.username)
      } else {
        localStorage.removeItem('rememberUsername')
      }

      // 跳转到首页
      router.push('/')
    }
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loginLoading.value = false
  }
}

// 处理手机号登录
const handleSmsLogin = async () => {
  try {
    // 1. 表单验证
    await smsFormRef.value.validate()

    loginLoading.value = true

    // 调用真实的登录 API
    const success = await userStore.login_by_phone({
      phone: smsForm.phone,
      code: smsForm.code
    })

    if (success) {
      // 跳转到首页
      router.push('/')
    }
  } catch (error) {
    console.error('验证码错误或者手机不存在')
  } finally {
    loginLoading.value = false
  }
}

// 跳转到注册页面
const handleGoToRegister = () => {
  router.push('/register')
}

// 组件卸载时清除定时器
import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})

// 页面挂载初始化
onMounted(() => {
  // 自动填充记住的用户名
  const rememberUsername = localStorage.getItem('rememberUsername')
  if (rememberUsername) {
    passwordForm.username = rememberUsername
    passwordForm.remember = true
  }
})
</script>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #e8f4f8 0%, #f0f8fb 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    radial-gradient(circle at 30% 20%, rgba(64, 158, 255, 0.05) 0%, transparent 40%),
    radial-gradient(circle at 70% 80%, rgba(64, 158, 255, 0.05) 0%, transparent 40%);
  z-index: 0;
}

.login-card {
  width: 420px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(149, 157, 165, 0.1);
  padding: 40px;
  position: relative;
  z-index: 1;
}

.login-logo {
  text-align: center;
  margin-bottom: 30px;
}

.login-logo h1 {
  color: #409eff;
  font-size: 28px;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.login-logo p {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.login-type-switch {
  margin-bottom: 30px;
  text-align: center;
}

.login-type-switch :deep(.el-radio-group) {
  display: flex;
}

.login-type-switch :deep(.el-radio-button) {
  flex: 1;
}

.login-type-switch :deep(.el-radio-button__inner) {
  width: 100%;
}

.login-form {
  width: 100%;
}

.login-form .el-form-item {
  margin-bottom: 20px;
}

.login-form-actions {
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.sms-code-item {
  position: relative;
}

.sms-btn {
  position: absolute;
  right: 1px;
  top: 1px;
  height: calc(100% - 2px);
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  color: #409eff;
  font-size: 14px;
  padding: 0 15px;
  min-width: 100px;
}

.sms-btn:disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.phone-prefix {
  display: flex;
  align-items: center;
  gap: 8px;
}

.country-code {
  color: #909399;
  font-size: 14px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.register-link span {
  color: #666;
  margin-right: 5px;
}

.quick-switch {
  text-align: center;
  margin-top: 15px;
}

:deep(.el-checkbox) {
  font-size: 14px;
}

:deep(.el-link) {
  font-size: 14px;
}
</style>