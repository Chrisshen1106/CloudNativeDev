<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAssetsStore } from '@/stores/assets'
import { useI18n } from '@/composables/useI18n'
import StatusBadge from '@/components/common/StatusBadge.vue'

const props = defineProps({
  id: [String, Number],
  modal: Boolean
})

const emit = defineEmits(['close'])

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const assetsStore = useAssetsStore()
const { t } = useI18n()

const assetId = computed(() => props.id || route.params.id)
const asset = ref(null)
const loading = ref(false)
const errorMsg = ref('')

async function fetchAssetDetail() {
  if (!assetId.value) return
  loading.value = true
  errorMsg.value = ''
  try {
    asset.value = await assetsStore.getAssetDetail(assetId.value, authStore.token)
  } catch (e) {
    errorMsg.value = e.message || '取得資產詳情失敗'
    asset.value = null
  } finally {
    loading.value = false
  }
}

// 根據 ID 取得名稱的邏輯（可依實際需求調整）
function getUserName(ownerId) {
  return ownerId ? `User (${ownerId})` : '未指派'
}

onMounted(fetchAssetDetail)
watch(assetId, fetchAssetDetail)

const relatedRequests = computed(() => asset.value?.maintenanceHistory || [])

const isWarrantyExpired = computed(() => {
  if (!asset.value?.warrantyExpiry) return false
  return new Date(asset.value.warrantyExpiry) < new Date()
})

function categoryIcon(cat) {
  const icons = { computer: '💻', phone: '📱', tablet: '平板' }
  return icons[cat] || '📦'
}
</script>

<template>
    <div :class="modal ? 'max-w-2xl' : 'max-w-3xl mx-auto'"
      class="p-6 md:p-8"
      style="max-height:90vh; min-height:200px; overflow-y:auto; box-sizing:border-box;">
    <div class="flex justify-between items-center mb-8">
      <div>
        <div class="text-2xl font-bold text-indigo-700 flex items-center gap-2">
          <span>{{ asset?.name }}</span>
          <span class="text-base font-mono bg-gray-100 px-2 py-0.5 rounded">{{ asset?.idEquipment || asset?.id || asset?.assetNumber }}</span>
        </div>
        <div class="text-sm text-gray-500 mt-1">{{ asset?.category }} / {{ asset?.model }}</div>
      </div>
      <button v-if="modal" @click="$emit('close')" class="text-gray-400 hover:text-red-500 text-2xl px-2 py-1 rounded-full focus:outline-none">×</button>
    </div>
    <div v-if="loading" class="flex justify-center p-10">
      <span class="text-gray-500 italic">載入資料中...</span>
    </div>
    <div v-else-if="errorMsg" class="bg-red-50 text-red-600 p-4 rounded-lg text-center">
      {{ errorMsg }}
    </div>
    <div v-else-if="asset" class="space-y-8">
      <!-- debug 資產物件區塊已移除 -->
      <!-- 資產資訊卡片 -->
      <div class="bg-white rounded-2xl shadow p-8 space-y-2 divide-y divide-gray-100">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 pb-4">
          <div class="flex items-center mb-2">
            <span class="w-28 text-gray-500">資產編號</span>
            <span class="font-mono text-indigo-600">{{ asset?.assetNumber ?? '無' }}</span>
          </div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">狀態</span><StatusBadge :status="asset?.status" type="asset" /></div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">分類</span><span>{{ asset?.category }}</span></div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">型號</span><span>{{ asset?.model }}</span></div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">規格</span><span>{{ asset?.specs }}</span></div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">序號</span><span class="font-mono">{{ asset?.serialNumber }}</span></div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">使用部門</span><span>{{ asset?.department }}</span></div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">負責人</span><span>{{ getUserName(asset?.ownerId) }}</span></div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">存放地點</span><span>{{ asset?.location }}</span></div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 pt-4 pb-4">
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">供應商</span><span>{{ asset?.supplier }}</span></div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">購買日期</span><span>{{ asset?.purchaseDate }}</span></div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">購買金額</span><span class="font-medium text-green-700">NT$ {{ asset?.purchasePrice?.toLocaleString() }}</span></div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">啟用日期</span><span>{{ asset?.activationDate }}</span></div>
          <div class="flex items-center mb-2"><span class="w-28 text-gray-500">保固期限</span><span :class="isWarrantyExpired ? 'text-red-600 font-medium' : ''">{{ asset?.warrantyExpiry }}<span v-if="isWarrantyExpired" class="text-xs text-red-500 ml-1">（已過期）</span></span></div>
        </div>
        <div v-if="asset?.notes" class="pt-4"><span class="w-28 text-gray-500 inline-block">備註</span><span class="text-gray-600 text-sm">{{ asset?.notes }}</span></div>
      </div>
      <!-- 維修紀錄 -->
      <div class="bg-white rounded-2xl shadow p-8">
        <h2 class="text-lg font-bold mb-4 border-b pb-2 text-indigo-600">維修/申請紀錄</h2>
        <div v-if="relatedRequests.length === 0" class="text-sm text-gray-400 text-center py-6">
          無維修紀錄
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="req in relatedRequests"
            :key="req.idForm"
            class="rounded-xl border border-gray-100 bg-gray-50 p-4 hover:bg-indigo-50 transition-colors"
          >
            <div class="flex flex-wrap gap-4 items-center mb-2">
              <span class="font-mono text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded">{{ req.idForm }}</span>
              <span class="text-xs text-gray-500">審查人：{{ req.reviewerName || req.reviewer_id }}</span>
              <span class="text-xs text-gray-500">開始：{{ req.repair_start_date }}</span>
              <span class="text-xs text-gray-500">結束：{{ req.repair_end_date }}</span>
              <span class="text-xs text-gray-500">費用：NT$ {{ req.repair_cost?.toLocaleString() }}</span>
            </div>
            <div class="mb-1 text-sm text-gray-700"><b>問題：</b>{{ req.issue_description }}</div>
            <div class="mb-1 text-sm text-gray-700"><b>維修說明：</b>{{ req.repair_description }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>