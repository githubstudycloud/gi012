<script setup lang="ts"></script>

<template>
  <div class="app-main">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </transition>
    </router-view>
  </div>
</template>

<style scoped lang="scss">
.app-main {
  position: relative;
  min-height: calc(100vh - 50px);
  padding: 16px;
  overflow: hidden;
}
</style>
