<script setup>
import { computed, onMounted, ref } from 'vue'
import { Columns3, ExternalLink, Filter, Play, RefreshCw, Search, MoreVertical, Trash2 } from 'lucide-vue-next'
import { getImages, runImage } from '@/services/colimaApi'

const images = ref([])
const loading = ref(true)
const error = ref(null)
const actionMessage = ref('')
const search = ref('')

const filteredImages = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return images.value
  return images.value.filter((image) =>
    image.name.toLowerCase().includes(q) ||
    image.tag.toLowerCase().includes(q) ||
    image.id.toLowerCase().includes(q)
  )
})

const totalSize = computed(() => {
  const total = images.value.reduce((sum, image) => sum + Number(image.size || 0), 0)
  return formatBytes(total)
})

async function loadImages() {
  loading.value = true
  error.value = null
  try {
    images.value = await getImages()
  } catch (err) {
    error.value = err.message || 'Could not load images'
  } finally {
    loading.value = false
  }
}

async function handleRun(image) {
  actionMessage.value = ''
  error.value = null

  const imageRef = image.tags?.[0] || image.name
  try {
    const result = await runImage(imageRef)
    actionMessage.value = `Started container ${result.container_name} from ${imageRef}`
  } catch (err) {
    error.value = err.message || `Could not run image ${imageRef}`
  }
}

function formatBytes(size) {
  if (!size) return '0 Bytes'
  const units = ['Bytes', 'kB', 'MB', 'GB', 'TB']
  let value = Number(size)
  let unit = 0
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024
    unit += 1
  }
  return unit === 0 ? `${value} ${units[unit]}` : `${value.toFixed(2)} ${units[unit]}`
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

onMounted(loadImages)
</script>

<template>
  <section class="page">
    <div class="page-title-row">
      <h1 class="page-title">Images</h1>
      <a href="#" class="feedback-link">Give feedback</a>
      <ExternalLink size="17" color="#2563eb" />
    </div>

    <p class="page-subtitle">
      View and manage your local and registry images.
      <a href="#" class="learn-link">Learn more</a>
      <ExternalLink size="17" color="#2563eb" />
    </p>

    <div class="tabs">
      <button class="tab active">Local</button>
      <button class="tab">Registry repositories</button>
    </div>

    <div class="usage-row">
      <div class="usage-left">
        <div>
          <div class="usage-bar"><div></div></div>
          <div>{{ totalSize }} in use&nbsp;&nbsp; {{ images.length }} images</div>
        </div>
      </div>

      <div class="refresh-row">
        <span>Last refresh: just now</span>
        <button class="icon-button" @click="loadImages"><RefreshCw size="31" /></button>
      </div>
    </div>

    <div class="toolbar">
      <label class="search-box">
        <Search size="30" />
        <input v-model="search" placeholder="Search" />
      </label>

      <button class="icon-button"><Filter size="31" /></button>
      <button class="icon-button"><Columns3 size="31" /></button>
    </div>

    <div v-if="actionMessage" class="loading-state">{{ actionMessage }}</div>
    <div v-if="loading" class="loading-state">Loading images...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>

    <div v-else class="table-panel">
      <table class="docker-table">
        <thead>
          <tr>
            <th class="check-cell"><div class="checkbox"></div></th>
            <th class="status-cell"></th>
            <th>Name</th>
            <th>Tag</th>
            <th>Image ID</th>
            <th>Created</th>
            <th>Size</th>
            <th class="actions-cell">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="image in filteredImages" :key="image.id">
            <td><div class="checkbox"></div></td>
            <td><span class="status-dot"></span></td>
            <td>{{ image.name }}</td>
            <td>{{ image.tag }}</td>
            <td>{{ image.id.replace('sha256:', '') }}</td>
            <td>{{ relativeTime(image.created) }}</td>
            <td>{{ image.size_text }}</td>
            <td class="actions-cell">
              <div class="action-buttons">
                <button title="Run image" @click="handleRun(image)"><Play size="30" /></button>
                <button><MoreVertical size="30" /></button>
                <span class="action-divider"></span>
                <button class="danger"><Trash2 size="28" /></button>
              </div>
            </td>
          </tr>

          <tr v-if="filteredImages.length === 0">
            <td colspan="8" class="empty-state">No images match your search.</td>
          </tr>
        </tbody>
      </table>

      <div style="text-align: right; padding: 16px; font-size: 18px;">
        Showing {{ filteredImages.length }} items
      </div>
    </div>
  </section>
</template>
