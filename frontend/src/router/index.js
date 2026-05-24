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
          meta: { titleKey: 'dashboard.title' },
        },
        {
          path: 'assets',
          name: 'AssetList',
          component: () => import('@/views/assets/AssetListView.vue'),
          meta: { titleKey: 'asset.title' },
        },
        {
          path: 'assets/new',
          name: 'AssetNew',
          component: () => import('@/views/assets/AssetFormView.vue'),
          meta: { titleKey: 'asset.addAsset', requiresManager: true },
        },
        {
          path: 'assets/:id',
          name: 'AssetDetail',
          component: () => import('@/views/assets/AssetDetailView.vue'),
          meta: { titleKey: 'assetDetail.assetDetail' },
        },
        {
          path: 'assets/:id/edit',
          name: 'AssetEdit',
          component: () => import('@/views/assets/AssetFormView.vue'),
          meta: { titleKey: 'asset.editAsset', requiresManager: true },
        },
        {
          path: 'requests',
          name: 'RequestList',
          component: () => import('@/views/requests/RequestListView.vue'),
          meta: { titleKey: 'request.title' },
        },
        {
          path: 'requests/new',
          name: 'RequestNew',
          component: () => import('@/views/requests/RequestFormView.vue'),
          meta: { titleKey: 'request.newRequest' },
        },
        {
          path: 'requests/:id',
          name: 'request-detail',
          component: () => import('@/views/requests/RequestDetailView.vue'),
          props: true,
          meta: { titleKey: 'request.info' },
        },
        {
          path: 'requests/:id/edit',
          name: 'RequestEdit',
          component: () => import('@/views/requests/RequestEditView.vue'),
          meta: { titleKey: 'request.editRequest' },
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
