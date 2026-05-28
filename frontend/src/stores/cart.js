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

  async function add(productId, quantity, extra = null) {
    const payload = { product_id: productId, quantity }
    if (extra?.sku) {
      payload.sku_specs = extra.sku.specs
      payload.sku_price = extra.sku.price
    }
    await addToCart(payload)
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
