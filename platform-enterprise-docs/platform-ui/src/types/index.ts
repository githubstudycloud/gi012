/**
 * 通用响应结果
 */
export interface Result<T = unknown> {
  code: number
  message: string
  data: T
  timestamp: number
  traceId?: string
}

/**
 * 分页响应结果
 */
export interface PageResult<T = unknown> extends Result<T[]> {
  pageNum: number
  pageSize: number
  total: number
  pages: number
  hasNext: boolean
  hasPrevious: boolean
}

/**
 * 分页请求参数
 */
export interface PageRequest {
  pageNum?: number
  pageSize?: number
}

/**
 * 用户信息
 */
export interface UserInfo {
  userId: number
  username: string
  nickname: string
  avatar: string
  email?: string
  mobile?: string
  roles: string[]
  permissions: string[]
}

/**
 * 登录请求
 */
export interface LoginRequest {
  username: string
  password: string
  captcha?: string
  captchaId?: string
  rememberMe?: boolean
}

/**
 * 登录响应
 */
export interface LoginResponse {
  accessToken: string
  refreshToken: string
  tokenType: string
  expiresIn: number
  userId: number
  username: string
  nickname: string
  avatar: string
  roles: string[]
  permissions: string[]
}

/**
 * 菜单项
 */
export interface MenuItem {
  id: number
  parentId: number
  name: string
  path: string
  component?: string
  icon?: string
  sort: number
  type: 'directory' | 'menu' | 'button'
  permission?: string
  visible: boolean
  children?: MenuItem[]
}
