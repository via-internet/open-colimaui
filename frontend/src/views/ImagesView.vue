<script setup>
import { onMounted, ref } from 'vue'
import { getImages } from '@/services/dockerApi'

const images = ref([])
const loading = ref(true)
const error = ref(null)

function formatSize(bytes) {
  if (!bytes) return '-'
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

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

onMounted(loadImages)
</script>

<template>
  <section class="page">
    <h1 class="page-title">Images</h1>
    <p class="page-subtitle">View local Docker images.</p>

    <div v-if="loading" class="loading-state">Loading images...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>

    <div v-else class="simple-card">
      <table class="simple-table">
        <thead>
          <tr>
            <th>Tags</th>
            <th>Size</th>
            <th>ID</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="image in images" :key="image.id">
            <td>{{ image.tags.length ? image.tags.join(', ') : '<none>' }}</td>
            <td>{{ formatSize(image.size) }}</td>
            <td>{{ image.id }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
