import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useAssetsStore } from './assets'
import { useAuthStore } from './auth'
import { useI18n } from '@/composables/useI18n'

const API_BASE = '/maintenance-api'
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']

function authHeaders(token) {
  return {
    'Authorization': token || localStorage.getItem('ams_token') || '',
  }
}

async function readError(res, fallback) {
  const data = await res.json().catch(async () => {
    const text = await res.text().catch(() => '')
    return text ? { error: text } : {}
  })
  return data.error || data.message || fallback
}

function normalizeFormId(id) {
  return String(id || '').replace(/[^\d]/g, '')
}

function normalizeAssetId(id) {
  if (id == null) return ''
  if (typeof id === 'number') return String(id)
  if (/^\d+$/.test(String(id))) return String(id)
  return ''
}

function attachmentIdFrom(value) {
  if (!value) return ''
  if (Array.isArray(value)) {
    const first = value[0]
    return first?.id || first?.imageId || first?.attachmentId || first?.data || ''
  }
  return String(value).trim().split(/\s+/)[0] || ''
}

async function mapAttachmentToImage(attachmentId, fallbackName = 'attachment') {
  if (!attachmentId) return null
  try {
    const { readUrl } = await getImageReadUrl(attachmentId)
    return {
      id: attachmentId,
      imageId: attachmentId,
      name: fallbackName,
      data: readUrl,
      url: readUrl,
    }
  } catch (error) {
    console.error('讀取附件圖片失敗', error)
    return {
      id: attachmentId,
      imageId: attachmentId,
      name: fallbackName,
      data: '',
      url: '',
      error: true,
    }
  }
}

async function createImageUploadUrl(fileName, contentType, token) {
  const res = await fetch(`${API_BASE}/images/upload-url`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(token),
    },
    body: JSON.stringify({ fileName, contentType }),
  })
  if (!res.ok) throw new Error(await readError(res, '建立圖片上傳連結失敗'))
  return await res.json()
}

async function uploadImageToS3(file, token) {
  if (!file) return ''
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    throw new Error('僅支援 JPG、PNG、WEBP、GIF 圖片')
  }

  const { imageId, uploadUrl } = await createImageUploadUrl(file.name, file.type, token)
  const uploadRes = await fetch(uploadUrl, {
    method: 'PUT',
    headers: {
      'Content-Type': file.type,
    },
    body: file,
  })

  if (!uploadRes.ok) throw new Error('圖片上傳到 S3 失敗')
  return imageId
}

async function getImageReadUrl(imageId, token) {
  const res = await fetch(`${API_BASE}/images/upload-url/${imageId}`, {
    headers: authHeaders(token),
  })
  if (!res.ok) throw new Error(await readError(res, '取得圖片讀取連結失敗'))
  return await res.json()
}

