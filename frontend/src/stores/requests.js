  async function fetchById(id) {
    // 只取數字部分
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
import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useAssetsStore } from './assets'

// API base url
const API_BASE = '/maintenance-api'

const STORAGE_KEY = 'ams_requests'

const defaultRequests = [
  {
    id: 'REQ-2024-001',
    assetId: 'A002',
    requesterId: 'U001',
    faultDescription: '手機螢幕出現豎條紋，嚴重影響工作效率，無法正常顯示內容。問題發生於三天前，且情況持續惡化。',
    status: 'under_repair',
    requestDate: '2024-03-01',
    attachments: [],
    reviewerId: 'U004',
    reviewDate: '2024-03-02',
    reviewNote: '問題屬實，同意送修，請儘速安排。',
    repairDate: '2024-03-05',
    repairContent: '螢幕模組損壞，導致部分顯示異常及豎條紋',
    repairSolution: '更換螢幕模組，並進行整體功能測試',
    repairCost: 8500,
    repairPersonnel: 'Apple 官方授權維修中心',
    completionDate: null,
  },
  {
    id: 'REQ-2024-002',
    assetId: 'A008',
    requesterId: 'U002',
    faultDescription: '手機電池膨脹，充電後電量下降速度異常快速，一小時內從100%降至30%。',
    status: 'pending',
    requestDate: '2024-03-15',
    attachments: [],
    reviewerId: null,
    reviewDate: null,
    reviewNote: null,
    repairDate: null,
    repairContent: null,
    repairSolution: null,
    repairCost: null,
    repairPersonnel: null,
    completionDate: null,
  },
  {
    id: 'REQ-2024-003',
    assetId: 'A001',
    requesterId: 'U001',
    faultDescription: 'MacBook 鍵盤按鍵失靈，A 鍵和 S 鍵無法正常輸入，嚴重影響日常工作。',
    status: 'completed',
    requestDate: '2024-02-10',
    attachments: [],
    reviewerId: 'U005',
    reviewDate: '2024-02-11',
    reviewNote: '已確認問題，安排送修。',
    repairDate: '2024-02-13',
    repairContent: '鍵盤按鍵機械結構損壞，按下無法回彈',
    repairSolution: '更換整片鍵盤模組',
    repairCost: 3500,
    repairPersonnel: 'Apple 授權維修中心',
    completionDate: '2024-02-20',
  },
  {
    id: 'REQ-2024-004',
    assetId: 'A003',
    requesterId: 'U002',
    faultDescription: 'iPad 觸控螢幕右側約三分之一區域失靈，無法正常觸控操作。',
    status: 'rejected',
    requestDate: '2024-03-05',
    attachments: [],
    reviewerId: 'U004',
    reviewDate: '2024-03-06',
    reviewNote: '此設備保固已於上月到期，建議使用者自行聯繫原廠維修，或提出設備報廢申請。',
    repairDate: null,
    repairContent: null,
    repairSolution: null,
    repairCost: null,
    repairPersonnel: null,
    completionDate: null,
  },
  {
    id: 'REQ-2024-005',
    assetId: 'A004',
    requesterId: 'U002',
    faultDescription: '電腦散熱風扇發出異常聲音，且機身過熱，影響效能表現。',
    status: 'under_repair',
    requestDate: '2024-03-18',
    attachments: [],
    reviewerId: 'U005',
    reviewDate: '2024-03-19',
    reviewNote: '問題屬實，立即安排維修以避免進一步損壞。',
    repairDate: '2024-03-20',
    repairContent: '散熱風扇積塵嚴重，風扇軸承磨損損壞',
    repairSolution: '清潔散熱系統，更換風扇模組',
    repairCost: 2000,
    repairPersonnel: '戴爾授權維修工程師 - 林師傅',
    completionDate: null,
  },
  {
    id: 'REQ-2024-006',
    assetId: 'A005',
    requesterId: 'U003',
    faultDescription: '手機後置主鏡頭故障，無法對焦，拍攝的照片完全模糊，影響業務需求。',
    status: 'pending',
    requestDate: '2024-03-20',
    attachments: [],
    reviewerId: null,
    reviewDate: null,
    reviewNote: null,
    repairDate: null,
    repairContent: null,
    repairSolution: null,
    repairCost: null,
    repairPersonnel: null,
    completionDate: null,
  },
  {
    id: 'REQ-2024-007',
    assetId: 'A007',
    requesterId: 'U001',
    faultDescription: 'MacBook Air 充電線外皮破損，金屬線外露，有安全疑慮且無法穩定充電。',
    status: 'completed',
    requestDate: '2024-01-25',
    attachments: [],
    reviewerId: 'U004',
    reviewDate: '2024-01-25',
    reviewNote: '確認配件損壞，立即更換，注意安全。',
    repairDate: '2024-01-26',
    repairContent: 'MagSafe 充電線外皮破損，造成間歇性充電中斷',
    repairSolution: '更換原廠充電線',
    repairCost: 1200,
    repairPersonnel: '資產管理部內部處理',
    completionDate: '2024-01-26',
  },
  {
    id: 'REQ-2024-008',
    assetId: 'A006',
    requesterId: 'U003',
    faultDescription: 'Surface Pro 磁吸式鍵盤接觸不良，連接後有時無法正常使用，需反覆重新接插。',
    status: 'pending',
    requestDate: '2024-03-22',
    attachments: [],
    reviewerId: null,
    reviewDate: null,
    reviewNote: null,
    repairDate: null,
    repairContent: null,
    repairSolution: null,
    repairCost: null,
    repairPersonnel: null,
    completionDate: null,
  },
]

