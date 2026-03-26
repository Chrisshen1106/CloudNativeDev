import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const mockUsers = [
  { id: 'U001', name: '王小明', role: 'holder', department: '研發部', email: 'wang@company.com' },
  { id: 'U002', name: '李美麗', role: 'holder', department: '業務部', email: 'li@company.com' },
  { id: 'U003', name: '張志偉', role: 'holder', department: '行銷部', email: 'zhang@company.com' },
  { id: 'U004', name: '陳大衛', role: 'manager', department: '資產管理部', email: 'chen@company.com' },
  { id: 'U005', name: '黃桂昱', role: 'manager', department: '資產管理部', email: 'huang@company.com' },
]

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref(
    JSON.parse(localStorage.getItem('ams_current_user') || 'null')
  )

  const isLoggedIn = computed(() => currentUser.value !== null)
  const isManager = computed(() => currentUser.value?.role === 'manager')
  const isHolder = computed(() => currentUser.value?.role === 'holder')

  function login(userId) {
    const user = mockUsers.find((u) => u.id === userId)
    if (user) {
      currentUser.value = user
      localStorage.setItem('ams_current_user', JSON.stringify(user))
      return true
    }
    return false
  }

  function logout() {
    currentUser.value = null
    localStorage.removeItem('ams_current_user')
  }

  return { currentUser, isLoggedIn, isManager, isHolder, login, logout }
})
