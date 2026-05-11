import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'ams_current_user'
const TOKEN_KEY = 'ams_token'

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref(
    JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')
  )
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')

  const isLoggedIn = computed(() => !!currentUser.value && !!token.value)
  const isManager = computed(() => currentUser.value?.role === 'manager' || currentUser.value?.role === 'admin')
  const isHolder = computed(() => currentUser.value?.role === 'holder' || currentUser.value?.role === 'user')

  async function login({ email, password }) {
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err?.message || '登入失敗')
      }
      const user = await res.json()
      console.log('JWT token:', user.token) // 新增這一行
      currentUser.value = user
      token.value = user.token
      localStorage.setItem(STORAGE_KEY, JSON.stringify(user))
      localStorage.setItem(TOKEN_KEY, user.token)
      return { success: true, user }
    } catch (e) {
      currentUser.value = null
      token.value = ''
      localStorage.removeItem(STORAGE_KEY)
      localStorage.removeItem(TOKEN_KEY)
      return { success: false, message: e.message }
    }
  }
  async function signup(payload) {
    const res = await fetch('/api/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err?.message || '註冊失敗')
    }
    return await res.json()
  }

  function logout() {
    currentUser.value = null
    token.value = ''
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(TOKEN_KEY)
  }

  return { currentUser, token, isLoggedIn, isManager, isHolder, login, logout }
})
