<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="$emit('cancel')">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('cancel')"></div>

      <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden animate-modal">
        <div class="px-6 py-5 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">{{ t('conflict.title') }}</h3>
          <p class="mt-1 text-sm text-gray-600">
            {{ t('conflict.description') }}
          </p>
        </div>

        <div class="overflow-auto max-h-[calc(90vh-150px)]">
          <div class="min-w-[760px]">
            <div class="grid grid-cols-[180px_1fr_1fr] gap-0 bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase">
              <div class="px-4 py-3">{{ t('common.field') }}</div>
              <div class="px-4 py-3 border-l border-gray-200">{{ t('common.myContent') }}</div>
              <div class="px-4 py-3 border-l border-gray-200">{{ t('common.latestContent') }}</div>
            </div>

            <div
              v-for="field in fields"
              :key="field.key"
              :class="[
                'grid grid-cols-[180px_1fr_1fr] gap-0 border-b border-gray-100',
                isDifferent(field.key) ? 'bg-red-50/80' : 'bg-white'
              ]"
            >
              <div class="px-4 py-3 text-sm font-medium text-gray-700">
                {{ field.label }}
              </div>
              <div :class="['px-4 py-3 border-l', isDifferent(field.key) ? 'border-red-200' : 'border-gray-200']">
                <select
                  v-if="field.control === 'select'"
                  v-model="draft[field.key]"
                  :class="['form-select', isDifferent(field.key) ? 'border-red-300 focus:ring-red-500' : '']"
                  @change="handleFieldChange(field.key)"
                >
                  <option value="">{{ field.placeholder }}</option>
                  <option
                    v-for="option in getOptions(field)"
                    :key="`${field.key}-${option.value}`"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
                <textarea
                  v-else-if="field.multiline"
                  v-model="draft[field.key]"
                  rows="2"
                  :class="['form-textarea min-h-[64px]', isDifferent(field.key) ? 'border-red-300 focus:ring-red-500' : '']"
                ></textarea>
                <input
                  v-else
                  v-model="draft[field.key]"
                  :type="field.type || 'text'"
                  :class="['form-input', isDifferent(field.key) ? 'border-red-300 focus:ring-red-500' : '']"
                />
              </div>
              <div :class="['px-4 py-3 border-l', isDifferent(field.key) ? 'border-red-200' : 'border-gray-200']">
                <div :class="[
                  'min-h-[38px] rounded-lg border px-3 py-2 text-sm text-gray-700 whitespace-pre-wrap',
                  isDifferent(field.key) ? 'border-red-200 bg-white' : 'border-gray-200 bg-gray-50'
                ]">
                  {{ displayFieldValue(field, latestContent?.[field.key]) }}
                </div>
              </div>
            </div>

            <div class="grid grid-cols-[180px_1fr_1fr] gap-0 bg-gray-50">
              <div class="px-4 py-3 text-sm font-medium text-gray-700">version</div>
              <div class="px-4 py-3 border-l border-gray-200 text-sm text-gray-500">
                {{ t('conflict.useLatestVersion') }}
              </div>
              <div class="px-4 py-3 border-l border-gray-200 text-sm font-mono text-gray-700">
                {{ latestContent?.version ?? '-' }}
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-white">
          <button type="button" class="btn-secondary" @click="$emit('cancel')">
            {{ t('conflict.cancelEdit') }}
          </button>
          <button type="button" class="btn-warning" @click="submit">
            {{ t('conflict.resubmitMine') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from '@/composables/useI18n'

const props = defineProps({
  myContent: { type: Object, required: true },
  latestContent: { type: Object, required: true },
  holderUsers: { type: Array, default: () => [] },
})

const emit = defineEmits(['submit', 'cancel'])
const { t } = useI18n()

const fields = computed(() => [
  { key: 'name', label: t('asset.name') },
  { key: 'category', label: t('asset.category'), control: 'select', placeholder: t('assetForm.categoryPlaceholder') },
  { key: 'status', label: t('asset.status'), control: 'select', placeholder: t('assetForm.statusPlaceholder') },
  { key: 'model', label: t('asset.model') },
  { key: 'specs', label: t('asset.specs') },
  { key: 'serial_Number', label: t('asset.serialNumber') },
  { key: 'notes', label: t('asset.notes'), multiline: true },
  { key: 'supplier', label: t('asset.supplier') },
  { key: 'purchase_price', label: t('asset.purchasePrice'), type: 'number' },
  { key: 'purchase_date', label: t('asset.purchaseDate'), type: 'date' },
  { key: 'activationDate', label: t('asset.activationDate'), type: 'date' },
  { key: 'warrantyExpiry', label: t('asset.warrantyExpiry'), type: 'date' },
  { key: 'location', label: t('asset.location') },
  { key: 'ownerId', label: t('asset.owner'), control: 'select', placeholder: t('assetForm.ownerPlaceholder') },
  { key: 'idUser', label: t('asset.idUser'), control: 'select', placeholder: t('conflict.selectIdUser') },
  { key: 'department', label: t('asset.department') },
  { key: 'userDepartment', label: t('asset.userDepartment') },
])

const categoryOptions = computed(() => [
  { value: 'computer', label: t('asset.categories.computer') },
  { value: 'phone', label: t('asset.categories.phone') },
  { value: 'tablet', label: t('asset.categories.tablet') },
])

const statusOptions = computed(() => [
  { value: 'in_use', label: t('asset.statuses.in_use') },
  { value: 'repairing', label: t('asset.statuses.repairing') },
  { value: 'scrapped', label: t('asset.statuses.scrapped') },
])

const draft = ref({})

watch(
  () => props.myContent,
  (value) => {
    draft.value = { ...value }
  },
  { immediate: true, deep: true }
)

function normalize(value) {
  if (value === null || value === undefined) return ''
  return String(value)
}

function displayValue(value) {
  const normalized = normalize(value)
  return normalized || '-'
}

function userId(user) {
  return user?.idUser ?? user?.id ?? ''
}

function userDepartment(user) {
  return user?.department || user?.departmentName || ''
}

function findUser(value) {
  return props.holderUsers.find((user) => normalize(userId(user)) === normalize(value))
}

function appendCurrentOption(options, key) {
  const values = [draft.value?.[key], props.latestContent?.[key]]
  const nextOptions = [...options]

  for (const value of values) {
    const normalized = normalize(value)
    if (!normalized) continue
    if (!nextOptions.some((option) => normalize(option.value) === normalized)) {
      nextOptions.push({ value, label: normalized })
    }
  }

  return nextOptions
}

function getOptions(field) {
  if (field.key === 'category') return appendCurrentOption(categoryOptions.value, field.key)
  if (field.key === 'status') return appendCurrentOption(statusOptions.value, field.key)
  if (field.key === 'ownerId') {
    const options = props.holderUsers.map((user) => ({
      value: userId(user),
      label: `${user.name || userId(user)} (${userDepartment(user)})`,
    }))
    return appendCurrentOption(options, field.key)
  }
  if (field.key === 'idUser') {
    const options = props.holderUsers.map((user) => ({
      value: userId(user),
      label: `${userId(user)} - ${user.name || ''}`,
    }))
    return appendCurrentOption(options, field.key)
  }
  return []
}

function displayFieldValue(field, value) {
  if (field.control !== 'select') return displayValue(value)

  const option = getOptions(field).find((item) => normalize(item.value) === normalize(value))
  return option?.label || displayValue(value)
}

function isDifferent(key) {
  return normalize(draft.value?.[key]) !== normalize(props.latestContent?.[key])
}

function handleFieldChange(key) {
  if (key === 'ownerId') {
    const user = findUser(draft.value.ownerId)
    draft.value.department = user ? userDepartment(user) : ''
  }

  if (key === 'idUser') {
    const user = findUser(draft.value.idUser)
    draft.value.userDepartment = user ? userDepartment(user) : ''
  }
}

function submit() {
  emit('submit', {
    ...props.myContent,
    ...draft.value,
    version: props.latestContent.version,
  })
}
</script>

<style scoped>
@keyframes modal-in {
  from { opacity: 0; transform: scale(0.96) translateY(-8px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.animate-modal {
  animation: modal-in 0.18s ease-out;
}
</style>
