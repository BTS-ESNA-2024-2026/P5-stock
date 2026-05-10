import type { CurrentUser } from '../types'

export interface AuthContextType {
  user: CurrentUser | null
  loading: boolean
  sessionExpired: boolean
  login: (username: string, password: string, otpCode?: string) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}
