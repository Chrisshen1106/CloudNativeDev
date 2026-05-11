import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useAssetsStore } from './assets'

// API base url
const API_BASE = '/maintenance-api'

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

  async function fetchByRequesterId(requesterId) {
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

  function mapApiToRequest(item) {
    return {
      id: item.idForm ? `REQ-${item.idForm}` : '',
      assetId: item.idEquipment ? `A${item.idEquipment}` : '',
      requesterId: item.applicant_id ? `U${item.applicant_id}` : '',
      faultDescription: item.issue_description,
      status: item.status,
      requestDate: item.requestDate,
      reviewerId: item.reviewer_id ? `U${item.reviewer_id}` : null,
      reviewDate: null,
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
  }
})