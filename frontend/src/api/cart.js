import api from './index'

export function getCart() {
  return api.get('/api/cart')
}

export function addToCart(data) {
  return api.post('/api/cart', data)
}

export function updateCartItem(id, data) {
  return api.put(`/api/cart/${id}`, data)
}

export function removeFromCart(id) {
  return api.delete(`/api/cart/${id}`)
}
