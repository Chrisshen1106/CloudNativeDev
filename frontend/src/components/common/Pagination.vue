<template>
  <div v-if="totalPages > 1" class="flex items-center justify-between pt-4">
    <p class="text-sm text-gray-500">
      共 <span class="font-medium text-gray-700">{{ total }}</span> 筆，
      第 <span class="font-medium text-gray-700">{{ currentPage }}</span> /
      <span class="font-medium text-gray-700">{{ totalPages }}</span> 頁
    </p>
    <div class="flex items-center gap-1">
      <button
        class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        :disabled="currentPage <= 1"
        @click="$emit('pageChange', currentPage - 1)"
      >
        ←
      </button>
      <button
        v-for="page in visiblePages"
        :key="page"
        class="px-3 py-1.5 text-sm rounded-lg border transition-colors"
        :class="page === currentPage
          ? 'bg-indigo-600 text-white border-indigo-600'
          : 'border-gray-200 text-gray-600 hover:bg-gray-50'"
        @click="page !== '...' && $emit('pageChange', page)"
      >
        {{ page }}
      </button>
      <button
        class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        :disabled="currentPage >= totalPages"
        @click="$emit('pageChange', currentPage + 1)"
      >
        →
      </button>
    </div>
  </div>
  <div v-else-if="total > 0" class="pt-4">
    <p class="text-sm text-gray-500">共 <span class="font-medium text-gray-700">{{ total }}</span> 筆</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  total: { type: Number, required: true },
  pageSize: { type: Number, default: 10 },
  currentPage: { type: Number, required: true },
})

defineEmits(['pageChange'])

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
