<script setup>
import { computed, onMounted, ref } from 'vue'
import { Cpu, Database, HardDrive, RefreshCw, Server } from 'lucide-vue-next'
import { getContainers, getColimaInfo, getImages } from '@/services/colimaApi'

const info = ref(null)
const containers = ref([])
const images = ref([])
const loading = ref(true)
const error = ref(null)

const memoryGb = computed(() => {
  if (!info.value?.memory_total) return '-'
  return (info.value.memory_total / 1024 / 1024 / 1024).toFixed(2)
})

const runningPercent = computed(() => {
  if (!info.value?.containers) return 0
  return Math.round((info.value.containers_running / info.value.containers) * 100)
})

async function loadData() {
  loading.value = true
  error.value = null

  try {
    const [colimaInfo, colimaContainers, colimaImages] = await Promise.all([
      getColimaInfo(),
      getContainers(),
      getImages()
    ])

    info.value = colimaInfo
    containers.value = colimaContainers
    images.value = colimaImages
  } catch (err) {
    error.value = err.message || 'Could not load Colima data'
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <section class="page">
    <header class="page-header">
      <div>
        <h1 class="page-title">Colima Dashboard</h1>
        <p class="page-subtitle">Live overview of Colima runtime, containers and images.</p>
      </div>

      <button class="primary-button" @click="loadData">
        <RefreshCw size="16" />
        Refresh
      </button>
    </header>

    <div v-if="loading" class="loading-box">Loading Colima information...</div>
    <div v-else-if="error" class="error-box">{{ error }}</div>

    <template v-else>
      <div class="stats-grid">
        <article class="stat-card card card-padding">
          <div class="stat-icon"><Server size="22" /></div>
          <span>Status</span>
          <strong>{{ info.status }}</strong>
        </article>

        <article class="stat-card card card-padding">
          <div class="stat-icon"><Database size="22" /></div>
          <span>Containers</span>
          <strong>{{ info.containers }}</strong>
        </article>

        <article class="stat-card card card-padding">
          <div class="stat-icon"><ActivityIcon /></div>
          <span>Running</span>
          <strong>{{ info.containers_running }}</strong>
        </article>

        <article class="stat-card card card-padding">
          <div class="stat-icon"><HardDrive size="22" /></div>
          <span>Images</span>
          <strong>{{ info.images }}</strong>
        </article>

        <article class="stat-card card card-padding">
          <div class="stat-icon"><Cpu size="22" /></div>
          <span>CPUs</span>
          <strong>{{ info.cpus }}</strong>
        </article>

        <article class="stat-card card card-padding">
          <div class="stat-icon"><HardDrive size="22" /></div>
          <span>Memory</span>
          <strong>{{ memoryGb }} GB</strong>
        </article>
      </div>

      <div class="dashboard-grid">
        <section class="card card-padding">
          <h2>Engine Information</h2>

          <dl class="info-list">
            <div>
              <dt>Server Version</dt>
              <dd>{{ info.server_version }}</dd>
            </div>
            <div>
              <dt>API Version</dt>
              <dd>{{ info.api_version }}</dd>
            </div>
            <div>
              <dt>Operating System</dt>
              <dd>{{ info.os }}</dd>
            </div>
            <div>
              <dt>Architecture</dt>
              <dd>{{ info.architecture }}</dd>
            </div>
            <div>
              <dt>Kernel</dt>
              <dd>{{ info.kernel_version }}</dd>
            </div>
            <div>
              <dt>Docker Root</dt>
              <dd>{{ info.docker_root_dir }}</dd>
            </div>
          </dl>
        </section>

        <section class="card card-padding">
          <h2>Container Health</h2>

          <div class="progress-header">
            <span>Running Containers</span>
            <strong>{{ runningPercent }}%</strong>
          </div>

          <div class="progress">
            <div :style="{ width: `${runningPercent}%` }"></div>
          </div>

          <div class="mini-stats">
            <span>Running: {{ info.containers_running }}</span>
            <span>Paused: {{ info.containers_paused }}</span>
            <span>Stopped: {{ info.containers_stopped }}</span>
          </div>
        </section>
      </div>

      <section class="card card-padding recent">
        <h2>Recent Containers</h2>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Image</th>
                <th>Status</th>
                <th>ID</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="container in containers.slice(0, 6)" :key="container.id">
                <td>{{ container.name }}</td>
                <td>{{ container.image }}</td>
                <td>
                  <span class="badge" :class="container.status || 'default'">
                    {{ container.status }}
                  </span>
                </td>
                <td>{{ container.id }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </section>
</template>

<script>
export default {
  components: {
    ActivityIcon: {
      template: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>'
    }
  }
}
</script>

<style scoped>
.primary-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 22px;
}

.stat-card span {
  display: block;
  color: #64748b;
  font-size: 13px;
  font-weight: 800;
  margin-top: 14px;
}

.stat-card strong {
  display: block;
  color: #0f172a;
  font-size: 28px;
  margin-top: 4px;
  text-transform: capitalize;
}

.stat-icon {
  color: #2563eb;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 22px;
  margin-bottom: 22px;
}

h2 {
  margin: 0 0 18px;
  color: #0f172a;
}

.info-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

dt {
  color: #64748b;
  font-size: 13px;
  font-weight: 800;
}

dd {
  margin: 5px 0 0;
  color: #111827;
  font-weight: 800;
  word-break: break-word;
}

.progress-header,
.mini-stats {
  display: flex;
  justify-content: space-between;
  color: #475569;
  font-weight: 800;
}

.progress {
  height: 14px;
  border-radius: 999px;
  background: #e5e7eb;
  overflow: hidden;
  margin: 18px 0;
}

.progress div {
  height: 100%;
  background: #2563eb;
}

.mini-stats {
  gap: 10px;
  flex-wrap: wrap;
  font-size: 13px;
}

@media (max-width: 1180px) {
  .stats-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 680px) {
  .stats-grid,
  .info-list {
    grid-template-columns: 1fr;
  }
}
</style>