export const useRequestsStore = defineStore('requests', () => {
  const { t } = useI18n()
  const requests = ref([])

  function getAll() {
    return requests.value
  }

  function getById(id) {
    return requests.value.find((r) => r.id === id) || null
  }

  async function createRequest(payload) {
    const attachmentImageId = payload.attachmentFile
      ? await uploadImageToS3(payload.attachmentFile)
      : attachmentIdFrom(payload.attachments)

    const reqBody = {
      idEquipment: normalizeAssetId(payload.idEquipment || payload.assetId),
      issue_description: payload.issue_description || payload.faultDescription,
      attachments: attachmentImageId,
    }

    const res = await fetch(`${API_BASE}/form`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify(reqBody),
    })
    if (!res.ok) throw new Error(await readError(res, t('common.apiError')))
    return await res.json()
  }

  async function fetchAll(token) {
    const res = await fetch(`${API_BASE}/forms`, {
      headers: authHeaders(token),
    })
    if (!res.ok) throw new Error(t('common.apiError'))

    const data = await res.json()
    const authStore = useAuthStore()
    const userId = authStore.currentUser?.id || null
    let items = (data.items || []).map(mapApiToRequest)

    if (!authStore.isManager && userId) {
      items = items.filter(item => item.requesterId === `U${userId}`)
    }

    requests.value = items
    return requests.value
  }

  async function fetchById(id) {
    const formId = normalizeFormId(id)
    const res = await fetch(`${API_BASE}/form/${formId}`, {
      headers: authHeaders(),
    })
    if (!res.ok) throw new Error(t('common.apiError'))

    const data = await res.json()
    const request = mapApiToRequest(data)
    const attachmentId = attachmentIdFrom(data.attachments)
    request.attachments = attachmentId ? [await mapAttachmentToImage(attachmentId, data.fileName || 'attachment')] : []
    return {
      ...data,
      ...request,
      attachmentId,
      reviewerName: data.reviewerName || '',
    }
  }

  async function reviewRequest(formId, { status, reviewNote, note }) {
    const authStore = useAuthStore()
    let reviewer_id = authStore.currentUser?.idUser || authStore.currentUser?.id
    if (typeof reviewer_id === 'string') {
      const match = reviewer_id.match(/(\d+)/)
      reviewer_id = match ? Number(match[1]) : undefined
    }

    const body = { status }
    const finalNote = reviewNote ?? note
    if (finalNote) body.reviewNote = finalNote
    if (typeof reviewer_id === 'number' && !isNaN(reviewer_id)) body.reviewer_id = reviewer_id

    const res = await fetch(`${API_BASE}/review/${normalizeFormId(formId)}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error(await readError(res, t('common.apiError')))

    const data = await res.json()
    if (data.status === 'approved' && data.idEquipment) {
      try {
        const assetsStore = useAssetsStore()
        await assetsStore.setAssetStatusRepairing(data.idEquipment, localStorage.getItem('ams_token') || '')
      } catch (e) {
        console.error('自動設資產狀態為 repairing 失敗', e)
      }
    }
    return data
  }

  async function sendRepairOnly(formId, repairForm = {}, token) {
    const id = normalizeFormId(formId)
    if (!id) throw new Error(t('request.invalidFormId'))

    const payload = {
      repair_description: repairForm?.repairContent || '',
      repair_solution: repairForm?.repairSolution || '',
      repair_cost: typeof repairForm?.repairCost === 'number' && !isNaN(repairForm.repairCost)
        ? repairForm.repairCost
        : 0,
      repair_vendor: repairForm?.repairPersonnel || '',
      repair_person: repairForm?.repairPersonnel || '',
    }

    const res = await fetch(`${API_BASE}/repair/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(token),
      },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error(await readError(res, t('common.apiError')))
    return await res.json()
  }

  async function completeRequest(formId, payload) {
    const apiPayload = {
      repair_description: payload.repairContent,
      repair_solution: payload.repairSolution,
      repair_cost: payload.repairCost,
      repair_vendor: payload.repairPersonnel,
      repair_person: payload.repairPerson || payload.repairPersonnel || '',
    }

    const res = await fetch(`${API_BASE}/complete/${normalizeFormId(formId)}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify(apiPayload),
    })
    if (!res.ok) throw new Error(await readError(res, t('common.apiError')))
    return await res.json()
  }

  async function editRequest(formId, payload) {
    const id = normalizeFormId(formId)
    if (!id) throw new Error(t('request.invalidFormId'))
    const nextPayload = {}
    if (typeof payload.issue_description === 'string') {
      nextPayload.issue_description = payload.issue_description
    }
    if (payload.attachmentFile) {
      nextPayload.attachments = await uploadImageToS3(payload.attachmentFile)
    } else if (Array.isArray(payload.attachments)) {
      nextPayload.attachments = attachmentIdFrom(payload.attachments)
    } else if (payload.attachments !== undefined && payload.attachments !== payload.originalAttachments) {
      nextPayload.attachments = attachmentIdFrom(payload.attachments)
    }

    const res = await fetch(`${API_BASE}/edit/form/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify(nextPayload),
    })
    if (res.status === 200) return await res.json()
    if (res.status === 404) throw new Error(t('request.notFound'))
    throw new Error(await readError(res, t('common.apiError')))
  }

  async function editRepairRequest(formId, payload, token) {
    const id = normalizeFormId(formId)
    if (!id) throw new Error(t('request.invalidFormId'))
    const nextPayload = {}
    if (typeof payload.issue_description === 'string') {
      nextPayload.issue_description = payload.issue_description
    }
    if (payload.attachmentFile) {
      nextPayload.attachments = await uploadImageToS3(payload.attachmentFile, token)
    } else if (Array.isArray(payload.attachments)) {
      nextPayload.attachments = attachmentIdFrom(payload.attachments)
    } else if (payload.attachments !== undefined && payload.attachments !== payload.originalAttachments) {
      nextPayload.attachments = attachmentIdFrom(payload.attachments)
    }

    const res = await fetch(`${API_BASE}/edit/form/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(token),
      },
      body: JSON.stringify(nextPayload),
    })
    if (res.status === 200) return await res.json()
    if (res.status === 404) throw new Error(t('request.notFound'))
    throw new Error(await readError(res, t('common.apiError')))
  }

  async function submitRepairRequest({ idEquipment, issue_description, attachments = '', repair_cost = 0, repair_description = '', repair_solution = '', repair_vendor = '', repair_person = '' }, token) {
    const res = await fetch(`${API_BASE}/repair/${idEquipment}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(token),
      },
      body: JSON.stringify({
        idEquipment,
        issue_description,
        attachments,
        repair_cost: repair_cost ?? 0,
        repair_description,
        repair_solution,
        repair_vendor,
        repair_person,
      }),
    })
    if (!res.ok) throw new Error(await readError(res, t('common.apiError')))
    return await res.json()
  }

  function mapApiToRequest(item) {
    const attachmentId = attachmentIdFrom(item.attachments)
    return {
      id: item.idForm ? `REQ-${item.idForm}` : item.id || '',
      assetId: item.idEquipment ? `A${item.idEquipment}` : item.assetId || '',
      idEquipment: item.idEquipment || null,
      requesterId: item.applicant_id ? `U${item.applicant_id}` : item.requesterId || '',
      applicant_id: item.applicant_id,
      faultDescription: item.issue_description || item.faultDescription || '',
      status: item.status,
      requestDate: item.requestDate,
      reviewerId: item.reviewer_id ? `U${item.reviewer_id}` : item.reviewerId || null,
      reviewDate: item.review_date || item.reviewDate,
      reviewNote: item.reviewNote,
      repairDate: item.repair_start_date || item.repairDate,
      repairContent: item.repair_description || item.repairContent,
      repairSolution: item.repair_solution || item.repairSolution,
      repairCost: item.repair_cost || item.repairCost,
      repairPersonnel: item.repair_person || item.repairPersonnel,
      completionDate: item.repair_end_date || item.completionDate,
      attachmentId,
      attachments: [],
    }
  }

  function getByRequesterId(requesterId) {
    return requests.value.filter((r) => r.requesterId === requesterId)
  }

  function getUserName(userId) {
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
    editRequest,
    editRepairRequest,
    reviewRequest,
    completeRequest,
    submitRepairRequest,
    sendRepairOnly,
    createImageUploadUrl,
    uploadImageToS3,
    getImageReadUrl,
  }
})
