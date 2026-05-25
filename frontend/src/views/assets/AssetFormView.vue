<template>
  <div class="max-w-2xl mx-auto">
    <!-- Header -->
    <div class="mb-6 flex flex-col items-start gap-3 sm:flex-row sm:items-center">
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
            <input v-model="form.name" type="text" class="form-input" required :placeholder="t('assetForm.namePlaceholder')" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.category') }} <span class="text-red-500">*</span></label>
            <select v-model="form.category" class="form-select" required>
              <option value="">-- {{ t('assetForm.categoryPlaceholder') }} --</option>
              <option value="computer">{{ t('asset.categories.computer') }}</option>
              <option value="phone">{{ t('asset.categories.phone') }}</option>
              <option value="tablet">{{ t('asset.categories.tablet') }}</option>
            </select>
          </div>
          <div>
            <label class="form-label">{{ t('asset.status') }}</label>
            <select v-model="form.status" class="form-select">
              <option value="">{{ t('assetForm.statusPlaceholder') }}</option>
              <option value="in_use">{{ t('asset.statuses.in_use') }}</option>
              <option value="repairing">{{ t('asset.statuses.repairing') }}</option>

            </select>
          </div>
          <div>
            <label class="form-label">{{ t('asset.model') }} <span class="text-red-500">*</span></label>
            <input v-model="form.model" type="text" class="form-input" required :placeholder="t('assetForm.modelPlaceholder')" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.specs') }}</label>
            <input v-model="form.specs" type="text" class="form-input" :placeholder="t('assetForm.specsPlaceholder')" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.serialNumber') }}</label>
            <input v-model="form.serialNumber" type="text" class="form-input" :placeholder="t('assetForm.serialNumberPlaceholder')" />
          </div>
          <div class="sm:col-span-2">
            <label class="form-label">{{ t('asset.notes') }}</label>
            <textarea v-model="form.notes" rows="2" class="form-textarea" :placeholder="t('assetForm.notesPlaceholder')" ></textarea>
          </div>
        </div>
      </div>

      <!-- Purchase info -->
      <div class="card p-5">
        <h2 class="section-title"> {{ t('asset.purchaseInfo') }}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="form-label">{{ t('asset.supplier') }}</label>
            <input v-model="form.supplier" type="text" class="form-input" :placeholder="t('assetForm.supplierPlaceholder')" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.purchasePrice') }} (NT$)</label>
            <input
              v-model.number="form.purchasePrice"
              type="number"
              class="form-input"
              min="0"
              placeholder="0"
              @wheel.prevent="blurNumberInput"
            />
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
            <input v-model="form.location" type="text" class="form-input" required :placeholder="t('assetForm.locationPlaceholder')" />
          </div>
          <div>
            <label class="form-label">{{ t('asset.owner') }} <span class="text-red-500">*</span></label>
            <select v-model="form.ownerId" class="form-select" required @change="handleUserChange">
              <option value="">-- {{ t('assetForm.ownerPlaceholder') }} --</option>
              <option v-for="user in holderUsers" :key="user.idUser || user.id" :value="user.idUser || user.id">
                {{ user.name }} ({{ user.department || user.departmentName || '' }})
              </option>
            </select>
          </div>
          <div>
            <label class="form-label">{{ t('assetForm.user') }} <span class="text-red-500">*</span></label>
            <select v-model="form.idUser" class="form-select" required @change="handleIdUserChange">
              <option value="">-- {{ t('assetForm.user') }} --</option>
              <option v-for="user in holderUsers" :key="user.idUser || user.id" :value="user.idUser || user.id">
                {{ user.idUser || user.id }} - {{ user.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="form-label">{{ t('assetForm.department') }}</label>
            <input v-model="form.department" type="text" class="form-input" :placeholder="t('assetForm.departmentPlaceholder')" />
          </div>
          <div>
            <label class="form-label">{{ t('assetForm.userDepartment') }}</label>
            <input v-model="form.userDepartment" type="text" class="form-input" :placeholder="t('assetForm.userDepartmentPlaceholder')" />
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <button type="button" class="btn-secondary" @click="router.back()">
          {{ t('common.cancel') }}
        </button>
        <button type="submit" class="btn-primary" :disabled="isSaving">
          {{ t('common.save') }}
        </button>
      </div>
      <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30 p-3">
        <div class="w-full max-w-xs rounded bg-white p-5 shadow-lg sm:p-6">
          <div class="mb-4 text-lg font-semibold text-gray-800">{{ t('asset.deleteConfirmTitle') }}</div>
          <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <button class="btn-secondary" @click="showDeleteConfirm = false">{{ t('common.cancel') }}</button>
            <button class="btn-danger" @click="handleDeleteAsset">{{ t('common.delete') }}</button>
          </div>
        </div>
      </div>
    </form>

    <AssetConflictModal
      v-if="assetConflict"
      :my-content="assetConflict.myContent"
      :latest-content="assetConflict.latestContent"
      :holder-users="holderUsers"
      @submit="handleConflictSubmit"
      @cancel="cancelConflictEdit"
    />
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
import AssetConflictModal from '@/components/common/AssetConflictModal.vue'

const route = useRoute()
const router = useRouter()
const assetsStore = useAssetsStore()
const notifStore = useNotificationsStore()
const { t } = useI18n()

const isEdit = computed(() => !!route.params.id)
const requestsStore = useRequestsStore()
const authStore = useAuthStore()

const holderUsers = ref([])
const isSaving = ref(false)
const assetConflict = ref(null)
// 當選擇負責人時自動帶出部門
function handleUserChange() {
  const user = holderUsers.value.find(u => (u.idUser || u.id) == form.value.ownerId)
  form.value.department = user ? (user.department || user.departmentName || '') : ''
}
// 當選擇 idUser 時自動帶出使用部門
function handleIdUserChange() {
  const user = holderUsers.value.find(u => (u.idUser || u.id) == form.value.idUser)
  form.value.userDepartment = user ? (user.department || user.departmentName || '') : ''
}

function blurNumberInput(event) {
  event.currentTarget.blur()
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
      if (asset) {
        // idOwner (string) 轉 int 給 idUser
        if (asset.idOwner && !asset.idUser) {
          form.value.idUser = parseInt(asset.idOwner, 10)
        } else if (asset.idUser) {
          form.value.idUser = asset.idUser
        }
        // 其餘欄位
        Object.assign(form.value, asset)
        // 修正底線命名欄位對應
        form.value.serialNumber = asset.serial_Number ?? asset.serialNumber ?? ''
        form.value.purchasePrice = asset.purchase_price ?? asset.purchasePrice ?? null
        form.value.purchaseDate = asset.purchase_date ?? asset.purchaseDate ?? ''
      }
    } catch (e) {
      notifStore.add(t('asset.detailLoadFailed'), 'error')
    }
  }
})

