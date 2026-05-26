<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAssetsStore } from '@/stores/assets'
import { useRequestsStore } from '@/stores/requests'
import { useI18n } from '@/composables/useI18n'
import StatusBadge from '@/components/common/StatusBadge.vue'
import LoadingState from '@/components/common/LoadingState.vue'

const props = defineProps({
  id: [String, Number],
  modal: Boolean
})

const emit = defineEmits(['close'])

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const assetsStore = useAssetsStore()
const requestsStore = useRequestsStore()
const { t } = useI18n()

const assetId = computed(() => props.id || route.params.id)
const asset = ref(null)
const users = ref([])
const loading = ref(false)
const errorMsg = ref('')

async function fetchAssetDetail() {
  if (!assetId.value) return
  loading.value = true
  errorMsg.value = ''
  try {
    asset.value = await assetsStore.getAssetDetail(assetId.value, authStore.token)
    if (authStore.isManager) {
      users.value = await authStore.fetchAllUsers().catch(() => [])
    }
  } catch (e) {
    errorMsg.value = e.message || t('asset.detailLoadFailed')
    asset.value = null
  } finally {
    loading.value = false
  }
}

async function goToRequestDetail(req) {
  const rawId = req.idForm || req.id || ''
  const match = String(rawId).match(/(\d+)$/)
  const formId = typeof rawId === 'number' ? rawId : match ? parseInt(match[1], 10) : 0
  if (!formId) return
  await requestsStore.fetchById(formId)
  router.push({ name: 'request-detail', params: { id: formId } })
}

function userFromId(id) {
  return users.value.find((u) => String(u.idUser || u.id) === String(id))
}

function getUserName(id, name) {
  if (!id) return t('assetDetail.unassigned')
  const userName = name || userFromId(id)?.name
  return userName ? `${userName} (U${id})` : `U${id}`
}

function getShortReqId(req) {
  const id = req.idForm || req.id || ''
  if (typeof id === 'number') return `REQ-${String(id).padStart(3, '0')}`
  const match = String(id).match(/REQ-(?:\d{4}-)?(\d+)/)
  return match ? `REQ-${match[1].padStart(3, '0')}` : id
}

function formatMoney(value) {
  if (value === null || value === undefined || value === '') return t('request.none')
  return `${t('common.currency')} ${Number(value).toLocaleString()}`
}

function displayValue(value) {
  return value || t('request.none')
}

function displayCategory(value) {
  if (!value) return t('request.none')
  const key = `asset.categories.${value}`
  const label = t(key)
  return label === key ? value : label
}

function isRejectedRequest(req) {
  return req?.status === 'rejected' || req?.review_result === 'rejected'
}

onMounted(fetchAssetDetail)
watch(assetId, fetchAssetDetail)

const relatedRequests = computed(() => asset.value?.maintenanceHistory || [])

const isWarrantyExpired = computed(() => {
  if (!asset.value?.warrantyExpiry) return false
  return new Date(asset.value.warrantyExpiry) < new Date()
})

const assignedUserName = computed(() => getUserName(asset.value?.idUser, asset.value?.userName))
const ownerUserName = computed(() => getUserName(asset.value?.ownerId, asset.value?.ownerName))
</script>

