import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getCart, addToCart, updateCartItem, removeFromCart } from '../api/cart'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  const totalAmount = ref(0)

  async function fetchCart() {
    try {
      const { data } = await getCart()
      items.value = data.items
      totalAmount.value = data.total_amount
    } catch {
      items.value = []
      totalAmount.value = 0
    }
  }

  async function add(productId, quantity) {
    await addToCart({ product_id: productId, quantity })
    await fetchCart()
  }

  async function update(id, quantity) {
    await updateCartItem(id, { quantity })
    await fetchCart()
  }

  async function remove(id) {
    await removeFromCart(id)
    await fetchCart()
  }

  return { items, totalAmount, fetchCart, add, update, remove }
})
