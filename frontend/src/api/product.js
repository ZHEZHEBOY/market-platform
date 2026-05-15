import api from './index'

export function getProducts(params) {
  return api.get('/api/products', { params })
}

export function getProduct(id) {
  return api.get(`/api/products/${id}`)
}

export function createProduct(data) {
  return api.post('/api/products', data)
}

export function updateProduct(id, data) {
  return api.put(`/api/products/${id}`, data)
}

export function deleteProduct(id) {
  return api.delete(`/api/products/${id}`)
}
