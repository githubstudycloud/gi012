<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  { id: 1, code: 'ADMIN', name: '超级管理员', status: 1, sort: 1, createdAt: '2026-01-01 00:00:00' },
  { id: 2, code: 'USER', name: '普通用户', status: 1, sort: 2, createdAt: '2026-01-01 00:00:00' },
  { id: 3, code: 'GUEST', name: '访客', status: 0, sort: 3, createdAt: '2026-01-01 00:00:00' },
])
</script>

<template>
  <div class="role-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色列表</span>
          <el-button type="primary" icon="Plus">新增角色</el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe border>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="code" label="角色编码" width="150" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default>
            <el-button type="primary" link icon="Edit">编辑</el-button>
            <el-button type="warning" link icon="Key">分配权限</el-button>
            <el-button type="danger" link icon="Delete">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.role-manage {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
