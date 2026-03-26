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
        <!-- Demo hint -->
        <div class="flex items-start gap-2 bg-blue-50 rounded-lg px-3 py-2.5 mb-6 text-xs text-blue-700">
          <span class="shrink-0 mt-0.5"></span>
          <span>{{ t('login.demoHint') }}</span>
        </div>

        <!-- User select -->
        <div class="mb-4">
          <label class="form-label">{{ t('login.selectUser') }}</label>
          <select v-model="selectedUserId" class="form-select">
            <option value="">{{ t('login.selectUserPlaceholder') }}</option>
            <option v-for="user in mockUsers" :key="user.id" :value="user.id">
              {{ user.name }} — {{ user.department }}
            </option>
          </select>
        </div>

        <!-- Selected user info -->
        <Transition name="fade-down">
          <div v-if="selectedUser" class="mb-4 bg-gray-50 rounded-xl p-4 border border-gray-100">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-sm">
                {{ selectedUser.name.charAt(0) }}
              </div>
              <div>
                <p class="font-semibold text-gray-900 text-sm">{{ selectedUser.name }}</p>
                <p class="text-xs text-gray-500">{{ selectedUser.email }}</p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="bg-white rounded-lg px-3 py-2 border border-gray-100">
                <p class="text-gray-400 mb-0.5">{{ t('login.roleLabel') }}</p>
                <div class="flex items-center gap-1">
                  <span
                    class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold"
                    :class="selectedUser.role === 'manager'
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'bg-emerald-100 text-emerald-700'"
                  >
                    {{ selectedUser.role === 'manager' ? ' ' + t('login.roleManager') : ' ' + t('login.roleHolder') }}
                  </span>
                </div>
              </div>
              <div class="bg-white rounded-lg px-3 py-2 border border-gray-100">
                <p class="text-gray-400 mb-0.5">{{ t('login.deptLabel') }}</p>
                <p class="font-medium text-gray-700">{{ selectedUser.department }}</p>
              </div>
            </div>
          </div>
        </Transition>

        <!-- Password -->
        <div class="mb-6">
          <label class="form-label">{{ t('login.password') }}</label>
          <input
            v-model="password"
            type="password"
            class="form-input"
            :placeholder="t('login.passwordPlaceholder')"
            @keyup.enter="handleLogin"
          />
        </div>

        <!-- Login button -->
        <button
          class="w-full btn-primary py-3 text-base font-semibold rounded-xl"
          :disabled="!selectedUserId || !password"
          @click="handleLogin"
        >
          {{ t('login.loginButton') }}
        </button>

        <!-- Error -->
        <Transition name="fade-down">
          <p v-if="errorMsg" class="mt-3 text-center text-sm text-red-600">{{ errorMsg }}</p>
        </Transition>
      </div>

      <!-- User list hint -->
      <div class="mt-6 text-center">
        <p class="text-indigo-300 text-xs">測試帳號密碼均為 <span class="font-mono bg-white/10 px-1.5 py-0.5 rounded">123456</span></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { mockUsers } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'

const authStore = useAuthStore()
const router = useRouter()
const { t } = useI18n()

const selectedUserId = ref('')
const password = ref('')
const errorMsg = ref('')

const selectedUser = computed(() =>
  selectedUserId.value ? mockUsers.find((u) => u.id === selectedUserId.value) : null
)

function handleLogin() {
  errorMsg.value = ''
  if (!selectedUserId.value) {
    errorMsg.value = '請選擇使用者'
    return
  }
  if (password.value !== '123456') {
    errorMsg.value = '密碼錯誤，測試密碼為 123456'
    return
  }
  authStore.login(selectedUserId.value)
  router.push('/dashboard')
}
</script>

<style scoped>
.fade-down-enter-active { transition: all 0.2s ease-out; }
.fade-down-leave-active { transition: all 0.15s ease-in; }
.fade-down-enter-from   { opacity: 0; transform: translateY(-6px); }
.fade-down-leave-to     { opacity: 0; transform: translateY(-6px); }
</style>
