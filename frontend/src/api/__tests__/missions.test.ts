import { describe, it, expect, vi } from 'vitest'
import { fetchMissions, createMission, updateMission, deleteMission } from '../missions'

function mockFetch(payload: unknown, status = 200) {
  vi.mocked(fetch).mockResolvedValueOnce(
    new Response(JSON.stringify(payload), { status }),
  )
}

beforeEach(() => vi.mocked(fetch).mockClear())

describe('fetchMissions', () => {
  it('calls GET /api/missions', async () => {
    mockFetch([])
    await fetchMissions()
    expect(fetch).toHaveBeenCalledWith('/api/missions', expect.any(Object))
  })

  it('returns the missions list', async () => {
    const missions = [{ id: 'm1', title: 'Op Alpha', status: 'ACTIVE', theatre: 'Europe' }]
    mockFetch(missions)
    const result = await fetchMissions()
    expect(result).toEqual(missions)
  })

  it('throws ApiError on 401', async () => {
    mockFetch({ message: 'Unauthorized' }, 401)
    await expect(fetchMissions()).rejects.toMatchObject({ status: 401 })
  })
})

describe('createMission', () => {
  it('calls POST /api/mission with payload', async () => {
    mockFetch({ message: 'Mission created' })
    const data = { title: 'Op Bravo', theatre: 'Africa', status: 'PLANNED' }
    await createMission(data)
    expect(fetch).toHaveBeenCalledWith(
      '/api/mission',
      expect.objectContaining({ method: 'POST', body: JSON.stringify(data) }),
    )
  })

  it('returns server message', async () => {
    mockFetch({ message: 'Mission created' })
    const result = await createMission({ title: 'x', theatre: 'y', status: 'PLANNED' })
    expect(result).toEqual({ message: 'Mission created' })
  })

  it('throws ApiError on 400', async () => {
    mockFetch({ message: 'Bad request' }, 400)
    await expect(createMission({})).rejects.toMatchObject({ status: 400 })
  })
})

describe('updateMission', () => {
  it('calls PUT /api/mission/:id', async () => {
    mockFetch({ message: 'updated' })
    await updateMission('m1', { title: 'Op Bravo Updated' })
    expect(fetch).toHaveBeenCalledWith(
      '/api/mission/m1',
      expect.objectContaining({ method: 'PUT' }),
    )
  })

  it('returns the updated message', async () => {
    mockFetch({ message: 'Mission updated' })
    const result = await updateMission('m1', { status: 'CLOSED' })
    expect(result).toEqual({ message: 'Mission updated' })
  })
})

describe('deleteMission', () => {
  it('calls DELETE /api/mission/:id', async () => {
    mockFetch({ message: 'deleted' })
    await deleteMission('m1')
    expect(fetch).toHaveBeenCalledWith(
      '/api/mission/m1',
      expect.objectContaining({ method: 'DELETE' }),
    )
  })

  it('throws ApiError on 404', async () => {
    mockFetch({ message: 'Not found' }, 404)
    await expect(deleteMission('missing')).rejects.toMatchObject({ status: 404 })
  })
})