export const useRequestsStore = defineStore('requests', () => {
  const saved = localStorage.getItem(STORAGE_KEY)
  const requests = ref(saved ? JSON.parse(saved) : defaultRequests)

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(requests.value))
  }


  async function fetchAll() {
    // 取得所有申請單（管理者）
    const res = await fetch(`${API_BASE}/api/forms/`, {
      headers: {
        'Authorization': localStorage.getItem('token') ? `Bearer ${localStorage.getItem('token')}` : undefined,
      },
    })
    if (!res.ok) throw new Error('API error')
    const data = await res.json()
    return data.items.map(mapApiToRequest)
  }

  async function fetchByRequesterId(requesterId) {
    // 取得自己的申請單（員工）
    const res = await fetch(`${API_BASE}/api/forms/`, {
      headers: {
        'Authorization': localStorage.getItem('token') ? `Bearer ${localStorage.getItem('token')}` : undefined,
      },
    })
    if (!res.ok) throw new Error('API error')
    const data = await res.json()
    // 後端會自動只回傳自己的單
    return data.items.map(mapApiToRequest)
  }

  // 將 API 回傳欄位轉換成前端格式
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

  function getByAssetId(assetId) {
    return requests.value.filter((r) => r.assetId === assetId)
  }

  function add(requestData) {
    const year = new Date().getFullYear()
    const maxNum = requests.value.reduce((max, r) => {
      const m = r.id.match(/REQ-\d{4}-(\d+)/)
      if (m) {
        const n = parseInt(m[1], 10)
        return n > max ? n : max
      }
      return max
    }, 0)
    const id = `REQ-${year}-${String(maxNum + 1).padStart(3, '0')}`
    const newReq = {
      id,
      status: 'pending',
      requestDate: new Date().toISOString().split('T')[0],
      reviewerId: null,
      reviewDate: null,
      reviewNote: null,
      repairDate: null,
      repairContent: null,
      repairSolution: null,
      repairCost: null,
      repairPersonnel: null,
      completionDate: null,
      attachments: [],
      ...requestData,
    }
    requests.value.push(newReq)
    persist()
    return newReq
  }


  async function approve(requestId, reviewerId, reviewNote) {
    // 取得 form_id
    const formId = requestId.replace(/[^\d]/g, '')
    try {
      const res = await fetch(`${API_BASE}/review/${formId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: 'approved' })
      })
      if (!res.ok) throw new Error('API error')
      const data = await res.json()
      // 更新本地資料
      const req = requests.value.find((r) => r.id === requestId)
      if (req) {
        req.status = 'under_repair'
        req.reviewerId = reviewerId
        req.reviewDate = new Date().toISOString().split('T')[0]
        req.reviewNote = reviewNote || ''
        persist()
        const assetsStore = useAssetsStore()
        assetsStore.updateStatus(req.assetId, 'under_repair')
      }
      return true
    } catch (e) {
      console.error('approve error', e)
      return false
    }
  }

  async function reject(requestId, reviewerId, reviewNote) {
    const formId = requestId.replace(/[^\d]/g, '')
    try {
      const res = await fetch(`${API_BASE}/review/${formId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: 'rejected' })
      })
      if (!res.ok) throw new Error('API error')
      const data = await res.json()
      // 更新本地資料
      const req = requests.value.find((r) => r.id === requestId)
      if (req) {
        req.status = 'rejected'
        req.reviewerId = reviewerId
        req.reviewDate = new Date().toISOString().split('T')[0]
        req.reviewNote = reviewNote || ''
        persist()
      }
      return true
    } catch (e) {
      console.error('reject error', e)
      return false
    }
  }

  function updateRepairDetails(requestId, repairData) {
    const req = requests.value.find((r) => r.id === requestId)
    if (!req) return false
    Object.assign(req, repairData)
    persist()
    return true
  }

  async function complete(requestId, repairData) {
    const formId = requestId.replace(/[^\d]/g, '')
    try {
      const res = await fetch(`${API_BASE}/complete/${formId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repair_description: repairData.repairContent,
          repair_solution: repairData.repairSolution,
          repair_cost: repairData.repairCost,
          repair_vendor: repairData.repairPersonnel,
          repair_person: repairData.repairPersonnel,
        })
      })
      if (!res.ok) throw new Error('API error')
      const data = await res.json()
      // 更新本地資料
      const req = requests.value.find((r) => r.id === requestId)
      if (req) {
        req.status = 'completed'
        req.completionDate = new Date().toISOString().split('T')[0]
        Object.assign(req, repairData)
        persist()
        const assetsStore = useAssetsStore()
        assetsStore.updateStatus(req.assetId, 'normal')
      }
      return true
    } catch (e) {
      console.error('complete error', e)
      return false
    }
  }

  function resetToDefault() {
    requests.value = JSON.parse(JSON.stringify(defaultRequests))
    persist()
  }

  return {
    requests,
    getAll,
    getById,
    getByRequesterId,
    getByAssetId,
    add,
    approve,
    reject,
    updateRepairDetails,
    complete,
    resetToDefault,
    fetchById,
  }
})
