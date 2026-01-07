<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const stats = ref([
  { title: '用户总数', value: '12,345', icon: 'User', color: '#409eff' },
  { title: '今日活跃', value: '2,456', icon: 'TrendCharts', color: '#67c23a' },
  { title: '订单数量', value: '8,789', icon: 'Document', color: '#e6a23c' },
  { title: '系统消息', value: '56', icon: 'Bell', color: '#f56c6c' },
])

const activities = ref([
  { user: '张三', action: '创建了用户', target: 'user001', time: '5分钟前' },
  { user: '李四', action: '修改了角色', target: 'admin', time: '10分钟前' },
  { user: '王五', action: '删除了菜单', target: '系统监控', time: '30分钟前' },
  { user: '赵六', action: '上传了文件', target: 'report.pdf', time: '1小时前' },
])
</script>

<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <div class="welcome-text">
          <h2>欢迎回来，{{ userStore.nickname || userStore.username }}</h2>
          <p>今天是个好日子，祝您工作愉快！</p>
        </div>
        <img src="@/assets/welcome.svg" alt="welcome" class="welcome-img" />
      </div>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col v-for="stat in stats" :key="stat.title" :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-title">{{ stat.title }}</div>
            </div>
            <div class="stat-icon" :style="{ backgroundColor: stat.color }">
              <el-icon :size="24"><component :is="stat.icon" /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 内容区域 -->
    <el-row :gutter="16">
      <!-- 快捷操作 -->
      <el-col :span="16">
        <el-card class="quick-actions">
          <template #header>
            <span>快捷操作</span>
          </template>
          <el-row :gutter="16">
            <el-col :span="6">
              <el-button type="primary" icon="Plus" class="action-btn">新建用户</el-button>
            </el-col>
            <el-col :span="6">
              <el-button type="success" icon="Upload" class="action-btn">上传文件</el-button>
            </el-col>
            <el-col :span="6">
              <el-button type="warning" icon="Download" class="action-btn">下载报表</el-button>
            </el-col>
            <el-col :span="6">
              <el-button type="info" icon="Setting" class="action-btn">系统设置</el-button>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- 最近活动 -->
      <el-col :span="8">
        <el-card class="activities">
          <template #header>
            <span>最近活动</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="activity in activities"
              :key="activity.time"
              :timestamp="activity.time"
              placement="top"
            >
              <span class="activity-user">{{ activity.user }}</span>
              {{ activity.action }}
              <el-tag size="small" type="info">{{ activity.target }}</el-tag>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
.dashboard {
  .welcome-card {
    margin-bottom: 16px;

    .welcome-content {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .welcome-text {
        h2 {
          margin: 0 0 8px;
          font-size: 24px;
          color: #333;
        }

        p {
          margin: 0;
          color: #999;
        }
      }

      .welcome-img {
        width: 150px;
        height: auto;
      }
    }
  }

  .stats-row {
    margin-bottom: 16px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        justify-content: space-between;

        .stat-info {
          .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: #333;
          }

          .stat-title {
            margin-top: 4px;
            font-size: 14px;
            color: #999;
          }
        }

        .stat-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 56px;
          height: 56px;
          border-radius: 8px;
          color: #fff;
        }
      }
    }
  }

  .quick-actions {
    .action-btn {
      width: 100%;
    }
  }

  .activities {
    .activity-user {
      font-weight: 500;
      color: #409eff;
    }
  }
}
</style>
