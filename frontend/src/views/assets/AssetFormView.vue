<template>
  <div class="max-w-2xl mx-auto">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="btn-secondary btn-sm" @click="router.back()">
        ← {{ t('common.back') }}
      </button>
      <h1 class="page-title text-xl">
        {{ isEdit ? t('asset.editAsset') : t('asset.addAsset') }}
      </h1>
    </div>

    <form @submit.prevent="handleAssetSubmit" class="space-y-5">
      <!-- Basic info -->
      <div class="card p-5">
        <h2 class="section-title">{{ t('asset.basicInfo') }}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="sm:col-span-2">
            <label class="form-label">{{ t('asset.name') }} <span class="text-red-500">*</span></label>
            <input v-model="form.name" type="text" class="form-input" required :placeholder="`例：MacBook Pro 16`" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.category') }} <span class="text-red-500">*</span></label>
            <select v-model="form.category" class="form-select" required>
              <option value="">-- 選擇分類 --</option>
              <option value="computer">{{ t('asset.categories.computer') }}</option>
              <option value="phone">{{ t('asset.categories.phone') }}</option>
              <option value="tablet">{{ t('asset.categories.tablet') }}</option>
            </select>
          </div>
          <div>
            <label class="form-label">{{ t('asset.status') }}</label>
            <select v-model="form.status" class="form-select">
              <option value="in_use">{{ t('asset.statuses.in_use') }}</option>
              <option value="repairing">{{ t('asset.statuses.repairing') }}</option>

            </select>
          </div>
          <div>
            <label class="form-label">{{ t('asset.model') }} <span class="text-red-500">*</span></label>
            <input v-model="form.model" type="text" class="form-input" required :placeholder="`例：MacBook Pro M3 Max`" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.specs') }}</label>
            <input v-model="form.specs" type="text" class="form-input" placeholder="例：48GB RAM, 1TB SSD" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.serialNumber') }}</label>
            <input v-model="form.serialNumber" type="text" class="form-input" placeholder="設備序號" />
          </div>
          <div class="sm:col-span-2">
            <label class="form-label">{{ t('asset.notes') }}</label>
            <textarea v-model="form.notes" rows="2" class="form-textarea" placeholder="備註..."></textarea>
          </div>
        </div>
      </div>

      <!-- Purchase info -->
      <div class="card p-5">
        <h2 class="section-title"> {{ t('asset.purchaseInfo') }}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="form-label">{{ t('asset.supplier') }}</label>
            <input v-model="form.supplier" type="text" class="form-input" placeholder="供應商名稱" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.purchasePrice') }} (NT$)</label>
            <input v-model.number="form.purchasePrice" type="number" class="form-input" min="0" placeholder="0" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.purchaseDate') }}</label>
            <input v-model="form.purchaseDate" type="date" class="form-input" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.activationDate') }}</label>
            <input v-model="form.activationDate" type="date" class="form-input" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.warrantyExpiry') }}</label>
            <input v-model="form.warrantyExpiry" type="date" class="form-input" />
          </div>
        </div>
      </div>

      <!-- Location/assignment -->
      <div class="card p-5">
        <h2 class="section-title"> {{ t('asset.locationInfo') }}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="sm:col-span-2">
            <label class="form-label">{{ t('asset.location') }} <span class="text-red-500">*</span></label>
            <input v-model="form.location" type="text" class="form-input" required placeholder="例：台北總部 3F-A302" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.owner') }} <span class="text-red-500">*</span></label>
            <select v-model="form.ownerId" class="form-select" required @change="handleUserChange">
              <option value="">-- 選擇負責人 --</option>
              <option v-for="user in holderUsers" :key="user.idUser || user.id" :value="user.idUser || user.id">
                {{ user.name }} ({{ user.department || user.departmentName || '' }})
              </option>
            </select>
          </div>
          <div>
            <label class="form-label">{{ t('asset.department') }}</label>
            <input v-model="form.department" type="text" class="form-input" placeholder="例：研發部" readonly />
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-3">
        <button type="button" class="btn-secondary" @click="router.back()">
          {{ t('common.cancel') }}
        </button>
        <button type="submit" class="btn-primary">
          {{ t('common.save') }}
        </button>
        <button v-if="isEdit" type="button" class="btn-danger" @click="showDeleteConfirm = true">
          刪除資產
        </button>
      </div>
      <div v-if="showDeleteConfirm" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-30 z-50">
        <div class="bg-white rounded shadow-lg p-6 w-80">
          <div class="mb-4 text-lg font-semibold text-gray-800">確認刪除？</div>
          <div class="flex justify-end gap-3">
            <button class="btn-secondary" @click="showDeleteConfirm = false">取消</button>
            <button class="btn-danger" @click="handleDeleteAsset">確認刪除</button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>

