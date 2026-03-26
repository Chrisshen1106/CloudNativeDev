<template>
  <div class="max-w-4xl mx-auto">
    <!-- Back & header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="btn-secondary btn-sm" @click="router.back()">
        ← {{ t('common.back') }}
      </button>
      <div class="flex-1">
        <h1 class="page-title text-xl">{{ asset?.name || '...' }}</h1>
        <p class="text-sm text-gray-500 font-mono">{{ asset?.assetNumber }}</p>
      </div>
      <StatusBadge v-if="asset" :status="asset.status" type="asset" />
      <RouterLink
        v-if="authStore.isManager && asset"
        :to="`/assets/${assetId}/edit`"
        class="btn-primary"
      >
         {{ t('common.edit') }}
      </RouterLink>
      <RouterLink
        v-if="authStore.isHolder && asset && asset.status === 'normal' && asset.ownerId === authStore.currentUser?.id"
        :to="`/requests/new?assetId=${assetId}`"
        class="btn-warning"
      >
         {{ t('asset.submitRepair') }}
      </RouterLink>
    </div>

    <div v-if="!asset" class="card p-12 text-center text-gray-400">
      <p class="text-4xl mb-2"></p>
      <p>找不到此資產</p>
    </div>

    <div v-else class="space-y-5">
      <!-- Basic info -->
      <div class="card p-5">
        <h2 class="section-title flex items-center gap-2">
          <span>{{ categoryIcon(asset.category) }}</span> {{ t('asset.basicInfo') }}
        </h2>
        <div class="divide-y divide-gray-50">
          <div class="detail-row"><span class="detail-label">{{ t('asset.assetNumber') }}</span><span class="detail-value font-mono text-indigo-600 font-medium">{{ asset.assetNumber }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('asset.name') }}</span><span class="detail-value font-medium">{{ asset.name }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('asset.category') }}</span><span class="detail-value">{{ t(`asset.categories.${asset.category}`) }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('asset.model') }}</span><span class="detail-value">{{ asset.model }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('asset.specs') }}</span><span class="detail-value">{{ asset.specs }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('asset.serialNumber') }}</span><span class="detail-value font-mono text-gray-600">{{ asset.serialNumber }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('asset.status') }}</span><span class="detail-value"><StatusBadge :status="asset.status" type="asset" /></span></div>
          <div v-if="asset.notes" class="detail-row"><span class="detail-label">{{ t('asset.notes') }}</span><span class="detail-value text-gray-600">{{ asset.notes }}</span></div>
        </div>
      </div>

      <!-- Purchase info -->
      <div class="card p-5">
        <h2 class="section-title"> {{ t('asset.purchaseInfo') }}</h2>
        <div class="divide-y divide-gray-50">
          <div class="detail-row"><span class="detail-label">{{ t('asset.supplier') }}</span><span class="detail-value">{{ asset.supplier }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('asset.purchaseDate') }}</span><span class="detail-value">{{ asset.purchaseDate }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('asset.purchasePrice') }}</span><span class="detail-value font-medium">NT$ {{ asset.purchasePrice?.toLocaleString() }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('asset.activationDate') }}</span><span class="detail-value">{{ asset.activationDate }}</span></div>
          <div class="detail-row">
            <span class="detail-label">{{ t('asset.warrantyExpiry') }}</span>
            <span class="detail-value" :class="isWarrantyExpired ? 'text-red-600 font-medium' : ''">
              {{ asset.warrantyExpiry }}
              <span v-if="isWarrantyExpired" class="text-xs text-red-500 ml-1">（已過期）</span>
            </span>
          </div>
        </div>
      </div>

      <!-- Location/assignment info -->
      <div class="card p-5">
        <h2 class="section-title"> {{ t('asset.locationInfo') }}</h2>
        <div class="divide-y divide-gray-50">
          <div class="detail-row"><span class="detail-label">{{ t('asset.location') }}</span><span class="detail-value">{{ asset.location }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('asset.owner') }}</span><span class="detail-value font-medium">{{ getUserName(asset.ownerId) }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('asset.department') }}</span><span class="detail-value">{{ asset.department }}</span></div>
        </div>
      </div>

      <!-- Maintenance history -->
      <div class="card p-5">
        <h2 class="section-title"> {{ t('asset.maintenanceHistory') }}</h2>
        <div v-if="relatedRequests.length === 0" class="text-sm text-gray-400 text-center py-6">
          {{ t('asset.noMaintenanceHistory') }}
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="req in relatedRequests"
            :key="req.id"
            class="flex items-start gap-3 p-3 rounded-xl bg-gray-50 hover:bg-indigo-50 transition-colors cursor-pointer"
            @click="router.push(`/requests/${req.id}`)"
          >
            <StatusBadge :status="req.status" type="request" />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-mono text-gray-500 text-xs">{{ req.id }}</p>
              <p class="text-sm text-gray-700 truncate">{{ req.faultDescription }}</p>
              <p v-if="req.completionDate" class="text-xs text-gray-400 mt-0.5">完成：{{ req.completionDate }} · 費用：NT$ {{ req.repairCost?.toLocaleString() }}</p>
            </div>
            <span class="text-xs text-gray-400 shrink-0">{{ req.requestDate }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAssetsStore } from '@/stores/assets'
import { useRequestsStore } from '@/stores/requests'
import { mockUsers } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'
import StatusBadge from '@/components/common/StatusBadge.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const assetsStore = useAssetsStore()
const requestsStore = useRequestsStore()
const { t } = useI18n()

const assetId = computed(() => route.params.id)
const asset = computed(() => assetsStore.getById(assetId.value))
const relatedRequests = computed(() =>
  requestsStore.getByAssetId(assetId.value)
    .sort((a, b) => b.requestDate.localeCompare(a.requestDate))
)

const isWarrantyExpired = computed(() => {
  if (!asset.value?.warrantyExpiry) return false
  return new Date(asset.value.warrantyExpiry) < new Date()
})

function getUserName(ownerId) {
  return mockUsers.find((u) => u.id === ownerId)?.name || ownerId
}

function categoryIcon(cat) {
  return { computer: '', phone: '', tablet: '' }[cat] || ''
}
</script>
