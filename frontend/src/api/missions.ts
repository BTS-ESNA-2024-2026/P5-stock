import { apiFetch } from './client'
import type { Mission } from '../types'

export function fetchMissions(): Promise<Mission[]> {
  return apiFetch<Mission[]>('/missions')
}

export function createMission(data: Record<string, unknown>): Promise<{ message: string }> {
  return apiFetch('/mission', { method: 'POST', body: JSON.stringify(data) })
}

export function updateMission(id: string, data: Record<string, unknown>): Promise<{ message: string }> {
  return apiFetch(`/mission/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export function deleteMission(id: string): Promise<{ message: string }> {
  return apiFetch(`/mission/${id}`, { method: 'DELETE' })
}
