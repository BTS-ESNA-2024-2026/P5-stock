import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Tell React it's running in a test environment so act() works correctly.
;(globalThis as Record<string, unknown>).IS_REACT_ACT_ENVIRONMENT = true

// Stub fetch globally — each test configures return values with mockResolvedValueOnce.
vi.stubGlobal('fetch', vi.fn())
