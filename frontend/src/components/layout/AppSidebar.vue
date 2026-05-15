<template>
  <nav class="fixed left-0 top-0 h-screen w-60 bg-indigo-950 text-white flex flex-col z-30 shadow-xl">
    <!-- Logo -->
    <div class="px-5 py-5 border-b border-indigo-800">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center shrink-0">
          <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M4 7h16" />
            <path d="M7 7V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v2" />
            <rect x="4" y="7" width="16" height="13" rx="2" />
            <path d="M9 12h6" />
          </svg>
        </div>
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
        <span class="w-5 h-5 shrink-0 flex items-center justify-center">
          <svg v-if="item.icon === 'dashboard'" viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="3" y="3" width="7" height="7" rx="1" />
            <rect x="14" y="3" width="7" height="7" rx="1" />
            <rect x="14" y="14" width="7" height="7" rx="1" />
            <rect x="3" y="14" width="7" height="7" rx="1" />
          </svg>
          <svg v-else-if="item.icon === 'assets'" viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M4 7h16" />
            <path d="M7 7V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v2" />
            <rect x="4" y="7" width="16" height="13" rx="2" />
            <path d="M8 12h8" />
          </svg>
          <svg v-else-if="item.icon === 'requests'" viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M8 3h8l4 4v14H4V3h4Z" />
            <path d="M16 3v5h5" />
            <path d="M8 13h8" />
            <path d="M8 17h5" />
          </svg>
          <svg v-else-if="item.icon === 'addAsset'" viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M4 7h16" />
            <rect x="4" y="7" width="16" height="13" rx="2" />
            <path d="M12 11v6" />
            <path d="M9 14h6" />
          </svg>
          <svg v-else-if="item.icon === 'newRequest'" viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M8 3h8l4 4v14H4V3h4Z" />
            <path d="M16 3v5h5" />
            <path d="M12 12v6" />
            <path d="M9 15h6" />
          </svg>
        </span>
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
        <span class="w-5 h-5 shrink-0 flex items-center justify-center">
          <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <path d="M16 17l5-5-5-5" />
            <path d="M21 12H9" />
          </svg>
        </span>
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
    { to: '/dashboard', icon: 'dashboard', label: t('nav.dashboard') },
    { to: '/assets',    icon: 'assets',    label: t('nav.assets') },
    { to: '/requests',  icon: 'requests',  label: t('nav.requests') },
  ]
  if (authStore.isManager) {
    items.push({ to: '/assets/new', icon: 'addAsset', label: t('nav.addAsset') })
  } else {
    items.push({ to: '/requests/new', icon: 'newRequest', label: t('nav.newRequest') })
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
