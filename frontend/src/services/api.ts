import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login if unauthorized
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// API Functions
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
  register: (username: string, password: string, name?: string) =>
    api.post('/auth/register', { username, password, name }),
}

export const assetsApi = {
  getAll: (params?: {
    page?: number
    per_page?: number
    status?: string
    type_id?: number
    search?: string
  }) => api.get('/api/assets', { params }),
  getById: (id: number) => api.get(`/api/assets/${id}`),
  create: (data: {
    name: string
    asset_type_id: number
    status: string
    number?: string
    room_id?: number
    quantity?: number
    shelf?: string
    sensible?: boolean
  }) => api.post('/api/asset', data),
  update: (id: number, data: Partial<{
    name: string
    number: string
    status: string
    room_id: number
    quantity: number
    shelf: string
    sensible: boolean
  }>) => api.put(`/api/asset/${id}`, data),
  delete: (id: number) => api.delete(`/api/asset/${id}`),
}

export const assetTypesApi = {
  getAll: () => api.get('/api/asset_types'),
  create: (type: string) => api.post('/api/asset_type', { type }),
}

export const basesApi = {
  getAll: () => api.get('/api/bases'),
  create: (name: string, address: string) =>
    api.post('/api/base', { name, address }),
  update: (id: number, data: { name?: string; address?: string }) =>
    api.put(`/api/base/${id}`, data),
}

export const roomsApi = {
  getAll: (base_id?: number) =>
    api.get('/api/rooms', { params: base_id ? { base_id } : {} }),
  create: (base_id: number, room: string) =>
    api.post('/api/room', { base_id, room }),
  update: (id: number, data: { base_id?: number; room?: string }) =>
    api.put(`/api/room/${id}`, data),
}

export const specsApi = {
  getAll: (type_id?: number) =>
    api.get('/api/specs', { params: type_id ? { type_id } : {} }),
  create: (type_id: number, name: string) =>
    api.post('/api/specs', { type_id, name }),
}

export const valuesApi = {
  getAll: (asset_id?: number) =>
    api.get('/api/values', { params: asset_id ? { asset_id } : {} }),
  create: (asset_id: number, spec_id: number, value: string) =>
    api.post('/api/value', { asset_id, spec_id, value }),
  update: (id: number, data: { asset_id?: number; spec_id?: number; value?: string }) =>
    api.put(`/api/value/${id}`, data),
}
