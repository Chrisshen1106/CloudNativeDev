<!-- 修正：移除檔案開頭多餘 HTML，<template> 必須為第一行 -->
<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-950 via-indigo-900 to-indigo-800 flex items-center justify-center p-4">
    <!-- Background decoration -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
    </div>

    <div class="relative w-full max-w-md">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-white/10 backdrop-blur rounded-2xl mb-4 shadow-lg">
          <svg viewBox="0 0 64 64" fill="none" class="w-10 h-10" xmlns="http://www.w3.org/2000/svg">
            <!-- Monitor frame -->
            <rect x="6" y="8" width="52" height="36" rx="4" stroke="white" stroke-width="2.5"/>
            <line x1="6" y1="36" x2="58" y2="36" stroke="white" stroke-width="2"/>
            <!-- Bar chart (dashboard) -->
            <rect x="14" y="24" width="7" height="8" rx="1" fill="white" opacity="0.35"/>
            <rect x="24" y="18" width="7" height="14" rx="1" fill="white" opacity="0.55"/>
            <rect x="34" y="21" width="7" height="11" rx="1" fill="white" opacity="0.35"/>
            <rect x="44" y="15" width="7" height="17" rx="1" fill="white" opacity="0.55"/>
            <!-- Monitor stand -->
            <path d="M27 44h10v2H27z" fill="white" opacity="0.5"/>
            <line x1="22" y1="49" x2="42" y2="49" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
            <!-- Checkmark badge -->
            <circle cx="54" cy="12" r="7" fill="#818cf8"/>
            <path d="M51 12l2 2.5 4-4.5" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">{{ t('login.title') }}</h1>
        <p class="text-indigo-200 text-sm">{{ t('login.subtitle') }}</p>
      </div>

      <!-- Card -->
      <div class="bg-white rounded-2xl shadow-2xl p-8">

        <!-- Email -->
        <!-- Email -->
        <div class="mb-4">
          <label class="form-label">電子信箱</label>
          <input
            v-model="email"
            type="email"
            class="form-input"
            placeholder="請輸入電子信箱"
            @keyup.enter="handleLogin"
          />
        </div>

        <!-- Password -->
        <div class="mb-6">
          <label class="form-label">{{ t('login.password') }}</label>
          <input
            v-model="password"
            type="password"
            class="form-input"
            placeholder="請輸入密碼"
            @keyup.enter="handleLogin"
          />
        </div>

        <!-- Login button -->
        <button
          class="w-full btn-primary py-3 text-base font-semibold rounded-xl"
          :disabled="!email || !password"
          @click="handleLogin"
        >
          {{ t('login.loginButton') }}
        </button>

        <!-- Register button -->
        <button
          class="w-full btn-secondary py-3 text-base font-semibold rounded-xl mt-3"
          @click="showRegister = true"
        >
          {{ t('login.registerButton') || '註冊帳號' }}
        </button>

        <!-- Error -->
        <Transition name="fade-down">
          <p v-if="errorMsg" class="mt-3 text-center text-sm text-red-600">{{ errorMsg }}</p>
        </Transition>
      </div>



      <!-- Register Modal -->
      <Transition name="fade-down">
        <div v-if="showRegister" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md relative">
            <button class="absolute top-3 right-3 text-gray-400 hover:text-gray-600" @click="showRegister = false">✕</button>
            <h2 class="text-xl font-bold mb-4">{{ t('login.registerTitle') || '註冊新帳號' }}</h2>
            <div class="mb-3">
              <label class="form-label">姓名</label>
              <input v-model="regName" type="text" class="form-input" placeholder="請輸入姓名" />
            </div>
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input v-model="regEmail" type="email" class="form-input" placeholder="請輸入 Email" />
            </div>
            <div class="mb-3">
              <label class="form-label">密碼</label>
              <input v-model="regPassword" type="password" class="form-input" placeholder="請輸入密碼" />
            </div>
            <div class="mb-3">
              <label class="form-label">部門</label>
              <select v-model="regDepartment" class="form-input">
                <option value="" disabled>請選擇部門</option>
                <option value="1">研發部</option>
                <option value="2">人資部</option>
                <option value="3">財務部</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">角色</label>
              <select v-model="regRole" class="form-input">
                <option value="user">一般使用者</option>
                <option value="admin">管理員</option>
              </select>
            </div>
            <button class="w-full btn-primary py-3 text-base font-semibold rounded-xl mt-2" :disabled="regLoading" @click="handleRegister">
              {{ regLoading ? '註冊中...' : (t('login.registerButton') || '註冊') }}
            </button>
            <Transition name="fade-down">
              <p v-if="regError" class="mt-3 text-center text-sm text-red-600">{{ regError }}</p>
            </Transition>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'

const authStore = useAuthStore()
const router = useRouter()
const { t } = useI18n()

const email = ref('')
const password = ref('')
const errorMsg = ref('')

// 註冊相關
const showRegister = ref(false)
const regName = ref('')
const regEmail = ref('')
const regPassword = ref('')
const regDepartment = ref('')
const regRole = ref('user')
const regError = ref('')
const regLoading = ref(false)
// 部門選單固定三個選項
function openRegister() {
  showRegister.value = true
}

async function handleLogin() {
  errorMsg.value = ''
  if (!email.value || !password.value) {
    errorMsg.value = '請輸入帳號與密碼'
    return
  }
  const { success, message } = await authStore.login({ email: email.value, password: password.value })
  if (success) {
    router.push('/dashboard')
  } else {
    errorMsg.value = message || '登入失敗'
  }
}

async function handleRegister() {
  regError.value = ''
  regLoading.value = true
  try {
    if (!regName.value || !regEmail.value || !regPassword.value || !regDepartment.value || !regRole.value) {
      regError.value = '請填寫所有欄位'
      regLoading.value = false
      return
    }
    const res = await fetch('/api/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: regName.value,
        email: regEmail.value,
        password: regPassword.value,
        idDepartment: Number(regDepartment.value),
        role: regRole.value
      })
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err?.message || '註冊失敗')
    }
    // 註冊成功自動填入登入表單
    const user = await res.json()
    email.value = regEmail.value
    password.value = regPassword.value
    showRegister.value = false
    regName.value = ''
    regEmail.value = ''
    regPassword.value = ''
    regDepartment.value = ''
    regRole.value = 'user'
    regError.value = ''
    regLoading.value = false
  } catch (e) {
    regError.value = e.message
    regLoading.value = false
  }
}
</script>

<style scoped>
.fade-down-enter-active { transition: all 0.2s ease-out; }
.fade-down-leave-active { transition: all 0.15s ease-in; }
.fade-down-enter-from   { opacity: 0; transform: translateY(-6px); }
.fade-down-leave-to     { opacity: 0; transform: translateY(-6px); }
</style>
