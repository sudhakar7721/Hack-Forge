import { useState } from 'react'
import { api } from '../api'
const ALLOWED = ['application/pdf', 'image/png', 'image/jpeg'], MAX = 5 * 1024 * 1024
export default function Uploads() {
  const [sid, setSid] = useState(''); const [docs, setDocs] = useState([]); const [msg, setMsg] = useState(null); const [busy, setBusy] = useState(false)
  const onFile = async e => {
    const file = e.target.files[0]; if (!file) return
    if (!ALLOWED.includes(file.type)) return setMsg({ err: 'Only PDF, PNG or JPEG files are allowed' })
    if (file.size > MAX) return setMsg({ err: 'File exceeds the 5 MB limit' })
    setBusy(true)
    try {
      const p = await api.presign({ student_id: Number(sid), filename: file.name, content_type: file.type, size: file.size })
      const r = await fetch(p.url, { method: 'PUT', headers: { 'Content-Type': file.type }, body: file })
      if (!r.ok) throw new Error('Storage upload failed')
      await api.confirm(p.key); setMsg({ ok: 'Uploaded: ' + file.name }); setDocs(await api.docs(sid))
    } catch (err) { setMsg({ err: err.message }) } finally { setBusy(false); e.target.value = '' } }
  return (<section className="card"><h2>Smart Uploads</h2>
    <div className="row"><input placeholder="Student ID" value={sid} onChange={e => setSid(e.target.value)} />
      <button className="secondary" onClick={async () => setDocs(await api.docs(sid))}>List documents</button></div>
    <input type="file" disabled={!sid || busy} onChange={onFile} />
    <p className="hint">PDF/PNG/JPEG, max 5 MB. Checked here and again on the server before a short-lived signed URL is issued.</p>
    {msg?.ok && <p className="ok">{msg.ok}</p>}{msg?.err && <p className="err">{msg.err}</p>}
    <ul>{docs.map(d => <li key={d.id}>{d.filename} ({Math.round(d.size / 1024)} KB) {d.url && <a href={d.url} target="_blank" rel="noreferrer">view</a>}</li>)}</ul></section>)
}