const form = ref({
  idEquipment: '', // 資產主鍵
  assetNumber: '', // 資產編號
  id: '', // 資產ID
  name: '',
  category: '',
  model: '',
  specs: '',
  serial_Number: '',
  supplier: '',
  purchase_date: '',
  purchase_price: null,
  location: '',
  ownerId: '',
  idUser: '',
  department: '',
  activationDate: '',
  warrantyExpiry: '',
  status: '',
  notes: '',
})

onMounted(() => {
  if (isEdit.value) {
    const asset = assetsStore.getById(route.params.id)
    if (asset) {
      // idOwner (string) 轉 int 給 idUser
      if (asset.idOwner && !asset.idUser) {
        form.value.idUser = parseInt(asset.idOwner, 10)
      } else if (asset.idUser) {
        form.value.idUser = asset.idUser
      }
      Object.assign(form.value, asset)
      // 修正底線命名欄位對應
      form.value.serialNumber = asset.serial_Number ?? asset.serialNumber ?? ''
      form.value.purchasePrice = asset.purchase_price ?? asset.purchasePrice ?? null
      form.value.purchaseDate = asset.purchase_date ?? asset.purchaseDate ?? ''
    }
  }
})


function buildAssetPayload(source = form.value) {
  const payload = {
    ...source,
    serial_Number: source.serialNumber ?? source.serial_Number ?? '',
    purchase_price: source.purchasePrice ?? source.purchase_price ?? null,
    purchase_date: source.purchaseDate ?? source.purchase_date ?? '',
  }

  if (payload.idUser) {
    payload.isOwner = String(payload.idUser)
  }

  delete payload.serialNumber
  delete payload.purchasePrice
  delete payload.purchaseDate

  return payload
}


async function handleAssetSubmit() {
  const payload = buildAssetPayload()
  try {
    isSaving.value = true
    if (isEdit.value) {
      await assetsStore.updateAsset(route.params.id, payload, authStore.token)
      notifStore.add(t('asset.updated'), 'success')
    } else {
      await assetsStore.createAsset(payload, authStore.token)
      notifStore.add(t('asset.created'), 'success')
    }
    router.back()
  } catch (e) {
    if (e.status === 409 && e.latestAsset) {
      assetConflict.value = {
        myContent: payload,
        latestContent: e.latestAsset || {},
      }
      notifStore.add(t('asset.conflictChanged'), 'error')
      return
    }
    notifStore.add(e.message || t('asset.saveFailed'), 'error')
  } finally {
    isSaving.value = false
  }
}

async function handleConflictSubmit(resolvedPayload) {
  try {
    isSaving.value = true
    const payload = buildAssetPayload(resolvedPayload)
    await assetsStore.updateAsset(route.params.id, payload, authStore.token)
    notifStore.add(t('asset.updated'), 'success')
    assetConflict.value = null
    router.back()
  } catch (e) {
    if (e.status === 409 && e.latestAsset) {
      assetConflict.value = {
        myContent: buildAssetPayload(resolvedPayload),
        latestContent: e.latestAsset || {},
      }
      notifStore.add(t('asset.conflictChangedAgain'), 'error')
      return
    }
    notifStore.add(e.message || t('asset.resubmitFailed'), 'error')
  } finally {
    isSaving.value = false
  }
}

function cancelConflictEdit() {
  assetConflict.value = null
  router.back()
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
          notifStore.add(t('asset.deleted'), 'success')
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
