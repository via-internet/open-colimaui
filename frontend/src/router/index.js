import { createRouter, createWebHistory } from 'vue-router'

import ContainersView from '@/views/ContainersView.vue'
import ImagesView from '@/views/ImagesView.vue'
import VolumesView from '@/views/VolumesView.vue'
import BuildsView from '@/views/BuildsView.vue'
import SettingsView from '@/views/SettingsView.vue'

const routes = [
  { path: '/', redirect: '/containers' },
  { path: '/containers', name: 'containers', component: ContainersView },
  { path: '/images', name: 'images', component: ImagesView },
  { path: '/volumes', name: 'volumes', component: VolumesView },
  { path: '/builds', name: 'builds', component: BuildsView },
  { path: '/settings', name: 'settings', component: SettingsView }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
