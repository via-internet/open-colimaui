<script setup>
import { computed, onMounted, ref } from 'vue'
import { ChevronDown, ChevronRight, Columns3, ExternalLink, MoreVertical, Play, Search, Square, Trash2 } from 'lucide-vue-next'
import { API_BASE, getContainers, getDockerInfo, startContainer, stopContainer } from '@/services/dockerApi'

const containers = ref([])
const info = ref(null)
const loading = ref(true)
const error = ref(null)
const actionMessage = ref('')
const search = ref('')
const onlyRunning = ref(false)
const expandedProjects = ref(new Set())

const groupedRows = computed(() => {
  const q = search.value.trim().toLowerCase()
  const filtered = containers.value.filter((container) => {
    const matchesSearch = !q || container.name.toLowerCase().includes(q) || container.image.toLowerCase().includes(q) || (container.project || '').toLowerCase().includes(q)
    const matchesRunning = !onlyRunning.value || container.status === 'running'
    return matchesSearch && matchesRunning
  })

  const projectMap = new Map()
  const loose = []

  for (const container of filtered) {
    if (container.project) {
      if (!projectMap.has(container.project)) projectMap.set(container.project, [])
      projectMap.get(container.project).push(container)
    } else {
      loose.push(container)
    }
  }

  const rows = []
  for (const [project, children] of projectMap.entries()) {
    rows.push({
      type: 'project',
      key: `project:${project}`,
      project,
      children,
      running: children.some((child) => child.status === 'running'),
      portsText: '-',
      cpu: children.reduce((sum, child) => sum + Number(child.cpu_percent || 0), 0),
      lastStarted: newestStarted(children)
    })

    if (expandedProjects.value.has(project)) {
      for (const child of children) rows.push({ type: 'container', key: child.id, container: child, child: true })
    }
  }

  for (const container of loose) rows.push({ type: 'container', key: container.id, container, child: false })

  return rows
})

const cpuTotal = computed(() => Math.max(0.01, (info.value?.containers_running || 0) * 0.31).toFixed(2))
const memoryText = computed(() => {
  const total = info.value?.memory_total || 0
  if (!total) return '0GB / 0GB'
  const totalGb = total / 1024 / 1024 / 1024
  const usedGb = Math.min(totalGb, Math.max(0.1, (info.value?.containers_running || 0) * 0.54))
  return `${usedGb.toFixed(2)}GB / ${totalGb.toFixed(2)}GB`
})

async function loadData() {
  loading.value = true
  error.value = null
  try {
    const [dockerInfo, dockerContainers] = await Promise.all([getDockerInfo(), getContainers()])
    info.value = dockerInfo
    containers.value = dockerContainers
    expandedProjects.value = new Set(dockerContainers.map((item) => item.project).filter(Boolean))
  } catch (err) {
    error.value = err.message || 'Could not load Docker containers'
  } finally {
    loading.value = false
  }
}

async function handleStart(container) {
  try {
    await startContainer(container.full_id)
    actionMessage.value = `Started ${container.name}`
    await loadData()
  } catch (err) {
    error.value = err.message || `Could not start ${container.name}`
  }
}

async function handleStop(container) {
  try {
    await stopContainer(container.full_id)
    actionMessage.value = `Stopped ${container.name}`
    await loadData()
  } catch (err) {
    error.value = err.message || `Could not stop ${container.name}`
  }
}

function openConsole(container) {
  window.open(`${API_BASE}${container.console_url}`, '_blank', 'noopener,noreferrer')
}

function toggleProject(project) {
  const next = new Set(expandedProjects.value)
  next.has(project) ? next.delete(project) : next.add(project)
  expandedProjects.value = next
}

function newestStarted(children) {
  const dates = children.map((child) => child.last_started || child.state?.started_at).filter(Boolean).sort()
  return dates.length ? relativeTime(dates[dates.length - 1]) : '-'
}

function relativeTime(value) {
  if (!value || value.startsWith('0001-')) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  const diffMin = Math.max(0, Math.floor((Date.now() - date.getTime()) / 60000))
  if (diffMin < 1) return 'just now'
  if (diffMin < 60) return `${diffMin} minutes ago`
  const diffHours = Math.floor(diffMin / 60)
  if (diffHours < 24) return `${diffHours} hours ago`
  return `${Math.floor(diffHours / 24)} days ago`
}

function statusClass(status) {
  return status === 'running' ? 'running' : ''
}

function cpuFor(container) {
  return container.status === 'running' ? '0.12%' : '0%'
}

onMounted(loadData)
</script>

