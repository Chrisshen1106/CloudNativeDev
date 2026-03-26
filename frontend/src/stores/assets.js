import { ref } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'ams_assets'

const defaultAssets = [
  {
    id: 'A001',
    assetNumber: 'AST-2024-001',
    name: 'MacBook Pro 16"',
    category: 'computer',
    model: 'MacBook Pro M3 Max',
    specs: '48GB RAM, 1TB SSD',
    serialNumber: 'C02XG2JHJGH5',
    supplier: 'Apple Taiwan',
    purchaseDate: '2024-01-15',
    purchasePrice: 89900,
    location: '台北總部 3F-A302',
    ownerId: 'U001',
    department: '研發部',
    activationDate: '2024-01-20',
    warrantyExpiry: '2027-01-20',
    status: 'normal',
    notes: '',
  },
  {
    id: 'A002',
    assetNumber: 'AST-2024-002',
    name: 'iPhone 15 Pro',
    category: 'phone',
    model: 'iPhone 15 Pro',
    specs: '256GB, 鈦金色',
    serialNumber: 'F2LX3JKHD7Y8',
    supplier: 'Apple Taiwan',
    purchaseDate: '2024-02-01',
    purchasePrice: 36900,
    location: '台北總部 2F',
    ownerId: 'U001',
    department: '研發部',
    activationDate: '2024-02-05',
    warrantyExpiry: '2026-02-05',
    status: 'under_repair',
    notes: '',
  },
  {
    id: 'A003',
    assetNumber: 'AST-2024-003',
    name: 'iPad Pro 12.9"',
    category: 'tablet',
    model: 'iPad Pro M2',
    specs: '256GB, Wi-Fi + 5G',
    serialNumber: 'DMPVF2JKHD7Y',
    supplier: 'Apple Taiwan',
    purchaseDate: '2024-01-20',
    purchasePrice: 42900,
    location: '台北總部 3F-B301',
    ownerId: 'U002',
    department: '業務部',
    activationDate: '2024-01-25',
    warrantyExpiry: '2026-01-25',
    status: 'normal',
    notes: '',
  },
  {
    id: 'A004',
    assetNumber: 'AST-2024-004',
    name: 'Dell XPS 15',
    category: 'computer',
    model: 'XPS 15 9530',
    specs: '32GB RAM, 512GB SSD, RTX 4060',
    serialNumber: 'D3LXS9530KR5',
    supplier: '戴爾科技',
    purchaseDate: '2024-03-10',
    purchasePrice: 65000,
    location: '台北總部 2F-C201',
    ownerId: 'U002',
    department: '業務部',
    activationDate: '2024-03-15',
    warrantyExpiry: '2027-03-15',
    status: 'under_repair',
    notes: '',
  },
  {
    id: 'A005',
    assetNumber: 'AST-2023-005',
    name: 'Samsung Galaxy S24 Ultra',
    category: 'phone',
    model: 'Galaxy S24 Ultra',
    specs: '512GB, 幻影黑',
    serialNumber: 'R58WA9KLMN23',
    supplier: '三星電子',
    purchaseDate: '2023-12-05',
    purchasePrice: 41900,
    location: '台北總部 1F-行銷部',
    ownerId: 'U003',
    department: '行銷部',
    activationDate: '2023-12-10',
    warrantyExpiry: '2025-12-10',
    status: 'normal',
    notes: '',
  },
  {
    id: 'A006',
    assetNumber: 'AST-2023-006',
    name: 'Microsoft Surface Pro 9',
    category: 'tablet',
    model: 'Surface Pro 9',
    specs: '16GB RAM, 256GB SSD',
    serialNumber: 'MS9P4Q7RNBV2',
    supplier: '微軟台灣',
    purchaseDate: '2023-10-20',
    purchasePrice: 52000,
    location: '台北總部 1F-行銷部',
    ownerId: 'U003',
    department: '行銷部',
    activationDate: '2023-10-25',
    warrantyExpiry: '2025-10-25',
    status: 'normal',
    notes: '',
  },
  {
    id: 'A007',
    assetNumber: 'AST-2024-007',
    name: 'MacBook Air 13"',
    category: 'computer',
    model: 'MacBook Air M2',
    specs: '16GB RAM, 512GB SSD',
    serialNumber: 'C02AG2MBJRK5',
    supplier: 'Apple Taiwan',
    purchaseDate: '2024-01-08',
    purchasePrice: 42900,
    location: '台北總部 3F-A303',
    ownerId: 'U001',
    department: '研發部',
    activationDate: '2024-01-10',
    warrantyExpiry: '2027-01-10',
    status: 'normal',
    notes: '',
  },
  {
    id: 'A008',
    assetNumber: 'AST-2024-008',
    name: 'iPhone 14',
    category: 'phone',
    model: 'iPhone 14',
    specs: '128GB, 午夜色',
    serialNumber: 'F1LX3JKHD890',
    supplier: 'Apple Taiwan',
    purchaseDate: '2024-04-01',
    purchasePrice: 26900,
    location: '台北總部 2F-業務部',
    ownerId: 'U002',
    department: '業務部',
    activationDate: '2024-04-05',
    warrantyExpiry: '2026-04-05',
    status: 'normal',
    notes: '',
  },
  {
    id: 'A009',
    assetNumber: 'AST-2024-009',
    name: 'Lenovo ThinkPad X1 Carbon',
    category: 'computer',
    model: 'ThinkPad X1 Carbon Gen 11',
    specs: '32GB RAM, 1TB SSD',
    serialNumber: 'LNV1X11CG11Z',
    supplier: '聯想科技',
    purchaseDate: '2024-02-15',
    purchasePrice: 57800,
    location: '台北總部 2F-業務部',
    ownerId: 'U002',
    department: '業務部',
    activationDate: '2024-02-20',
    warrantyExpiry: '2027-02-20',
    status: 'normal',
    notes: '',
  },
  {
    id: 'A010',
    assetNumber: 'AST-2023-010',
    name: 'iPad Air 5th Gen',
    category: 'tablet',
    model: 'iPad Air M1',
    specs: '256GB, 太空灰',
    serialNumber: 'DMPVA1JKHD5Y',
    supplier: 'Apple Taiwan',
    purchaseDate: '2023-09-01',
    purchasePrice: 23900,
    location: '台北總部 1F-行銷部',
    ownerId: 'U003',
    department: '行銷部',
    activationDate: '2023-09-05',
    warrantyExpiry: '2025-09-05',
    status: 'normal',
    notes: '',
  },
]

export const useAssetsStore = defineStore('assets', () => {
  const saved = localStorage.getItem(STORAGE_KEY)
  const assets = ref(saved ? JSON.parse(saved) : defaultAssets)

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

  function updateStatus(id, status) {
    const asset = assets.value.find((a) => a.id === id)
    if (asset) {
      asset.status = status
      persist()
    }
  }

  function resetToDefault() {
    assets.value = JSON.parse(JSON.stringify(defaultAssets))
    persist()
  }

  return { assets, getAll, getById, getByOwnerId, add, update, updateStatus, resetToDefault }
})
