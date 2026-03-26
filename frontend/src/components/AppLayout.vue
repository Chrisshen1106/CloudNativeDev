<template>
  <div class="flex h-screen overflow-hidden bg-gray-50">
    <AppSidebar />
    <div class="flex-1 flex flex-col overflow-hidden ml-60">
      <AppHeader />
      <main class="flex-1 overflow-y-auto p-6">
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
