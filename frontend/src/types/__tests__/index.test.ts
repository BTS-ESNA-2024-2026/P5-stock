import { describe, it, expect } from 'vitest'
import {
  ASSET_STATUS_LABELS,
  ASSET_STATUS_BADGE,
} from '../index'
import type { AssetStatus } from '../index'

// ---------------------------------------------------------------------------
// AssetStatus labels
// ---------------------------------------------------------------------------

describe('ASSET_STATUS_LABELS', () => {
  const allStatuses: AssetStatus[] = ['STOCK', 'DESTROYED', 'SOLD', 'LOST', 'TRANSIT', 'PURCHASED']

  it('has a label for every status', () => {
    for (const status of allStatuses) {
      expect(ASSET_STATUS_LABELS[status]).toBeTruthy()
    }
  })

  it('STOCK maps to "En stock"', () => {
    expect(ASSET_STATUS_LABELS['STOCK']).toBe('En stock')
  })

  it('DESTROYED maps to "Detruit"', () => {
    expect(ASSET_STATUS_LABELS['DESTROYED']).toBe('Detruit')
  })

  it('SOLD maps to "Vendu"', () => {
    expect(ASSET_STATUS_LABELS['SOLD']).toBe('Vendu')
  })

  it('LOST maps to "Perdu"', () => {
    expect(ASSET_STATUS_LABELS['LOST']).toBe('Perdu')
  })

  it('TRANSIT maps to "En transit"', () => {
    expect(ASSET_STATUS_LABELS['TRANSIT']).toBe('En transit')
  })

  it('PURCHASED maps to "Achete"', () => {
    expect(ASSET_STATUS_LABELS['PURCHASED']).toBe('Achete')
  })
})

// ---------------------------------------------------------------------------
// AssetStatus badge classes
// ---------------------------------------------------------------------------

describe('ASSET_STATUS_BADGE', () => {
  it('STOCK uses success badge', () => {
    expect(ASSET_STATUS_BADGE['STOCK']).toBe('badge-success')
  })

  it('DESTROYED uses danger badge', () => {
    expect(ASSET_STATUS_BADGE['DESTROYED']).toBe('badge-danger')
  })

  it('LOST uses danger badge', () => {
    expect(ASSET_STATUS_BADGE['LOST']).toBe('badge-danger')
  })

  it('TRANSIT uses info badge', () => {
    expect(ASSET_STATUS_BADGE['TRANSIT']).toBe('badge-info')
  })

  it('PURCHASED uses info badge', () => {
    expect(ASSET_STATUS_BADGE['PURCHASED']).toBe('badge-info')
  })

  it('SOLD uses warning badge', () => {
    expect(ASSET_STATUS_BADGE['SOLD']).toBe('badge-warning')
  })
})
