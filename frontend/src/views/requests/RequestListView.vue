<template>
  <div class="max-w-6xl mx-auto">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ authStore.isManager ? t('request.title') : t('request.titleMy') }}</h1>
        <p class="text-sm text-gray-500 mt-1">{{ t('common.total') }} {{ filteredRequests.length }} {{ t('common.items') }}</p>
      </div>
      <RouterLink
        v-if="authStore.isHolder"
        to="/requests/new"
        class="btn-primary"
      >
        <span></span> {{ t('request.newRequest') }}
      </RouterLink>
    </div>

    <!-- Filters -->
    <div class="card p-4 mb-5">
      <div class="flex flex-wrap gap-3 items-center">
        <div class="flex-1 min-w-56">
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></span>
            <input
              v-model="searchQuery"
              type="text"
              class="form-input pl-9"
              :placeholder="t('request.searchPlaceholder')"
            />
          </div>
        </div>
        <select v-model="filterStatus" class="form-select w-40">
          <option value="">{{ t('request.filterStatus') }}: {{ t('common.all') }}</option>
          <option value="pending">{{ t('request.statuses.pending') }}</option>
          <option value="under_repair">{{ t('request.statuses.under_repair') }}</option>
          <option value="completed">{{ t('request.statuses.completed') }}</option>
          <option value="rejected">{{ t('request.statuses.rejected') }}</option>
        </select>
        <button
          v-if="searchQuery || filterStatus"
          class="btn-secondary btn-sm"
          @click="resetFilters"
        >{{ t('common.reset') }}</button>
      </div>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ t('request.requestId') }}</th>
              <th>{{ t('request.assetName') }}</th>
              <th v-if="authStore.isManager">{{ t('request.requester') }}</th>
              <th>{{ t('request.requestDate') }}</th>
              <th>{{ t('request.faultDescription') }}</th>
              <th>{{ t('asset.status') }}</th>
              <th class="text-center">{{ t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="pagedRequests.length === 0">
              <td :colspan="authStore.isManager ? 7 : 6" class="text-center py-12 text-gray-400">
                <div class="flex flex-col items-center gap-2">
                  <span class="text-4xl"></span>
                  <span>{{ t('common.noData') }}</span>
                </div>
              </td>
            </tr>
            <tr v-for="req in pagedRequests" :key="req.id">
              <td class="font-mono text-xs text-indigo-600 font-medium whitespace-nowrap">{{ req.id }}</td>
              <td class="font-medium text-gray-900 whitespace-nowrap">{{ getAssetName(req.assetId) }}</td>
              <td v-if="authStore.isManager" class="text-gray-600">{{ getUserName(req.requesterId) }}</td>
              <td class="text-gray-500 text-sm whitespace-nowrap">{{ req.requestDate }}</td>
              <td class="text-gray-600 max-w-xs">
                <span class="line-clamp-1 text-sm">{{ req.faultDescription }}</span>
              </td>
              <td><StatusBadge :status="req.status" type="request" /></td>
              <td class="text-center whitespace-nowrap">
                <RouterLink :to="`/requests/${req.id}`" class="btn-secondary btn-sm">
                  {{ t('common.detail') }}
                </RouterLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-4 pb-4">
        <Pagination
          :total="filteredRequests.length"
          :page-size="pageSize"
          :current-page="currentPage"
          @page-change="currentPage = $event"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAssetsStore } from '@/stores/assets'
import { useRequestsStore } from '@/stores/requests'
import { mockUsers } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'
import StatusBadge from '@/components/common/StatusBadge.vue'
import Pagination from '@/components/common/Pagination.vue'

const authStore = useAuthStore()
const assetsStore = useAssetsStore()
const requestsStore = useRequestsStore()
const { t } = useI18n()

const searchQuery = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = 10

const sourceRequests = computed(() =>
  authStore.isManager
    ? requestsStore.getAll()
    : requestsStore.getByRequesterId(authStore.currentUser?.id)
)

const filteredRequests = computed(() => {
  let list = [...sourceRequests.value].sort((a, b) => b.requestDate.localeCompare(a.requestDate))
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter((r) =>
      r.id.toLowerCase().includes(q) ||
      getAssetName(r.assetId).toLowerCase().includes(q) ||
      getUserName(r.requesterId).toLowerCase().includes(q)
    )
  }
  if (filterStatus.value) list = list.filter((r) => r.status === filterStatus.value)
  return list
})

const pagedRequests = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredRequests.value.slice(start, start + pageSize)
})

function resetFilters() {
  searchQuery.value = ''
  filterStatus.value = ''
  currentPage.value = 1
}

function getAssetName(assetId) {
  return assetsStore.getById(assetId)?.name || assetId
}

function getUserName(userId) {
  return mockUsers.find((u) => u.id === userId)?.name || userId
}
</script>
