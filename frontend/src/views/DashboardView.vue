<template>
  <div class="max-w-6xl mx-auto">
    <!-- Welcome -->
    <div class="mb-6">
      <h1 class="page-title">{{ t('dashboard.welcomeBack') }}，{{ authStore.currentUser?.name }}</h1>
      <p class="text-sm text-gray-500 mt-1">
        {{ new Date().toLocaleDateString(currentLocale === 'zh-TW' ? 'zh-TW' : 'en-US', { year:'numeric', month:'long', day:'numeric', weekday:'long' }) }}
      </p>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div v-for="stat in statCards" :key="stat.key" class="card p-5">
        <div class="flex items-start justify-between mb-3">
          <div class="text-2xl">{{ stat.icon }}</div>
          <span
            class="text-xs px-2 py-0.5 rounded-full font-medium"
            :class="stat.tagClass"
          >{{ stat.tag }}</span>
        </div>
        <p class="text-3xl font-bold text-gray-900 mb-1">{{ stat.value }}</p>
        <p class="text-sm text-gray-500">{{ stat.label }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Recent requests -->
      <div class="lg:col-span-2 card p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="section-title mb-0">{{ t('dashboard.recentRequests') }}</h2>
          <RouterLink to="/requests" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium transition-colors">
            查看全部 →
          </RouterLink>
        </div>
        <div v-if="recentRequests.length === 0" class="text-center py-8 text-gray-400 text-sm">
          {{ t('dashboard.noRecentRequests') }}
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="req in recentRequests"
            :key="req.id"
            class="flex items-center gap-3 p-3 rounded-xl bg-gray-50 hover:bg-indigo-50 transition-colors cursor-pointer"
            @click="router.push(`/requests/${req.id}`)"
          >
            <div class="text-xl"></div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-sm font-medium text-gray-800 truncate">{{ getAssetName(req.assetId) }}</span>
                <StatusBadge :status="req.status" type="request" />
              </div>
              <p class="text-xs text-gray-500 mt-0.5 truncate">{{ req.faultDescription }}</p>
            </div>
            <div class="text-xs text-gray-400 shrink-0">{{ req.requestDate }}</div>
          </div>
        </div>
      </div>

      <!-- Quick actions -->
      <div class="card p-5">
        <h2 class="section-title">{{ t('dashboard.quickActions') }}</h2>
        <div class="space-y-2">
          <RouterLink
            v-for="action in quickActions"
            :key="action.to"
            :to="action.to"
            class="flex items-center gap-3 px-4 py-3 rounded-xl border border-gray-100 hover:bg-indigo-50 hover:border-indigo-200 transition-all group"
          >
            <span class="text-xl">{{ action.icon }}</span>
            <span class="text-sm font-medium text-gray-700 group-hover:text-indigo-700 transition-colors">{{ action.label }}</span>
            <span class="ml-auto text-gray-300 group-hover:text-indigo-400 transition-colors">→</span>
          </RouterLink>
        </div>

        <!-- Status summary (manager) -->
        <div v-if="authStore.isManager" class="mt-6">
          <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">待處理事項</h3>
          <div class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600"> 待審查申請</span>
              <span class="font-bold text-blue-600">{{ pendingCount }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-600"> 維修中資產</span>
              <span class="font-bold text-amber-600">{{ underRepairCount }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAssetsStore } from '@/stores/assets'
import { useRequestsStore } from '@/stores/requests'
import { useI18n } from '@/composables/useI18n'
import StatusBadge from '@/components/common/StatusBadge.vue'

const authStore = useAuthStore()
const assetsStore = useAssetsStore()
const requestsStore = useRequestsStore()
const router = useRouter()
const { t, currentLocale } = useI18n()

const userId = computed(() => authStore.currentUser?.id)

const myAssets = computed(() =>
  authStore.isManager
    ? assetsStore.getAll()
    : assetsStore.getByOwnerId(userId.value)
)

const myRequests = computed(() =>
  authStore.isManager
    ? requestsStore.getAll()
    : requestsStore.getByRequesterId(userId.value)
)

const pendingCount = computed(() =>
  requestsStore.getAll().filter((r) => r.status === 'pending').length
)

const underRepairCount = computed(() =>
  assetsStore.getAll().filter((a) => a.status === 'under_repair').length
)

const statCards = computed(() => {
  if (authStore.isManager) {
    const all = assetsStore.getAll()
    return [
      {
        key: 'total', icon: '', value: all.length,
        label: t('dashboard.totalAssets'),
        tag: '全部', tagClass: 'bg-gray-100 text-gray-600',
      },
      {
        key: 'normal', icon: '', value: all.filter(a => a.status === 'normal').length,
        label: t('dashboard.normalAssets'),
        tag: '正常', tagClass: 'bg-emerald-100 text-emerald-700',
      },
      {
        key: 'repair', icon: '', value: underRepairCount.value,
        label: t('dashboard.underRepairAssets'),
        tag: '維修中', tagClass: 'bg-amber-100 text-amber-700',
      },
      {
        key: 'pending', icon: '', value: pendingCount.value,
        label: t('dashboard.pendingRequests'),
        tag: '待審', tagClass: 'bg-blue-100 text-blue-700',
      },
    ]
  } else {
    const mine = myAssets.value
    const myReqs = myRequests.value
    return [
      {
        key: 'total', icon: '', value: mine.length,
        label: t('dashboard.myAssets'),
        tag: '我的', tagClass: 'bg-indigo-100 text-indigo-700',
      },
      {
        key: 'normal', icon: '', value: mine.filter(a => a.status === 'normal').length,
        label: t('dashboard.myNormal'),
        tag: '正常', tagClass: 'bg-emerald-100 text-emerald-700',
      },
      {
        key: 'repair', icon: '', value: mine.filter(a => a.status === 'under_repair').length,
        label: t('dashboard.myUnderRepair'),
        tag: '維修中', tagClass: 'bg-amber-100 text-amber-700',
      },
      {
        key: 'pending', icon: '', value: myReqs.filter(r => r.status === 'pending').length,
        label: t('dashboard.myPending'),
        tag: '待審', tagClass: 'bg-blue-100 text-blue-700',
      },
    ]
  }
})

const recentRequests = computed(() =>
  [...myRequests.value]
    .sort((a, b) => b.requestDate.localeCompare(a.requestDate))
    .slice(0, 5)
)

const quickActions = computed(() => {
  if (authStore.isManager) {
    return [
      { to: '/assets/new',   icon: '', label: t('dashboard.registerAsset') },
      { to: '/assets',       icon: '', label: t('dashboard.allAssets') },
      { to: '/requests',     icon: '', label: t('dashboard.allRequests') },
    ]
  }
  return [
    { to: '/requests/new', icon: '', label: t('dashboard.submitRequest') },
    { to: '/assets',       icon: '', label: t('dashboard.myAssetList') },
    { to: '/requests',     icon: '', label: t('dashboard.myRequests') },
  ]
})

function getAssetName(assetId) {
  return assetsStore.getById(assetId)?.name || assetId
}
</script>
