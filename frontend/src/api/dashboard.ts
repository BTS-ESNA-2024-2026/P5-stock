import { apiFetch } from './client'
import type { LogEntry } from '../types'

export function fetchLogs(): Promise<LogEntry[]> {
  return apiFetch<LogEntry[]>('/logs')
}
