import { authFetch } from './client'

export interface OtpSetupResponse {
  secret: string
  uri: string
  algorithm: string
  digits: number
  period: number
  type: string
  issuer: string
}

export function setupOtp(): Promise<OtpSetupResponse> {
  return authFetch<OtpSetupResponse>('/otp/setup', { method: 'POST' })
}

export function verifyOtp(secret: string, otp_code: string): Promise<{ message: string }> {
  return authFetch('/otp/verify', {
    method: 'POST',
    body: JSON.stringify({ secret, otp_code }),
  })
}

export function disableOtp(): Promise<{ message: string }> {
  return authFetch('/otp/setup', { method: 'DELETE' })
}
