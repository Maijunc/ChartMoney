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

        <el-form-item prop="phone">
          <el-input
            v-model="registerForm.phone"
            placeholder="请输入手机号（11位）"
            prefix-icon="Phone"
            size="large"
            maxlength="11"
          />
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
            @click="handleRegister"
          >
            注册
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 注册表单
const registerFormRef = ref(null)
const registerForm = reactive({
  username: '',
  phone: '',  // 改为 phone，匹配后端字段（仅支持手机号）
  password: '',
  confirmPassword: '',
  agreement: false,
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
      pattern: /^1[3-9]\d{9}$/,
      message: '请输入有效的11位手机号',
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

// 注册状态
const registerLoading = ref(false)

// 处理注册
const handleRegister = async () => {
  try {
    // 表单验证
    await registerFormRef.value.validate()

    registerLoading.value = true

    // 调用真实的注册 API
    const success = await userStore.register({
      username: registerForm.username,
      phone: registerForm.phone,
      password: registerForm.password
    })

    if (success) {
      // 注册成功，跳转到登录页面
      router.push('/login')
    }
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    registerLoading.value = false
  }
}

// 跳转到登录页面
const handleGoToLogin = () => {
  router.push('/login')
}
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
  width: 450px;
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

.captcha-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
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
</style>
