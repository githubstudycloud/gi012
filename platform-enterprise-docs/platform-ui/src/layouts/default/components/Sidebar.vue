<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const isCollapse = computed(() => !appStore.sidebarOpened)
const activeMenu = computed(() => route.path)

const menuList = computed(() => {
  return router.options.routes
    .filter((r) => r.meta?.hidden !== true && r.children?.length)
    .map((r) => ({
      path: r.path,
      title: r.meta?.title || r.name,
      icon: r.meta?.icon,
      children: r.children
        ?.filter((c) => c.meta?.hidden !== true)
        .map((c) => ({
          path: `${r.path}/${c.path}`.replace('//', '/'),
          title: c.meta?.title || c.name,
          icon: c.meta?.icon,
        })),
    }))
})
</script>

<template>
  <div class="sidebar">
    <div class="logo">
      <img src="@/assets/logo.svg" alt="logo" class="logo-img" />
      <span v-show="!isCollapse" class="logo-text">Platform</span>
    </div>

    <el-scrollbar>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :unique-opened="true"
        :collapse-transition="false"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        router
      >
        <template v-for="menu in menuList" :key="menu.path">
          <!-- 只有一个子菜单 -->
          <el-menu-item
            v-if="menu.children?.length === 1"
            :index="menu.children[0].path"
          >
            <el-icon v-if="menu.children[0].icon">
              <component :is="menu.children[0].icon" />
            </el-icon>
            <template #title>{{ menu.children[0].title }}</template>
          </el-menu-item>

          <!-- 多个子菜单 -->
          <el-sub-menu v-else :index="menu.path">
            <template #title>
              <el-icon v-if="menu.icon">
                <component :is="menu.icon" />
              </el-icon>
              <span>{{ menu.title }}</span>
            </template>

            <el-menu-item
              v-for="child in menu.children"
              :key="child.path"
              :index="child.path"
            >
              <el-icon v-if="child.icon">
                <component :is="child.icon" />
              </el-icon>
              <template #title>{{ child.title }}</template>
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<style scoped lang="scss">
.sidebar {
  height: 100%;

  .logo {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 50px;
    padding: 10px;
    background-color: #2b2f3a;

    .logo-img {
      width: 32px;
      height: 32px;
    }

    .logo-text {
      margin-left: 10px;
      font-size: 18px;
      font-weight: bold;
      color: #fff;
    }
  }

  :deep(.el-menu) {
    border-right: none;
  }
}
</style>
