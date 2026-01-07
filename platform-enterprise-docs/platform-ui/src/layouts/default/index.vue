<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'
import AppMain from './components/AppMain.vue'

const appStore = useAppStore()

const classObj = computed(() => ({
  hideSidebar: !appStore.sidebarOpened,
  openSidebar: appStore.sidebarOpened,
  mobile: appStore.device === 'mobile',
}))
</script>

<template>
  <div class="app-wrapper" :class="classObj">
    <Sidebar class="sidebar-container" />
    <div class="main-container">
      <Navbar />
      <AppMain />
    </div>
  </div>
</template>

<style scoped lang="scss">
.app-wrapper {
  position: relative;
  width: 100%;
  height: 100%;

  &.mobile.openSidebar {
    position: fixed;
    top: 0;
  }
}

.sidebar-container {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 1001;
  width: 210px;
  height: 100%;
  overflow: hidden;
  background-color: #304156;
  transition: width 0.28s;

  .hideSidebar & {
    width: 64px;
  }
}

.main-container {
  position: relative;
  min-height: 100%;
  margin-left: 210px;
  transition: margin-left 0.28s;

  .hideSidebar & {
    margin-left: 64px;
  }
}
</style>
