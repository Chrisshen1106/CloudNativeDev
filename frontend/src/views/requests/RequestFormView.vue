<template>
  <div class="max-w-2xl mx-auto">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="btn-secondary btn-sm" @click="router.back()">
        ← {{ t('common.back') }}
      </button>
      <h1 class="page-title text-xl">{{ t('request.newRequest') }}</h1>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-5">
      <!-- Asset selection -->
      <div class="card p-5">
        <h2 class="section-title"> {{ t('request.selectAsset') }}</h2>
        <div>
          <label class="form-label">{{ t('request.selectAsset') }} <span class="text-red-500">*</span></label>
          <select v-model="form.assetId" class="form-select" required @change="onAssetChange">
            <option value="">{{ t('request.selectAssetPlaceholder') }}</option>
            <option
              v-for="asset in eligibleAssets"
              :key="asset.id"
              :value="asset.id"
              :disabled="asset.status === 'under_repair'"
            >
              {{ asset.assetNumber }} — {{ asset.name }}
              <template v-if="asset.status === 'under_repair'"> （維修中，不可申請）</template>
            </option>
          </select>
          <p v-if="selectedAsset" class="mt-2 text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2">
            型號：{{ selectedAsset.model }} ｜ 地點：{{ selectedAsset.location }}
          </p>
        </div>
      </div>

      <!-- Fault description -->
      <div class="card p-5">
        <h2 class="section-title"> 故障說明</h2>
        <div class="space-y-4">
          <div>
            <label class="form-label">{{ t('request.faultDescription') }} <span class="text-red-500">*</span></label>
            <textarea
              v-model="form.faultDescription"
              rows="5"
              class="form-textarea"
              required
              :placeholder="t('request.faultDescPlaceholder')"
            ></textarea>
            <p class="text-xs text-gray-400 mt-1 text-right">{{ form.faultDescription.length }} 字</p>
          </div>

          <!-- Image upload -->
          <div>
            <label class="form-label">{{ t('request.attachments') }}</label>
            <div
              class="border-2 border-dashed border-gray-200 rounded-xl p-6 text-center hover:border-indigo-400 hover:bg-indigo-50/30 transition-all cursor-pointer"
              @click="fileInput?.click()"
              @dragover.prevent
              @drop.prevent="handleDrop"
            >
              <div class="text-3xl mb-2"></div>
              <p class="text-sm text-gray-500 mb-1">點擊或拖曳圖片至此處上傳</p>
              <p class="text-xs text-gray-400">{{ t('request.attachmentsHint') }}</p>
            </div>
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              multiple
              class="hidden"
              @change="handleFileChange"
            />

            <!-- Preview -->
            <div v-if="form.attachments.length > 0" class="flex flex-wrap gap-3 mt-3">
              <div
                v-for="(att, idx) in form.attachments"
                :key="idx"
                class="relative group"
              >
                <img
                  :src="att.data"
                  :alt="att.name"
                  class="w-20 h-20 object-cover rounded-xl border border-gray-200"
                />
                <button
                  type="button"
                  class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow"
                  @click="removeAttachment(idx)"
                >×</button>
                <p class="text-xs text-gray-400 text-center mt-0.5 w-20 truncate">{{ att.name }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3">
        <button type="button" class="btn-secondary" @click="router.back()">
          {{ t('common.cancel') }}
        </button>
        <button type="submit" class="btn-primary" :disabled="!form.assetId || !form.faultDescription.trim()">
          {{ t('common.submit') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAssetsStore } from '@/stores/assets'
import { useRequestsStore } from '@/stores/requests'
import { useNotificationsStore } from '@/stores/notifications'
import { useI18n } from '@/composables/useI18n'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const assetsStore = useAssetsStore()
const requestsStore = useRequestsStore()
const notifStore = useNotificationsStore()
const { t } = useI18n()

const fileInput = ref(null)

const form = ref({
  assetId: route.query.assetId || '',
  faultDescription: '',
  attachments: [],
})

// Holders only see their assets; managers see all
const eligibleAssets = computed(() =>
  authStore.isManager
    ? assetsStore.getAll()
    : assetsStore.getByOwnerId(authStore.currentUser?.id)
)

const selectedAsset = computed(() =>
  form.value.assetId ? assetsStore.getById(form.value.assetId) : null
)

function onAssetChange() {
  // Clear if under_repair
  if (selectedAsset.value?.status === 'under_repair') {
    form.value.assetId = ''
  }
}

function handleFileChange(event) {
  processFiles(Array.from(event.target.files))
  event.target.value = ''
}

function handleDrop(event) {
  const files = Array.from(event.dataTransfer.files).filter((f) => f.type.startsWith('image/'))
  processFiles(files)
}

function processFiles(files) {
  files.forEach((file) => {
    if (file.size > 5 * 1024 * 1024) {
      notifStore.add(`${file.name} 超過 5MB 限制，已略過`, 'warning')
      return
    }
    const reader = new FileReader()
    reader.onloadend = () => {
      form.value.attachments.push({ name: file.name, type: file.type, data: reader.result })
    }
    reader.readAsDataURL(file)
  })
}

function removeAttachment(idx) {
  form.value.attachments.splice(idx, 1)
}

async function handleSubmit() {
  try {
    // 準備 API 請求資料
    const payload = {
      idEquipment: form.value.assetId,
      issue_description: form.value.faultDescription,
      attachments: form.value.attachments.map(att => att.data),
    }
    // 呼叫後端 API
    const res = await fetch('/maintenance-api/form', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authStore.token ? { 'Authorization': `Bearer ${authStore.token}` } : {})
      },
      body: JSON.stringify(payload)
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err?.message || '申請失敗')
    }
    const data = await res.json()
    notifStore.add(t('request.submitSuccess'), 'success')
    // 跳轉到申請詳情頁或列表
    router.push(`/requests`)
  } catch (e) {
    notifStore.add(e.message || '申請失敗', 'error')
  }
}
</script>
