<template>
  <div class="mine-admin-container">
    <!-- 顶部导航 -->
    <AppTopNav :breadcrumb="[{ label: '仪表盘', to: '/' }, { label: '支出管理' }]" />

    <!-- 主体区域 -->
    <div class="main-content">
      <!-- 左侧菜单 -->
      <div class="sidebar">
        <el-menu default-active="menu-management" class="sidebar-menu" @select="handleMenuSelect">
          <el-menu-item index="dashboard">
            <template #title>
              <el-icon><House /></el-icon>
              <span>首页</span>
            </template>
          </el-menu-item>

          <el-menu-item index="Coin">
            <template #title>
              <el-icon><Coin /></el-icon>
              <span>收入管理</span>
            </template>
          </el-menu-item>

          <!-- 支出管理作为父级折叠菜单，包含信用卡借入记录子项 -->
          <el-sub-menu index="Goods">
            <template #title>
              <el-icon><Goods /></el-icon>
              <span>支出管理</span>
            </template>

            <el-menu-item index="CreditCard">
              <el-icon><CreditCard /></el-icon>
              <span>信用卡记录</span>
            </el-menu-item>

            <el-menu-item index="DailyExpense" @click="handleJumpToExpend()">
              <el-icon><Wallet /></el-icon>
              <span>日常支出</span>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item index="Tickets">
            <template #title>
              <el-icon><Tickets /></el-icon>
              <span>购物预算管理</span>
            </template>
          </el-menu-item>

          <el-menu-item index="data">
            <template #title>
              <el-icon><DataAnalysis /></el-icon>
              <span>消费年度总结</span>
            </template>
          </el-menu-item>

          <el-menu-item index="tools">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>设置</span>
            </template>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 右侧内容区 -->
      <div class="content-panel">
        <!-- 标签页导航（顶部小标签） -->
        <PageTagsNav :paddingTop="60" />

        <!-- 菜单管理内容 -->
        <div class="menu-management-panel">
          <!-- 搜索区域 -->
          <div class="search-bar">
            <el-form :inline="false" @submit.prevent="onSearch">
              <el-form-item label="创建时间">
                <el-date-picker
                  v-model="searchForm.createTime"
                  type="date"
                  placeholder="开始日期"
                  style="width: 200px"
                />
              </el-form-item>
              <el-form-item label="消费种类">
                <el-select
                  v-model="searchForm.type"
                  placeholder="请选择消费种类"
                  style="width: 200px"
                  clearable
                >
                  <!-- 子选项列表 -->
                  <el-option label="餐饮美食" value="餐饮美食" />
                  <el-option label="交通出行" value="交通出行" />
                  <el-option label="居住房租" value="居住房租" />
                  <el-option label="购物消费" value="购物消费" />
                  <el-option label="休闲娱乐" value="休闲娱乐" />
                  <el-option label="医疗健康" value="医疗健康" />
                </el-select>
              </el-form-item>

              <el-form-item label="消费名称">
                <el-input v-model="searchForm.name" placeholder="请输入消费名称" />
              </el-form-item>

              <div style="display: block; width: 100%">
                <el-form-item label="消费金额">
                  <el-input
                    v-model="searchForm.money"
                    placeholder="请输入消费金额"
                    type="number"
                    min="0"
                    step="0.01"
                    @input="handleMoneyInput"
                    style="width: 300px"
                  />
                </el-form-item>

                <el-form-item label="备&nbsp&nbsp&nbsp注" label-width="84px">
                  <el-input
                    v-model="searchForm.extra"
                    placeholder="无"
                    maxlength="80"
                    show-word-limit
                    :word-limit-format="(used, total) => `${used}/${total} 字`"
                    style="width: 100%"
                  />
                </el-form-item>
              </div>
              <el-form-item style="margin-left: auto; margin-bottom: 0; margin-right: 165px">
                <el-button type="primary" @click="onSearch">提交</el-button>
                <el-button @click="onReset">清空</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 菜单表格 -->
          <el-table :data="menuList" border style="width: 100%">
            <el-table-column prop="time" label="日期" al width="100" ign="center" />
            <el-table-column prop="icon" label="图标" width="60" align="center">
              <template #default="scope">
                <!-- 表格图标改为字符串匹配（全局注册后直接使用组件名） -->
                <el-icon :size="20">
                  <component :is="scope.row.iconName" />
                </el-icon>
              </template>
            </el-table-column>

            <el-table-column prop="type" label="消费种类" width="90%" align="center" />

            <el-table-column prop="name" label="消费名称" align="center" />
            <el-table-column prop="money" label="消费金额" width="100%" align="center" />
            <el-table-column prop="extra" label="备注" align="center" />

            <el-table-column label="操作" width="120" align="center">
              <template #default>
                <el-button type="text" size="small">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
                <el-button type="danger" size="small">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageTagsNav from '@/components/PageTagsNav.vue'

const router = useRouter()
const handleJumpToExpend = () => {
  router.push('/expend')
}

// 搜索表单
const searchForm = ref({
  type: '',
  name: '',
  money: '',
  extra: '',
  createTime: [],
})

// 菜单列表数据
const menuList = ref([
  {
    time: '2026-01-09',
    iconName: 'ShoppingTrolley', // 改为字符串（对应全局注册的图标组件名）
    type: '购物消费',
    name: '银行卡',
    money: '10000',
    extra: '10月3日之前还清',
  },
  {
    time: '2026-01-10',
    iconName: 'Van',
    type: '交通出行',
    name: '公交车',
    money: '200',
    extra: '无',
  },
  {
    time: '2026-01-19',
    iconName: 'House',
    type: '居住房租',
    name: '月租',
    money: '1400',
    extra: '无',
  },
  {
    time: '2026-01-02',
    iconName: 'FirstAidKit',
    type: '医疗健康',
    name: '医保',
    money: '389',
    extra: '无',
  },
])

// 左侧菜单选择（保留：这里只做激活标签页显示用途；真正的标签页导航由 PageTagsNav + router.afterEach 驱动）
const handleMenuSelect = (key) => {
  // 这里不做标签数组维护，真正的标签由路由驱动
}

// 过滤消费金额：只保留非负的数字和一个小数点
const handleMoneyInput = () => {
  searchForm.value.money = searchForm.value.money
    .replace(/[^0-9.]/g, '') // 移除所有非数字、非小数点的字符
    .replace(/^\./, '') // 移除开头的小数点（避免.123这种格式）
    .replace(/\.{2,}/g, '.') // 多个小数点只保留第一个
    .replace(/^0+(\d)/, '$1') // 移除开头多余的0（避免00123这种格式）
    .replace(/(\.\d{2}).*/g, '$1') // 可选：限制小数点后最多2位（金额精确到分）
}

onMounted(() => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  searchForm.value.createTime = `${year}-${month}-${day}`
})

// 搜索提交
const onSearch = () => {
  console.log('搜索参数：', searchForm.value)
}

// 搜索清空
const onReset = () => {
  searchForm.value = {
    type: '',
    name: '',
    money: '',
    extra: '',
    createTime: [],
  }
}
</script>

<style scoped>
@import '../styles/framework.css'; /* 导入外部CSS文件，通过@import方式并保留scoped */
</style>
