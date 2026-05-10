import { apiFetch } from './client'
import type { LogEntry, LogKind } from '../types'

export function fetchLogs(): Promise<LogEntry[]> {
  return apiFetch<LogEntry[]>('/logs')
}

export function fetchAdminLogs(opts: { type?: LogKind | ''; limit?: number } = {}): Promise<LogEntry[]> {
  const params = new URLSearchParams()
  if (opts.type) params.set('type', opts.type)
  if (opts.limit) params.set('limit', String(opts.limit))
  const query = params.toString()
  return apiFetch<LogEntry[]>(`/admin/logs${query ? `?${query}` : ''}`)
}
