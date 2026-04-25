// Asset statuses matching backend enum
export type AssetStatus = 'STOCK' | 'DESTROYED' | 'SOLD' | 'LOST' | 'TRANSIT' | 'PURCHASED'

export const ASSET_STATUS_LABELS: Record<AssetStatus, string> = {
  STOCK: 'En stock',
  DESTROYED: 'Detruit',
  SOLD: 'Vendu',
  LOST: 'Perdu',
  TRANSIT: 'En transit',
  PURCHASED: 'Achete',
}

export const ASSET_STATUS_BADGE: Record<AssetStatus, string> = {
  STOCK: 'badge-success',
  DESTROYED: 'badge-danger',
  SOLD: 'badge-warning',
  LOST: 'badge-danger',
  TRANSIT: 'badge-info',
  PURCHASED: 'badge-info',
}

export interface Asset {
  id: string
  type_asset_id: string
  mission_id?: string
  room_id?: string
  DA: string
  DE: string
  name: string
  number?: string
  status: AssetStatus
  quantity?: number
  shelf?: string
  sensible?: boolean
  // Joined fields from backend
  type_name?: string
  room_name?: string
  base_name?: string
  mission_title?: string
}

export interface AssetType {
  id: string
  type: string
}

export interface Spec {
  id: string
  type_id: string
  name: string
  type_name?: string
}

export interface Value {
  id: string
  asset_id: string
  spec_id: string
  DA: string
  DE: string
  value: string
  spec_name?: string
}

export interface Mission {
  id: string
  DA: string
  DE: string
  date_start?: string
  date_end?: string
  title: string
  description?: string
  status: string
  theatre: string
  asset_count?: number
}

export interface Room {
  id: string
  base_id: string
  room: string
  base_name?: string
}

export interface Base {
  id: string
  name: string
  address: string
}

export interface User {
  id: string
  username: string
  name?: string
  group_id: string
  active: boolean
  DA: string
  DE: string
  role_name?: string
}

export interface Role {
  id: string
  name: string
  desc?: string
}

export interface CurrentUser {
  id: string
  username: string
  name?: string
  role: string
  active: boolean
}

export interface LogEntry {
  id: string
  asset_id?: string
  spec_id?: string
  value_id?: string
  D: string
  action: string
  description?: string
  asset_name?: string
}
