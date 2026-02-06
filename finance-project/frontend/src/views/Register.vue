<template>
  <div class="register-container">
    <!-- 背景装饰 -->
    <div class="background-decoration"></div>

    <!-- 注册卡片 -->
    <div class="register-card">
      <!-- Logo区域 -->
      <div class="register-logo">
        <h1>MyFinancePal</h1>
        <p>创建您的个人账户</p>
      </div>

      <!-- 注册表单 -->
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="0px"
        class="register-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（2-20个字符）"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <!-- 手机号输入区域 -->
        <el-form-item prop="phone">
          <div class="phone-input-container">
            <el-input
              v-model="registerForm.phone"
              placeholder="请输入手机号（11位）"
              prefix-icon="Phone"
              size="large"
              maxlength="11"
              :disabled="phoneVerified"
            />
            <el-button
              type="primary"
              :disabled="sendCodeDisabled"
              :loading="sendingCode"
              @click="handleSendCode"
              class="send-code-btn"
            >
              {{ sendCodeText }}
            </el-button>
          </div>
        </el-form-item>

        <!-- 验证码输入区域 -->
        <el-form-item v-if="showVerificationCode" prop="verificationCode">
          <div class="verification-code-container">
            <el-input
              v-model="registerForm.verificationCode"
              placeholder="请输入4位验证码"
              prefix-icon="Message"
              size="large"
              maxlength="4"
              :disabled="phoneVerified"
            />
            <el-button
              type="success"
              :disabled="verifyCodeDisabled"
              :loading="verifyingCode"
              @click="handleVerifyCode"
              class="verify-code-btn"
            >
              验证
            </el-button>
          </div>
          <div v-if="countdown > 0" class="countdown-text">
            验证码已发送，{{ countdown }}秒后可重新获取
          </div>
          <div v-else-if="showVerificationCode" class="hint-text">
            请查收短信验证码
          </div>
        </el-form-item>

        <!-- 手机验证状态显示 -->
        <el-form-item v-if="phoneVerified">
          <div class="verified-info">
            <el-icon color="success" style="margin-right: 8px;">
              <Check />
            </el-icon>
            <span>手机号已验证</span>
          </div>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请设置密码（至少6位）"
            prefix-icon="Lock"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            prefix-icon="Lock"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="agreement">
          <el-checkbox v-model="registerForm.agreement">
            我已阅读并同意
            <el-link type="primary">《用户服务协议》</el-link>
            和
            <el-link type="primary">《隐私政策》</el-link>
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="register-btn"
            :loading="registerLoading"
            :disabled="!phoneVerified"
            @click="handleRegister"
          >
            {{ phoneVerified ? '注册' : '请先验证手机号' }}
          </el-button>
        </el-form-item>

        <el-form-item class="login-link">
          <span>已有账号？</span>
          <el-link type="primary" @click="handleGoToLogin">立即登录</el-link>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { Check } from '@element-plus/icons-vue'
import { sendVerifyCode, verifyCode} from '@/api/verification'

const router = useRouter()
const userStore = useUserStore()

// 注册表单
const registerFormRef = ref(null)
const registerForm = reactive({
  username: '',
  phone: '',
  password: '',
  confirmPassword: '',
  verificationCode: '',
  agreement: false,
})

// 状态管理
const showVerificationCode = ref(false)
const phoneVerified = ref(false)
const sendingCode = ref(false)
const verifyingCode = ref(false)
const countdown = ref(0)
const countdownTimer = ref(null)

// 计算属性
const sendCodeDisabled = computed(() => {
  return !registerForm.phone || !/^1[3-9]\d{9}$/.test(registerForm.phone) || 
         phoneVerified.value || countdown.value > 0
})

const verifyCodeDisabled = computed(() => {
  return !registerForm.verificationCode || 
         registerForm.verificationCode.length !== 4 || 
         phoneVerified.value
})

const sendCodeText = computed(() => {
  if (countdown.value > 0) {
    return `${countdown.value}秒后重发`
  }
  return '发送验证码'
})

