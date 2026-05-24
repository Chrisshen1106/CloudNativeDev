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
          <option value="approved">{{ t('request.statuses.approved') }}</option>
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
      <div v-if="error && filteredRequests.length === 0" class="mb-4 text-red-500 text-sm">
        {{ error }}
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ t('request.requestId') }}</th>
              <th>{{ t('request.assetNumber') }}</th>
              <th v-if="authStore.isManager">{{ t('request.requester') }}</th>
              <th>{{ t('request.requestDate') }}</th>
              <th>{{ t('request.faultDescription') }}</th>
              <th>{{ t('asset.status') }}</th>
              <th class="text-center pl-2">{{ t('common.actions') }}</th>
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
              <td class="text-center whitespace-nowrap pl-4">
                <div class="flex items-center gap-2 justify-start">
                  <RouterLink :to="`/requests/${req.id}`" class="btn-secondary btn-sm">
                    {{ t('common.detail') }}
                  </RouterLink>
                  <RouterLink
                    v-if="canEditRequest(req)"
                    :to="`/requests/${req.id}/edit`"
                    class="btn-primary btn-sm"
                  >
                    {{ t('common.edit') }}
                  </RouterLink>
                  <button
                    v-if="['pending', 'completed', 'rejected'].includes(req.status)"
                    class="btn-danger btn-sm"
                    @click="openDeleteConfirm(req.id)"
                  >{{ t('common.delete') }}</button>
                </div>
              </td>
              <div v-if="showDeleteConfirm" style="position:fixed;top:30%;left:50%;transform:translate(-50%,0);z-index:1000;">
                <div class="bg-white rounded shadow-lg p-6 w-80 border border-gray-200">
                  <div class="mb-4 text-lg font-semibold text-gray-800">{{ t('request.deleteConfirmTitle') }}</div>
                  <div class="flex justify-end gap-3">
                    <button class="btn-secondary" @click="showDeleteConfirm = false">{{ t('common.cancel') }}</button>
                    <button class="btn-danger" @click="handleDeleteRequest">{{ t('common.delete') }}</button>
                  </div>
                </div>
              </div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRequestsStore } from '@/stores/requests'
import { useI18n } from '@/composables/useI18n'
import StatusBadge from '@/components/common/StatusBadge.vue'
import Pagination from '@/components/common/Pagination.vue'

const authStore = useAuthStore()
const requestsStore = useRequestsStore()
const { t } = useI18n()

const searchQuery = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = 10

const sourceRequests = ref([])
const users = ref([])
const loading = ref(false)
const error = ref(null)

const currentUserId = computed(() => {
  const user = authStore.currentUser || {}
  return String(user.idUser || user.id || user.userId || '').replace(/[^\d]/g, '')
})

async function loadRequests() {
  loading.value = true
  error.value = null
  try {
    // fetchAll 會自動依權限過濾
    await requestsStore.fetchAll(authStore.token)
    sourceRequests.value = requestsStore.getAll()
    if (authStore.isManager) {
      users.value = await authStore.fetchAllUsers().catch(() => [])
    }
  } catch (e) {
    error.value = e.message || t('request.loadFailed')
  } finally {
    loading.value = false
  }
}
const showDeleteConfirm = ref(false)
const deleteTargetId = ref(null)

function openDeleteConfirm(id) {
  deleteTargetId.value = id
  showDeleteConfirm.value = true
}

async function handleDeleteRequest() {
  try {
    let id = deleteTargetId.value
    if (typeof id === 'string') {
      const match = id.match(/(\d+)/)
      if (match) id = match[1]
    }
    const token = authStore.token || localStorage.getItem('ams_token') || ''
    const res = await fetch(`/maintenance-api/form/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': token
      }
    })
    if (!res.ok) throw new Error(t('request.deleteFailed'))
    showDeleteConfirm.value = false
    deleteTargetId.value = null
    await loadRequests()
  } catch (e) {
    showDeleteConfirm.value = false
    deleteTargetId.value = null
    // 可加通知：刪除失敗
  }
}
onMounted(loadRequests)
watch(() => currentUserId.value, loadRequests)

const filteredRequests = computed(() => {
  let list = [...sourceRequests.value].sort((a, b) => (b.requestDate || '').localeCompare(a.requestDate || ''))
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter((r) =>
      (r.id || '').toLowerCase().includes(q) ||
      getAssetName(r.assetId || '').toLowerCase().includes(q) ||
      getUserName(r.requesterId || '').toLowerCase().includes(q)
    )
  }
  if (filterStatus.value) {
    if (filterStatus.value === 'under_repair') {
      list = list.filter((r) => r.status === 'under_repair' || r.status === 'repairing')
    } else {
      list = list.filter((r) => r.status === filterStatus.value)
    }
  }
  return list
})

const pagedRequests = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredRequests.value.slice(start, start + pageSize)
})

function resetFilters() {
  searchQuery.value = ''
  filterStatus.value = ''
}

function getAssetName(assetId) {
  // 可根據資產 id 顯示名稱
  return assetId
}

function getUserName(userId) {
  const id = String(userId || '').replace(/[^\d]/g, '')
  const user = users.value.find((u) => String(u.idUser || u.id) === id)
  if (!id) return userId || ''
  return user?.name ? `${user.name} (U${id})` : `U${id}`
}

function canEditRequest(req) {
  if (!req || req.status !== 'pending' || authStore.isManager) return false
  const applicantId = String(req.applicant_id || req.requesterId || '').replace(/[^\d]/g, '')
  return !!currentUserId.value && applicantId === currentUserId.value
}

</script>
