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

// 批量操作
export function batchToggleProducts(productIds, isActive) {
  return api.post('/api/seller/products/batch-toggle', productIds, { params: { is_active: isActive } })
}
export function batchDeleteProducts(productIds) {
  return api.delete('/api/seller/products/batch', { data: productIds })
}

// 库存预警
export function getLowStockProducts(threshold = 10) {
  return api.get('/api/seller/products/low-stock', { params: { threshold } })
}

// 订单
export function getMyOrders(params) { return api.get('/api/seller/orders', { params }) }
export function shipMyOrder(id) { return api.put(`/api/seller/orders/${id}/ship`) }

// 订单导出
export function exportOrders(status = '') {
  return api.get('/api/seller/orders/export', { params: { status }, responseType: 'blob' })
}

// 数据统计
export function getSellerDashboard() { return api.get('/api/seller/dashboard') }
