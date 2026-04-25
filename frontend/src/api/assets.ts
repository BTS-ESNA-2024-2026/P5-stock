import { apiFetch } from './client'
import type { Asset, AssetType, Spec, Value, Room, Base } from '../types'

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

export function updateAssetType(id: string, data: { type: string }): Promise<{ message: string }> {
  return apiFetch(`/asset_type/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export function deleteAssetType(id: string): Promise<{ message: string }> {
  return apiFetch(`/asset_type/${id}`, { method: 'DELETE' })
}

export function fetchSpecs(): Promise<Spec[]> {
  return apiFetch<Spec[]>('/specs')
}

export function createSpec(data: { type_id: string; name: string }): Promise<{ message: string }> {
  return apiFetch('/spec', { method: 'POST', body: JSON.stringify(data) })
}

export function updateSpec(id: string, data: { name: string }): Promise<{ message: string }> {
  return apiFetch(`/spec/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export function deleteSpec(id: string): Promise<{ message: string }> {
  return apiFetch(`/spec/${id}`, { method: 'DELETE' })
}

export function fetchAssetValues(assetId: string): Promise<Value[]> {
  return apiFetch<Value[]>(`/asset/${assetId}/values`)
}

export function createValue(data: { asset_id: string; spec_id: string; value: string }): Promise<{ message: string }> {
  return apiFetch('/value', { method: 'POST', body: JSON.stringify(data) })
}

export function updateValue(id: string, data: { value: string }): Promise<{ message: string }> {
  return apiFetch(`/value/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export function deleteValue(id: string): Promise<{ message: string }> {
  return apiFetch(`/value/${id}`, { method: 'DELETE' })
}

export function fetchRooms(): Promise<Room[]> {
  return apiFetch<Room[]>('/rooms')
}

export function fetchBases(): Promise<Base[]> {
  return apiFetch<Base[]>('/bases')
}

export function createBase(data: { name: string; address: string }): Promise<{ message: string }> {
  return apiFetch('/base', { method: 'POST', body: JSON.stringify(data) })
}

export function updateBase(id: string, data: { name: string; address: string }): Promise<{ message: string }> {
  return apiFetch(`/base/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export function deleteBase(id: string): Promise<{ message: string }> {
  return apiFetch(`/base/${id}`, { method: 'DELETE' })
}
