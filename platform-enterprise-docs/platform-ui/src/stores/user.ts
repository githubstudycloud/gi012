import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi, getCurrentUser } from '@/api/auth'
import type { UserInfo, LoginRequest, LoginResponse } from '@/types'
import router from '@/router'

export const useUserStore = defineStore(
  'user',
  () => {
    // 状态
    const token = ref<string>('')
    const refreshToken = ref<string>('')
    const userInfo = ref<UserInfo | null>(null)

    // 计算属性
    const isLoggedIn = computed(() => !!token.value)
    const username = computed(() => userInfo.value?.username || '')
    const nickname = computed(() => userInfo.value?.nickname || '')
    const avatar = computed(() => userInfo.value?.avatar || '')
    const roles = computed(() => userInfo.value?.roles || [])
    const permissions = computed(() => userInfo.value?.permissions || [])

    // 登录
    async function login(loginForm: LoginRequest) {
      const { data } = await loginApi(loginForm)
      setLoginInfo(data)
      return data
    }

    // 设置登录信息
    function setLoginInfo(data: LoginResponse) {
      token.value = data.accessToken
      refreshToken.value = data.refreshToken
      userInfo.value = {
        userId: data.userId,
        username: data.username,
        nickname: data.nickname,
        avatar: data.avatar,
        roles: data.roles,
        permissions: data.permissions,
      }
    }

    // 获取用户信息
    async function fetchUserInfo() {
      try {
        const { data } = await getCurrentUser()
        setLoginInfo(data)
        return data
      } catch (error) {
        logout()
        throw error
      }
    }

    // 登出
    async function logout() {
      try {
        if (token.value) {
          await logoutApi()
        }
      } finally {
        resetState()
        router.push('/login')
      }
    }

    // 重置状态
    function resetState() {
      token.value = ''
      refreshToken.value = ''
      userInfo.value = null
    }

    // 检查权限
    function hasPermission(permission: string): boolean {
      return permissions.value.includes(permission)
    }

    // 检查角色
    function hasRole(role: string): boolean {
      return roles.value.includes(role)
    }

    return {
      // 状态
      token,
      refreshToken,
      userInfo,
      // 计算属性
      isLoggedIn,
      username,
      nickname,
      avatar,
      roles,
      permissions,
      // 方法
      login,
      logout,
      fetchUserInfo,
      resetState,
      hasPermission,
      hasRole,
    }
  },
  {
    persist: {
      key: 'platform-user',
      pick: ['token', 'refreshToken', 'userInfo'],
    },
  }
)
