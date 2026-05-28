import api from './index'

// 店铺
export function getMyShop() { return api.get('/api/seller/shop') }
export function updateMyShop(data) { return api.put('/api/seller/shop', data) }

// 商品
export function getMyProducts(params) { return api.get('/api/seller/products', { params }) }
export function createMyProduct(data) { return api.post('/api/seller/products', data) }
export function updateMyProduct(id, data) { return api.put(`/api/seller/products/${id}`, data) }
export function deleteMyProduct(id) { return api.delete(`/api/seller/products/${id}`) }
export function uploadProductImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/api/seller/products/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 订单
export function getMyOrders(params) { return api.get('/api/seller/orders', { params }) }
export function shipMyOrder(id) { return api.put(`/api/seller/orders/${id}/ship`) }

// 数据统计
export function getSellerDashboard() { return api.get('/api/seller/dashboard') }
