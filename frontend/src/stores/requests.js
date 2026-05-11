import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useAssetsStore } from './assets'

// API base url
// 若要走 8002（maintenance），請設 '/maintenance-api'
const API_BASE = 'http://localhost:8002'
  // 送出維修申請
  async function createRequest(payload) {
    const res = await fetch(`${API_BASE}/api/form`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': localStorage.getItem('token') ? `Bearer ${localStorage.getItem('token')}` : undefined,
      },
      body: JSON.stringify(payload),
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

  async function fetchAll() {
    const res = await fetch(`${API_BASE}/api/forms/`, {
      headers: {
        'Authorization': localStorage.getItem('token') ? `Bearer ${localStorage.getItem('token')}` : undefined,
      },
    })
    if (!res.ok) throw new Error('API error')
    const data = await res.json()
    requests.value = data.items.map(mapApiToRequest)
    return requests.value
  }

  async function fetchById(id) {
    const formId = id.replace(/[^\d]/g, '')
    const res = await fetch(`${API_BASE}/api/form/${formId}`, {
      headers: {
        'Authorization': localStorage.getItem('token') ? `Bearer ${localStorage.getItem('token')}` : undefined,
      },
    })
    if (!res.ok) throw new Error('API error')
    const data = await res.json()
    return mapApiToRequest(data)
  }

  async function reviewRequest(formId, status) {
    const res = await fetch(`${API_BASE}/api/review/${formId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': localStorage.getItem('token') ? `Bearer ${localStorage.getItem('token')}` : undefined,
      },
      body: JSON.stringify({ status }),
    })
    if (!res.ok) throw new Error('API error')
    return await res.json()
  }

  async function completeRequest(formId, payload) {
    const res = await fetch(`${API_BASE}/api/complete/${formId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': localStorage.getItem('token') ? `Bearer ${localStorage.getItem('token')}` : undefined,
      },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error('API error')
    return await res.json()
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
    fetchByRequesterId,
    getByRequesterId,
    getUserName,
    createRequest,
  }
})