const BASE = '/api'

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...opts?.headers },
    ...opts,
  })
  if (res.status === 204) return undefined as T
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || body.violations?.join(', ') || res.statusText)
  }
  return res.json()
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (path: string) => request<void>(path, { method: 'DELETE' }),
  upload: <T>(path: string, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return fetch(`${BASE}${path}`, { method: 'POST', body: form }).then(async r => {
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText)
      return r.json() as Promise<T>
    })
  },
}
