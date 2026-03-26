import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/',
      component: () => import('@/components/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/dashboard' },
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { title: '儀表板', titleEn: 'Dashboard' },
        },
        {
          path: 'assets',
          name: 'AssetList',
          component: () => import('@/views/assets/AssetListView.vue'),
          meta: { title: '資產列表', titleEn: 'Asset List' },
        },
        {
          path: 'assets/new',
          name: 'AssetNew',
          component: () => import('@/views/assets/AssetFormView.vue'),
          meta: { title: '新增資產', titleEn: 'Add Asset', requiresManager: true },
        },
        {
          path: 'assets/:id',
          name: 'AssetDetail',
          component: () => import('@/views/assets/AssetDetailView.vue'),
          meta: { title: '資產詳情', titleEn: 'Asset Detail' },
        },
        {
          path: 'assets/:id/edit',
          name: 'AssetEdit',
          component: () => import('@/views/assets/AssetFormView.vue'),
          meta: { title: '編輯資產', titleEn: 'Edit Asset', requiresManager: true },
        },
        {
          path: 'requests',
          name: 'RequestList',
          component: () => import('@/views/requests/RequestListView.vue'),
          meta: { title: '申請單列表', titleEn: 'Request List' },
        },
        {
          path: 'requests/new',
          name: 'RequestNew',
          component: () => import('@/views/requests/RequestFormView.vue'),
          meta: { title: '新增維修申請', titleEn: 'New Repair Request' },
        },
        {
          path: 'requests/:id',
          name: 'RequestDetail',
          component: () => import('@/views/requests/RequestDetailView.vue'),
          meta: { title: '申請單詳情', titleEn: 'Request Detail' },
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return { path: '/login' }
  }
  if (to.meta.guest && authStore.isLoggedIn) {
    return { path: '/dashboard' }
  }
  if (to.meta.requiresManager && !authStore.isManager) {
    return { path: '/dashboard' }
  }
})

export default router
