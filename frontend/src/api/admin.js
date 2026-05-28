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

// 店铺审核
export function listShops(params) {
  return api.get('/api/admin/shops', { params })
}

export function approveShop(id) {
  return api.put(`/api/admin/shops/${id}/approve`)
}

export function rejectShop(id) {
  return api.put(`/api/admin/shops/${id}/reject`)
}