import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssetsStore } from '@/stores/assets'
import { useRequestsStore } from '@/stores/requests'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { useI18n } from '@/composables/useI18n'

const route = useRoute()
const router = useRouter()
const assetsStore = useAssetsStore()
const notifStore = useNotificationsStore()
const { t } = useI18n()

const isEdit = computed(() => !!route.params.id)
const requestsStore = useRequestsStore()
const authStore = useAuthStore()

const holderUsers = ref([])
// 當選擇負責人時自動帶出部門
function handleUserChange() {
  const user = holderUsers.value.find(u => (u.idUser || u.id) == form.value.ownerId)
  form.value.department = user ? (user.department || user.departmentName || '') : ''
}
onMounted(async () => {
  try {
    const users = await authStore.fetchAllUsers()
    holderUsers.value = users
  } catch (e) {
    holderUsers.value = []
  }
  if (isEdit.value) {
    try {
      const asset = await assetsStore.getAssetDetail(route.params.id, authStore.token)
      if (asset) Object.assign(form.value, asset)
    } catch (e) {
      notifStore.add('取得資產詳情失敗', 'error')
    }
  }
})

const form = ref({
  name: '',
  category: '',
  model: '',
  specs: '',
  serialNumber: '',
  supplier: '',
  purchaseDate: '',
  purchasePrice: null,
  location: '',
  ownerId: '',
  department: '',
  activationDate: '',
  warrantyExpiry: '',
  status: '',
  notes: '',
})

onMounted(() => {
  if (isEdit.value) {
    const asset = assetsStore.getById(route.params.id)
    if (asset) Object.assign(form.value, asset)
  }
})



async function handleAssetSubmit() {
  try {
    if (isEdit.value) {
      // 編輯資產
      await assetsStore.updateAsset(route.params.id, form.value, authStore.token)
      notifStore.add('資產已更新', 'success')
    } else {
      // 新增資產
      await assetsStore.createAsset(form.value, authStore.token)
      notifStore.add('資產已新增', 'success')
    }
    router.back()
  } catch (e) {
    notifStore.add(e.message || '儲存失敗', 'error')
  }
}
import { onUnmounted } from 'vue'
    const showDeleteConfirm = ref(false)
    onUnmounted(() => { showDeleteConfirm.value = false })
    async function handleDeleteAsset() {
      try {
        let id = route.params.id
        if (typeof id === 'string') {
          const match = id.match(/(\d+)/)
          if (match) id = match[1]
        }
        const res = await assetsStore.deleteAsset(id, authStore.token)
        if (res && res.success !== false) {
          // 取得所有與該資產相關的維修單
          await requestsStore.fetchAll(authStore.token)
          const assetIdStr = `A${id}`
          const relatedRequests = requestsStore.getAll().filter(r => r.assetId === assetIdStr)
          const token = authStore.token || localStorage.getItem('ams_token') || ''
          for (const req of relatedRequests) {
            let reqId = req.id
            if (typeof reqId === 'string') {
              const match = reqId.match(/(\d+)/)
              if (match) reqId = match[1]
            }
            await fetch(`/maintenance-api/form/${reqId}`, {
              method: 'DELETE',
              headers: { 'Authorization': token }
            })
          }
          notifStore.add('資產已刪除', 'success')
          showDeleteConfirm.value = false
          router.push('/assets').then(() => {
            setTimeout(() => { window.location.reload() }, 100)
          })
          return
        }
      } catch (e) {
        showDeleteConfirm.value = false
      }
    }
</script>