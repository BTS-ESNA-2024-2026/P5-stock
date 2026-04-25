import { describe, it, expect, vi } from 'vitest'
import { ApiError, apiFetch, authFetch } from '../client'

// ---------------------------------------------------------------------------
// ApiError
// ---------------------------------------------------------------------------

describe('ApiError', () => {
  it('is an instance of Error', () => {
    const err = new ApiError(404, 'Not found')
    expect(err).toBeInstanceOf(Error)
  })

  it('has the correct name', () => {
    const err = new ApiError(401, 'Unauthorized')
    expect(err.name).toBe('ApiError')
  })

  it('stores the HTTP status code', () => {
    const err = new ApiError(500, 'Server error')
    expect(err.status).toBe(500)
  })

  it('stores the message', () => {
    const err = new ApiError(403, 'Forbidden')
    expect(err.message).toBe('Forbidden')
  })
})

// ---------------------------------------------------------------------------
// apiFetch
// ---------------------------------------------------------------------------

describe('apiFetch', () => {
  it('calls the correct /api-prefixed URL', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ ok: true }), { status: 200 }),
    )

    await apiFetch('/assets')

    expect(fetch).toHaveBeenCalledWith(
      '/api/assets',
      expect.objectContaining({
        credentials: 'include',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
      }),
    )
  })

  it('returns parsed JSON on success', async () => {
    const payload = [{ id: '1', name: 'Laptop' }]
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify(payload), { status: 200 }),
    )

    const result = await apiFetch('/assets')
    expect(result).toEqual(payload)
  })

  it('throws ApiError when response is not ok', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ message: 'Not found' }), { status: 404 }),
    )

    await expect(apiFetch('/asset/unknown')).rejects.toMatchObject({
      status: 404,
      message: 'Not found',
    })
  })

  it('falls back to "Request failed" when body has no message', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response('{}', { status: 400 }),
    )

    await expect(apiFetch('/bad')).rejects.toMatchObject({
      status: 400,
      message: 'Request failed',
    })
  })

  it('uses the error field when message is absent', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ error: 'Custom error' }), { status: 422 }),
    )

    await expect(apiFetch('/bad')).rejects.toMatchObject({
      message: 'Custom error',
    })
  })

  it('passes extra request options through', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({}), { status: 200 }),
    )

    await apiFetch('/asset', { method: 'POST', body: JSON.stringify({ name: 'x' }) })

    expect(fetch).toHaveBeenCalledWith(
      '/api/asset',
      expect.objectContaining({ method: 'POST' }),
    )
  })
})

// ---------------------------------------------------------------------------
// authFetch
// ---------------------------------------------------------------------------

describe('authFetch', () => {
  beforeEach(() => {
    vi.spyOn(globalThis, 'fetch')
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('calls the correct /auth-prefixed URL', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ id: 'u1' }), { status: 200 }),
    )

    await authFetch('/me')

    expect(fetch).toHaveBeenCalledWith(
      '/auth/me',
      expect.objectContaining({ credentials: 'include' }),
    )
  })

  it('returns parsed JSON on success', async () => {
    const payload = { id: 'u1', username: 'alice' }
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify(payload), { status: 200 }),
    )

    const result = await authFetch('/me')
    expect(result).toEqual(payload)
  })

  it('throws ApiError when response is not ok', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ message: 'Unauthorized' }), { status: 401 }),
    )

    await expect(authFetch('/me')).rejects.toMatchObject({ status: 401 })
  })
})
