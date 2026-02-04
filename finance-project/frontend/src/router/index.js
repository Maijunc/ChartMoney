import { createRouter, createWebHistory } from 'vue-router'
import testView from '../views/testView.vue' // 测试页面2
import FirstView from '../views/FirstView.vue' // 测试页面1

import HomeView from '../views/HomeView.vue' //首页
import CoinView from '../views/CoinView.vue' // 收入管理
import ExpendView from '../views/ExpendView.vue' // 支出管理
import BudgetView from '../views/BudgetView.vue' // 预算管理
import AnalysisView from '../views/AnalysisView.vue' // 可视化分析
import SettingsView from '../views/SettingsView.vue' //设置页面

import Login from '../views/Login.vue' //登录页面
import Register from '../views/Register.vue' //注册页面

import ApiTestView from '../views/ApiTestView.vue'
import { useTagsViewStore } from '@/stores/tagsView.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/test', //默认页面
      name: 'test',
      component: testView,
      meta: { title: '第二测试页面' },
    },
    {
      path: '/first', //ceshi页面
      name: 'first',
      component: FirstView,
      meta: { title: '第一测试页面' },
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: '首页 - 个人财政支出管理系统' },
    },

    {
      path: '/coin',
      name: 'coin',
      component: CoinView,
      meta: { title: '收入管理 - 个人财政支出管理系统' },
    },
    {
      path: '/expend',
      name: 'expend',
      component: ExpendView,
      meta: { title: '支出管理 - 个人财政支出管理系统' },
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: AnalysisView,
      meta: { title: '可视化分析 - 个人财政支出管理系统' },
    },
    {
      path: '/budget',
      name: 'budget',
      component: BudgetView,
      meta: { title: '预算管理 - 个人财政支出管理系统' },
    },

    {
      path: '/settings', //访问路径
      name: 'settings',
      component: SettingsView,
      meta: { title: '设置 - 个人财政支出管理系统' },
    },
    {
      path: '/register', //访问路径
      name: 'register',
      component: Register,
      meta: { title: '注册页面' },
    },
    {
      path: '/login', //访问路径
      name: 'login',
      component: Login,
      meta: { title: '登录页面' },
    },
    {
    path: '/api-test',
    name: 'apiTest',
    component: ApiTestView,
    meta: { title: 'API服务层测试页面' }
    },
  ],
})

// 路由守卫：设置页面标题
router.beforeEach((to) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
})

// 路由后置：同步“标签页导航”状态
router.afterEach((to) => {
  // Pinia store 需要在 app.use(pinia) 之后才可用；afterEach 触发时一般已就绪
  try {
    const tags = useTagsViewStore()
    tags.ensureTab(to)
  } catch {
    // ignore
  }
})

export default router
