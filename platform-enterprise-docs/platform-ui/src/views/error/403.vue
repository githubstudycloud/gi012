<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push('/')
}

function goBack() {
  router.back()
}
</script>

<template>
  <div class="error-page">
    <div class="error-content">
      <h1 class="error-code">403</h1>
      <h2 class="error-title">无权访问</h2>
      <p class="error-desc">抱歉，您没有权限访问此页面</p>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上页</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f5f7fa;

  .error-content {
    text-align: center;

    .error-code {
      font-size: 120px;
      font-weight: 700;
      color: #f56c6c;
      margin: 0;
    }

    .error-title {
      font-size: 24px;
      font-weight: 500;
      color: #333;
      margin: 16px 0;
    }

    .error-desc {
      font-size: 14px;
      color: #999;
      margin-bottom: 24px;
    }

    .error-actions {
      .el-button {
        margin: 0 8px;
      }
    }
  }
}
</style>
