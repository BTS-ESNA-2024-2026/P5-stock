export type AssetStatus = 'AVAILABLE' | 'IN_USE' | 'MAINTENANCE'

export type AssetRecord = {
  id: string
  name: string
  number: string
  type: string
  status: AssetStatus
  room: string
}