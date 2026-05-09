<template>
  <div class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="btn-secondary btn-sm" @click="router.back()">
        ← {{ t('common.back') }}
      </button>
      <div class="flex-1">
        <h1 class="page-title text-xl font-mono">{{ request?.id || '...' }}</h1>
        <p class="text-sm text-gray-500">{{ getAssetName(request?.assetId) }}</p>
      </div>
      <StatusBadge v-if="request" :status="request.status" type="request" />
    </div>

    <div v-if="!request" class="card p-12 text-center text-gray-400">
      <p class="text-4xl mb-2"></p>
      <p>找不到此申請單</p>
    </div>

    <div v-else class="space-y-5">
      <!-- Workflow timeline -->
      <div class="card p-5">
        <h2 class="section-title">{{ t('request.workflowTitle') }}</h2>
        <div class="relative">
          <!-- Line -->
          <div class="absolute left-4 top-4 bottom-4 w-0.5 bg-gray-200"></div>
          <div class="space-y-4">
            <div v-for="(step, idx) in timelineSteps" :key="idx" class="flex gap-4 relative">
              <!-- Dot -->
              <div class="relative z-10 w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm shrink-0"
                :class="stepDotClass(step.status)">
                {{ step.icon }}
              </div>
              <!-- Content -->
              <div class="flex-1 pb-2">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="text-sm font-semibold" :class="step.status === 'rejected' ? 'text-red-700' : 'text-gray-800'">
                    {{ step.label }}
                  </span>
                  <span v-if="step.date" class="text-xs text-gray-400">{{ step.date }}</span>
                  <span v-if="step.status === 'pending'" class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">等待中</span>
                </div>
                <p v-if="step.desc" class="text-xs text-gray-500 mt-0.5">{{ step.desc }}</p>
                <p v-if="step.note" class="text-xs mt-1 px-2 py-1 rounded bg-amber-50 text-amber-700 border border-amber-100">
                   {{ step.note }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Request info -->
      <div class="card p-5">
        <h2 class="section-title"> 申請資訊</h2>
        <div class="divide-y divide-gray-50">
          <div class="detail-row">
            <span class="detail-label">{{ t('request.requestId') }}</span>
            <span class="detail-value font-mono text-indigo-600 font-medium">{{ request.id }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">資產名稱</span>
            <RouterLink :to="`/assets/${request.assetId}`" class="detail-value text-indigo-600 hover:underline font-medium">
              {{ getAssetName(request.assetId) }}
            </RouterLink>
          </div>
          <div class="detail-row">
            <span class="detail-label">資產編號</span>
            <span class="detail-value font-mono text-gray-600 text-xs">{{ getAssetNumber(request.assetId) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">{{ t('request.requester') }}</span>
            <span class="detail-value font-medium">{{ getUserName(request.requesterId) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">{{ t('request.requestDate') }}</span>
            <span class="detail-value">{{ request.requestDate }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">{{ t('request.faultDescription') }}</span>
            <span class="detail-value leading-relaxed">{{ request.faultDescription }}</span>
          </div>
          <!-- Attachments -->
          <div v-if="request.attachments?.length > 0" class="detail-row">
            <span class="detail-label">{{ t('request.attachments') }}</span>
            <div class="flex flex-wrap gap-2">
              <img
                v-for="(att, idx) in request.attachments"
                :key="idx"
                :src="att.data"
                :alt="att.name"
                class="w-20 h-20 object-cover rounded-lg border border-gray-200 cursor-pointer hover:opacity-80"
                @click="previewImage = att.data"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Manager Actions: Pending review -->
      <div v-if="authStore.isManager && request.status === 'pending'" class="card p-5 border-2 border-blue-100">
        <h2 class="section-title text-blue-700"> 審查申請</h2>
        <p class="text-sm text-gray-600 mb-4">請審查此維修申請，確認是否同意送修。</p>
        <div class="flex gap-3">
          <button class="btn-success flex-1" @click="showApproveModal = true">
            {{ t('common.approve') }}
          </button>
          <button class="btn-danger flex-1" @click="showRejectModal = true">
            {{ t('common.reject') }}
          </button>
        </div>
      </div>

      <!-- Review result (approved/rejected) -->
      <div v-if="request.reviewDate" class="card p-5">
        <h2 class="section-title"> 審查結果</h2>
        <div class="divide-y divide-gray-50">
          <div class="detail-row">
            <span class="detail-label">{{ t('request.reviewer') }}</span>
            <span class="detail-value font-medium">{{ getUserName(request.reviewerId) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">{{ t('request.reviewDate') }}</span>
            <span class="detail-value">{{ request.reviewDate }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">{{ t('request.reviewNote') }}</span>
            <span class="detail-value text-gray-600">{{ request.reviewNote || '—' }}</span>
          </div>
        </div>
      </div>

      <!-- Repair Info (read-only when completed/rejected) -->
      <div v-if="request.status === 'completed' && request.repairDate" class="card p-5">
        <h2 class="section-title"> {{ t('request.repairInfo') }}</h2>
        <div class="divide-y divide-gray-50">
          <div class="detail-row"><span class="detail-label">{{ t('request.repairDate') }}</span><span class="detail-value">{{ request.repairDate }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('request.repairContent') }}</span><span class="detail-value">{{ request.repairContent }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('request.repairSolution') }}</span><span class="detail-value">{{ request.repairSolution }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('request.repairCost') }}</span><span class="detail-value font-medium">NT$ {{ request.repairCost?.toLocaleString() }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('request.repairPersonnel') }}</span><span class="detail-value">{{ request.repairPersonnel }}</span></div>
          <div class="detail-row"><span class="detail-label">{{ t('request.completionDate') }}</span><span class="detail-value font-medium text-emerald-700">{{ request.completionDate }}</span></div>
        </div>
      </div>

      <!-- Manager Repair Form: under_repair -->
      <div v-if="authStore.isManager && request.status === 'under_repair'" class="card p-5 border-2 border-amber-100">
        <h2 class="section-title text-amber-700"> 填寫維修資訊</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="form-label">{{ t('request.repairDate') }}</label>
            <input v-model="repairForm.repairDate" type="date" class="form-input" />
          </div>
          <div>
            <label class="form-label">{{ t('request.repairPersonnel') }}</label>
            <input v-model="repairForm.repairPersonnel" type="text" class="form-input" placeholder="維修人員或廠商名稱" />
          </div>
          <div class="sm:col-span-2">
            <label class="form-label">{{ t('request.repairContent') }}</label>
            <textarea v-model="repairForm.repairContent" rows="2" class="form-textarea" placeholder="詳細說明故障原因..."></textarea>
          </div>
          <div class="sm:col-span-2">
            <label class="form-label">{{ t('request.repairSolution') }}</label>
            <textarea v-model="repairForm.repairSolution" rows="2" class="form-textarea" placeholder="說明維修方案及處理方式..."></textarea>
          </div>
          <div>
            <label class="form-label">{{ t('request.repairCost') }} (NT$)</label>
            <input v-model.number="repairForm.repairCost" type="number" min="0" class="form-input" placeholder="0" />
          </div>
        </div>
        <div class="flex gap-3 mt-5">
          <button class="btn-secondary flex-1" @click="handleSaveRepair">
             {{ t('request.saveRepairInfo') }}
          </button>
          <button class="btn-success flex-1" @click="showCompleteModal = true">
             {{ t('request.markComplete') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Approve modal -->
    <ConfirmModal
      v-if="showApproveModal"
      :title="t('request.approveConfirmTitle')"
      :message="t('request.approveConfirmMsg')"
      :confirm-text="t('common.approve')"
      variant="success"
      show-input
      :input-label="t('request.reviewNote') + '（選填）'"
      :input-placeholder="'填寫審查備註（非必填）'"
      @confirm="handleApprove"
      @cancel="showApproveModal = false"
    />

    <!-- Reject modal -->
    <ConfirmModal
      v-if="showRejectModal"
      :title="t('request.rejectTitle')"
      :input-label="t('request.rejectReasonLabel')"
      :input-placeholder="t('request.rejectReasonPlaceholder')"
      :confirm-text="t('common.reject')"
      variant="danger"
      show-input
      require-input
      @confirm="handleReject"
      @cancel="showRejectModal = false"
    />

    <!-- Complete modal -->
    <ConfirmModal
      v-if="showCompleteModal"
      :title="t('request.completeConfirmTitle')"
      :message="t('request.completeConfirmMsg')"
      :confirm-text="t('request.markComplete')"
      variant="success"
      @confirm="handleComplete"
      @cancel="showCompleteModal = false"
    />

    <!-- Image preview -->
    <Teleport to="body">
      <div
        v-if="previewImage"
        class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
        @click="previewImage = null"
      >
        <img :src="previewImage" class="max-w-full max-h-full rounded-xl object-contain" />
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAssetsStore } from '@/stores/assets'
import { useRequestsStore } from '@/stores/requests'
// import { mockUsers } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { useI18n } from '@/composables/useI18n'
import StatusBadge from '@/components/common/StatusBadge.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const assetsStore = useAssetsStore()
const requestsStore = useRequestsStore()
const notifStore = useNotificationsStore()
const { t } = useI18n()


const requestId = computed(() => route.params.id)
const request = ref(null)
const loading = ref(true)
const error = ref(null)

const showApproveModal = ref(false)
const showRejectModal  = ref(false)
const showCompleteModal = ref(false)
const previewImage = ref(null)

const repairForm = ref({
  repairDate: '',
  repairContent: '',
  repairSolution: '',
  repairCost: null,
  repairPersonnel: '',
})


onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    request.value = await requestsStore.fetchById(requestId.value)
    repairForm.value = {
      repairDate: request.value.repairDate || '',
      repairContent: request.value.repairContent || '',
      repairSolution: request.value.repairSolution || '',
      repairCost: request.value.repairCost || null,
      repairPersonnel: request.value.repairPersonnel || '',
    }
  } catch (e) {
    error.value = e.message || '載入失敗'
  } finally {
    loading.value = false
  }
})

function handleApprove(note) {
  requestsStore.approve(requestId.value, authStore.currentUser.id, note)
  showApproveModal.value = false
  notifStore.add(t('request.approveSuccess'), 'success')
}

function handleReject(reason) {
  requestsStore.reject(requestId.value, authStore.currentUser.id, reason)
  showRejectModal.value = false
  notifStore.add(t('request.rejectSuccess'), 'warning')
}

function handleSaveRepair() {
  requestsStore.updateRepairDetails(requestId.value, { ...repairForm.value })
  notifStore.add(t('request.repairSaved'), 'success')
}

async function handleComplete() {
  requestsStore.updateRepairDetails(requestId.value, { ...repairForm.value })
  await requestsStore.complete(requestId.value, { ...repairForm.value })
  showCompleteModal.value = false
  notifStore.add(t('request.completeSuccess'), 'success')
}

function getAssetName(assetId) {
  return assetsStore.getById(assetId)?.name || assetId
}

function getAssetNumber(assetId) {
  return assetsStore.getById(assetId)?.assetNumber || ''
}

// function getUserName(userId) {
//   return mockUsers.find((u) => u.id === userId)?.name || userId
// }

function stepDotClass(status) {
  const map = {
    done:     'bg-emerald-500 border-emerald-500 text-white',
    current:  'bg-amber-400 border-amber-400 text-white',
    pending:  'bg-white border-gray-300 text-gray-400',
    rejected: 'bg-red-500 border-red-500 text-white',
  }
  return map[status] || 'bg-white border-gray-300 text-gray-400'
}

const timelineSteps = computed(() => {
  const req = request.value
  if (!req) return []

  const steps = [
    {
      label: t('request.workflow.submitted'),
      date: req.requestDate,
      desc: `申請人：${getUserName(req.requesterId)}`,
      status: 'done',
      icon: '',
      note: null,
    },
  ]

  if (req.status === 'pending') {
    steps.push({
      label: t('request.workflow.reviewing'),
      date: null,
      desc: '等待管理人員審查',
      status: 'pending',
      icon: '',
      note: null,
    })
    return steps
  }

  if (req.status === 'rejected') {
    steps.push({
      label: t('request.workflow.rejected'),
      date: req.reviewDate,
      desc: `審查人員：${getUserName(req.reviewerId)}`,
      status: 'rejected',
      icon: '',
      note: req.reviewNote,
    })
    return steps
  }

  // Approved path
  steps.push({
    label: t('request.workflow.approved'),
    date: req.reviewDate,
    desc: `審查人員：${getUserName(req.reviewerId)}`,
    status: 'done',
    icon: '',
    note: req.reviewNote,
  })

  if (req.status === 'under_repair') {
    steps.push({
      label: t('request.workflow.repairing'),
      date: req.repairDate || null,
      desc: req.repairPersonnel ? `維修人員：${req.repairPersonnel}` : '維修進行中',
      status: 'current',
      icon: '',
      note: null,
    })
  } else if (req.status === 'completed') {
    steps.push({
      label: t('request.workflow.repairing'),
      date: req.repairDate,
      desc: `維修人員：${req.repairPersonnel}`,
      status: 'done',
      icon: '',
      note: null,
    })
    steps.push({
      label: t('request.workflow.completed'),
      date: req.completionDate,
      desc: '維修已完成，資產恢復正常使用',
      status: 'done',
      icon: '',
      note: null,
    })
  }

  return steps
})
</script>
