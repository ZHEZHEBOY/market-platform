import api from './index'

// 获取可领取的优惠券
export const getAvailableCoupons = () => api.get('/coupons/available')

// 领取优惠券
export const claimCoupon = (couponId) => api.post(`/coupons/claim/${couponId}`)

// 获取我的优惠券
export const getMyCoupons = (status) => api.get('/coupons/my', { params: { status } })

// 使用优惠券
export const useCoupon = (userCouponId, orderId) => api.post(`/coupons/use/${userCouponId}`, null, { params: { order_id: orderId } })

// 管理端：创建优惠券
export const createCoupon = (data) => api.post('/coupons/admin/create', data)

// 管理端：获取所有优惠券
export const listCoupons = () => api.get('/coupons/admin/list')

// 管理端：启用/禁用优惠券
export const toggleCoupon = (couponId) => api.patch(`/coupons/admin/${couponId}/toggle`)
