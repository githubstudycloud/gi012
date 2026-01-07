import request from '@/utils/request'
import type { LoginRequest, LoginResponse, Result } from '@/types'

/**
 * 用户登录
 */
export function login(data: LoginRequest): Promise<Result<LoginResponse>> {
  return request.post<LoginResponse>('/auth/login', data)
}

/**
 * 刷新令牌
 */
export function refreshToken(refreshToken: string): Promise<Result<LoginResponse>> {
  return request.post<LoginResponse>('/auth/refresh', null, {
    params: { refreshToken },
  })
}

/**
 * 用户登出
 */
export function logout(): Promise<Result<void>> {
  return request.post<void>('/auth/logout')
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser(): Promise<Result<LoginResponse>> {
  return request.get<LoginResponse>('/auth/me')
}
