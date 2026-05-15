<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
      <button class="btn-secondary btn-sm" @click="router.back()">
        ← 返回
      </button>
      <h1 class="page-title text-xl">編輯維修申請單</h1>
    </div>
    <form @submit.prevent="handleSubmit" class="space-y-5">
      <div class="card p-5">
        <h2 class="section-title">資產資訊</h2>
        <div class="mb-2">
          <span class="font-mono text-indigo-600">{{ request?.assetId }}</span>
        </div>
      </div>
      <div class="card p-5">
        <h2 class="section-title">故障說明</h2>
        <textarea v-model="form.issue_description" rows="5" class="form-textarea w-full" required></textarea>
      </div>
      <div class="card p-5">
        <h2 class="section-title">附件</h2>
        <input type="text" v-model="form.attachments" class="form-input w-full" placeholder="多個網址以空格分隔" />
      </div>
      <div class="flex justify-end gap-3">
        <button type="button" class="btn-secondary" @click="router.back()">取消</button>
        <button type="submit" class="btn-primary">儲存</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRequestsStore } from '@/stores/requests'
import { useNotificationsStore } from '@/stores/notifications'

const route = useRoute()
const router = useRouter()
const requestsStore = useRequestsStore()
const notifStore = useNotificationsStore()

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
    notifStore.add('編輯成功', 'success')
    router.push(`/requests/${id}`)
  } catch (e) {
    notifStore.add(e.message || '編輯失敗', 'error')
  }
}
</script>
