// 編輯維修申請單
async function editRepairRequest(formId, payload, token) {
  const id = String(formId).replace(/[^\d]/g, '')
  const res = await fetch(`/maintenance-api/edit/form/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token || localStorage.getItem('ams_token') || '',
    },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error('API error')
  return await res.json()
}
import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useAssetsStore } from './assets'
import { useAuthStore } from './auth'

// API base url
// 若要走 8002（maintenance），請設 '/maintenance-api'
const API_BASE = '/maintenance-api'
  // 送出維修申請
  async function createRequest(payload) {
    // 確保 attachments 欄位存在
    const reqBody = {
      ...payload,
      attachments: payload.attachments !== undefined ? payload.attachments : '',
    }
    const res = await fetch(`${API_BASE}/forms`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': localStorage.getItem('ams_token') || '',
      },
      body: JSON.stringify(reqBody),
    })
    if (!res.ok) throw new Error('API error')
    return await res.json()
  }
  // 刪除維修單
  async function deleteRequest(formId) {
    const id = formId.replace(/[^\d]/g, '')
    const res = await fetch(`${API_BASE}/form/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': localStorage.getItem('ams_token') || '',
      },
    })
    if (res.status === 200) return {}
    if (res.status === 404) throw new Error('Form not found')
    const data = await res.json()
    throw new Error(data.error || 'API error')
  }

  // 送出維修申請
  async function submitRepairRequest({ idEquipment, issue_description, attachments = '' }, token) {
    const res = await fetch('/maintenance-api/form', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token || localStorage.getItem('ams_token') || '',
      },
      body: JSON.stringify({ idEquipment, issue_description, attachments }),
    })
    if (!res.ok) throw new Error('API error')
    return await res.json()
  }

export const useRequestsStore = defineStore('requests', () => {
  // 所有資料都從 API 取得
  const requests = ref([])

  function getAll() {
    return requests.value
  }

  function getById(id) {
    return requests.value.find((r) => r.id === id) || null
  }

  async function fetchAll(token) {
    const auth = token || localStorage.getItem('ams_token') || ''
    const res = await fetch(`${API_BASE}/forms`, {
      headers: {
        'Authorization': auth,
      },
    })
    if (!res.ok) throw new Error('API error')
    const data = await res.json()
    const authStore = useAuthStore()
    const userId = authStore.currentUser?.id || null
    let items = data.items.map(mapApiToRequest)
    // 一般 user 只顯示自己的申請單
    if (!authStore.isManager && userId) {
      items = items.filter(item => item.requesterId === `U${userId}`)
    }
    requests.value = items
    return requests.value
  }

  async function fetchById(id) {
    const formId = id.replace(/[^\d]/g, '')
    // 統一從 localStorage.getItem('ams_token') 取得 Bearer ...
    const token = localStorage.getItem('ams_token') || ''
    const res = await fetch(`${API_BASE}/form/${formId}`, {
      headers: {
        'Authorization': token,
      },
    })
    if (!res.ok) throw new Error('API error')
    const data = await res.json()
    return mapApiToRequest(data)
  }
  //審核
  async function reviewRequest(formId, { status, note }) {
    const body = note ? { status, note } : { status }
    const res = await fetch(`${API_BASE}/review/${formId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': localStorage.getItem('ams_token') || '',
      },
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error('API error')
    return await res.json()
  }
  //完成
  async function completeRequest(formId, payload) {
    const id = formId.replace(/[^\d]/g, '')
    // 將前端欄位轉換為後端 API 需要的格式
    const apiPayload = {
      repair_description: payload.repairContent,
      repair_solution: payload.repairSolution,
      repair_cost: payload.repairCost,
      repair_vendor: payload.repairPersonnel,
      repair_person: payload.repairPerson || '',
    }
    // 這裡加 log
    console.log('completeRequest id', id)
    console.log('completeRequest payload', apiPayload)

    const res = await fetch(`${API_BASE}/complete/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': localStorage.getItem('ams_token') || '',
      },
      body: JSON.stringify(apiPayload),
    })
    if (!res.ok) throw new Error('API error')
    return await res.json()
  }

  // 編輯維修單
  async function editRequest(formId, payload) {
    const id = formId.replace(/[^\d]/g, '')
    const res = await fetch(`${API_BASE}/edit/form/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': localStorage.getItem('ams_token') || '',
      },
      body: JSON.stringify(payload),
    })
    if (res.status === 200) return await res.json()
    if (res.status === 404) throw new Error('Form not found')
    const data = await res.json()
    throw new Error(data.error || 'API error')
  }

  function mapApiToRequest(item) {
    return {
      id: item.idForm ? `REQ-${item.idForm}` : '',
      assetId: item.idEquipment ? `A${item.idEquipment}` : '',
      requesterId: item.applicant_id ? `U${item.applicant_id}` : '',
      faultDescription: item.issue_description,
      status: item.status,
      requestDate: item.requestDate,
      reviewerId: item.reviewer_id ? `U${item.reviewer_id}` : null,
      reviewDate: item.review_date,
      reviewNote: item.reviewNote,
      repairDate: item.repair_start_date,
      repairContent: item.repair_description,
      repairSolution: item.repair_solution,
      repairCost: item.repair_cost,
      repairPersonnel: item.repair_person,
      completionDate: item.repair_end_date,
      attachments: [],
    }
  }

  function getByRequesterId(requesterId) {
    return requests.value.filter((r) => r.requesterId === requesterId)
  }

  function getUserName(userId) {
    // 目前沒有 users 資料，直接回傳 ownerId
    return userId
  }

  return {
    requests,
    getAll,
    getById,
    fetchAll,
    fetchById,
    getByRequesterId,
    getUserName,
    createRequest,
    deleteRequest,
    editRequest,
    reviewRequest,
    completeRequest,
    submitRepairRequest,
    editRepairRequest,
  }
})