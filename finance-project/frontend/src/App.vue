<template>
  <div class="app-container">
    <div class="card">
      <h1>💰 ChartMoney</h1>
      
      <div class="divider"></div>

      <p class="status-text">
        当前状态：
        <span :class="connectionStatus ? 'success' : 'pending'">
          {{ message }}
        </span>
      </p>

      <el-button 
        type="primary" 
        size="large" 
        @click="testApi" 
        :loading="loading"
      >
        🚀 测试后端连接
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
// 关键点：必须导入 ElMessage 才能弹窗，否则会报错导致白屏
import { ElMessage } from 'element-plus'

const message = ref('等待连接...')
const connectionStatus = ref(false)
const loading = ref(false)

const testApi = async () => {
  loading.value = true
  try {
    // 这里的地址对应你后端的地址
    const res = await axios.get('http://127.0.0.1:8000/')
    
    // 如果成功拿到数据
    message.value = `连接成功！后端说：${res.data.message}`
    connectionStatus.value = true
    
    // 弹出绿色成功提示
    ElMessage.success('后端连接成功，可以开始开发了！')
  } catch (error) {
    // 如果失败
    message.value = '连接失败，请检查后端黑窗口是否开启'
    connectionStatus.value = false
    console.error(error)
    
    // 弹出红色错误提示
    ElMessage.error('连接失败，请按 F12 查看控制台报错')
  } finally {
    loading.value = false
  }
}
</script>

<style>
/* 简单美化一下页面，让它看起来不那么单调 */
.app-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 400px;
}

h1 {
  color: #303133;
  font-size: 24px;
  margin-bottom: 20px;
}

.divider {
  height: 1px;
  background: #ebeef5;
  margin: 20px 0;
}

.status-text {
  margin-bottom: 20px;
  color: #606266;
}

.success {
  color: #67c23a;
  font-weight: bold;
}

.pending {
  color: #e6a23c;
}
</style>