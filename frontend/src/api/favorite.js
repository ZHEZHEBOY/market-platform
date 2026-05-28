import api from './index'

export function listFavorites(params) {
  return api.get('/api/favorites', { params })
}

export function addFavorite(productId) {
  return api.post(`/api/favorites/${productId}`)
}

export function removeFavorite(productId) {
  return api.delete(`/api/favorites/${productId}`)
}

export function checkFavorite(productId) {
  return api.get(`/api/favorites/check/${productId}`)
}
