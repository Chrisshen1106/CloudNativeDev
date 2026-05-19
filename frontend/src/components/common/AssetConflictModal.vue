<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="$emit('cancel')">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('cancel')"></div>

      <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden animate-modal">
        <div class="px-6 py-5 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">資料已被其他人更新</h3>
          <p class="mt-1 text-sm text-gray-600">
            請比較你目前要儲存的內容與資料庫最新內容。左側可直接修改，重新提交時會使用最新版本號。
          </p>
        </div>

        <div class="overflow-auto max-h-[calc(90vh-150px)]">
          <div class="min-w-[760px]">
            <div class="grid grid-cols-[180px_1fr_1fr] gap-0 bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase">
              <div class="px-4 py-3">欄位</div>
              <div class="px-4 py-3 border-l border-gray-200">我的內容</div>
              <div class="px-4 py-3 border-l border-gray-200">資料庫最新內容</div>
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
                將改用最新版本重送
              </div>
              <div class="px-4 py-3 border-l border-gray-200 text-sm font-mono text-gray-700">
                {{ latestContent?.version ?? '-' }}
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-white">
          <button type="button" class="btn-secondary" @click="$emit('cancel')">
            取消本次編輯
          </button>
          <button type="button" class="btn-warning" @click="submit">
            用我的內容重新提交
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  myContent: { type: Object, required: true },
  latestContent: { type: Object, required: true },
  holderUsers: { type: Array, default: () => [] },
})

const emit = defineEmits(['submit', 'cancel'])

const fields = [
  { key: 'name', label: '資產名稱' },
  { key: 'category', label: '分類', control: 'select', placeholder: '-- 選擇分類 --' },
  { key: 'status', label: '狀態', control: 'select', placeholder: '-- 選擇狀態 --' },
  { key: 'model', label: '型號' },
  { key: 'specs', label: '規格' },
  { key: 'serial_Number', label: '序號' },
  { key: 'notes', label: '備註', multiline: true },
  { key: 'supplier', label: '供應商' },
  { key: 'purchase_price', label: '採購金額', type: 'number' },
  { key: 'purchase_date', label: '採購日期', type: 'date' },
  { key: 'activationDate', label: '啟用日期', type: 'date' },
  { key: 'warrantyExpiry', label: '保固期限', type: 'date' },
  { key: 'location', label: '存放地點' },
  { key: 'ownerId', label: '負責人', control: 'select', placeholder: '-- 選擇負責人 --' },
  { key: 'idUser', label: '使用者ID', control: 'select', placeholder: '-- 選擇 idUser --' },
  { key: 'department', label: '部門' },
  { key: 'userDepartment', label: '使用部門' },
]

const categoryOptions = [
  { value: 'computer', label: '電腦類' },
  { value: 'phone', label: '手機類' },
  { value: 'tablet', label: '平板類' },
]

const statusOptions = [
  { value: 'in_use', label: '正常使用' },
  { value: 'repairing', label: '維修中' },
  { value: 'scrapped', label: '已報廢' },
]

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
  if (field.key === 'category') return appendCurrentOption(categoryOptions, field.key)
  if (field.key === 'status') return appendCurrentOption(statusOptions, field.key)
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
