import { ref } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'ams_assets'

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
    return assets.value.filter((a) => a.ownerId === ownerId)
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

  return { assets, getAll, getById, getByOwnerId, add, update }
})
