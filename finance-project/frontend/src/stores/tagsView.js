import { defineStore } from 'pinia'

// 一个很轻量的“标签页导航”全局状态：
// - tabs: [{ key, label, to, affix }]
// - activeKey: 当前激活标签 key
export const useTagsViewStore = defineStore('tagsView', {
  state: () => ({
    tabs: [
      { key: 'home', label: '仪表盘', to: '/', affix: true },
    ],
    activeKey: 'home',
  }),
  actions: {
    _getKeyByRoute(to) {
      return to?.name ? String(to.name) : String(to?.path || '')
    },
    _getLabelByRoute(to) {
      const metaLabel = to?.meta?.tagLabel || to?.meta?.title
      if (metaLabel) return String(metaLabel).split('-')[0].trim()
      if (to?.name) return String(to.name)
      return String(to?.path || '页面')
    },
    ensureTab(to) {
      if (!to) return
      const key = this._getKeyByRoute(to)
      if (!key) return

      // 首页保持 key=home，避免出现两个“/”标签
      if (to.path === '/' || to.name === 'home') {
        this.activeKey = 'home'
        return
      }

      const exists = this.tabs.some((t) => t.key === key)
      if (!exists) {
        this.tabs.push({
          key,
          label: this._getLabelByRoute(to),
          to: to.fullPath || to.path || '/',
          affix: !!to?.meta?.affix,
        })
      }
      this.activeKey = key
    },
    setActiveByRoute(to) {
      if (!to) return
      if (to.path === '/' || to.name === 'home') {
        this.activeKey = 'home'
        return
      }
      const key = this._getKeyByRoute(to)
      if (key) this.activeKey = key
    },
    closeTab(key) {
      const idx = this.tabs.findIndex((t) => t.key === key)
      if (idx === -1) return null
      if (this.tabs[idx].affix) return null

      const wasActive = this.activeKey === key
      this.tabs.splice(idx, 1)

      if (!wasActive) return null

      // 返回应该跳转到的目标（优先左侧标签，否则右侧，否则首页）
      const next = this.tabs[idx - 1] || this.tabs[idx] || this.tabs[0]
      this.activeKey = next?.key || 'home'
      return next?.to || '/'
    },
    closeOthers(key) {
      this.tabs = this.tabs.filter((t) => t.affix || t.key === key)
      this.activeKey = key
    },
    closeAll() {
      this.tabs = this.tabs.filter((t) => t.affix)
      this.activeKey = this.tabs[0]?.key || 'home'
    },
  },
})
