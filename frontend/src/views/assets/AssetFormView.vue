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

    <form @submit.prevent="createRequestSubmit" class="space-y-5">
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
              <option value="normal">{{ t('asset.statuses.normal') }}</option>
              <option value="under_repair">{{ t('asset.statuses.under_repair') }}</option>
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
        <button type="button" class="btn-primary" @click="handleSubmitEmployee" :disabled="employeeLoading">
          {{ employeeLoading ? t('common.submitting') : '送出維修申請(員工)' }}
        </button>
      const employeeLoading = ref(false)
      async function handleSubmitEmployee() {
        employeeLoading.value = true
        try {
          // 只組維修申請需要的欄位
          const payload = {
            idEquipment: form.value.idEquipment || '',
            issue_description: form.value.issue_description || '',
            attachments: form.value.attachments || '',
          }
          await requestsStore.createRequest(payload)
          notifStore.add('維修申請已送出', 'success')
          // router.push('/requests') // 如需跳轉可開啟
        } catch (e) {
          notifStore.add(e.message || '維修申請失敗', 'error')
        } finally {
          employeeLoading.value = false
        }
      }
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


async function createRequestSubmit() {
  try {
    const payload = {
      ...form.value,
      attachments: form.value.attachments || '',
    }
    await requestsStore.createRequest(payload)
    notifStore.add('維修申請已送出', 'success')
    // router.push('/requests') // 如需跳轉可開啟
  } catch (e) {
    notifStore.add(e.message || '維修申請失敗', 'error')
  }
}