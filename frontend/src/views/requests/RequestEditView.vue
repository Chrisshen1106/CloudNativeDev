<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
      <button class="btn-secondary btn-sm" @click="router.back()">
        ← {{ t('common.back') }}
      </button>
      <h1 class="page-title text-xl">{{ t('request.editRequest') }}</h1>
    </div>
    <form @submit.prevent="handleSubmit" class="space-y-5">
      <div class="card p-5">
        <h2 class="section-title">{{ t('request.assetInfo') }}</h2>
        <div class="mb-2">
          <span class="font-mono text-indigo-600">{{ request?.assetId }}</span>
        </div>
      </div>
      <div class="card p-5">
        <h2 class="section-title">{{ t('request.faultDescription') }}</h2>
        <textarea v-model="form.issue_description" rows="5" class="form-textarea w-full" required></textarea>
      </div>
      <div class="card p-5">
        <h2 class="section-title">{{ t('request.attachments') }}</h2>
        <input type="text" v-model="form.attachments" class="form-input w-full" :placeholder="t('request.attachmentsUrlPlaceholder')" />
      </div>
      <div class="flex justify-end gap-3">
        <button type="button" class="btn-secondary" @click="router.back()">{{ t('common.cancel') }}</button>
        <button type="submit" class="btn-primary">{{ t('common.save') }}</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRequestsStore } from '@/stores/requests'
import { useNotificationsStore } from '@/stores/notifications'
import { useI18n } from '@/composables/useI18n'

const route = useRoute()
const router = useRouter()
const requestsStore = useRequestsStore()
const notifStore = useNotificationsStore()
const { t } = useI18n()

const request = ref(null)
const form = ref({
  issue_description: '',
  attachments: ''
})

onMounted(async () => {
  // 取得原始申請單資料
  const id = route.params.id
  request.value = await requestsStore.fetchById(id)
  form.value.issue_description = request.value.faultDescription || ''
  form.value.attachments = request.value.attachments?.join(' ') || ''
})

async function handleSubmit() {
  try {
    const id = route.params.id
    await requestsStore.editRepairRequest(id, form.value)
    notifStore.add(t('request.editSuccess'), 'success')
    router.push(`/requests/${id}`)
  } catch (e) {
    notifStore.add(e.message || t('request.editFailed'), 'error')
  }
}
</script>
