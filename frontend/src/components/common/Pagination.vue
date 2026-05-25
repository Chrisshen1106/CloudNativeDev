<template>
  <div v-if="totalPages > 1" class="flex flex-col gap-3 pt-4 sm:flex-row sm:items-center sm:justify-between">
    <p class="text-sm text-gray-500">
      {{ t('pagination.summary', { total, current: currentPage, totalPages }) }}
    </p>
    <div class="flex max-w-full items-center gap-1 overflow-x-auto pb-1">
      <button
        class="shrink-0 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
        :disabled="currentPage <= 1"
        @click="$emit('pageChange', currentPage - 1)"
      >
        ←
      </button>
      <button
        v-for="page in visiblePages"
        :key="page"
        class="shrink-0 rounded-lg border px-3 py-1.5 text-sm transition-colors"
        :class="page === currentPage
          ? 'bg-indigo-600 text-white border-indigo-600'
          : 'border-gray-200 text-gray-600 hover:bg-gray-50'"
        @click="page !== '...' && $emit('pageChange', page)"
      >
        {{ page }}
      </button>
      <button
        class="shrink-0 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
        :disabled="currentPage >= totalPages"
        @click="$emit('pageChange', currentPage + 1)"
      >
        →
      </button>
    </div>
  </div>
  <div v-else-if="total > 0" class="pt-4">
    <p class="text-sm text-gray-500">{{ t('pagination.totalOnly', { total }) }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '@/composables/useI18n'

const props = defineProps({
  total: { type: Number, required: true },
  pageSize: { type: Number, default: 10 },
  currentPage: { type: Number, required: true },
})

defineEmits(['pageChange'])
const { t } = useI18n()

const totalPages = computed(() => Math.ceil(props.total / props.pageSize))

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = props.currentPage
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  if (current <= 4) return [1, 2, 3, 4, 5, '...', total]
  if (current >= total - 3) return [1, '...', total - 4, total - 3, total - 2, total - 1, total]
  return [1, '...', current - 1, current, current + 1, '...', total]
})
</script>
