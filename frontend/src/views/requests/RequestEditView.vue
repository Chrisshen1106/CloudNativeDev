<template>
  <div class="max-w-3xl mx-auto">
    <div class="page-header items-start gap-4">
      <div class="min-w-0">
        <button class="btn-secondary btn-sm mb-3" @click="router.back()">
          ← {{ t('common.back') }}
        </button>
        <h1 class="page-title text-xl">{{ t('request.editRequest') }}</h1>
        <p class="text-sm text-gray-500 mt-1 font-mono">{{ request?.id || route.params.id }}</p>
      </div>
      <StatusBadge v-if="request" :status="request.status" type="request" />
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-5">
      <div class="card overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 bg-gray-50/70">
          <h2 class="section-title mb-0">{{ t('request.assetInfo') }}</h2>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-gray-100">
          <div class="p-5">
            <p class="text-xs font-medium text-gray-500 mb-1">{{ t('request.requestId') }}</p>
            <p class="font-mono text-sm text-indigo-600 truncate">{{ request?.id || '-' }}</p>
          </div>
          <div class="p-5">
            <p class="text-xs font-medium text-gray-500 mb-1">{{ t('request.assetNumber') }}</p>
            <p class="font-mono text-sm text-gray-900 truncate">{{ request?.assetId || '-' }}</p>
          </div>
          <div class="p-5">
            <p class="text-xs font-medium text-gray-500 mb-1">{{ t('request.requestDate') }}</p>
            <p class="text-sm text-gray-900 truncate">{{ request?.requestDate || '-' }}</p>
          </div>
        </div>
      </div>

      <div class="card p-5">
        <div class="flex items-center justify-between gap-3 mb-3">
          <h2 class="section-title mb-0">{{ t('request.faultDescription') }}</h2>
          <span class="text-xs text-gray-400">{{ t('request.characterCount', { count: form.issue_description.length }) }}</span>
        </div>
        <textarea
          v-model="form.issue_description"
          rows="7"
          class="form-textarea w-full leading-6"
          required
          :placeholder="t('request.faultDescPlaceholder')"
        ></textarea>
      </div>

      <div class="card p-5">
        <div class="flex items-center justify-between gap-3 mb-4">
          <div>
            <h2 class="section-title mb-0">{{ t('request.attachments') }}</h2>
            <p class="text-xs text-gray-500 mt-1">{{ t('request.attachmentsHint') }}</p>
          </div>
        </div>

        <input
          ref="fileInput"
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          class="hidden"
          @change="handleFileChange"
        />

        <div
          v-if="!previewUrl"
          class="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center hover:border-indigo-400 hover:bg-indigo-50/30 transition-all cursor-pointer"
          @click="fileInput?.click()"
          @dragover.prevent
          @drop.prevent="handleDrop"
        >
          <p class="text-sm font-medium text-gray-700">{{ t('request.uploadPrompt') }}</p>
          <p class="text-xs text-gray-400 mt-1">{{ t('request.attachmentsHint') }}</p>
        </div>

        <div v-else class="flex flex-col sm:flex-row gap-4 rounded-lg border border-gray-200 bg-gray-50 p-3">
          <img :src="previewUrl" :alt="form.attachmentName" class="w-full sm:w-36 aspect-video sm:aspect-square object-cover rounded-md border border-gray-200 bg-white" />
          <div class="min-w-0 flex-1 flex flex-col justify-between gap-3 py-1">
            <div>
              <p class="text-sm font-medium text-gray-900 truncate">{{ form.attachmentName || t('request.attachments') }}</p>
              <p class="text-xs text-gray-500 mt-1">{{ form.attachmentFile ? form.attachmentFile.type : t('request.attachments') }}</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <button type="button" class="btn-secondary btn-sm" @click="fileInput?.click()">
                {{ t('common.edit') }}
              </button>
              <button type="button" class="btn-danger btn-sm" @click="removeAttachment">
                {{ t('common.delete') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 pt-1">
        <button type="button" class="btn-secondary" @click="router.back()">{{ t('common.cancel') }}</button>
        <button type="submit" class="btn-primary" :disabled="!form.issue_description.trim()">{{ t('common.save') }}</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRequestsStore } from '@/stores/requests'
import { useNotificationsStore } from '@/stores/notifications'
import { useI18n } from '@/composables/useI18n'
import StatusBadge from '@/components/common/StatusBadge.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const requestsStore = useRequestsStore()
const notifStore = useNotificationsStore()
const { t } = useI18n()

const request = ref(null)
const previewUrl = ref('')
const fileInput = ref(null)
const form = ref({
  issue_description: '',
  attachments: '',
  original_issue_description: '',
  originalAttachments: '',
  attachmentFile: null,
  attachmentName: ''
})

onMounted(async () => {
  // 取得原始申請單資料
  try {
    const id = route.params.id
    request.value = await requestsStore.fetchById(id)
    if (!canEditRequest(request.value)) {
      notifStore.add(t('request.editNotAllowed'), 'warning')
      router.replace(`/requests/${id}`)
      return
    }
    form.value.issue_description = request.value.faultDescription || ''
    form.value.attachments = request.value.attachmentId || ''
    form.value.original_issue_description = request.value.faultDescription || ''
    form.value.originalAttachments = request.value.attachmentId || ''
    form.value.attachmentName = request.value.attachments?.[0]?.name || ''
    previewUrl.value = request.value.attachments?.[0]?.data || ''
  } catch (e) {
    notifStore.add(e.message || t('request.loadFailed'), 'error')
    router.replace('/requests')
  }
})

function currentUserId() {
  const user = authStore.currentUser || {}
  return String(user.idUser || user.id || user.userId || '').replace(/[^\d]/g, '')
}

function canEditRequest(req) {
  if (!req || req.status !== 'pending' || authStore.isManager) return false
  const applicantId = String(req.applicant_id || req.requesterId || '').replace(/[^\d]/g, '')
  return !!currentUserId() && applicantId === currentUserId()
}

function handleFileChange(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  applyAttachmentFile(file)
}

function handleDrop(event) {
  const file = Array.from(event.dataTransfer.files).find((item) => item.type.startsWith('image/'))
  if (file) applyAttachmentFile(file)
}

function applyAttachmentFile(file) {
  if (file.size > 5 * 1024 * 1024) {
    notifStore.add(t('request.fileTooLarge', { name: file.name }), 'warning')
    return
  }
  form.value.attachmentFile = file
  form.value.attachmentName = file.name
  previewUrl.value = URL.createObjectURL(file)
}

function removeAttachment() {
  form.value.attachments = ''
  form.value.attachmentFile = null
  form.value.attachmentName = ''
  previewUrl.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

async function handleSubmit() {
  try {
    const id = route.params.id
    if (!canEditRequest(request.value)) {
      notifStore.add(t('request.editNotAllowed'), 'warning')
      return
    }
    const payload = {
      issue_description: form.value.issue_description,
      attachments: form.value.attachments,
      originalAttachments: form.value.originalAttachments,
      attachmentFile: form.value.attachmentFile,
    }
    await requestsStore.editRepairRequest(id, payload)
    notifStore.add(t('request.editSuccess'), 'success')
    router.push(`/requests/${id}`)
  } catch (e) {
    notifStore.add(e.message || t('request.editFailed'), 'error')
  }
}
</script>
