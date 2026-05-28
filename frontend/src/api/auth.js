import api from './index'

export function login(data) {
  return api.post('/api/auth/login', data)
}

export function register(data) {
  return api.post('/api/auth/register', data)
}

export function registerSeller(data) {
  return api.post('/api/auth/register/seller', data)
}

export function getMe() {
  return api.get('/api/auth/me')
}

export function updateMe(data) {
  return api.put('/api/auth/me', data)
}

export function changePassword(data) {
  return api.put('/api/auth/password', data)
}

export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/api/auth/avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