// 注册验证规则
const registerRules = reactive({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在2到20个字符之间', trigger: 'blur' },
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请输入手机号'))
        } else if (!/^1[3-9]\d{9}$/.test(value)) {
          callback(new Error('请输入有效的11位手机号'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  verificationCode: [
    {
      validator: (rule, value, callback) => {
        if (showVerificationCode.value && !phoneVerified.value) {
          if (!value) {
            callback(new Error('请输入验证码'))
          } else if (value.length !== 4) {
            callback(new Error('验证码为4位数字'))
          } else {
            callback()
          }
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  password: [
    { required: true, message: '请设置密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  agreement: [
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error('请阅读并同意用户协议和隐私政策'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
})

// 发送验证码
const handleSendCode = async () => {
  try {
    // 验证手机号格式
    if (!/^1[3-9]\d{9}$/.test(registerForm.phone)) {
      ElMessage.error('请输入有效的手机号')
      return
    }

    sendingCode.value = true
    
    // 调用后端发送验证码API
    // 注意：sendVerifyCode函数需要一个对象参数，包含phone和type
    const response = await sendVerifyCode({
      phone: registerForm.phone,
      type: 1  // 1表示注册登录类型
    })
    
    // 发送成功，移除setTimeout模拟延迟
    sendingCode.value = false
    showVerificationCode.value = true
    startCountdown(60)
    
    if (response && response.data && response.data.message) {
      ElMessage.success(response.data.message)
    } else {
      ElMessage.success('验证码已发送，请查收短信')
    }
    
  } catch (error) {
    sendingCode.value = false
    console.error('发送验证码失败:', error)
  }
}

// 验证验证码
const handleVerifyCode = async () => {
  try {
    // 验证验证码格式
    if (!registerForm.verificationCode || registerForm.verificationCode.length !== 4) {
      ElMessage.error('请输入4位验证码')
      return
    }

    verifyingCode.value = true
    
    // 调用后端验证验证码API
    // 注意：verifyCode函数需要一个对象参数 {phone, verify_code}
    const response = await verifyCode({
      phone: registerForm.phone,
      verify_code: registerForm.verificationCode
    })
    
    // 移除setTimeout模拟延迟
    verifyingCode.value = false
    
    // 验证成功 - HTTP状态码200会直接到这里
    phoneVerified.value = true
    ElMessage.success('手机号验证成功')
    
    // 清除倒计时
    clearCountdown()
    
  } catch (error) {
    verifyingCode.value = false
    console.error('验证码验证失败:', error)
  }
}

// 开始倒计时
const startCountdown = (seconds) => {
  countdown.value = seconds
  countdownTimer.value = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearCountdown()
    }
  }, 1000)
}

// 清除倒计时
const clearCountdown = () => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
    countdownTimer.value = null
  }
}

// 处理注册
const handleRegister = async () => {
  try {
    // 验证表单
    await registerFormRef.value.validate()
    
    // 确保手机号已验证
    if (!phoneVerified.value) {
      ElMessage.error('请先验证手机号')
      return
    }

    registerLoading.value = true

    // 调用注册API
    const success = await userStore.register({
      username: registerForm.username,
      phone: registerForm.phone,
      password: registerForm.password,
    })

    if (success) {
      // 注册成功，跳转到登录页面
      router.push('/login')
    }
  } catch (error) {
    console.error('注册失败:', error)
    ElMessage.error('注册失败，请检查输入信息')
  } finally {
    registerLoading.value = false
  }
}

// 跳转到登录页面
const handleGoToLogin = () => {
  router.push('/login')
}

// 组件卸载时清除定时器
onUnmounted(() => {
  clearCountdown()
})

// 注册状态
const registerLoading = ref(false)
</script>

<style scoped>
.register-container {
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

.register-card {
  width: 480px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(149, 157, 165, 0.1);
  padding: 40px;
  position: relative;
  z-index: 1;
}

.register-logo {
  text-align: center;
  margin-bottom: 30px;
}

.register-logo h1 {
  color: #409eff;
  font-size: 28px;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.register-logo p {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.register-form {
  width: 100%;
}

.register-form .el-form-item {
  margin-bottom: 20px;
}

/* 手机号输入容器 */
.phone-input-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.send-code-btn {
  width: 120px;
  flex-shrink: 0;
  white-space: nowrap;
}

/* 验证码输入容器 */
.verification-code-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.verify-code-btn {
  width: 80px;
  flex-shrink: 0;
}

/* 倒计时提示 */
.countdown-text {
  font-size: 12px;
  color: #67c23a;
  margin-top: 8px;
}

.hint-text {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

/* 已验证信息 */
.verified-info {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border-radius: 4px;
  border: 1px solid #409eff;
  color: #409eff;
}

.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.register-btn:disabled {
  background-color: #c0c4cc;
  border-color: #c0c4cc;
}

.login-link {
  text-align: center;
  margin-top: 10px;
}

.login-link span {
  color: #666;
  margin-right: 5px;
}

:deep(.el-checkbox) {
  font-size: 14px;
}

:deep(.el-link) {
  font-size: 14px;
}

/* 禁用状态样式 */
:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: #f5f7fa;
  cursor: not-allowed;
}
</style>