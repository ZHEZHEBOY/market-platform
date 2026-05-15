import api from './index'

export function getDashboard() {
  return api.get('/api/admin/dashboard')
}

export function adminListOrders(params) {
  return api.get('/api/orders/admin/all', { params })
}

export function shipOrder(id) {
  return api.put(`/api/orders/admin/${id}/ship`)
}
