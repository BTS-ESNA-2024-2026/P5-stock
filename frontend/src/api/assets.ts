import { apiFetch } from './client'
import type { Asset, AssetType, Room, Base } from '../types'

export function fetchAssets(): Promise<Asset[]> {
  return apiFetch<Asset[]>('/assets')
}

export function createAsset(data: Record<string, unknown>): Promise<{ message: string }> {
  return apiFetch('/asset', { method: 'POST', body: JSON.stringify(data) })
}

export function updateAsset(id: string, data: Record<string, unknown>): Promise<{ message: string }> {
  return apiFetch(`/asset/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export function deleteAsset(id: string): Promise<{ message: string }> {
  return apiFetch(`/asset/${id}`, { method: 'DELETE' })
}

export function fetchAssetTypes(): Promise<AssetType[]> {
  return apiFetch<AssetType[]>('/asset_types')
}

export function createAssetType(data: { type: string }): Promise<{ message: string }> {
  return apiFetch('/asset_type', { method: 'POST', body: JSON.stringify(data) })
}

export function fetchRooms(): Promise<Room[]> {
  return apiFetch<Room[]>('/rooms')
}

export function fetchBases(): Promise<Base[]> {
  return apiFetch<Base[]>('/bases')
}
