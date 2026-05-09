<script setup>
import { onMounted, ref } from 'vue'
import { getVolumes } from '@/services/dockerApi'

const volumes = ref([])
const loading = ref(true)
const error = ref(null)

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

onMounted(loadVolumes)
</script>

<template>
  <section class="page">
    <h1 class="page-title">Volumes</h1>
    <p class="page-subtitle">View Docker volumes.</p>

    <div v-if="loading" class="loading-state">Loading volumes...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>

    <div v-else class="simple-card">
      <table class="simple-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Driver</th>
            <th>Mountpoint</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="volume in volumes" :key="volume.name">
            <td>{{ volume.name }}</td>
            <td>{{ volume.driver }}</td>
            <td>{{ volume.mountpoint }}</td>
            <td>{{ volume.created_at }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
