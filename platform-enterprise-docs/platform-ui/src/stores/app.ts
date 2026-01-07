import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore(
  'app',
  () => {
    // 状态
    const sidebar = ref({
      opened: true,
      withoutAnimation: false,
    })
    const device = ref<'desktop' | 'mobile'>('desktop')
    const size = ref<'large' | 'default' | 'small'>('default')

    // 计算属性
    const sidebarOpened = computed(() => sidebar.value.opened)

    // 切换侧边栏
    function toggleSidebar(withoutAnimation = false) {
      sidebar.value.opened = !sidebar.value.opened
      sidebar.value.withoutAnimation = withoutAnimation
    }

    // 关闭侧边栏
    function closeSidebar(withoutAnimation = false) {
      sidebar.value.opened = false
      sidebar.value.withoutAnimation = withoutAnimation
    }

    // 切换设备
    function toggleDevice(val: 'desktop' | 'mobile') {
      device.value = val
    }

    // 设置尺寸
    function setSize(val: 'large' | 'default' | 'small') {
      size.value = val
    }

    return {
      sidebar,
      device,
      size,
      sidebarOpened,
      toggleSidebar,
      closeSidebar,
      toggleDevice,
      setSize,
    }
  },
  {
    persist: {
      key: 'platform-app',
      pick: ['sidebar', 'size'],
    },
  }
)
