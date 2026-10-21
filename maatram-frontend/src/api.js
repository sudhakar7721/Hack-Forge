const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
async function req(path, opts = {}) {
  const res = await fetch(BASE + path, { headers: { 'Content-Type': 'application/json' }, ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined })
  if (!res.ok) { let d; try { d = (await res.json()).detail } catch {} ; throw new Error(d || res.statusText) }
  return res.status === 204 ? null : res.json()
}
const qs = o => '?' + new URLSearchParams(Object.fromEntries(Object.entries(o).filter(([, v]) => v !== '' && v != null)))
export const api = {
  cycles: () => req('/cycles'),
  createCycle: b => req('/cycles', { method: 'POST', body: b }),
  compare: years => req('/cycles/compare' + qs({ years: years.join(',') })),
  apps: f => req('/applications' + qs(f)),
  saveDraft: (b, id) => id ? req(`/applications/${id}`, { method: 'PUT', body: b }) : req('/applications', { method: 'POST', body: b }),
  submit: id => req(`/applications/${id}/submit`, { method: 'POST' }),
  bulk: b => req('/applications/bulk', { method: 'POST', body: b }),
  audit: id => req(`/applications/${id}/audit`),
  events: (sid, f) => req(`/students/${sid}/events` + qs(f)),
  addEvent: (sid, b) => req(`/students/${sid}/events`, { method: 'POST', body: b }),
  replay: (sid, b) => req(`/students/${sid}/replay`, { method: 'POST', body: b }),
  addCareer: (aid, b) => req(`/alumni/${aid}/careers`, { method: 'POST', body: b }),
  profile: aid => req(`/alumni/${aid}/profile`),
  byCompany: c => req('/alumni/search' + qs({ company: c })),
  presign: b => req('/uploads/presign', { method: 'POST', body: b }),
  confirm: key => req('/uploads/confirm', { method: 'POST', body: { key } }),
  docs: sid => req(`/students/${sid}/documents`),
}
