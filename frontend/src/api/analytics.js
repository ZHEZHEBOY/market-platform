import api from './index'

// 获取销售趋势
export const getSalesTrend = (days = 30) => api.get('/analytics/sales-trend', { params: { days } })

// 获取用户增长
export const getUserGrowth = (days = 30) => api.get('/analytics/user-growth', { params: { days } })

// 获取订单状态分布
export const getOrderStatus = () => api.get('/analytics/order-status')

// 获取分类销售排行
export const getCategorySales = () => api.get('/analytics/category-sales')

// 获取热销商品排行
export const getTopProducts = (limit = 10) => api.get('/analytics/top-products', { params: { limit } })

// 获取总览数据
export const getOverview = () => api.get('/analytics/overview')
