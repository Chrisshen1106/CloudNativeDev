  // 刪除資產
  async function deleteAsset(id, token) {
    // 只傳純數字 id
    if (typeof id === 'string') {
      const match = id.match(/(\d+)/)
      if (match) id = match[1]
    }
    const res = await fetch(`${API_BASE}/assets/${id}`, {
      method: 'DELETE',
      headers: {
        ...(token ? { 'Authorization': token } : {})
      }
    })
    if (!res.ok) throw new Error('刪除資產失敗')
    // 刪除本地 assets 資料
    const idx = assets.value.findIndex(a => String(a.id).replace(/\D/g, '') === String(id))
    if (idx !== -1) {
      assets.value.splice(idx, 1)
      persist()
    }
    return true
  }
import { ref } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'ams_assets'
const API_BASE = '/user-api'

export const useAssetsStore = defineStore('assets', () => {
  const assets = ref([])

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(assets.value))
  }

  function getAll() {
    return assets.value
  }

  function getById(id) {
    return assets.value.find((a) => a.id === id) || null
  }

  function getByOwnerId(ownerId) {
    return assets.value.filter((a) => String(a.ownerId) === String(ownerId))
  }

  function add(assetData) {
    const maxNum = assets.value.reduce((max, a) => {
      const n = parseInt(a.id.replace('A', ''), 10)
      return n > max ? n : max
    }, 0)
    const id = 'A' + String(maxNum + 1).padStart(3, '0')
    const year = new Date().getFullYear()
    const assetNumber = `AST-${year}-${String(maxNum + 1).padStart(3, '0')}`
    const newAsset = { id, assetNumber, ...assetData }
    assets.value.push(newAsset)
    persist()
    return newAsset
  }

  function update(id, assetData) {
    const idx = assets.value.findIndex((a) => a.id === id)
    if (idx !== -1) {
      assets.value[idx] = { ...assets.value[idx], ...assetData }
      persist()
      return assets.value[idx]
    }
    return null
  }

  // 抓那個人的資產
  async function fetchUserAssets(token, page = 1, pageSize = 20) {
    const res = await fetch(`${API_BASE}/user?page=${page}&pageSize=${pageSize}`, {
      headers: {
        'Authorization': token
      }
    })
    if (!res.ok) throw new Error('取得資產失敗')
    const data = await res.json()
    console.log('API 回傳 data:', data)
    assets.value = data.items.map(item => ({
      id: item.assetNumber,
      assetNumber: item.assetNumber,
      idEquipment: item.idEquipment || item.id || null, // 保留資料庫主鍵
      name: item.name || '',
      category: item.category || '',
      model: item.model || '',
      location: item.location || '',
      ownerId: item.idOwner || item.ownerId || '',
      department: item.department || '',
      status: item.status || '',
      ...item
    }))
    persist()
    // 回傳 API 分頁資訊
    return {
      total: data.total,
      page: data.page,
      pageSize: data.pageSize,
      items: assets.value
    }
  }

  // 取得資產詳情（支援 assetNumber 查詢）
  async function getAssetDetail(idOrAssetNumber, token) {
    let id = idOrAssetNumber
    // 如果傳進來的是 assetNumber，先找出主鍵 id
    if (typeof idOrAssetNumber === 'string' && !/^[0-9]+$/.test(idOrAssetNumber)) {
      const found = assets.value.find(a => a.assetNumber === idOrAssetNumber)
      if (found) id = found.id
    }
    const res = await fetch(`${API_BASE}/assets/${id}`, {
      headers: token ? { 'Authorization': token } : {}
    })
    if (!res.ok) throw new Error('取得資產詳情失敗')
    const data = await res.json()
    return data
  }
  
  // 編輯資產（支援 assetNumber 查詢）
  async function updateAsset(idOrAssetNumber, assetData, token) {
    let id = idOrAssetNumber
    // 如果傳進來的是 assetNumber，先找出主鍵 id
    if (typeof idOrAssetNumber === 'string' && !/^[0-9]+$/.test(idOrAssetNumber)) {
      const found = assets.value.find(a => a.assetNumber === idOrAssetNumber)
      if (found) id = found.id
    }
    // 如果 id 是純數字字串，轉成數字
    if (typeof id === 'string' && /^[0-9]+$/.test(id)) {
      id = parseInt(id, 10)
    }
    const res = await fetch(`${API_BASE}/assets/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': token } : {})
      },
      body: JSON.stringify(assetData)
    })
    if (!res.ok) throw new Error('資產更新失敗')
    return await res.json()
  }

  // 新增資產
  async function createAsset(assetData, token) {
    const res = await fetch(`${API_BASE}/assets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': token } : {})
      },
      body: JSON.stringify(assetData)
    })
    if (!res.ok) throw new Error('新增資產失敗')
    const data = await res.json()
    return data
  }

  // 設定資產狀態為 repairing
  async function setAssetStatusRepairing(idOrAssetNumber, token) {
    // 只要能轉成數字就直接呼叫 API，不查 assets.value
    let id = idOrAssetNumber
    if (typeof idOrAssetNumber === 'object' && idOrAssetNumber !== null && idOrAssetNumber.idEquipment) {
      id = idOrAssetNumber.idEquipment
    }
    id = parseInt(id, 10)
    if (isNaN(id)) throw new Error('資產 id 不正確')
    const res = await fetch(`${API_BASE}/asset/status/repairing/${id}`, {
      method: 'PUT',
      headers: {
        ...(token ? { 'Authorization': token } : {})
      }
    })
    if (!res.ok) throw new Error('設為維修中失敗')
    return await res.json()
  }

  async function setAssetStatusInUse(idOrAssetNumber, token) {
    let id = idOrAssetNumber
    if (typeof idOrAssetNumber === 'string' && !/^[0-9]+$/.test(idOrAssetNumber)) {
      const found = assets.value.find(a => a.assetNumber === idOrAssetNumber || a.id === idOrAssetNumber)
      if (found && found.idEquipment) id = found.idEquipment
    }
    // 只取數字
    if (typeof id === 'string') {
      const match = id.match(/(\d+)/)
      if (match) id = match[1]
    }
    const res = await fetch(`${API_BASE}/asset/status/in_use/${id}`, {
      method: 'PUT',
      headers: {
        ...(token ? { 'Authorization': token } : {})
      }
    })
    if (!res.ok) throw new Error('設為使用中失敗')
    return await res.json()
  }

  return {
    assets,
    getAll,
    getById,
    getByOwnerId,
    add,
    update,
    fetchUserAssets,
    getAssetDetail,
    createAsset,
    updateAsset,
    setAssetStatusRepairing,
    setAssetStatusInUse,
    deleteAsset
  }
})
