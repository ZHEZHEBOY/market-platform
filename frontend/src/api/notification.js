import api from './index'

export function getNotifications(params) {
  return api.get('/api/notifications', { params })
}

export function getUnreadCount() {
  return api.get('/api/notifications/unread-count')
}

export function markAsRead(id) {
  return api.put(`/api/notifications/${id}/read`)
}

export function markAllAsRead() {
  return api.put('/api/notifications/read-all')
}

export function deleteNotification(id) {
  return api.delete(`/api/notifications/${id}`)
}
