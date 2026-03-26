<template>
  <span :class="badgeClass" class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold whitespace-nowrap">
    <span class="w-1.5 h-1.5 rounded-full" :class="dotClass"></span>
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '@/composables/useI18n'

const props = defineProps({
  status: { type: String, required: true },
  type: { type: String, default: 'asset' }, // 'asset' | 'request'
})

const { t } = useI18n()

const label = computed(() => {
  if (props.type === 'asset') return t(`asset.statuses.${props.status}`)
  return t(`request.statuses.${props.status}`)
})

const config = {
  // asset statuses
  normal:       { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  // request statuses
  pending:      { bg: 'bg-blue-50',    text: 'text-blue-700',    dot: 'bg-blue-500' },
  under_repair: { bg: 'bg-amber-50',   text: 'text-amber-700',   dot: 'bg-amber-500' },
  completed:    { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  rejected:     { bg: 'bg-red-50',     text: 'text-red-700',     dot: 'bg-red-500' },
}

const current = computed(() => config[props.status] || { bg: 'bg-gray-50', text: 'text-gray-600', dot: 'bg-gray-400' })
const badgeClass = computed(() => `${current.value.bg} ${current.value.text}`)
const dotClass   = computed(() => current.value.dot)
</script>
