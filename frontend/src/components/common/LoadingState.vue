<template>
  <div class="flex min-h-40 flex-col items-center justify-center gap-4 px-4 py-10 text-center">
    <div class="relative h-12 w-12">
      <div class="absolute inset-0 rounded-full border-4 border-gray-200"></div>
      <div class="absolute inset-0 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent"></div>
    </div>
    <div class="w-full max-w-xs">
      <div class="mb-2 flex items-center justify-between text-xs font-medium text-gray-500">
        <span>{{ label || t('common.loading') }}</span>
        <span>{{ Math.round(displayProgress) }}%</span>
      </div>
      <div class="h-2 overflow-hidden rounded-full bg-gray-100">
        <div
          class="h-full rounded-full bg-indigo-600 transition-all duration-300"
          :style="barStyle"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from '@/composables/useI18n'

const props = defineProps({
  label: {
    type: String,
    default: '',
  },
  progress: {
    type: Number,
    default: null,
  },
})

const { t } = useI18n()
const simulatedProgress = ref(8)
let timer = null

const normalizedProgress = computed(() => {
  if (props.progress === null || Number.isNaN(props.progress)) return null
  return Math.min(100, Math.max(0, props.progress))
})

const displayProgress = computed(() => normalizedProgress.value ?? simulatedProgress.value)
const barStyle = computed(() => ({ width: `${displayProgress.value}%` }))

function startSimulatedProgress() {
  if (timer || normalizedProgress.value !== null) return
  timer = window.setInterval(() => {
    const current = simulatedProgress.value
    if (current < 70) {
      simulatedProgress.value += Math.random() * 8 + 3
    } else if (current < 90) {
      simulatedProgress.value += Math.random() * 3 + 1
    } else if (current < 96) {
      simulatedProgress.value += 0.4
    }
    simulatedProgress.value = Math.min(simulatedProgress.value, 96)
  }, 350)
}

function stopSimulatedProgress() {
  if (!timer) return
  window.clearInterval(timer)
  timer = null
}

watch(normalizedProgress, (value) => {
  if (value === null) {
    startSimulatedProgress()
  } else {
    stopSimulatedProgress()
  }
})

onMounted(startSimulatedProgress)
onUnmounted(stopSimulatedProgress)
</script>
