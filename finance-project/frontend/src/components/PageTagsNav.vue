<template>
  <div class="page-tags" :style="wrapperStyle">
    <el-tag
      v-for="tab in tags.tabs"
      :key="tab.key"
      :closable="!tab.affix"
      @close="onClose(tab.key)"
      @click="onClick(tab)"
      :effect="tags.activeKey === tab.key ? 'dark' : 'light'"
      class="page-tag-item"
    >
      {{ tab.label }}
    </el-tag>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTagsViewStore } from '@/stores/tagsView.js'

const props = defineProps({
  paddingTop: { type: [String, Number], default: 10 },
})

const router = useRouter()
const route = useRoute()
const tags = useTagsViewStore()

const wrapperStyle = computed(() => ({
  paddingTop: typeof props.paddingTop === 'number' ? `${props.paddingTop}px` : String(props.paddingTop),
}))

// 首次进入页面也确保有对应 tab
tags.ensureTab(route)

const onClick = (tab) => {
  if (!tab?.to) return
  tags.activeKey = tab.key
  router.push(tab.to)
}

const onClose = async (key) => {
  const nextTo = tags.closeTab(key)
  if (nextTo) {
    await router.push(nextTo)
  }
}
</script>

<style scoped>
.page-tag-item {
  margin-right: 8px;
  cursor: pointer;
}
</style>
