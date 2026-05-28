import api from './index'

export function getCategories(params) {
  return api.get('/api/categories', { params })
}

export function createCategory(data) {
  return api.post('/api/categories', data)
}

export function updateCategory(id, data) {
  return api.put(`/api/categories/${id}`, data)
}

export function deleteCategory(id) {
  return api.delete(`/api/categories/${id}`)
}
