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

  return { assets, getAll, getById, getByOwnerId, add, update, fetchUserAssets, getAssetDetail, createAsset, updateAsset }
})
