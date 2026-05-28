import api from './index'

export function createReview(data) {
  return api.post('/api/reviews', data)
}

export function getProductReviews(productId, params) {
  return api.get(`/api/reviews/product/${productId}`, { params })
}

export function getMyReviewableItems() {
  return api.get('/api/reviews/my')
}

export function deleteReview(reviewId) {
  return api.delete(`/api/reviews/${reviewId}`)
}
