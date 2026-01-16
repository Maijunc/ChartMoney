import { createApp } from 'vue'
import App from './App.vue'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
// 3. 导入路由（保留你原有路由配置）
import router from './router'
// 4. 导入Pinia（如果有）
import { createPinia } from 'pinia'

// 创建应用实例
const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
// 5. 全局配置Element Plus，强制中文
app.use(ElementPlus, {
  locale: zhCn, // 核心：绑定中文语言包
})
// 6. 挂载路由和Pinia（保留原有配置）
app.use(router)
app.use(createPinia())
// 7. 挂载应用
app.mount('#app')