<template>
  <section class="page">
    <div class="page-title-row">
      <h1 class="page-title">Containers</h1>
      <a href="#" class="feedback-link">Give feedback</a>
      <ExternalLink size="17" color="#2563eb" />
    </div>

    <p class="page-subtitle">
      View all your running containers and applications.
      <a href="#" class="learn-link">Learn more</a>
      <ExternalLink size="17" color="#2563eb" />
    </p>

    <div class="metric-grid">
      <div>
        <div class="metric-label">Container CPU usage <span class="info-dot">i</span></div>
        <div class="metric-value"><strong>{{ cpuTotal }}%</strong> / {{ (info?.cpus || 8) * 100 }}% <span>({{ info?.cpus || 8 }} CPUs available)</span></div>
      </div>

      <div>
        <div class="metric-label">Container memory usage <span class="info-dot">i</span></div>
        <div class="metric-value"><strong>{{ memoryText.split(' / ')[0] }}</strong> / {{ memoryText.split(' / ')[1] }}</div>
      </div>

      <a href="#" class="show-link">Show charts</a>
    </div>

    <div class="toolbar">
      <label class="search-box">
        <Search size="30" />
        <input v-model="search" placeholder="Search" />
      </label>

      <button class="icon-button" title="Columns"><Columns3 size="31" /></button>

      <label class="switch-row">
        <button class="switch" :class="{ active: onlyRunning }" type="button" @click="onlyRunning = !onlyRunning"></button>
        <span>Only show running containers</span>
      </label>
    </div>

    <div v-if="actionMessage" class="loading-state">{{ actionMessage }}</div>
    <div v-if="loading" class="loading-state">Loading containers...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>

    <div v-else class="table-panel">
      <table class="docker-table">
        <thead>
          <tr>
            <th class="check-cell"><div class="checkbox"></div></th>
            <th class="expand-cell"></th>
            <th class="status-cell"></th>
            <th>Name <span class="sort-arrow">↑</span></th>
            <th>Port(s)</th>
            <th>CPU (%)</th>
            <th>Last started</th>
            <th class="actions-cell">Actions</th>
          </tr>
        </thead>

        <tbody>
          <template v-for="row in groupedRows" :key="row.key">
            <tr v-if="row.type === 'project'" class="project-row">
              <td><div class="checkbox"></div></td>
              <td class="expand-cell">
                <button class="icon-button" @click="toggleProject(row.project)">
                  <ChevronDown v-if="expandedProjects.has(row.project)" size="25" />
                  <ChevronRight v-else size="25" />
                </button>
              </td>
              <td><span class="status-dot" :class="{ running: row.running }"></span></td>
              <td><a href="#" class="name-link">{{ row.project }}</a></td>
              <td>{{ row.portsText }}</td>
              <td>{{ row.cpu.toFixed(0) }}%</td>
              <td>{{ row.lastStarted }}</td>
              <td class="actions-cell"><span class="action-buttons"><button><MoreVertical size="30" /></button></span></td>
            </tr>

            <tr v-else class="child-row">
              <td><div class="checkbox"></div></td>
              <td class="expand-cell"></td>
              <td><span class="status-dot" :class="statusClass(row.container.status)"></span></td>
              <td :class="{ 'child-name': row.child }">
                <button class="link-button name-link" @click="openConsole(row.container)">
                  {{ row.container.name }}
                </button>
              </td>
              <td>
                <template v-if="row.container.port_links?.length">
                  <a
                    v-for="port in row.container.port_links"
                    :key="port.label"
                    class="port-link"
                    :href="port.url"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {{ port.label }}
                  </a>
                </template>
                <template v-else>-</template>
              </td>
              <td>{{ cpuFor(row.container) }}</td>
              <td>{{ relativeTime(row.container.last_started || row.container.state?.started_at) }}</td>
              <td class="actions-cell">
                <div class="action-buttons">
                  <button v-if="row.container.status === 'running'" title="Stop container" @click="handleStop(row.container)">
                    <Square size="27" fill="#2563eb" />
                  </button>
                  <button v-else title="Start container" @click="handleStart(row.container)">
                    <Play size="30" />
                  </button>
                  <button><MoreVertical size="30" /></button>
                  <span class="action-divider"></span>
                  <button class="danger" title="Delete placeholder"><Trash2 size="28" /></button>
                </div>
              </td>
            </tr>
          </template>

          <tr v-if="groupedRows.length === 0">
            <td colspan="8" class="empty-state">No containers match your filters.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.link-button {
  border: 0;
  background: transparent;
  padding: 0;
  font: inherit;
  cursor: pointer;
}
</style>
