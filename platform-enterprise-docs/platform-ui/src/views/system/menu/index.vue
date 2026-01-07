<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    id: 1,
    name: '系统管理',
    path: '/system',
    icon: 'Setting',
    type: 'directory',
    sort: 1,
    status: 1,
    children: [
      { id: 11, name: '用户管理', path: 'user', icon: 'User', type: 'menu', sort: 1, status: 1 },
      { id: 12, name: '角色管理', path: 'role', icon: 'UserFilled', type: 'menu', sort: 2, status: 1 },
      { id: 13, name: '菜单管理', path: 'menu', icon: 'Menu', type: 'menu', sort: 3, status: 1 },
    ],
  },
  {
    id: 2,
    name: '系统监控',
    path: '/monitor',
    icon: 'Monitor',
    type: 'directory',
    sort: 2,
    status: 1,
    children: [
      { id: 21, name: '在线用户', path: 'online', icon: 'Connection', type: 'menu', sort: 1, status: 1 },
      { id: 22, name: '服务监控', path: 'server', icon: 'Cpu', type: 'menu', sort: 2, status: 1 },
    ],
  },
])

const typeMap: Record<string, { label: string; type: '' | 'success' | 'warning' }> = {
  directory: { label: '目录', type: '' },
  menu: { label: '菜单', type: 'success' },
  button: { label: '按钮', type: 'warning' },
}
</script>

<template>
  <div class="menu-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>菜单列表</span>
          <el-button type="primary" icon="Plus">新增菜单</el-button>
        </div>
      </template>

      <el-table :data="tableData" row-key="id" :tree-props="{ children: 'children' }" stripe border>
        <el-table-column prop="name" label="菜单名称" min-width="200" />
        <el-table-column prop="icon" label="图标" width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.icon"><component :is="row.icon" /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路径" min-width="150" />
        <el-table-column prop="type" label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="typeMap[row.type].type">
              {{ typeMap[row.type].label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '显示' : '隐藏' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default>
            <el-button type="primary" link icon="Edit">编辑</el-button>
            <el-button type="success" link icon="Plus">新增</el-button>
            <el-button type="danger" link icon="Delete">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.menu-manage {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
