import api from './index'

// 创建退款申请
export const createRefund = (data) => api.post('/refunds/create', data)

// 获取我的退款申请
export const getMyRefunds = () => api.get('/refunds/my')

// 取消退款申请
export const cancelRefund = (refundId) => api.post(`/refunds/cancel/${refundId}`)

// 管理端：获取所有退款申请
export const listRefunds = (status) => api.get('/refunds/admin/list', { params: { status } })

// 管理端：审核退款申请
export const reviewRefund = (refundId, data) => api.patch(`/refunds/admin/${refundId}/review`, data)
