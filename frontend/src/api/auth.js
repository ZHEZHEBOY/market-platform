import api from './index'

export function login(data) {
  return api.post('/api/auth/login', data)
}

export function register(data) {
  return api.post('/api/auth/register', data)
}

export function getMe() {
  return api.get('/api/auth/me')
}

export function updateMe(data) {
  return api.put('/api/auth/me', data)
}
