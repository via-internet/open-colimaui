const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(path) {
  const response = await fetch(`${API_BASE}${path}`)

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed: ${response.status}`)
  }

  return response.json()
}

export function getHealth() {
  return request('/health')
}

export function getDockerInfo() {
  return request('/docker/info')
}

export function getContainers() {
  return request('/docker/containers')
}

export function getImages() {
  return request('/docker/images')
}

export function getVolumes() {
  return request('/docker/volumes')
}

export { API_BASE }
