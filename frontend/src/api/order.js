import api from './index'

export function getOrders(params) {
  return api.get('/api/orders', { params })
}

export function getOrder(id) {
  return api.get(`/api/orders/${id}`)
}

export function placeOrder(data) {
  return api.post('/api/orders', data)
}

export function cancelOrder(id) {
  return api.put(`/api/orders/${id}/cancel`)
}

export function payOrder(id) {
  return api.get(`/api/payment/pay/${id}`)
}

export function queryPayment(id) {
  return api.get(`/api/payment/query/${id}`)
}
