const API_BASE = 'http://localhost:8000'

export async function apiCall(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    })
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('API call failed:', error)
    throw error
  }
}

export async function getStats() {
  return apiCall('/api/dashboard/stats')
}

export async function getPosts(platform = '', status = '') {
  const params = new URLSearchParams()
  if (platform) params.set('platform', platform)
  if (status) params.set('status', status)
  return apiCall(`/api/posts?${params}`)
}

export async function searchPosts(query) {
  return apiCall(`/api/posts/search?q=${encodeURIComponent(query)}`)
}

export async function getSimilarPosts(content) {
  return apiCall('/api/posts/search/similar', {
    method: 'POST',
    body: JSON.stringify({ content })
  })
}

export async function getPost(id) {
  return apiCall(`/api/posts/${id}`)
}

export async function createPost(content, metadata) {
  return apiCall('/api/posts', {
    method: 'POST',
    body: JSON.stringify({ content, metadata })
  })
}

export async function updatePost(id, content, metadata) {
  return apiCall(`/api/posts/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ content, metadata })
  })
}

export async function deletePost(id) {
  return apiCall(`/api/posts/${id}`, { method: 'DELETE' })
}

export async function publishPost(id) {
  return apiCall(`/api/posts/${id}/publish`, { method: 'POST' })
}

export async function generateContent(topic, platforms, tone) {
  return apiCall('/api/generate', {
    method: 'POST',
    body: JSON.stringify({ topic, platforms, tone })
  })
}
