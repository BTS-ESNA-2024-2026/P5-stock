import { apiFetch } from './client'
import type { User, Role } from '../types'

export function fetchUsers(): Promise<User[]> {
  return apiFetch<User[]>('/users')
}

export function fetchRoles(): Promise<Role[]> {
  return apiFetch<Role[]>('/roles')
}

export interface UserCreatePayload {
  username: string
  password: string
  group_id: string
  name?: string
  active?: boolean
}

export interface UserUpdatePayload {
  username?: string
  password?: string
  group_id?: string
  name?: string | null
  active?: boolean
}

export function createUser(data: UserCreatePayload): Promise<{ message: string; id: string }> {
  return apiFetch('/user', { method: 'POST', body: JSON.stringify(data) })
}

export function updateUser(id: string, data: UserUpdatePayload): Promise<{ message: string }> {
  return apiFetch(`/user/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export function deleteUser(id: string): Promise<{ message: string }> {
  return apiFetch(`/user/${id}`, { method: 'DELETE' })
}

export function clearUserMfa(id: string): Promise<{ message: string }> {
  return apiFetch(`/user/${id}/mfa`, { method: 'DELETE' })
}