<template>
  <div
    :class="modal ? 'w-full' : 'max-w-4xl mx-auto'"
    class="max-h-[88vh] min-h-[200px] overflow-y-auto overflow-x-hidden bg-gray-50"
  >
    <LoadingState v-if="loading" :label="t('assetDetail.loading')" />

    <div v-else-if="errorMsg" class="m-6 rounded-lg bg-red-50 p-4 text-center text-sm text-red-600">
      {{ errorMsg }}
    </div>

    <div v-else-if="asset" class="space-y-4 p-4 sm:p-5">
      <div class="rounded-lg border border-gray-100 bg-white p-4 shadow-sm sm:p-5">
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0 flex-1">
            <div class="mb-2 flex flex-wrap items-center gap-2">
              <h1 class="min-w-0 break-words text-lg font-semibold text-gray-950 sm:text-xl">{{ asset?.name }}</h1>
              <span class="rounded-md bg-indigo-50 px-2 py-1 font-mono text-xs font-semibold text-indigo-700">
                {{ asset?.idEquipment || asset?.assetNumber || asset?.id }}
              </span>
            </div>
            <p class="break-words text-sm text-gray-500">
              {{ displayCategory(asset?.category) }} / {{ displayValue(asset?.model) }}
            </p>
          </div>
          <button
            v-if="modal"
            class="rounded-full px-2 py-1 text-2xl leading-none text-gray-400 hover:bg-gray-100 hover:text-red-500 focus:outline-none"
            @click="emit('close')"
          >×</button>
        </div>

        <div class="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-3">
          <div class="min-w-0 rounded-lg bg-gray-50 px-3 py-2.5">
            <div class="text-xs font-medium text-gray-500">{{ t('assetDetail.user') }}</div>
            <div class="mt-1 truncate text-sm font-semibold text-gray-900">{{ assignedUserName }}</div>
          </div>
          <div class="min-w-0 rounded-lg bg-gray-50 px-3 py-2.5">
            <div class="text-xs font-medium text-gray-500">{{ t('assetDetail.userDepartment') }}</div>
            <div class="mt-1 truncate text-sm font-semibold text-gray-900">{{ displayValue(asset?.userDepartment) }}</div>
          </div>
          <div class="min-w-0 rounded-lg bg-gray-50 px-3 py-2.5">
            <div class="text-xs font-medium text-gray-500">{{ t('assetDetail.status') }}</div>
            <div class="mt-1"><StatusBadge :status="asset?.status" type="asset" /></div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
        <section class="min-w-0 rounded-lg border border-gray-100 bg-white p-4 shadow-sm">
          <h2 class="mb-3 text-sm font-semibold text-gray-900">{{ t('assetDetail.assetDetail') }}</h2>
          <div class="divide-y divide-gray-100">
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.assetNumber') }}</span><span class="asset-detail-value font-mono text-indigo-700">{{ asset?.idEquipment || asset?.assetNumber || asset?.id }}</span></div>
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.category') }}</span><span class="asset-detail-value">{{ displayCategory(asset?.category) }}</span></div>
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.model') }}</span><span class="asset-detail-value">{{ displayValue(asset?.model) }}</span></div>
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.specs') }}</span><span class="asset-detail-value">{{ displayValue(asset?.specs) }}</span></div>
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.serialNumber') }}</span><span class="asset-detail-value font-mono">{{ displayValue(asset?.serial_Number ?? asset?.serialNumber) }}</span></div>
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.location') }}</span><span class="asset-detail-value">{{ displayValue(asset?.location) }}</span></div>
          </div>
        </section>

        <section class="min-w-0 rounded-lg border border-gray-100 bg-white p-4 shadow-sm">
          <h2 class="mb-3 text-sm font-semibold text-gray-900">{{ t('assetDetail.owner') }}</h2>
          <div class="divide-y divide-gray-100">
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.department') }}</span><span class="asset-detail-value">{{ displayValue(asset?.department) }}</span></div>
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.owner') }}</span><span class="asset-detail-value">{{ ownerUserName }}</span></div>
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.supplier') }}</span><span class="asset-detail-value">{{ displayValue(asset?.supplier) }}</span></div>
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.purchaseDate') }}</span><span class="asset-detail-value">{{ displayValue(asset?.purchase_date ?? asset?.purchaseDate) }}</span></div>
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.purchasePrice') }}</span><span class="asset-detail-value font-medium text-emerald-700">{{ formatMoney(asset?.purchase_price ?? asset?.purchasePrice) }}</span></div>
            <div class="asset-detail-row"><span class="asset-detail-label">{{ t('assetDetail.activationDate') }}</span><span class="asset-detail-value">{{ displayValue(asset?.activationDate) }}</span></div>
            <div class="asset-detail-row">
              <span class="asset-detail-label">{{ t('assetDetail.warrantyExpiry') }}</span>
              <span class="asset-detail-value" :class="isWarrantyExpired ? 'font-medium text-red-600' : ''">
                {{ displayValue(asset?.warrantyExpiry) }}
                <span v-if="isWarrantyExpired" class="ml-1 text-xs text-red-500">（{{ t('assetDetail.expired') }}）</span>
              </span>
            </div>
          </div>
        </section>
      </div>

      <section v-if="asset?.notes" class="rounded-lg border border-gray-100 bg-white p-4 shadow-sm">
        <h2 class="mb-2 text-sm font-semibold text-gray-900">{{ t('assetDetail.notes') }}</h2>
        <p class="whitespace-pre-line break-words text-sm leading-6 text-gray-600">{{ asset?.notes }}</p>
      </section>

      <section class="rounded-lg border border-gray-100 bg-white p-4 shadow-sm">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-sm font-semibold text-gray-900">{{ t('assetDetail.maintenanceRecords') }}</h2>
          <span class="text-xs text-gray-400">{{ relatedRequests.length }} {{ t('common.items') }}</span>
        </div>

        <div v-if="relatedRequests.length === 0" class="rounded-lg border border-dashed border-gray-200 py-6 text-center text-sm text-gray-400">
          {{ t('assetDetail.noMaintenanceRecord') }}
        </div>

        <div v-else class="space-y-3">
          <button
            v-for="req in relatedRequests"
            :key="req.idForm || req.id"
            type="button"
            class="w-full rounded-lg border border-gray-100 bg-gray-50 p-4 text-left transition hover:border-indigo-200 hover:bg-indigo-50"
            @click="goToRequestDetail(req)"
          >
            <div class="mb-2 flex flex-wrap items-center gap-2">
              <span class="rounded-md bg-white px-2 py-1 font-mono text-xs font-semibold text-indigo-700">{{ getShortReqId(req) }}</span>
              <span
                v-if="isRejectedRequest(req)"
                class="rounded-full bg-red-50 px-2 py-0.5 text-xs font-semibold text-red-700"
              >
                {{ t('assetDetail.rejectedRequest') }}
              </span>
              <span class="text-xs text-gray-500">{{ t('assetDetail.reviewer') }}：{{ req.reviewerName || getUserName(req.reviewerId || req.reviewer_id) }}</span>
              <span class="text-xs text-gray-500">{{ t('assetDetail.cost') }}：{{ formatMoney(req.repairCost ?? req.repair_cost) }}</span>
            </div>
            <div class="line-clamp-2 text-sm text-gray-700">
              <span class="font-medium">{{ t('assetDetail.issue') }}：</span>{{ req.faultDescription || req.issue_description || t('request.none') }}
            </div>
            <div v-if="isRejectedRequest(req)" class="mt-1 line-clamp-2 text-sm text-red-700">
              <span class="font-medium">{{ t('assetDetail.rejectionReason') }}：</span>{{ req.reviewNote || t('request.none') }}
            </div>
            <div v-else class="mt-1 line-clamp-2 text-sm text-gray-600">
              <span class="font-medium">{{ t('assetDetail.repairDescription') }}：</span>{{ req.repairSolution || req.repair_solution || req.repairContent || req.repair_description || t('request.none') }}
            </div>
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.asset-detail-row {
  display: grid;
  grid-template-columns: minmax(5rem, 6.5rem) minmax(0, 1fr);
  gap: 0.75rem;
  padding: 0.625rem 0;
}

.asset-detail-label {
  color: rgb(107 114 128);
  font-size: 0.8125rem;
  font-weight: 500;
}

.asset-detail-value {
  min-width: 0;
  overflow-wrap: anywhere;
  color: rgb(17 24 39);
  font-size: 0.875rem;
}

@media (max-width: 520px) {
  .asset-detail-row {
    grid-template-columns: 1fr;
    gap: 0.25rem;
  }
}
</style>
