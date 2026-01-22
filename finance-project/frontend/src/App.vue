<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user.js'

const userStore = useUserStore()

// 应用启动时初始化用户信息
onMounted(() => {
  userStore.initUserInfo()
})
</script>

