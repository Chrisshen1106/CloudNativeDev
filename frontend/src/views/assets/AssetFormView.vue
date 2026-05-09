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

    <form @submit.prevent="handleSubmit" class="space-y-5">
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
            <select v-model="form.ownerId" class="form-select" required>
              <option value="">-- 選擇負責人 --</option>
              <option v-for="user in holderUsers" :key="user.id" :value="user.id">
                {{ user.name }} ({{ user.department }})
              </option>
            </select>
          </div>
          <div>
            <label class="form-label">{{ t('asset.department') }}</label>
            <input v-model="form.department" type="text" class="form-input" placeholder="例：研發部" />
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
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssetsStore } from '@/stores/assets'
// import { mockUsers } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { useI18n } from '@/composables/useI18n'

const route = useRoute()
const router = useRouter()
const assetsStore = useAssetsStore()
const notifStore = useNotificationsStore()
const { t } = useI18n()

const isEdit = computed(() => !!route.params.id)
// const holderUsers = computed(() => mockUsers.filter((u) => u.role === 'holder'))

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
  status: 'normal',
  notes: '',
})

onMounted(() => {
  if (isEdit.value) {
    const asset = assetsStore.getById(route.params.id)
    if (asset) Object.assign(form.value, asset)
  }
})

function handleSubmit() {
  if (isEdit.value) {
    assetsStore.update(route.params.id, { ...form.value })
    notifStore.add(t('asset.updateSuccess'), 'success')
    router.push(`/assets/${route.params.id}`)
  } else {
    const newAsset = assetsStore.add({ ...form.value })
    notifStore.add(t('asset.saveSuccess'), 'success')
    router.push(`/assets/${newAsset.id}`)
  }
}
</script>
