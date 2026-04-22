import { apiFetch } from './client'
import type { User, Role } from '../types'

export function fetchUsers(): Promise<User[]> {
  return apiFetch<User[]>('/users')
}

export function fetchRoles(): Promise<Role[]> {
  return apiFetch<Role[]>('/roles')
}
