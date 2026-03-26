<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
      <TransitionGroup name="toast">
        <div
          v-for="item in notifStore.items"
          :key="item.id"
          class="pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl shadow-lg border max-w-sm"
          :class="toastClass(item.type)"
        >
          <span class="text-base mt-0.5 shrink-0">{{ toastIcon(item.type) }}</span>
          <p class="text-sm font-medium leading-snug">{{ item.message }}</p>
          <button
            class="ml-auto shrink-0 opacity-60 hover:opacity-100 text-lg leading-none"
            @click="notifStore.remove(item.id)"
          >×</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useNotificationsStore } from '@/stores/notifications'

const notifStore = useNotificationsStore()

function toastClass(type) {
  const map = {
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    error:   'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
    info:    'bg-blue-50 border-blue-200 text-blue-800',
  }
  return map[type] || map.info
}

function toastIcon(type) {
  const map = { success: '', error: '', warning: '', info: '' }
  return map[type] || 'ℹ️'
}
</script>

<style scoped>
.toast-enter-active { transition: all 0.25s ease-out; }
.toast-leave-active { transition: all 0.2s ease-in; }
.toast-enter-from  { opacity: 0; transform: translateX(100%); }
.toast-leave-to    { opacity: 0; transform: translateX(100%); }
</style>
