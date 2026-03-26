import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useNotificationsStore = defineStore('notifications', () => {
  const items = ref([])
  let nextId = 1

  function add(message, type = 'success') {
    const id = nextId++
    items.value.push({ id, message, type })
    setTimeout(() => remove(id), 3500)
  }

  function remove(id) {
    const idx = items.value.findIndex((n) => n.id === id)
    if (idx !== -1) items.value.splice(idx, 1)
  }

  return { items, add, remove }
})
