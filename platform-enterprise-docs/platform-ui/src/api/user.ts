import request from '@/utils/request'
import type { PageResult, Result } from '@/types'

export interface UserDTO {
  id: number
  username: string
  nickname: string
  avatar: string
  email: string
  mobile: string
  gender: number
  status: number
  deptId: number
  deptName: string
  roleIds: number[]
  roleNames: string[]
  lastLoginAt: string
  createdAt: string
  remark: string
}

export interface UserQueryRequest {
  pageNum?: number
  pageSize?: number
  username?: string
  nickname?: string
  mobile?: string
  email?: string
  status?: number
  deptId?: number
}

export interface UserCreateRequest {
  username: string
  password: string
  nickname?: string
  email?: string
  mobile?: string
  gender?: number
  deptId?: number
  roleIds: number[]
  remark?: string
}

/**
 * 分页查询用户
 */
export function getUserPage(params: UserQueryRequest): Promise<PageResult<UserDTO>> {
  return request.get<UserDTO[]>('/users', { params }) as Promise<PageResult<UserDTO>>
}

/**
 * 获取用户详情
 */
export function getUserById(id: number): Promise<Result<UserDTO>> {
  return request.get<UserDTO>(`/users/${id}`)
}

/**
 * 创建用户
 */
export function createUser(data: UserCreateRequest): Promise<Result<number>> {
  return request.post<number>('/users', data)
}

/**
 * 更新用户
 */
export function updateUser(id: number, data: UserCreateRequest): Promise<Result<void>> {
  return request.put<void>(`/users/${id}`, data)
}

/**
 * 删除用户
 */
export function deleteUser(id: number): Promise<Result<void>> {
  return request.delete<void>(`/users/${id}`)
}

/**
 * 批量删除用户
 */
export function batchDeleteUsers(ids: number[]): Promise<Result<void>> {
  return request.delete<void>('/users/batch', { data: ids })
}

/**
 * 更新用户状态
 */
export function updateUserStatus(id: number, status: number): Promise<Result<void>> {
  return request.patch<void>(`/users/${id}/status`, null, { params: { status } })
}

/**
 * 重置用户密码
 */
export function resetUserPassword(id: number, newPassword: string): Promise<Result<void>> {
  return request.patch<void>(`/users/${id}/password`, null, { params: { newPassword } })
}
