<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-8 animate-modal">
        <button class="absolute top-3 right-3 btn-secondary btn-sm" @click="$emit('close')">×</button>
        <h2 class="text-xl font-bold mb-4">資產詳情</h2>
        <div v-if="loading" class="text-center py-8 text-gray-400">載入中...</div>
        <div v-else-if="errorMsg" class="text-center py-8 text-red-500">{{ errorMsg }}</div>
        <div v-else-if="asset">
          <div class="mb-4">
            <div class="font-bold text-lg mb-1">{{ asset.name }}</div>
            <div class="text-sm text-gray-500 mb-2">資產編號：{{ asset.id }}</div>
            <div>型號：{{ asset.model }}</div>
            <div>分類：{{ asset.category }}</div>
            <div>序號：{{ asset.serialNumber }}</div>
            <div>狀態：{{ asset.status }}</div>
            <div>啟用日：{{ asset.startDate }}</div>
            <div>保固到期：{{ asset.warrantyExpiry }}</div>
            <div>位置：{{ asset.location }}</div>
            <div>部門：{{ asset.department }}</div>
            <div>擁有者：{{ asset.ownerId }}</div>
            <div>備註：{{ asset.notes }}</div>
          </div>
          <div>
            <h3 class="font-semibold mb-2">維修紀錄</h3>
            <div v-if="!asset.maintenanceHistory?.length" class="text-gray-400">無維修紀錄</div>
            <ul v-else class="space-y-2">
              <li v-for="h in asset.maintenanceHistory" :key="h.idForm" class="border rounded p-2">
                <div>申請單號：{{ h.idForm }}</div>
                <div>描述：{{ h.issueDescription }}</div>
                <div>審核人：{{ h.reviewerName }}</div>
                <div>維修說明：{{ h.repairDescription }}</div>
                <div>維修費用：{{ h.repairCost }}</div>
                <div>維修起訖：{{ h.repairStartDate }} ~ {{ h.repairEndDate }}</div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { toRefs } from 'vue'
const props = defineProps({
  show: Boolean,
  asset: Object,
  loading: Boolean,
  errorMsg: String
})
</script>
