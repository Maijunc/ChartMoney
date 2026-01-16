<template>
  <div class="login-container">
    <!-- 背景装饰（与注册页保持一致） -->
    <div class="background-decoration"></div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- Logo区域 -->
      <div class="login-logo">
        <h1>MyFinancePal</h1>
        <p>个人财务管理系统</p>
      </div>

      <!-- 登录表单 -->
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="0px"
        class="login-form"
      >
        <el-form-item prop="account">
          <el-input
            v-model="loginForm.account"
            placeholder="请输入用户名/手机号/邮箱"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <!-- 可选验证码（登录失败后显示） -->
        <el-form-item prop="captcha" v-if="showCaptcha">
          <div class="captcha-container">
            <el-input
              v-model="loginForm.captcha"
              placeholder="请输入验证码"
              prefix-icon="Picture"
              size="large"
              style="width: 70%"
            />
            <div class="captcha-img" @click="refreshCaptcha">
              {{ captchaCode }}
            </div>
          </div>
        </el-form-item>

        <!-- 记住密码 & 忘记密码 -->
        <el-form-item class="login-form-actions">
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
          <el-link type="primary" @click="showForgetPassword = true">忘记密码？</el-link>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loginLoading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>

        <!-- 注册链接 -->
        <el-form-item class="register-link">
          <span>还没有账号？</span>
          <el-link type="primary" @click="handleGoToRegister">立即注册</el-link>
        </el-form-item>
      </el-form>
    </div>

    <!-- 忘记密码弹窗 -->
    <el-dialog v-model="showForgetPassword" title="找回密码" width="400px" center>
      <el-form :model="forgetForm" label-width="80px">
        <el-form-item label="手机号/邮箱">
          <el-input v-model="forgetForm.account" placeholder="请输入注册的手机号或邮箱" />
        </el-form-item>
        <el-form-item label="验证码">
          <div class="captcha-container">
            <el-input
              v-model="forgetForm.captcha"
              placeholder="请输入验证码"
              size="default"
              style="width: 70%"
            />
            <el-button
              type="primary"
              @click="sendResetCaptcha"
              :disabled="resetCaptchaDisabled"
              size="small"
            >
              {{ resetCaptchaText }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input
            v-model="forgetForm.newPassword"
            type="password"
            placeholder="请输入新密码（至少6位）"
          />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="forgetForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForgetPassword = false">取消</el-button>
        <el-button type="primary" @click="handleResetPassword">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

// 登录表单
const loginFormRef = ref(null)
const loginForm = reactive({
  account: '',
  password: '',
  captcha: '',
  remember: false,
})

// 登录验证规则
const loginRules = reactive({
  account: [{ required: true, message: '请输入用户名/手机号/邮箱', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码长度为4位', trigger: 'blur' },
  ],
})

// 验证码相关（登录失败后显示）
const showCaptcha = ref(false)
const captchaCode = ref('8888')
const refreshCaptcha = () => {
  // 生成随机4位数字验证码
  captchaCode.value = Math.floor(1000 + Math.random() * 9000).toString()
}

// 登录状态
const loginLoading = ref(false)

// 忘记密码弹窗
const showForgetPassword = ref(false)
const forgetForm = reactive({
  account: '',
  captcha: '',
  newPassword: '',
  confirmPassword: '',
})

// 找回密码验证码倒计时
const resetCaptchaDisabled = ref(false)
const resetCaptchaText = ref('获取验证码')
let resetCaptchaTimer = null

// 发送找回密码验证码
const sendResetCaptcha = () => {
  if (!forgetForm.account) {
    ElMessage.warning('请输入手机号/邮箱')
    return
  }

  // 简单验证账号格式
  const phoneReg = /^1[3-9]\d{9}$/
  const emailReg = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!phoneReg.test(forgetForm.account) && !emailReg.test(forgetForm.account)) {
    ElMessage.warning('请输入有效的手机号或邮箱')
    return
  }

  // 模拟发送验证码
  resetCaptchaDisabled.value = true
  let count = 60
  resetCaptchaText.value = `${count}秒后重新获取`

  resetCaptchaTimer = setInterval(() => {
    count--
    resetCaptchaText.value = `${count}秒后重新获取`

    if (count <= 0) {
      clearInterval(resetCaptchaTimer)
      resetCaptchaDisabled.value = false
      resetCaptchaText.value = '获取验证码'
    }
  }, 1000)

  ElMessage.success('验证码已发送，请注意查收')
}

// 重置密码
const handleResetPassword = () => {
  if (!forgetForm.account) {
    ElMessage.warning('请输入手机号/邮箱')
    return
  }

  if (!forgetForm.captcha) {
    ElMessage.warning('请输入验证码')
    return
  }

  if (!forgetForm.newPassword || forgetForm.newPassword.length < 6) {
    ElMessage.warning('请设置至少6位的新密码')
    return
  }

  if (forgetForm.newPassword !== forgetForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  // 模拟重置密码请求
  ElMessage.success('密码重置成功，请使用新密码登录')
  showForgetPassword.value = false
  // 清空密码框
  loginForm.password = ''
}

// 处理登录
const handleLogin = async () => {
  try {
    // 表单验证
    await loginFormRef.value.validate()

    // 模拟验证码验证（如果显示了验证码）
    if (showCaptcha.value && loginForm.captcha.toLowerCase() !== captchaCode.value.toLowerCase()) {
      ElMessage.error('验证码错误')
      refreshCaptcha()
      return
    }

    loginLoading.value = true

    // 模拟登录请求
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // 登录成功逻辑
    ElMessage.success('登录成功')

    // 记住密码逻辑（实际项目中可加密存储）
    if (loginForm.remember) {
      localStorage.setItem('rememberAccount', loginForm.account)
    } else {
      localStorage.removeItem('rememberAccount')
    }

    // 跳转到首页
    router.push('/')
  } catch (error) {
    console.error('登录验证失败:', error)
    // 验证失败时显示验证码
    if (!showCaptcha.value) {
      showCaptcha.value = true
      refreshCaptcha()
    }
  } finally {
    loginLoading.value = false
  }
}

// 跳转到注册页面
const handleGoToRegister = () => {
  router.push('/register')
}

// 页面挂载初始化
onMounted(() => {
  // 自动填充记住的账号
  const rememberAccount = localStorage.getItem('rememberAccount')
  if (rememberAccount) {
    loginForm.account = rememberAccount
    loginForm.remember = true
  }

  // 初始化验证码
  refreshCaptcha()
})

// 组件卸载时清除定时器
onUnmounted(() => {
  if (resetCaptchaTimer) {
    clearInterval(resetCaptchaTimer)
  }
})
</script>

<style scoped>
/* 整体布局与注册页保持一致 */
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

/* 背景装饰（与注册页完全相同） */
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

/* 登录卡片（尺寸略小于注册卡，更紧凑） */
.login-card {
  width: 400px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(149, 157, 165, 0.1);
  padding: 40px;
  position: relative;
  z-index: 1;
}

/* Logo区域（与注册页风格统一） */
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

/* 表单样式 */
.login-form {
  width: 100%;
}

.login-form .el-form-item {
  margin-bottom: 20px;
}

/* 验证码容器 */
.captcha-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 验证码图片样式 */
.captcha-img {
  width: 30%;
  height: 40px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #409eff;
  font-size: 16px;
  letter-spacing: 4px;
  cursor: pointer;
  user-select: none;
}

/* 记住密码 & 忘记密码布局 */
.login-form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

/* 注册链接 */
.register-link {
  text-align: center;
  margin-top: 10px;
}

.register-link span {
  color: #666;
  margin-right: 5px;
}

/* 弹窗样式适配 */
:deep(.el-dialog__body) {
  padding: 20px 20px 10px;
}

:deep(.el-dialog__footer) {
  padding: 10px 20px 20px;
}

/* 统一字体样式（与注册页一致） */
:deep(.el-checkbox) {
  font-size: 14px;
}

:deep(.el-link) {
  font-size: 14px;
}
</style>
