<script setup>
import { computed, onMounted, ref } from 'vue'
import { Columns3, Copy, ExternalLink, Filter, Search, Trash2 } from 'lucide-vue-next'
import { getVolumes } from '@/services/colimaApi'

const volumes = ref([])
const loading = ref(true)
const error = ref(null)
const search = ref('')

const filteredVolumes = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return volumes.value
  return volumes.value.filter((volume) =>
    volume.name.toLowerCase().includes(q) ||
    (volume.driver || '').toLowerCase().includes(q) ||
    (volume.mountpoint || '').toLowerCase().includes(q)
  )
})

async function loadVolumes() {
  loading.value = true
  error.value = null

  try {
    volumes.value = await getVolumes()
  } catch (err) {
    error.value = err.message || 'Could not load volumes'
  } finally {
    loading.value = false
  }
}

function relativeTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  const diffMin = Math.max(0, Math.floor((Date.now() - date.getTime()) / 60000))
  if (diffMin < 60) return `${diffMin} minutes ago`
  const diffHours = Math.floor(diffMin / 60)
  if (diffHours < 24) return `${diffHours} hours ago`
  return `${Math.floor(diffHours / 24)} days ago`
}

onMounted(loadVolumes)
</script>

<template>
  <section class="page">
    <div class="page-title-row">
      <h1 class="page-title">Volumes</h1>
      <a href="#" class="feedback-link">Give feedback</a>
      <ExternalLink size="17" color="#2563eb" />
    </div>

    <p class="page-subtitle">
      Manage your volumes, view usage, and inspect their contents.
      <a href="#" class="learn-link">Learn more</a>
      <ExternalLink size="17" color="#2563eb" />
    </p>

    <div class="toolbar with-right">
      <div class="toolbar-left">
        <label class="search-box">
          <Search size="30" />
          <input v-model="search" placeholder="Search" />
        </label>

        <button class="icon-button"><Filter size="31" /></button>
        <button class="icon-button"><Columns3 size="31" /></button>
      </div>

      <button class="primary-button">Create</button>
    </div>

    <div v-if="loading" class="loading-state">Loading volumes...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>

    <div v-else class="table-panel">
      <table class="docker-table">
        <thead>
          <tr>
            <th class="check-cell"><div class="checkbox"></div></th>
            <th class="status-cell"></th>
            <th>Name <span class="sort-arrow">↑</span></th>
            <th>Created</th>
            <th>Size</th>
            <th class="actions-cell">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="volume in filteredVolumes" :key="volume.name">
            <td><div class="checkbox"></div></td>
            <td><span class="status-dot" :class="{ running: volume.in_use }"></span></td>
            <td>{{ volume.name }}</td>
            <td>{{ relativeTime(volume.created_at) }}</td>
            <td>{{ volume.size_text }}</td>
            <td class="actions-cell">
              <div class="action-buttons">
                <button title="Copy volume name" @click="navigator.clipboard?.writeText(volume.name)">
                  <Copy size="28" />
                </button>
                <button class="danger"><Trash2 size="28" /></button>
              </div>
            </td>
          </tr>

          <tr v-if="filteredVolumes.length === 0">
            <td colspan="6" class="empty-state">No volumes match your search.</td>
          </tr>
        </tbody>
      </table>

      <div style="text-align: right; padding: 16px; font-size: 18px;">
        Showing {{ filteredVolumes.length }} items
      </div>
    </div>
  </section>
</template>
