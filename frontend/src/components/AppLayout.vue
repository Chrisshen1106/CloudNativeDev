<template>
  <div class="flex h-dvh flex-col overflow-hidden bg-gray-50 lg:flex-row">
    <AppSidebar />
    <div class="flex min-w-0 flex-1 flex-col overflow-hidden lg:ml-60">
      <AppHeader />
      <main class="min-w-0 flex-1 overflow-y-auto overflow-x-hidden p-4 sm:p-6">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" :key="$route.path" />
          </Transition>
        </RouterView>
      </main>
    </div>
    <ToastNotification />
  </div>
</template>

<script setup>
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import ToastNotification from '@/components/common/ToastNotification.vue'
</script>

<style scoped>
.page-enter-active, .page-leave-active { transition: opacity 0.12s ease; }
.page-enter-from, .page-leave-to { opacity: 0; }
</style>
