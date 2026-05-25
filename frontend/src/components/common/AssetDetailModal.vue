<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-8 animate-modal">
        <button class="absolute top-3 right-3 btn-secondary btn-sm" @click="$emit('close')">×</button>
        <h2 class="text-xl font-bold mb-4">{{ t('assetDetail.assetDetail') }}</h2>
        <div v-if="loading" class="text-center py-8 text-gray-400">{{ t('common.loading') }}</div>
        <div v-else-if="errorMsg" class="text-center py-8 text-red-500">{{ errorMsg }}</div>
        <div v-else-if="asset">
          <div class="mb-4">
            <div class="font-bold text-lg mb-1">{{ asset.name }}</div>
            <div class="text-sm text-gray-500 mb-2">{{ t('assetDetail.assetNumber') }}：{{ asset.id }}</div>
            <div>{{ t('assetDetail.model') }}：{{ asset.model }}</div>
            <div>{{ t('assetDetail.category') }}：{{ displayCategory(asset.category) }}</div>
            <div>{{ t('assetDetail.serialNumber') }}：{{ asset.serialNumber }}</div>
            <div>{{ t('assetDetail.status') }}：{{ asset.status }}</div>
            <div>{{ t('assetDetail.startDate') }}：{{ asset.startDate }}</div>
            <div>{{ t('assetDetail.warrantyDue') }}：{{ asset.warrantyExpiry }}</div>
            <div>{{ t('assetDetail.position') }}：{{ asset.location }}</div>
            <div>{{ t('assetDetail.department') }}：{{ asset.department }}</div>
            <div>{{ t('assetDetail.owner') }}：{{ asset.ownerId }}</div>
            <div>{{ t('assetDetail.notes') }}：{{ asset.notes }}</div>
          </div>
          <div>
            <h3 class="font-semibold mb-2">{{ t('assetDetail.maintenanceRecords') }}</h3>
            <div v-if="!asset.maintenanceHistory?.length" class="text-gray-400">{{ t('assetDetail.noMaintenanceRecord') }}</div>
            <ul v-else class="space-y-2">
              <li v-for="h in asset.maintenanceHistory" :key="h.idForm" class="border rounded p-2">
                <div>{{ t('request.requestId') }}：{{ h.idForm }}</div>
                <div>{{ t('assetDetail.description') }}：{{ h.issueDescription }}</div>
                <div>{{ t('assetDetail.reviewer') }}：{{ h.reviewerName }}</div>
                <div>{{ t('assetDetail.repairDescription') }}：{{ h.repair_solution || h.repairDescription || t('request.none') }}</div>
                <div>{{ t('request.repairCost') }}：{{ h.repairCost }}</div>
                <div>{{ t('assetDetail.repairPeriod') }}：{{ h.repairStartDate }} ~ {{ h.repairEndDate }}</div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useI18n } from '@/composables/useI18n'
const props = defineProps({
  show: Boolean,
  asset: Object,
  loading: Boolean,
  errorMsg: String
})
const { t } = useI18n()

function displayCategory(value) {
  if (!value) return t('request.none')
  const key = `asset.categories.${value}`
  const label = t(key)
  return label === key ? value : label
}
</script>
