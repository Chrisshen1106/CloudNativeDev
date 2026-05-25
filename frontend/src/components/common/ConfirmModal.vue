<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4" @click.self="$emit('cancel')">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('cancel')"></div>

      <!-- Modal -->
      <div class="relative max-h-[calc(100dvh-1.5rem)] w-full max-w-md overflow-y-auto rounded-2xl bg-white p-5 shadow-2xl animate-modal sm:p-6">
        <!-- Icon -->
        <div class="flex items-center gap-3 mb-4">
          <div :class="iconWrapClass" class="flex items-center justify-center w-10 h-10 rounded-full shrink-0">
            <span class="text-xl">{{ iconEmoji }}</span>
          </div>
          <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
        </div>

        <!-- Message -->
        <p v-if="message" class="text-sm text-gray-600 mb-4 leading-relaxed">{{ message }}</p>

        <!-- Input (optional) -->
        <div v-if="showInput" class="mb-4">
          <label class="form-label">{{ inputLabel }}</label>
          <textarea
            v-model="inputValue"
            :placeholder="inputPlaceholder"
            rows="3"
            class="form-textarea"
          ></textarea>
        </div>

        <!-- Slot for extra content -->
        <slot></slot>

        <!-- Actions -->
        <div class="mt-5 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button type="button" class="btn-secondary" @click="$emit('cancel')">
            {{ cancelText || t('common.cancel') }}
          </button>
          <button
            type="button"
            :class="confirmBtnClass"
            :disabled="showInput && requireInput && !inputValue.trim()"
            @click="handleConfirm"
          >
            {{ confirmText || t('common.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from '@/composables/useI18n'

const props = defineProps({
  title: { type: String, required: true },
  message: { type: String, default: '' },
  confirmText: { type: String, default: '' },
  cancelText: { type: String, default: '' },
  variant: { type: String, default: 'primary' }, // 'primary' | 'danger' | 'warning' | 'success'
  showInput: { type: Boolean, default: false },
  inputLabel: { type: String, default: '' },
  inputPlaceholder: { type: String, default: '' },
  requireInput: { type: Boolean, default: false },
})

const emit = defineEmits(['confirm', 'cancel'])
const { t } = useI18n()

const inputValue = ref('')

const confirmBtnClass = computed(() => {
  const map = { primary: 'btn-primary', danger: 'btn-danger', warning: 'btn-warning', success: 'btn-success' }
  return map[props.variant] || 'btn-primary'
})

const iconWrapClass = computed(() => {
  const map = {
    primary: 'bg-indigo-100',
    danger:  'bg-red-100',
    warning: 'bg-amber-100',
    success: 'bg-emerald-100',
  }
  return map[props.variant] || 'bg-indigo-100'
})

const iconEmoji = computed(() => {
  const map = { primary: '', danger: '', warning: '', success: '' }
  return map[props.variant] || ''
})

function handleConfirm() {
  emit('confirm', inputValue.value)
  inputValue.value = ''
}
</script>

<style scoped>
@keyframes modal-in {
  from { opacity: 0; transform: scale(0.95) translateY(-8px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}
.animate-modal {
  animation: modal-in 0.18s ease-out;
}
</style>
