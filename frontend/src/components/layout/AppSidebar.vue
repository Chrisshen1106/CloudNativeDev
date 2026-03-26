<template>
  <nav class="fixed left-0 top-0 h-screen w-60 bg-indigo-950 text-white flex flex-col z-30 shadow-xl">
    <!-- Logo -->
    <div class="px-5 py-5 border-b border-indigo-800">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center text-base font-bold shrink-0"></div>
        <div>
          <p class="text-sm font-bold leading-tight">{{ t('login.title') }}</p>
          <p class="text-xs text-indigo-300 leading-tight">AMS</p>
        </div>
      </div>
    </div>

    <!-- User info -->
    <div class="px-5 py-4 border-b border-indigo-800">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-full bg-indigo-600 flex items-center justify-center text-sm font-bold shrink-0">
          {{ authStore.currentUser?.name?.charAt(0) }}
        </div>
        <div class="min-w-0">
          <p class="text-sm font-semibold truncate">{{ authStore.currentUser?.name }}</p>
          <p class="text-xs text-indigo-300 truncate">
            {{ authStore.isManager ? t('login.roleManager') : t('login.roleHolder') }}
            · {{ authStore.currentUser?.department }}
          </p>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-3 py-4 overflow-y-auto space-y-1">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150"
        :class="isActive(item.to)
          ? 'bg-indigo-600 text-white shadow-md'
          : 'text-indigo-200 hover:bg-indigo-800 hover:text-white'"
      >
        <span class="text-base">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>

    <!-- Bottom actions -->
    <div class="px-3 py-4 border-t border-indigo-800 space-y-1">
      <!-- Language switcher -->
      <div class="flex items-center gap-2 px-3 py-2">
        <span class="text-xs text-indigo-400 mr-1"></span>
        <button
          v-for="lang in langs"
          :key="lang.code"
          class="text-xs px-2 py-0.5 rounded transition-colors"
          :class="currentLocale === lang.code
            ? 'bg-indigo-600 text-white'
            : 'text-indigo-300 hover:text-white'"
          @click="setLocale(lang.code)"
        >{{ lang.label }}</button>
      </div>
      <!-- Logout -->
      <button
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-indigo-200 hover:bg-indigo-800 hover:text-white transition-all duration-150"
        @click="handleLogout"
      >
        <span class="text-base"></span>
        <span>登出</span>
      </button>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const { t, currentLocale, setLocale } = useI18n()

const langs = [
  { code: 'zh-TW', label: '繁中' },
  { code: 'en',    label: 'EN' },
]

const navItems = computed(() => {
  const items = [
    { to: '/dashboard', icon: '', label: t('nav.dashboard') },
    { to: '/assets',    icon: '', label: t('nav.assets') },
    { to: '/requests',  icon: '', label: t('nav.requests') },
  ]
  if (authStore.isManager) {
    items.push({ to: '/assets/new', icon: '', label: t('nav.addAsset') })
  } else {
    items.push({ to: '/requests/new', icon: '', label: t('nav.newRequest') })
  }
  return items
})

function isActive(to) {
  if (to === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(to)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
