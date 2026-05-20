import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useI18n } from '@/composables/useI18n'

const STORAGE_KEY = 'ams_current_user'
const TOKEN_KEY = 'ams_token'

export const useAuthStore = defineStore('auth', () => {
  const { t } = useI18n()
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
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data?.message || t('login.loginFailed'))
      }
      console.log('JWT token:', data.token)
      currentUser.value = data
      token.value = 'Bearer ' + data.token
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
      localStorage.setItem(TOKEN_KEY, 'Bearer ' + data.token)
      return { success: true, user: data }
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
      throw new Error(err?.message || t('login.registerFailed'))
    }
    return await res.json()
  }

  function logout() {
    currentUser.value = null
    token.value = ''
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(TOKEN_KEY)
  }

  // 取得所有使用者資料
  async function fetchAllUsers() {
    const headers = {
      'Authorization': localStorage.getItem('ams_token') || '',
    }
    const endpoints = ['/user-api/users', '/api/users']

    for (const endpoint of endpoints) {
      const res = await fetch(endpoint, { headers })
      if (res.ok) return await res.json()
    }

    throw new Error(t('login.fetchUsersFailed'))
  }

  return { currentUser, token, isLoggedIn, isManager, isHolder, login, logout, fetchAllUsers }
})
