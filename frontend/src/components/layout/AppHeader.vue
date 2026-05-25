<template>
  <header class="flex min-h-14 shrink-0 items-center justify-between gap-3 border-b border-gray-200 bg-white px-4 py-3 shadow-sm sm:px-6">
    <!-- Breadcrumb -->
    <div class="flex min-w-0 items-center gap-2 text-sm">
      <RouterLink to="/dashboard" class="text-gray-400 hover:text-indigo-600 transition-colors">
        {{ t('nav.dashboard') }}
      </RouterLink>
      <span v-if="breadcrumb" class="text-gray-300 select-none">/</span>
      <span v-if="breadcrumb" class="truncate text-gray-700 font-medium">{{ breadcrumb }}</span>
    </div>

    <!-- Right side -->
    <div class="flex min-w-0 shrink-0 items-center gap-3">
      <!-- Role badge -->
      <span
        class="hidden sm:inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full font-medium"
        :class="authStore.isManager
          ? 'bg-indigo-100 text-indigo-700'
          : 'bg-emerald-100 text-emerald-700'"
      >
        <span>{{ authStore.isManager ? '' : '' }}</span>
        {{ authStore.isManager ? t('login.roleManager') : t('login.roleHolder') }}
      </span>

      <!-- User name -->
      <span class="max-w-28 truncate text-sm font-medium text-gray-700 sm:max-w-none">{{ authStore.currentUser?.name }}</span>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'

const authStore = useAuthStore()
const route = useRoute()
const { t } = useI18n()

const breadcrumb = computed(() => {
  const meta = route.meta
  if (meta?.titleKey) return t(meta.titleKey)
  return ''
})
</script>
