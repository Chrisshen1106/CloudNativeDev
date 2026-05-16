<template>
  <div class="max-w-6xl mx-auto">
    <!-- Page header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          {{ authStore.isManager ? t('asset.title') : t('asset.titleMy') }}
        </h1>
        <p class="text-sm text-gray-500 mt-1">{{ t('common.total') }} {{ filteredAssets.length }} {{ t('common.items') }}</p>
      </div>
      <RouterLink v-if="authStore.isManager" to="/assets/new" class="btn-primary">
        <span></span> {{ t('asset.addAsset') }}
      </RouterLink>
    </div>

    <!-- Filters -->
    <div class="card p-4 mb-5">
      <div class="flex flex-wrap gap-3 items-center">
        <!-- Search -->
        <div class="flex-1 min-w-56">
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm"></span>
            <input
              v-model="searchQuery"
              type="text"
              class="form-input pl-9"
              :placeholder="t('asset.searchPlaceholder')"
            />
          </div>
        </div>
        <!-- Category filter -->
        <select v-model="filterCategory" class="form-select w-36">
          <option value="">{{ t('asset.filterCategory') }}: {{ t('common.all') }}</option>
          <option value="computer">{{ t('asset.categories.computer') }}</option>
          <option value="phone">{{ t('asset.categories.phone') }}</option>
          <option value="tablet">{{ t('asset.categories.tablet') }}</option>
        </select>
        <!-- Status filter -->
        <select v-model="filterStatus" class="form-select w-36">
          <option value="">{{ t('asset.filterStatus') }}: {{ t('common.all') }}</option>
          <option value="in_use">{{ t('asset.statuses.in_use') }}</option>
          <option value="repairing">{{ t('asset.statuses.repairing') }}</option>

        </select>
        <!-- Reset -->
        <button
          v-if="searchQuery || filterCategory || filterStatus"
          class="btn-secondary btn-sm"
          @click="resetFilters"
        >{{ t('common.reset') }}</button>
      </div>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div v-if="errorMsg && filteredAssets.length === 0" class="mb-4 text-red-500 text-sm">
        {{ errorMsg }}
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ t('asset.assetNumber') }}</th>
              <th>{{ t('asset.name') }}</th>
              <th>{{ t('asset.category') }}</th>
              <th>{{ t('asset.model') }}</th>
              <th>{{ t('asset.location') }}</th>
              <th v-if="authStore.isManager">{{ t('asset.owner') }}</th>
              <th>{{ t('asset.department') }}</th>
              <th>{{ t('asset.status') }}</th>
              <th class="text-center">{{ t('common.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="pagedAssets.length === 0">
              <td :colspan="authStore.isManager ? 9 : 8" class="text-center py-12 text-gray-400">
                <div class="flex flex-col items-center gap-2">
                  <span class="text-4xl"></span>
                  <span>{{ t('common.noData') }}</span>
                </div>
              </td>
            </tr>
            <tr v-for="asset in pagedAssets" :key="asset.id">
              <td class="font-mono text-xs text-indigo-600 font-medium">{{ asset.assetNumber }}</td>
              <td class="font-medium text-gray-900">{{ asset.name }}</td>
              <td>
                <span class="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 font-medium">
                  {{ categoryIcon(asset.category) }} {{ t(`asset.categories.${asset.category}`) }}
                </span>
              </td>
              <td class="text-gray-600">{{ asset.model }}</td>
              <td class="text-gray-600 text-xs">{{ asset.location }}</td>
              <td v-if="authStore.isManager" class="text-gray-600">{{ getUserName(asset.ownerId) }}</td>
              <td class="text-gray-600 text-xs">{{ asset.department }}</td>
              <td><StatusBadge :status="asset.status" type="asset" /></td>
              <td class="text-center">
                <div class="flex items-center justify-center gap-2">
                  <button
                    class="btn-secondary btn-sm"
                    @click="openDetailModal(asset.idEquipment || asset.id)"
                  >{{ t('common.detail') }}</button>
                  <!-- 詳情 Modal 直接寫在這裡（每一列一個 Teleport） -->
                  <Teleport to="body">
                    <div v-if="showDetailModal && detailAssetId === (asset.idEquipment || asset.id)" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="closeDetailModal">
                      <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeDetailModal"></div>
                      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-8 animate-modal">
                        <AssetDetailView v-if="detailAssetId" :id="String(detailAssetId)" modal @close="closeDetailModal" />
                      </div>
                    </div>
                  </Teleport>
                  <RouterLink
                    v-if="authStore.isManager"
                    :to="`/assets/${asset.id}/edit`"
                    class="btn-primary btn-sm"
                  >{{ t('common.edit') }}</RouterLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Pagination -->
      <div class="px-4 pb-4">
        <Pagination
          :total="filteredAssets.length"
          :page-size="pageSize"
          :current-page="currentPage"
          @page-change="currentPage = $event"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import AssetDetailView from './AssetDetailView.vue'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAssetsStore } from '@/stores/assets'
// import { mockUsers } from '@/stores/auth'
import { useI18n } from '@/composables/useI18n'
import StatusBadge from '@/components/common/StatusBadge.vue'
import Pagination from '@/components/common/Pagination.vue'


const authStore = useAuthStore()
const assetsStore = useAssetsStore()
const { t } = useI18n()

const showDetailModal = ref(false)
const detailAsset = ref(null)
const detailLoading = ref(false)
const detailError = ref('')

const detailAssetId = ref(null)
function openDetailModal(assetId) {
  console.log('openDetailModal', assetId)
  detailAssetId.value = assetId
  showDetailModal.value = true
}
function closeDetailModal() {
  showDetailModal.value = false
}


const errorMsg = ref('')
async function fetchAssets() {
  errorMsg.value = ''
  console.log('authStore.token', authStore.token)
  if (authStore.token) {
    try {
      await assetsStore.fetchUserAssets(authStore.token)
      // 這裡加 log
      console.log('authStore.currentUser', authStore.currentUser)
      console.log('authStore.currentUser.sub', authStore.currentUser?.sub)
      console.log('assetsStore.assets', assetsStore.assets)
    } catch (e) {
      errorMsg.value = e.message || '取得資產失敗'
      console.error(e)
    }
  }
}
              
onBeforeUnmount(() => {
  window.removeEventListener('refresh-assets', fetchAssets)
})
onMounted(() => {
  console.log('token:', authStore.token) // 應該要有 Bearer 開頭
  fetchAssets()
  window.addEventListener('refresh-assets', fetchAssets)
})
const searchQuery = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = 10

// user 直接顯示 API 回傳的所有資產，不再用 ownerId 過濾
const sourceAssets = computed(() => assetsStore.getAll())

const filteredAssets = computed(() => {
  let list = sourceAssets.value
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter((a) =>
      a.name.toLowerCase().includes(q) ||
      (a.assetNumber ? a.assetNumber.toString().toLowerCase() : '').includes(q) ||
      (a.model ? a.model.toString().toLowerCase() : '').includes(q) ||
      (a.location ? a.location.toString().toLowerCase() : '').includes(q) ||
      (getUserName(a.ownerId) ? getUserName(a.ownerId).toString().toLowerCase() : '').includes(q)
    )
  }
  if (filterCategory.value) list = list.filter((a) => a.category === filterCategory.value)
  if (filterStatus.value)   list = list.filter((a) => a.status === filterStatus.value)
  return list
})

const pagedAssets = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredAssets.value.slice(start, start + pageSize)
})

function resetFilters() {
  searchQuery.value = ''
  filterCategory.value = ''
  filterStatus.value = ''
  currentPage.value = 1
  fetchAssets(1)
}


function getUserName(ownerId) {
  // 目前沒有 users 資料，直接回傳 ownerId
  return ownerId
}

function categoryIcon(cat) {
  return { computer: '', phone: '', tablet: '' }[cat] || ''
}
</script>
