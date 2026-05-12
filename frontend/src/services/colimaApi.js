const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed: ${response.status}`)
  }

  return response.json()
}

export function getHealth() {
  return request('/health')
}

export function getColimaInfo() {
  return request('/colima/info')
}

export function getContainers() {
  return request('/colima/containers')
}

export function startContainer(containerId) {
  return request(`/colima/containers/${containerId}/start`, { method: 'POST' })
}

export function stopContainer(containerId) {
  return request(`/colima/containers/${containerId}/stop`, { method: 'POST' })
}

export function getImages() {
  return request('/colima/images')
}

export function runImage(image) {
  return request('/colima/images/run', {
    method: 'POST',
    body: JSON.stringify({ image })
  })
}

export function getVolumes() {
  return request('/colima/volumes')
}

export { API_BASE }
