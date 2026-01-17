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
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
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

        <!-- 记住我 -->
        <el-form-item class="login-form-actions">
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

// 登录表单
const loginFormRef = ref(null)
const loginForm = reactive({
  username: '',
  password: '',
  remember: false,
})

// 登录验证规则
const loginRules = reactive({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
})

// 登录状态
const loginLoading = ref(false)

// 处理登录
const handleLogin = async () => {
  try {
    // 表单验证
    await loginFormRef.value.validate()

    loginLoading.value = true

    // 调用真实的登录 API
    const success = await userStore.login({
      username: loginForm.username,
      password: loginForm.password
    })

    if (success) {
      // 记住用户名逻辑
      if (loginForm.remember) {
        localStorage.setItem('rememberUsername', loginForm.username)
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

// 跳转到注册页面
const handleGoToRegister = () => {
  router.push('/register')
}

// 页面挂载初始化
onMounted(() => {
  // 自动填充记住的用户名
  const rememberUsername = localStorage.getItem('rememberUsername')
  if (rememberUsername) {
    loginForm.username = rememberUsername
    loginForm.remember = true
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

/* 记住我样式 */
.login-form-actions {
  display: flex;
  justify-content: flex-start;
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


/* 统一字体样式（与注册页一致） */
:deep(.el-checkbox) {
  font-size: 14px;
}

:deep(.el-link) {
  font-size: 14px;
}
</style>
