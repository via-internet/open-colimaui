<script setup>
import { onMounted, ref } from 'vue'
import { API_BASE, getHealth } from '@/services/colimaApi'

const health = ref('checking')
const error = ref(null)

async function testConnection() {
  health.value = 'checking'
  error.value = null

  try {
    const result = await getHealth()
    health.value = result.status === 'ok' ? 'online' : 'unknown'
  } catch (err) {
    health.value = 'offline'
    error.value = err.message
  }
}

onMounted(testConnection)
</script>

<template>
  <section class="page">
    <h1 class="page-title">Extensions</h1>
    <p class="page-subtitle">Demo settings and backend status.</p>

    <div class="simple-card" style="margin-top: 32px;">
      <h2>Backend API</h2>
      <p><strong>URL:</strong> {{ API_BASE }}</p>
      <p><strong>Status:</strong> {{ health }}</p>
      <p v-if="error"><strong>Error:</strong> {{ error }}</p>

      <button class="primary-button" @click="testConnection">Test connection</button>
    </div>
  </section>
</template>
